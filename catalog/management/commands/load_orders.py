# -*- coding: utf-8 -*-
"""Импорт заявок из data/orders/*.json (пишет devserver/Worker) в базу.

Запуск: python manage.py load_orders   (идемпотентно — по номеру заявки)
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

from catalog.models import Order


class Command(BaseCommand):
    help = "Импорт заявок из data/orders/*.json в базу"

    def handle(self, *args, **opts):
        src = Path(__file__).resolve().parents[3] / "data" / "orders"
        files = sorted(src.glob("*.json")) if src.is_dir() else []
        created = updated = 0
        for f in files:
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except Exception as e:
                self.stderr.write(f"  ! {f.name}: {e}")
                continue
            cl = d.get("client") or {}
            created_dt = parse_datetime(d.get("created") or "") or None
            defaults = dict(
                created=created_dt,
                distributor=d.get("distributor") or "__ALL__",
                client_name=cl.get("name") or "",
                client_phone=cl.get("phone") or "",
                client_email=cl.get("email") or "",
                client_type=cl.get("type") or "",
                client_org=cl.get("org") or "",
                client_requisites=cl.get("requisites") or "",
                client_city=cl.get("city") or "",
                comment=d.get("comment") or "",
                items=d.get("items") or [],
            )
            _, was_created = Order.objects.update_or_create(
                order_id=f.stem, defaults=defaults)
            created += was_created
            updated += (not was_created)
        self.stdout.write(self.style.SUCCESS(
            f"OK: новых заявок {created}, обновлено {updated} (файлов {len(files)})"))
