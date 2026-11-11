#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Импорт каталога ИЭК из API личного кабинета (lk.iek.ru) в формат сайта.

Использование (из корня проекта):
    python3 -I tools/import_lk.py [--kind "Модульное оборудование"] [--limit N]

Что делает:
  1. Тянет дерево групп ДДП (/api/ddp) и фильтрует по направлению (--kind).
  2. По каждой группе выкачивает товары с сущностями: цены (price/roc/rrc),
     Description, Advantages, ImgPng, LeftPeriod (гарантия), Analog.
  3. Берёт остатки со складов из _downloads/lk_residues.json (если файл есть).
  4. Считает РРЦ в BYN по курсу НБРБ (при недоступности — fallback-курс).
  5. Пишет data/lk-catalog.json со схемой build.py (site-блок копируется
     из data/catalog.json).

Креды берутся из .env (LK_API_LOGIN / LK_API_PASSWORD). Артикулы ИЭК —
реальные, названия и описания — официальные.
"""
import socket
import base64
import io
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build import slugify  # noqa: E402

API = "https://lk.iek.ru/api"
FALLBACK_RUB_BYN = 0.036  # ~27.5 RUB за BYN; используется только если НБРБ недоступен
ENTITIES = "Description,Advantages,ImgPng,ImgJpeg,rrc,roc,LeftPeriod,Analog"
# Сертификаты/паспорта/схемы НЕ вшиваем в статику — они приходят живьём
# через Worker: GET /api/docs?sku=... (актуально «а вдруг изменится»).
IMG_DIR = ROOT / "site" / "assets" / "img"


socket.setdefaulttimeout(75)


def load_env() -> tuple[str, str]:
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v.strip().strip("'\"")
    return env["LK_API_LOGIN"], env["LK_API_PASSWORD"]


def get(url: str, auth: str, retries: int = 3) -> bytes:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "Authorization": "Basic " + base64.b64encode(auth.encode()).decode(),
                "User-Agent": "iek-bel-import/1.0",
            })
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            if attempt == retries - 1:
                raise
            print(f"  ! {e}; повтор {attempt + 2}/{retries}")
            time.sleep(3)


def fetch_json(url: str, auth: str):
    return json.loads(get(url, auth).decode("utf-8"))


def nbrb_rub_byn() -> float:
    """Курс НБРБ: сколько BYN стоит 1 RUB."""
    try:
        req = urllib.request.Request(
            "https://api.nbrb.by/exrates/rates?periodicity=0",
            headers={"User-Agent": "iek-bel-import/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            rub = next(x for x in json.loads(r.read().decode("utf-8"))
                       if x["Cur_Abbreviation"] == "RUB")
        rate = rub["Cur_OfficialRate"] / rub["Cur_Scale"]
        print(f"Курс НБРБ: 1 RUB = {rate:.6f} BYN ({rub.get('Date', '')[:10]})")
        return rate
    except Exception as e:  # noqa: BLE001
        print(f"! НБРБ недоступен ({e}), fallback 1 RUB = {FALLBACK_RUB_BYN} BYN")
        return FALLBACK_RUB_BYN


def image_uri(item: dict):
    """Ссылка на фото товара: ImgPng в приоритете, затем ImgJpeg."""
    for ent in ("ImgPng", "ImgJpeg"):
        arr = item.get(ent) or []
        if arr and isinstance(arr[0], dict):
            uri = (arr[0].get("file_ref") or {}).get("uri")
            if uri:
                return uri
    return None


def download_image(sku: str, uri: str, auth: str, width: int = 640) -> bool:
    """Скачивает фото (Basic-авторизация) и сохраняет JPEG шириной `width`."""
    dest = IMG_DIR / f"{sku}.jpg"
    if dest.exists():
        return True
    try:
        req = urllib.request.Request(uri, headers={
            "Authorization": "Basic " + base64.b64encode(auth.encode()).decode(),
            "User-Agent": "iek-bel-import/1.0"})
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read()
        try:
            from PIL import Image
            im = Image.open(io.BytesIO(raw))
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGBA")
                bg = Image.new("RGB", im.size, (255, 255, 255))
                bg.paste(im, mask=im.split()[-1])
                im = bg
            elif im.mode != "RGB":
                im = im.convert("RGB")
            if im.width > width:
                im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            im.save(dest, "JPEG", quality=84, optimize=True)
        except ImportError:
            dest.write_bytes(raw)  # PIL недоступен — кладём оригинал
        return True
    except Exception:  # noqa: BLE001
        return False


def grab_images(items: list, auth: str) -> dict:
    """Скачивает фото параллельно, возвращает {sku: True/False}."""
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    jobs = [(it["art"], u) for it in items
            if (u := image_uri(it)) and not (IMG_DIR / f"{it['art']}.jpg").exists()]
    print(f"Фото: к загрузке {len(jobs)} из {len(items)} товаров")
    result = {sku: (IMG_DIR / f"{sku}.jpg").exists() for sku, _ in
              [(it["art"], None) for it in items if image_uri(it)]}
    done = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(download_image, sku, uri, auth): sku for sku, uri in jobs}
        for f in as_completed(futs):
            sku = futs[f]
            ok = f.result()
            result[sku] = ok
            done += 1
            if done % 250 == 0:
                print(f"  фото {done}/{len(jobs)}")
    return result


def main() -> None:
    args = sys.argv[1:]
    kind = "Модульное оборудование"
    limit = 0
    images = True
    if "--kind" in args:
        kind = args[args.index("--kind") + 1]
    if "--limit" in args:
        limit = int(args[args.index("--limit") + 1])
    if "--no-images" in args:
        images = False

    login, pwd = load_env()
    auth = f"{login}:{pwd}"

    # 1. дерево групп ДДП (кэш)
    cache = ROOT / "_downloads" / "lk_ddp.json"
    if cache.exists():
        ddp = json.loads(cache.read_text(encoding="utf-8"))
    else:
        ddp = fetch_json(f"{API}/ddp?format=json", auth)
        cache.write_text(json.dumps(ddp, ensure_ascii=False), encoding="utf-8")

    if kind == "__ALL__":
        groups = [g for g in ddp if "фиктивн" not in (g.get("group") or "").lower()]
        print(f"ВСЕ направления: {len(groups)} групп ДДП")
    else:
        groups = [g for g in ddp if g.get("kind") == kind]
        print(f"Направление «{kind}»: {len(groups)} групп ДДП")

    # 2. остатки со складов (локальный файл, качается отдельно)
    residues, store_abbr = {}, {}
    rfile = ROOT / "_downloads" / "lk_residues.json"
    if rfile.exists():
        res = json.loads(rfile.read_text(encoding="utf-8"))
        store_abbr = {guid: s.get("abbr", guid) for guid, s in res.get("stores", {}).items()}
        for it in res.get("shopItems", []):
            rmap = it.get("residues") or {}
            total = sum(q or 0 for q in rmap.values())
            if total:
                per = {}
                for guid, q in rmap.items():
                    if not q:
                        continue
                    abbr = store_abbr.get(guid)
                    if abbr:
                        per[abbr] = per.get(abbr, 0) + q
                    else:
                        per["др. склады"] = per.get("др. склады", 0) + q
                residues[it["sku"]] = {"total": total, "stores": per}
        print(f"Остатки: {len(residues)} SKU с ненулевым наличием")
    else:
        print("! Файла остатков нет (_downloads/lk_residues.json) — пропускаю наличие")

    rate = nbrb_rub_byn()

    # 3. товары по группам
    categories = []
    all_items = []   # сырые товары (нужны URI фото)
    all_prods = []   # собранные карточки
    n_products = 0
    partial = ROOT / "data" / "import_partial.json"
    done_groups = set()
    if partial.exists():  # докатка: пропускаем уже импортированные группы
        try:
            done_groups = {g["ddp_id"] for g in
                           json.loads(partial.read_text(encoding="utf-8"))["categories"]}
            print(f"докатка: {len(done_groups)} групп уже готовы — пропускаются")
        except Exception:
            done_groups = set()
    for gi, g in enumerate(groups, 1):
        gid, gname = g["groupId"], g["group"]
        slug = f"{slugify(gname)}-{gid.replace('.', '-')}"
        desc_ru = (g.get("desc") or {}).get("ru") if isinstance(g.get("desc"), dict) else None

        page, products, total = 1, [], None
        first_sku_prev = None
        try:
            while page <= 40:  # предохранитель: максимум 20 000 позиций на группу
                url = (f"{API}/products?groupId={gid}&pageSize=500&page={page}"
                       f"&entity={ENTITIES}&format=json")
                data = fetch_json(url, auth)
                if isinstance(data, dict):
                    items = data.get("items", [])
                    total = data.get("totalElements")
                else:
                    items = data
                if not items:
                    break
                # API проигнорировал пагинацию и отдаёт ту же страницу — выходим
                first_sku_now = items[0].get("art") if isinstance(items[0], dict) else None
                if first_sku_now and first_sku_now == first_sku_prev:
                    print(f"  ! группа {gid}: пагинация не двигается — обрываю на {len(products)}")
                    break
                first_sku_prev = first_sku_now
                products.extend(items)
                if total is not None and len(products) >= total:
                    break
                if len(items) < 500:
                    break
                page += 1
                time.sleep(0.25)
        except Exception as e:  # noqa: BLE001
            print(f"  ! группа {gid}: сбой ({e}) — пропущена, вернёмся при перезапуске")
            continue

        if limit:
            products = products[:limit]

        all_items.extend(products)
        prods = []
        for it in products:
            art = it.get("art")
            if not art:
                continue
            desc_list = it.get("Description") or []
            desc = (desc_list[0].get("desc_ru") if desc_list else None) or ""
            adv_list = it.get("Advantages") or []
            adv = " ".join(a.get("desc", "") for a in adv_list if a.get("desc"))
            stock = residues.get(art)
            rrc = it.get("rrc")

            # LeftPeriod приходит структурой: {"serviceLifeLimit","serviceLife","serviceLifeUnit","warrantyYears"}
            lp = it.get("LeftPeriod")
            life_feats = []
            if isinstance(lp, list) and lp:
                lp = lp[0]
            if isinstance(lp, dict):
                wl = lp.get("warrantyYears")
                sl = lp.get("serviceLife")
                su = lp.get("serviceLifeUnit") or "лет"
                if wl:
                    life_feats.append(f"Гарантия: {wl} лет")
                if sl:
                    life_feats.append(f"Срок службы: {sl} {su.lower()}")
            elif isinstance(lp, (str, int, float)) and lp:
                life_feats.append(f"Гарантия: {lp}")

            # аналоги (внутренние замены серий), без дублей
            analog_feats, seen_an = [], set()
            for a in (it.get("Analog") or []):
                an = a.get("analog")
                if an and an not in seen_an:
                    seen_an.add(an)
                    view = a.get("view") or "аналог"
                    analog_feats.append(f"Аналог ({view.lower()}): {an}")

            # документы и сертификаты (отдаются через прокси /docs/{file})
            docs = []
            for ent, label in (("Certificates", "сертификат"), ("Passport", "паспорт"),
                               ("WiringDiagram", "схема подключения")):
                for d in (it.get(ent) or []):
                    fr = d.get("file_ref") or {}
                    if not fr.get("name"):
                        continue
                    nm = (d.get("pubName") or d.get("name") or label)[:90]
                    docs.append({"name": nm, "type": label, "file": fr["name"]})

            prods.append({
                "sku": art,
                "title": it.get("name", art),
                "desc": (desc or adv or f"{it.get('name', art)} — продукция ИЭК, группа {gname}.")[:700],
                "features": ([f"Группа ДДП: {gid}"] + life_feats + analog_feats),
                "docs": docs[:12],
                "price": {
                    "base": it.get("price"),
                    "roc": it.get("roc"),
                    "rrc": rrc,
                    "rrc_byn": round(rrc * rate, 2) if isinstance(rrc, (int, float)) else None,
                    "stock_total": stock["total"] if stock else 0,
                    "stock_stores": list(stock["stores"].keys()) if stock else [],
                },
            })

        all_prods.extend(prods)
        done_groups.add(gid)
        partial.write_text(json.dumps(
            {"note": "инкрементальный прогресс импорта",
             "categories": [{"ddp_id": gid_} for gid_ in sorted(done_groups)]},
            ensure_ascii=False), encoding="utf-8")
        categories.append({
            "slug": slug,
            "title": gname,
            "kind": kind,
            "ddp_id": gid,
            "intro": (desc_ru or f"{gname} — официальная продукция ИЭК. Наличие и заказ у "
                                f"дистрибьюторов в Беларуси.").strip()[:600],
            "products": prods,
        })
        n_products += len(prods)
        print(f"[{gi}/{len(groups)}] {gid} {gname}: {len(prods)} товаров")

    categories = [c for c in categories if c["products"]]  # пустые группы не публикуем

    # 4. фото товаров (авторизованные ссылки lk.iek.ru/api/store/...)
    if images:
        img_map = grab_images(all_items, auth)
        for p in all_prods:
            p["img"] = bool(img_map.get(p["sku"]))
    else:
        for p in all_prods:
            p["img"] = False

    # 4. сборка итогового файла
    site = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))["site"]
    out = {"site": site, "categories": categories}
    dest = ROOT / "data" / "lk-catalog.json"
    dest.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"\nOK: {len(categories)} категорий, {n_products} товаров → {dest}")


if __name__ == "__main__":
    main()
