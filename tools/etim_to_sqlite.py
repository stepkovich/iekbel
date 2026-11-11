#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETIM JSON (410 МБ) → SQLite (etim.db): потоковый парсинг, низкий RAM."""
import ijson
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "_downloads" / "lk_etim.json"
DB = ROOT / "data" / "etim.db"

def main():
    DB.parent.mkdir(parents=True, exist_ok=True)
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE etim (sku TEXT PRIMARY KEY, class_name TEXT, features TEXT)")
    n = 0
    with open(SRC, "rb") as f:
        for it in ijson.items(f, "item"):
            sku = (it.get("Code") or "").upper()
            feats = []
            for fr in it.get("Features", []):
                a, v = fr.get("Attribute"), fr.get("value")
                if not a or v is None:
                    continue
                if a.endswith("_Code"):
                    continue  # коды ETIM оставим на потом; берём человекочитаемые
                unit = fr.get("unit")
                feats.append({"n": a.replace("_Name", ""), "v": str(v), "u": unit or ""})
            if feats:
                con.execute("INSERT OR REPLACE INTO etim VALUES (?,?,?)",
                            (sku, (it.get("class_name") or "") if it.get("Features") else "",
                             json.dumps(feats, ensure_ascii=False)))
            n += 1
            if n % 10000 == 0:
                print(f"  {n} записей...", flush=True)
    con.commit()
    cnt = con.execute("SELECT COUNT(*) FROM etim").fetchone()[0]
    con.close()
    print(f"OK: {cnt} SKU с характеристиками → {DB}")

if __name__ == "__main__":
    main()
