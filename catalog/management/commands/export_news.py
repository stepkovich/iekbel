# -*- coding: utf-8 -*-
"""Выгрузка опубликованных новостей в data/news.json (+ фото в data/news_photos/).

Читает сборщик (build.py — он вне Django). Запуск перед сборкой:
    python manage.py export_news
"""
import json
import shutil
from pathlib import Path

from django.core.management.base import BaseCommand

from catalog.models import News


class Command(BaseCommand):
    help = "Выгрузка новостей для сборщика сайта"

    def handle(self, *args, **opts):
        root = Path(__file__).resolve().parents[3]
        photos = root / "data" / "news_photos"
        photos.mkdir(parents=True, exist_ok=True)
        items = []
        for n in News.objects.filter(is_published=True):
            photo_name = ""
            if n.photo:
                shutil.copy2(n.photo.path, photos / Path(n.photo.path).name)
                photo_name = Path(n.photo.path).name
            items.append({
                "title": n.title,
                "slug": n.slug,
                "date": n.date.isoformat(),
                "kind": n.kind,
                "announcement": n.announcement,
                "body": n.body,
                "photo": photo_name,
                "photo_caption": n.photo_caption,
            })
        (root / "data" / "news.json").write_text(
            json.dumps(items, ensure_ascii=False), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"OK: {len(items)} новостей → data/news.json"))
