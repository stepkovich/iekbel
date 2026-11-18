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

        # контент-корпус для graphify: markdown по каждой новости
        corpus = root / "content"
        corpus.mkdir(exist_ok=True)
        (corpus / "news").mkdir(exist_ok=True)
        for old_md in (corpus / "news").glob("*.md"):
            old_md.unlink()
        kinds = {"news": "новость", "event": "мероприятие", "company": "о представительстве"}
        for it in items:
            md = (f"# {it['title']}\n\n"
                  f"- Тип: {kinds.get(it['kind'], it['kind'])}\n"
                  f"- Дата: {it['date']}\n"
                  f"- Ссылка на сайте: /news/{it['slug']}/\n\n"
                  f"{it['announcement']}\n\n"
                  f"{it['body']}\n")
            (corpus / "news" / f"{it['date']}_{it['slug']}.md").write_text(md, encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(
            f"OK: {len(items)} новостей → data/news.json + content/news/*.md"))
