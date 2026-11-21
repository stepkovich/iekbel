#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Потоковая разбивка lk-catalog.json на файлы по группам (экономия RAM).

Зачем: json.load всего каталога (136 МБ) в Python-объектах занимает 5-8 ГБ
и на машинах с открытым ZCode/браузером вызывает OOM. Сборка должна читать
по одной группе за раз.

Использование: python3 -I tools/split_catalog.py
Вход:  data/lk-catalog.json
Выход: data/lk-cats/_site.json   (блок "site")
       data/lk-cats/_index.json  (метаданные групп: slug, title, kind, ddp_id,
                                  intro, count, photo_sku — всё лёгкое)
       data/lk-cats/NNN-slug.json (полные группы, по одной)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "lk-catalog.json"
DEST = ROOT / "data" / "lk-cats"


def extract_top_level_objects(text: str, array_key: str):
    """Yield текстовые фрагменты объектов верхнего уровня массива array_key.

    Работает по скобочной глубине, весь файл в память не парсится (json.loads
    вызывается на каждый объект отдельно).
    """
    m = re.search(rf'"{array_key}"\s*:\s*\[', text)
    if not m:
        return
    i = m.end()
    n = len(text)
    while i < n:
        while i < n and text[i] in " \t\r\n,":
            i += 1
        if i >= n or text[i] == "]":
            return
        if text[i] != "{":
            raise ValueError(f"ожидался объект на позиции {i}")
        depth, j, instr, esc = 0, i, False, False
        while j < n:
            ch = text[j]
            if instr:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    instr = False
            else:
                if ch == '"':
                    instr = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        j += 1
                        break
            j += 1
        yield text[i:j]
        i = j


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for old in DEST.glob("*.json"):
        old.unlink()
    raw = SRC.read_text(encoding="utf-8")

    # блок "site" — маленький, парсим отдельно
    ms = re.search(r'"site"\s*:\s*(\{)', raw)
    depth, j = 0, ms.start(1)
    instr, esc = False, False
    while True:
        ch = raw[j]
        if instr:
            esc = (ch == "\\") and not esc or (esc and ch != "\\")
            if ch == '"' and not esc:
                instr = False
        else:
            if ch == '"':
                instr, esc = True, False
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
        j += 1
    site = json.loads(raw[ms.start(1):j])
    (DEST / "_site.json").write_text(json.dumps(site, ensure_ascii=False), encoding="utf-8")

    index, n = [], 0
    for frag in extract_top_level_objects(raw, "categories"):
        c = json.loads(frag)
        prods = c.get("products") or []
        photo_sku = ""
        for p in prods:
            if p.get("img", True):
                photo_sku = p["sku"]
                break
        if not photo_sku and prods:
            photo_sku = prods[0]["sku"]
        meta = {k: c.get(k) for k in ("slug", "title", "kind", "ddp_id", "intro")}
        meta["count"] = len(prods)
        meta["photo_sku"] = photo_sku
        index.append(meta)
        n += 1
        dest = DEST / f"{n:03d}-{c['slug']}.json"
        dest.write_text(json.dumps(c, ensure_ascii=False, separators=(",", ":")),
                        encoding="utf-8")
        del c, frag

    (DEST / "_index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    # снапшот для гита: свежий клон собирается без API и .env
    import subprocess
    subprocess.run(["git", "add", "-A", "."], cwd=str(DEST), check=False)
    print(f"OK: {n} групп → {DEST} ({sum(f.stat().st_size for f in DEST.glob('*.json'))//1048576} МБ)")


if __name__ == "__main__":
    sys.exit(main())
