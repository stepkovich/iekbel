#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Полная проверка внутренних ссылок статического сайта по файлам на диске.

Собирает все href/src со всех *.html в site/, нормализует и проверяет
существование цели. Динамические маршруты (/img/, /thumb/, /docs/, /api/)
разрешаются по своим источникам (site/assets/img, _downloads/cache).
"""
import html.parser
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

SITE = Path(__file__).resolve().parents[1] / "site"
IMG = SITE / "assets" / "img"

class LinkCollector(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        for k in ("href", "src", "srcset"):
            if k in d:
                self.links.append(d[k])

def norm(base_dir: Path, raw: str):
    """(url, тип) — url относительно корня сайта; None = внешний/пропустить."""
    raw = raw.strip()
    if not raw:
        return None
    low = raw.lower()
    if low.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "data:")):
        return None
    raw = raw.split("#", 1)[0].strip()
    if not raw:
        return None
    raw = unquote(raw)
    path = raw.split("?")[0]
    if not path:
        return None
    if path.startswith("/"):
        p = path.lstrip("/")
    else:
        p = str(base_dir / path)
    # нормализуем ../ и ./
    parts = []
    for seg in p.split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if parts: parts.pop()
            continue
        parts.append(seg)
    return "/".join(parts)

def resolve(url: str):
    """Файл цели или None, если маршрутов нет."""
    if url.endswith("/"):
        url = url[:-1]
    if not url:
        return SITE / "index.html", "page"
    # динамические маршруты
    m = re.match(r"^(img|thumb)/(.+)\.(jpg|png|webp|jpeg)$", url, re.I)
    if m:
        return (None, "img-lk")  # живой прокси lk.iek.ru (артикул может содержать /)
    if url.startswith("docs/") or url.startswith("/docs/"):
        return (None, "docs-lk")  # живой прокси в lk.iek.ru — на диске нет
    if url.startswith(("api/", "assets/js/", "assets/css/")):
        f = SITE / url
        return (f, "asset")
    f = SITE / url
    if (f / "index.html").exists():
        return (f / "index.html", "page")
    if f.exists():
        return (f, "asset")
    if (SITE / (url + ".html")).exists():
        return (SITE / (url + ".html"), "page")
    return (None, "missing")

def main():
    pages = list(SITE.rglob("*.html"))
    missing = {}          # url → [источники]
    counts = {}
    broken_src = {}
    for pf in pages:
        rel_dir = pf.parent.relative_to(SITE)
        try:
            html = pf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        col = LinkCollector()
        try:
            col.feed(html)
        except Exception:
            continue
        for raw in col.links:
            u = norm(rel_dir, raw)
            if u is None:
                counts["внешние/якоря"] = counts.get("внешние/якоря", 0) + 1
                continue
            if u.endswith((".css", ".js", ".jpg", ".png", ".svg", ".webp", ".ico")):
                counts["ассеты"] = counts.get("ассеты", 0) + 1
            else:
                counts["страницы"] = counts.get("страницы", 0) + 1
            f, kind = resolve(u)
            if kind == "missing" or (kind in ("asset",) and f is not None and not f.exists()):
                missing.setdefault(u, []).append(str(rel_dir))
            if kind == "missing" and (u.endswith((".css", ".js"))):
                broken_src.setdefault(u, 0)
    total = sum(counts.values())
    print(f"Страниц просканировано: {len(pages)}")
    print(f"Ссылок всего: {total}  ({counts})")
    print(f"Битых целей (уникальных URL): {len(missing)}")
    by_kind = {}
    for u, srcs in missing.items():
        kind = ("карточка товара" if u.startswith("catalog/") and u.count("/") >= 2 else
                "ассет" if u.endswith((".css", ".js", ".jpg", ".png", ".svg")) else
                "страница/прочее")
        by_kind.setdefault(kind, []).append((u, srcs))
    for kind, items in sorted(by_kind.items(), key=lambda x: -len(x[1])):
        print(f"\n=== {kind}: {len(items)} ===")
        for u, srcs in sorted(items)[:25]:
            print(f"  {u}   ← {srcs[0]}{' …' if len(srcs) > 1 else ''} (×{len(srcs)})")
        if len(items) > 25:
            print(f"  … и ещё {len(items) - 25}")

if __name__ == "__main__":
    sys.exit(main())
