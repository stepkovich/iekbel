"""Загрузка каталога ИЭК из выгрузок ЛК в базу Django.

Запуск: python manage.py load_lk
Источники: data/lk-catalog.json (товары+ДДП), _downloads/lk_etim.json (ETIM),
           _downloads/lk_residues.json (остатки).
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import DdpNode, Product

BASE = Path(__file__).resolve().parents[3]


class Command(BaseCommand):
    help = "Импорт каталога ИЭК из выгрузок ЛК (товары, ДДП, ETIM, остатки)"

    def handle(self, *args, **opts):
        data = json.loads((BASE / "data" / "lk-catalog.json").read_text(encoding="utf-8"))
        cats = data["categories"]

        # --- ДДП-узлы: L1 (01) → L2 (01.01) → L3 (01.01.01), родителям — PK после создания
        nodes = {}
        for c in cats:
            gid = c["ddp_id"]
            for lvl, pid in ((1, gid[:2]), (2, gid[:5]), (3, gid)):
                info = nodes.setdefault(pid, {"level": lvl, "kind": c.get("kind", ""), "count": 0})
                if lvl == 3:
                    info["count"] += len(c["products"])
        kind_by_l1 = {}
        for c in cats:
            kind_by_l1.setdefault(c["ddp_id"][:2], c.get("kind", ""))

        l2name = {}
        ddpf = BASE / "_downloads" / "lk_ddp.json"
        if ddpf.exists():
            for e in json.loads(ddpf.read_text(encoding="utf-8")):
                l2name.setdefault(e["groupId"][:5], e.get("section") or "")

        def make(pid, lvl):
            title = (l2name.get(pid) or f"Раздел {pid}") if lvl == 2 else kind_by_l1.get(pid[:2], pid)
            return DdpNode(ddp_id=pid, level=lvl, title=title,
                           kind=kind_by_l1.get(pid[:2], ""), products_count=nodes[pid]["count"])

        pk_map = {}
        for lvl in (1, 2, 3):
            batch = [make(pid, lvl) for pid, info in nodes.items() if info["level"] == lvl]
            DdpNode.objects.bulk_create(batch, batch_size=500, ignore_conflicts=True)
            for n in DdpNode.filter_all() if False else []:
                pass
            for n in batch:
                pk_map[n.ddp_id] = DdpNode.objects.values_list("id", flat=True).get(ddp_id=n.ddp_id)
            # родители: L2 → L1, L3 → L2
            for n in batch:
                if lvl == 2:
                    DdpNode.objects.filter(ddp_id=n.ddp_id).update(parent_id=pk_map[n.ddp_id[:2]])
                if lvl == 3:
                    DdpNode.objects.filter(ddp_id=n.ddp_id).update(parent_id=pk_map.get(n.ddp_id[:5]))
        self.stdout.write(f"ДДП-узлов: {len(pk_map)}")

        # --- остатки со складов ---
        stocks = {}
        rf = BASE / "_downloads" / "lk_residues.json"
        if rf.exists():
            res = json.loads(rf.read_text(encoding="utf-8"))
            abbr = {g: s.get("abbr", g) for g, s in (res.get("stores") or {}).items()}
            for it in res.get("shopItems", []):
                rmap = it.get("residues") or {}
                per, total = {}, 0
                for guid, q in rmap.items():
                    if not q:
                        continue
                    total += q
                    a = abbr.get(guid, guid)
                    per[a] = per.get(a, 0) + q
                if total:
                    stocks[it["sku"].upper()] = {"total": total, "stores": per}
        self.stdout.write(f"остатков: {len(stocks)} SKU")

        # --- ETIM-характеристики ---
        etim = {}
        ef = BASE / "_downloads" / "lk_etim.json"
        if ef.exists():
            for it in json.loads(ef.read_text(encoding="utf-8")):
                feats = [(f.get("Attribute"), f.get("value"), f.get("unit"))
                         for f in it.get("Features", []) if f.get("Attribute") and f.get("value")]
                if feats:
                    etim[it.get("Code", "").upper()] = feats
            self.stdout.write(f"ETIM: {len(etim)} SKU")

        # --- товары ---
        products = []
        for c in cats:
            node_pk = pk_map.get(c["ddp_id"])
            for p in c["products"]:
                sku = p["sku"].upper()
                st = stocks.get(sku, {})
                et = etim.get(sku, [])
                products.append(Product(
                    sku=sku,
                    name=(p.get("title") or "")[:250],
                    ddp_id=node_pk,
                    tm=(p.get("tm") or "IEK")[:40],
                    desc=(p.get("desc") or "")[:4000],
                    price=(p.get("price") or {}).get("base"),
                    rrc=p.get("rrc"),
                    roc=p.get("roc"),
                    stock_total=st.get("total", 0),
                    stock_stores=st.get("stores", {}),
                    features=[{"n": a, "v": v, "u": u} for a, v, u in et],
                    docs=p.get("docs", []),
                    analogs=p.get("analogs", []),
                ))
        with transaction.atomic():
            for i in range(0, len(products), 500):
                Product.objects.bulk_create(products[i:i + 500], batch_size=500,
                                            ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"Товаров загружено: {len(products)}"))
