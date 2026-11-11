#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Полная выгрузка ETIM-характеристик всех товаров: _downloads/lk_etim.json"""
import base64
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://lk.iek.ru/api/etim"
PARTIAL = ROOT / "_downloads" / "lk_etim.json"


def load_env():
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v.strip().strip("'\"")
    return f"{env['LK_API_LOGIN']}:{env['LK_API_PASSWORD']}"


def get(url: str, auth: str):
    last = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={
                "Authorization": "Basic " + base64.b64encode(auth.encode()).decode(),
                "User-Agent": "iek-bel-import/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"  ! {e} — пауза {5 * attempt + 3}с", flush=True)
            time.sleep(5 * attempt + 3)
    raise RuntimeError(f"ETIM страница не получилась: {last}")


def main():
    auth = load_env()
    all_items, page = [], 1
    while page <= 300:
        d = get(f"{API}?pageSize=500&page={page}", auth)
        items = d if isinstance(d, list) else d.get("items", [])
        if not items:
            break
        all_items.extend(items)
        if page % 20 == 0:  # инкрементальное сохранение каждые 10k записей
            PARTIAL.write_text(json.dumps(all_items, ensure_ascii=False), encoding="utf-8")
            print(f"  сохранено {len(all_items)}", flush=True)
        print(f"ETIM: стр. {page}, всего {len(all_items)}", flush=True)
        if len(items) < 500:
            break
        page += 1
        time.sleep(0.5)
    PARTIAL.write_text(json.dumps(all_items, ensure_ascii=False), encoding="utf-8")
    print(f"OK: {len(all_items)} ETIM-записей → {PARTIAL}", flush=True)


if __name__ == "__main__":
    main()
