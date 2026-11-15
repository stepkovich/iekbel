#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Локальный dev-сервер иэк.бел: статика + тот же контракт, что у Cloudflare Worker.

Запуск: python3 -I tools/devserver.py [порт=8090]

Маршруты (полностью повторяют воркер):
  /img/{SKU}.jpg      → фото из lk.iek.ru (Basic-авторизация здесь, на сервере)
  /docs/{file}        → документы/сертификаты из lk.iek.ru
  /api/docs?sku=X     → метаданные документов товара
  /api/stock?sku=A,B  → остатки со складов ИЭК (из _downloads/lk_residues.json)
  /api/order (POST)   → сохраняет заказ в data/orders/*.json (демо-маршрутизация)
  всё остальное       → статика из site/
"""
import base64
import json
import os
import re
import sys
import time
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
CACHE = ROOT / "_downloads" / "cache"
LK = "https://lk.iek.ru"

AUTH = ""
RESIDUES = None  # {sku: {"total": n, "stores": {...}}}
IMG_URI = {}      # sku → uri фото (кэш метаданных)
DOC_META = {}     # sku → docs list (кэш метаданных)


def load_env():
    global AUTH
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v.strip().strip("'\"")
    AUTH = "Basic " + base64.b64encode(
        f"{env['LK_API_LOGIN']}:{env['LK_API_PASSWORD']}".encode()).decode()


def lk_json(path_qs: str):
    req = urllib.request.Request(LK + path_qs, headers={
        "Authorization": AUTH, "User-Agent": "iek-bel-devserver/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8"))


def lk_bytes(url: str):
    req = urllib.request.Request(url, headers={
        "Authorization": AUTH, "User-Agent": "iek-bel-devserver/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.headers.get("Content-Type", "application/octet-stream")


def load_residues():
    global RESIDUES
    f = ROOT / "_downloads" / "lk_residues.json"
    if not f.exists():
        RESIDUES = {}
        return
    data = json.loads(f.read_text(encoding="utf-8"))
    abbr = {g: ((s.get("name") or s.get("abbr") or "Склад").replace(" склад", "").strip())
            for g, s in (data.get("stores") or {}).items()}
    out = {}
    for it in data.get("shopItems", []):
        rmap = it.get("residues") or {}
        per, total = {}, 0
        for guid, q in rmap.items():
            if not q:
                continue
            total += q
            a = abbr.get(guid, "др.")
            per[a] = per.get(a, 0) + q
        if total:
            out[it["sku"].upper()] = {"total": total, "stores": per}
    RESIDUES = out
    print(f"[dev] остатки: {len(RESIDUES)} SKU")


def items_for(sku: str):
    """Товар из LK API по артикулу (кэш метаданных в памяти)."""
    if sku in IMG_URI and sku in DOC_META:
        return IMG_URI[sku], DOC_META[sku]
    d = lk_json(f"/api/products?art={sku}&entity=ImgPng,ImgJpeg,Certificates,Passport,WiringDiagram,InstallationProduct&format=json")
    item = (d if isinstance(d, list) else d.get("items", []))
    item = item[0] if item else None
    uri = None
    for ent in ("ImgPng", "ImgJpeg"):
        arr = (item or {}).get(ent) or []
        if arr and arr[0].get("file_ref", {}).get("uri"):
            uri = arr[0]["file_ref"]["uri"]
            break
    docs = []
    for ent, label in (("Certificates", "сертификат"), ("Passport", "паспорт"),
                       ("WiringDiagram", "схема подключения"), ("InstallationProduct", "руководство")):
        for x in (item or {}).get(ent) or []:
            fr = x.get("file_ref") or {}
            if fr.get("name"):
                docs.append({"name": (x.get("pubName") or x.get("name") or label)[:120],
                             "type": label, "url": "/docs/" + fr["name"]})
    IMG_URI[sku] = uri
    DOC_META[sku] = docs
    return uri, docs


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(SITE), **kw)

    def log_message(self, fmt, *args):
        pass  # не мусорим в лог

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    # ---------- служебное ----------
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _bytes(self, data, ctype, cache=True):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if cache:
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def _cached(self, name):
        """Дисковый кэш файлов: качаем один раз."""
        CACHE.mkdir(parents=True, exist_ok=True)
        p = CACHE / name
        if p.exists():
            return p.read_bytes()
        return None

    # ---------- маршруты ----------
    def do_GET(self):
        u = urlparse(self.path)
        path = unquote(u.path)

        if path.startswith("/thumb/"):
            sku = re.sub(r"^/thumb/|\.jpg$", "", path).upper()
            if not re.fullmatch(r"[A-Z0-9._-]{3,64}", sku):
                return self.send_error(400)
            data = self._cached(f"thumb-{sku}.jpg")
            if not data:
                try:
                    full = self._cached(f"img-{sku}.jpg")
                    if not full:
                        uri, _ = items_for(sku)
                        if not uri:
                            return self.send_error(404)
                        full, _ = lk_bytes(uri)
                        (CACHE / f"img-{sku}.jpg").write_bytes(full)
                    from PIL import Image, ImageOps
                    import io as _io
                    im = Image.open(_io.BytesIO(full))
                    if im.mode in ("RGBA", "LA", "P"):
                        im = im.convert("RGBA")
                        bg = Image.new("RGB", im.size, (255, 255, 255))
                        bg.paste(im, mask=im.split()[-1])
                        im = bg
                    else:
                        im = im.convert("RGB")
                    im = ImageOps.exif_transpose(im)
                    w = 480
                    if im.width > w:
                        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
                    buf = _io.BytesIO()
                    im.save(buf, "JPEG", quality=80, optimize=True)
                    data = buf.getvalue()
                    (CACHE / f"thumb-{sku}.jpg").write_bytes(data)
                except Exception as e:
                    return self.send_error(502, str(e))
            return self._bytes(data, "image/jpeg")

        if path.startswith("/img/"):
            sku = re.sub(r"^/img/|\.jpg$", "", path).upper()
            if not re.fullmatch(r"[A-Z0-9._-]{3,64}", sku):
                return self.send_error(400)
            data = self._cached(f"img-{sku}.jpg")
            if not data:
                try:
                    uri, _ = items_for(sku)
                    if not uri:
                        return self.send_error(404)
                    data, _ = lk_bytes(uri)
                    (CACHE / f"img-{sku}.jpg").write_bytes(data)
                except Exception as e:
                    return self.send_error(502, str(e))
            return self._bytes(data, "image/jpeg")

        if path.startswith("/docs/"):
            fname = path[len("/docs/"):]
            if not re.fullmatch(r"[A-Za-z0-9._-]{8,100}", fname):
                return self.send_error(400)
            data = self._cached(f"doc-{fname}")
            if not data:
                try:
                    data, ctype = lk_bytes(f"{LK}/api/store/{fname}")
                    (CACHE / f"doc-{fname}").write_bytes(data)
                except Exception as e:
                    return self.send_error(502, str(e))
            else:
                ctype = "application/pdf" if fname.endswith(".pdf") else "application/octet-stream"
            return self._bytes(data, ctype)

        if u.path == "/api/docs":
            sku = (parse_qs(u.query).get("sku") or [""])[0].strip().upper()
            if not re.fullmatch(r"[A-Z0-9._-]{3,64}", sku):
                return self._json({"error": "sku required"}, 400)
            try:
                _, docs = items_for(sku)
            except Exception as e:
                return self._json({"error": str(e)}, 502)
            return self._json({"sku": sku, "docs": docs})

        if u.path == "/api/stock":
            if RESIDUES is None:
                load_residues()
            q = (parse_qs(u.query).get("sku") or [""])[0]
            skus = [s.strip().upper() for s in q.split(",") if s.strip()][:50]
            items = {s: {"iek": {"total": RESIDUES[s]["total"],
                                 "stores": RESIDUES[s]["stores"]},
                         "partners": []}
                     for s in skus if s in RESIDUES}
            return self._json({"updated": time.strftime("%Y-%m-%dT%H:%M:%S"), "items": items})

        # брендированная 404 для статических путей
        rel = unquote(u.path).lstrip("/")
        t = SITE / rel
        has_dot = "." in Path(rel).name
        exists = (t / "index.html").exists() if not has_dot else t.exists()
        if u.path != "/" and not has_dot and not exists:
            page404 = SITE / "404.html"
            if page404.exists():
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(page404.stat().st_size))
                self.end_headers()
                self.wfile.write(page404.read_bytes())
                return
        return super().do_GET()

    def do_POST(self):
        u = urlparse(self.path)
        if u.path != "/api/order":
            return self.send_error(404)
        n = int(self.headers.get("Content-Length", 0))
        try:
            order = json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return self._json({"error": "bad json"}, 400)
        if not order.get("items") or not order.get("client", {}).get("phone"):
            return self._json({"error": "items + client.phone required"}, 400)
        oid = f"IEK-{time.strftime('%y%m%d')}-{os.urandom(3).hex().upper()}"
        order["orderId"] = oid
        d = ROOT / "data" / "orders"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{oid}.json").write_text(json.dumps(order, ensure_ascii=False, indent=1),
                                       encoding="utf-8")
        print(f"[dev] заказ {oid}: {len(order['items'])} поз. → {order.get('distributor')}")
        return self._json({"ok": True, "orderId": oid,
                           "routed": [{"target": "local-demo", "ok": True}]})


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    load_env()
    load_residues()
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"[dev] http://127.0.0.1:{port}/  (статика + прокси API ИЭК)")
    srv.serve_forever()


if __name__ == "__main__":
    main()
