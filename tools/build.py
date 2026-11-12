#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор статического сайта иэк.бел (единый чистый файл).

Запуск: python3 -I tools/build.py data/lk-catalog.json data/distributors.json site
"""
import json
import re
import sys
import time as _time
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

PAGES = []
DOMAIN = ""
SITE_PHONE = ""
SITE_EMAIL = ""
BUILD = str(int(_time.time()))
CSS = (Path(__file__).with_name("style.css").read_text(encoding="utf-8"))

# ---------- инлайн-иконки (24×24, line-style, currentColor) ----------
_I = {
 "cart": '<circle cx="9" cy="20" r="1.6"/><circle cx="17" cy="20" r="1.6"/><path d="M3 3h2.2l2.5 11.6a1.2 1.2 0 0 0 1.2 1h8.3a1.2 1.2 0 0 0 1.2-.9L20.6 7H6"/>',
 "search": '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.4-4.4"/>',
 "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.6a2 2 0 0 1-.5 2.1L8 9.6a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.8.3 1.7.5 2.6.6a2 2 0 0 1 1.7 2z"/>',
 "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>',
 "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
 "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 11.5 2 2 4-4"/>',
 "tag": '<path d="M20.6 13.4 12 22 2 12V2h10l8.6 8.6a2 2 0 0 1 0 2.8z"/><circle cx="7" cy="7" r="1.5"/>',
 "truck": '<path d="M1 4h14v12H1z"/><path d="M15 8h4l3 3v5h-7"/><circle cx="6" cy="18.5" r="1.8"/><circle cx="17.5" cy="18.5" r="1.8"/>',
 "doc": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M8 13h8M8 17h5"/>',
 "bolt": '<path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/>',
 "breaker": '<rect x="6" y="2.5" width="12" height="19" rx="1.5"/><path d="M9.5 6.5h5"/><path d="M12 6.5v6"/><circle cx="12" cy="15.5" r="1.6"/><path d="M6 18.5h12"/>',
 "uzo": '<rect x="6" y="2.5" width="12" height="19" rx="1.5"/><circle cx="12" cy="9" r="2.2"/><path d="M9.5 15.5h5"/><path d="M9.5 18.5h5"/>',
 "cab": '<rect x="4.5" y="3" width="15" height="18" rx="1.5"/><path d="M4.5 12h15"/><rect x="15.2" y="14" width="2.6" height="4" rx=".8"/><path d="M8 7.5h6"/>',
 "bulb": '<path d="M9.5 18h5"/><path d="M10.2 21h3.6"/><path d="M12 2.5a6.5 6.5 0 0 0-3.7 11.8c.6.5.9 1.1.9 1.8v.4h5.6v-.4c0-.7.3-1.3.9-1.8A6.5 6.5 0 0 0 12 2.5z"/>',
 "gear": '<circle cx="12" cy="12" r="3.2"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1.87-.34 1.7 1.7 0 0 0-1 1.55V21a2 2 0 1 1-4 0v-.09a1.7 1.7 0 0 0-1-1.55 1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.7 1.7 0 0 0 .34-1.87 1.7 1.7 0 0 0-1.55-1H3a2 2 0 1 1 0-4h.09a1.7 1.7 0 0 0 1.55-1 1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.7 1.7 0 0 0 1.87.34h.08a1.7 1.7 0 0 0 1-1.55V3a2 2 0 1 1 4 0v.09a1.7 1.7 0 0 0 1 1.55 1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.7 1.7 0 0 0-.34 1.87v.08a1.7 1.7 0 0 0 1.55 1H21a2 2 0 1 1 0 4h-.09a1.7 1.7 0 0 0-1.55 1z"/>',
 "toggle": '<rect x="2.5" y="7" width="19" height="10" rx="5"/><circle cx="16.5" cy="12" r="3"/>',
 "meter": '<path d="M3.5 18a9 9 0 1 1 17 0"/><path d="M12 12l4-4"/><circle cx="12" cy="18" r="1.4"/><path d="M2 18h20"/>',
 "socket": '<path d="M9 2.5h6v5H9z"/><path d="M7 7.5h10v6a5 5 0 0 1-10 0z"/><path d="M9.5 11h.01M14.5 11h.01"/><path d="M12 18.5V22"/>',
 "plug": '<path d="M9 2.5v6M15 2.5v6"/><path d="M6.5 8.5h11v3a5.5 5.5 0 0 1-11 0z"/><path d="M12 17v4.5"/>',
 "wrench": '<path d="M14.7 6.3a4.5 4.5 0 0 0-6 5.6L3 17.6V21h3.4l5.7-5.7a4.5 4.5 0 0 0 5.6-6L14.4 12l-2.5-2.5 2.8-3.2z"/>',
 "battery": '<rect x="2.5" y="7" width="17" height="10" rx="2"/><path d="M22 10.5v3"/><path d="M6.5 10.5v3M10 10.5v3"/>',
 "pole": '<path d="M12 22V8"/><path d="M12 8c0-3 1.5-5.5 4-6"/><path d="M8.5 3.5 12 8l3.5-4.5"/><path d="M7.5 22h9"/><circle cx="12" cy="9.5" r="1.2"/>',
 "server": '<rect x="3" y="3.5" width="18" height="7" rx="1.5"/><rect x="3" y="13.5" width="18" height="7" rx="1.5"/><path d="M7 7h.01M7 17h.01"/><path d="M11 7h6M11 17h6"/>',
 "code": '<path d="m8 8-5 4 5 4"/><path d="m16 8 5 4-5 4"/><path d="m13 5-2 14"/>',
 "bus": '<path d="M3 6h18"/><path d="M3 12h18"/><path d="M3 18h18"/><circle cx="7" cy="6" r="1.2"/><circle cx="14" cy="12" r="1.2"/><circle cx="9" cy="18" r="1.2"/>',
 "link2": '<path d="M9 12h6"/><path d="M9 7H7a5 5 0 0 0 0 10h2"/><path d="M15 7h2a5 5 0 0 1 0 10h-2"/>',
 "flame": '<path d="M12 22c4.4 0 7-2.8 7-6.5 0-3-1.8-4.8-3-6.5-.4 1.6-1.4 2.4-2.3 2.4C12.6 11.4 14 7 12 2c0 0-1 3-3.5 5.5C6.6 9.4 5 11.5 5 15.5 5 19.2 7.6 22 12 22z"/>',
 "ev": '<path d="M5 21V4a1.5 1.5 0 0 1 3 0v17"/><path d="M5 12h3"/><path d="M8 5h11v13a2 2 0 0 1-2 2h-9"/><path d="m13.5 8-2 4h3l-2 4"/>',
 "package": '<path d="M12 2 3 7v10l9 5 9-5V7z"/><path d="M3 7l9 5 9-5"/><path d="M12 12v10"/><path d="m7.5 4.5 9 5"/>',
 "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 "arrow": '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
}

def icon(name: str, size: int = 20) -> str:
    return (f'<svg class="icn" width="{size}" height="{size}" viewBox="0 0 24 24" '
            f'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{_I[name]}</svg>')

KIND_ICON = {
    "Модульное оборудование": "breaker",
    "Силовое оборудование защиты и коммутации": "toggle",
    "Приборы учета, контроля, измерения и оборудование электропитания": "meter",
    "Щитовое оборудование": "cab",
    "Системы для прокладки кабеля": "bus",
    "Изделия электроустановочные, удлинители и силовые разъемы": "socket",
    "Оборудование коммутационное и устройства управления": "toggle",
    "Изделия электромонтажные и инструменты": "wrench",
    "Элементы питания": "battery",
    "Светотехника": "bulb",
    "Проектная светотехника LEDEL и FEREKS": "bulb",
    "Металлоконструкции для наружного освещения, дорожной и телекоммуникационной инфраструктуры": "pole",
    "Оборудование телекоммуникационное": "server",
    "Программное обеспечение для инженерной и ИТ-инфраструктуры": "code",
    "Программное обеспечение МПС софт": "code",
    "Автоматизация зданий и процессов": "gear",
    "Решения автоматизации": "gear",
    "Шинопровод": "bus",
    "Продукция Контактор": "breaker",
    "Продукция НЕОСАН": "gear",
    "Продукция ТМ GENERICA": "package",
    "АСИП, кабельные муфты, силовые наконечники и гильзы": "link2",
    "Арматура для СИП, кабельные муфты, силовые наконечники и гильзы": "link2",
    "Лимитированный ассортимент LEGRAND": "plug",
    "Зарядная инфраструктура": "ev",
    "Системы электрического обогрева": "flame",
}

_RU = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
       "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
       "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
       "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
       "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya"}

def slugify(s: str) -> str:
    out = []
    for c in s.lower():
        if c.isascii() and (c.isalnum() or c in "-_"):
            out.append(c)
        elif c in _RU:
            out.append(_RU[c])
        else:
            out.append("-")
    res = "".join(out)
    while "--" in res:
        res = res.replace("--", "-")
    return res.strip("-")[:80] or "item"

def cat_icon_key(slug: str, title: str, kind: str = "") -> str:
    if kind and kind in KIND_ICON:
        return KIND_ICON[kind]
    s = (slug + " " + title).lower()
    for k, ic in KIND_ICON.items():
        kws = {"Модульное оборудование": ["модульн"], "Щитовое оборудование": ["щит", "корпус"],
               "Светотехника": ["свет"], "Системы для прокладки кабеля": ["кабел", "прокладк"],
               "Автоматизация зданий и процессов": ["автоматиз"], "Элементы питания": ["питани"]}.get(k, [])
        if any(w in s for w in kws):
            return ic
    if "uzo" in s or "дифференц" in s: return "uzo"
    if "выключат" in s or "автомат" in s: return "breaker"
    return "package"

def ddp_tree(cats: list) -> dict:
    """Уровни ДДП: L1 (01) → L2 (01.01) → L3 (01.01.01 = группа с товарами)."""
    l2name = {}
    ddpf = ROOT / "_downloads" / "lk_ddp.json"
    if ddpf.exists():
        for e in json.loads(ddpf.read_text(encoding="utf-8")):
            l2name.setdefault(e["groupId"][:5], e.get("section") or "")
    tree = {}
    for c in cats:
        gid = c.get("ddp_id", "")
        l1, l2 = gid[:2], gid[:5]
        t = tree.setdefault(l1, {"title": c.get("kind") or "Каталог",
                                 "icon": cat_icon_key(c["slug"], c["title"], c.get("kind", "")),
                                 "l2": {}})
        t["l2"].setdefault(l2, {"title": l2name.get(l2) or f"Раздел {l2}", "groups": []})
        t["l2"][l2]["groups"].append(c)
    return tree

def kind_slug(k: str, idx: int) -> str:
    s = slugify(k)
    return (s[:40] + f"-k{idx}") if len(s) > 40 else s

def split_kinds(cats: list) -> tuple[list, dict]:
    kinds, by_kind = [], {}
    for c in cats:
        k = c.get("kind") or "Каталог"
        if k not in by_kind:
            by_kind[k] = []
            kinds.append(k)
        by_kind[k].append(c)
    return kinds, by_kind

def fmt_byn(x) -> str:
    return f"{x:,.2f}".replace(",", " ").replace(".", ",")

def price_line(p: dict) -> str:
    return "цена у дистрибьютора"

def breadcrumbs_html(items: list[tuple[str, str]]) -> str:
    parts = ['<nav class="crumbs">']
    for i, (href, t) in enumerate(items):
        sep = '<span class="sep">›</span>' if i else ""
        link = f'<a href="{href}">{escape(t)}</a>' if href else f"<span>{escape(t)}</span>"
        parts.append(sep + link)
    parts.append("</nav>")
    return "".join(parts)

def breadcrumbs_ld(base: str, items: list[tuple[str, str]]) -> str:
    return json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": t, **({"item": base + quote(h)} if h else {})}
            for i, (h, t) in enumerate(items)
        ]
    }, ensure_ascii=False)

def org_ld(cfg: dict) -> str:
    return json.dumps({
        "@context": "https://schema.org", "@type": "Organization",
        "name": "иэк.бел", "url": f"https://{DOMAIN}/",
        "description": "Официальный портал заказа продукции ИЭК у дистрибьюторов в Республике Беларусь",
        "telephone": cfg["site"]["phone"], "email": cfg["site"]["email"], "areaServed": "BY",
    }, ensure_ascii=False)

def website_ld(cfg: dict) -> str:
    return json.dumps({
        "@context": "https://schema.org", "@type": "WebSite",
        "name": "иэк.бел", "url": f"https://{DOMAIN}/",
        "potentialAction": {"@type": "SearchAction",
            "target": {"@type": "EntryPoint", "urlTemplate": f"https://{DOMAIN}/search/?q={{search_term_string}}"},
            "query-input": "required name=search_term_string"},
    }, ensure_ascii=False)

def product_ld(cfg: dict, cat: dict, p: dict) -> str:
    return json.dumps({
        "@context": "https://schema.org", "@type": "Product",
        "name": p["title"], "sku": p["sku"], "category": cat["title"],
        "brand": {"@type": "Brand", "name": "ИЭК"},
        "description": p["desc"],
        "offers": {"@type": "Offer", "availability": "https://schema.org/InStock",
                   "seller": {"@type": "Organization", "name": "Официальные дистрибьюторы ИЭК в Республике Беларусь"}},
    }, ensure_ascii=False)

def distributors_ld(cfg: dict, dists: list) -> str:
    items = []
    for d in dists:
        for L in (d.get("locations") or []):
            if not (L.get("lat") and L.get("lon")):
                continue
            item = {"@type": "LocalBusiness", "name": d.get("name", ""),
                    "address": {"@type": "PostalAddress", "streetAddress": L.get("address", ""),
                                "addressLocality": L.get("city", ""), "addressCountry": "BY"},
                    "geo": {"@type": "GeoCoordinates", "latitude": L["lat"], "longitude": L["lon"]}}
            if L.get("phone"):
                item["telephone"] = L["phone"]
            if d.get("site"):
                item["url"] = d["site"]
            items.append(item)
    return json.dumps({"@context": "https://schema.org", "@graph": items}, ensure_ascii=False)

# ---------- шаблон страницы ----------
def page(path: str, title: str, desc: str, body: str, base: str, canon: str,
         ld: str = "", og_img: str = "", noindex: bool = False) -> str:
    nav_items = [("", "Главная"), ("catalog/", "Каталог"), ("distributors/", "Дистрибьюторы"), ("cart/", "Корзина")]
    nav_html = "".join(f'<a href="{base}{h}">{t}</a>' for h, t in nav_items)
    ld_block = f'<script type="application/ld+json">{ld}</script>' if ld else ""
    robots = '<meta name="robots" content="noindex, nofollow">' if noindex else ""
    og = og_img or f"https://{DOMAIN}/assets/logo-iek.png"
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
{robots}
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:site_name" content="иэк.бел">
<meta property="og:image" content="{og}">
<link rel="icon" type="image/png" href="{base}assets/logo-iek.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;500;600;700&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/style.css?v={BUILD}">
{ld_block}
</head>
<body>
<header class="top">
  <div class="wrap nav">
    <a class="logo" href="{base}"><img src="{base}assets/logo-iek.svg" alt="ИЭК — купить продукцию в Беларуси" height="40"><span class="dom">.бел</span></a>
    <form class="searchbox" action="{base}search/" role="search">
      <input type="search" name="q" placeholder="Поиск по каталогу ИЭК" aria-label="Поиск по каталогу">
      <button type="submit">Найти</button>
    </form>
    <nav>{nav_html}</nav>
    <a class="btn btn-primary header-cta" href="{base}cart/">{icon("cart", 18)} Корзина <span class="cart-count" style="display:none"></span></a>
    <button class="burger" aria-label="Меню" aria-expanded="false">☰</button>
  </div>
  <div class="mnav" id="mnav">
    <form class="searchbox msearch" action="{base}search/" role="search">
      <input type="search" name="q" placeholder="Поиск по каталогу ИЭК" aria-label="Поиск по каталогу">
      <button type="submit">Найти</button>
    </form>
    {nav_html}
    <a href="{base}order/">Быстрый заказ по артикулу</a>
  </div>
</header>
<main>{body}</main>
<footer><div class="wrap">
  <div class="cols">
    <div>
      <div class="brandline"><strong class="dom">иэк.бел</strong><span class="marker" style="margin:0"></span></div>
      <p class="about">Портал заказа продукции ИЭК у официальных дистрибьюторов в Республике Беларусь. Работает под эгидой представительства ПАО «ИЭК ХОЛДИНГ» в РБ: оригинальная продукция, счёт от дистрибьютора по вашим реквизитам, без посредников.</p>
    </div>
    <div>
      <h4>Покупателям</h4>
      <ul>
        <li><a href="{base}catalog/">Каталог продукции</a></li>
        <li><a href="{base}cart/">Корзина — запрос счёта</a></li>
        <li><a href="{base}order/">Быстрый заказ по артикулу</a></li>
        <li><a href="{base}search/">Поиск по каталогу</a></li>
      </ul>
    </div>
    <div>
      <h4>Партнёрская сеть</h4>
      <ul>
        <li><a href="{base}distributors/">Дистрибьюторы в РБ</a></li>
        <li><a href="{base}distributors/map/">Карта точек продаж</a></li>
        <li><a href="https://www.iek.ru/company/brandbook/" target="_blank" rel="nofollow">Брендбук ИЭК</a></li>
      </ul>
    </div>
    <div>
      <h4>Контакты</h4>
      <ul>
        <li class="c-row">{icon("phone", 17)} {SITE_PHONE}</li>
        <li class="c-row">{icon("mail", 17)} {SITE_EMAIL}</li>
        <li class="c-row">{icon("pin", 17)} Республика Беларусь, г. Минск</li>
      </ul>
    </div>
  </div>
  <div class="bottom">
    <span>© 2026 Официальное представительство ПАО ИЭК ХОЛДИНГ в Республике Беларусь</span>
    <span>Товарный знак «ИЭК» принадлежит ПАО «ИЭК ХОЛДИНГ»</span>
  </div>
</div></footer>
<script src="{base}assets/js/cart.js?v={BUILD}" defer></script>
<script src="{base}assets/js/catalog.js?v={BUILD}" defer></script>
<script src="{base}assets/js/live.js?v={BUILD}" defer></script>
</body>
</html>"""

def write(out: Path, rel: str, html: str) -> None:
    p = out / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
    PAGES.append(rel)

def write_page(out: Path, cfg: dict, rel: str, title: str, desc: str, body: str,
               ld: str = "", og_img: str = "", noindex: bool = False) -> None:
    canon = (f"https://{cfg['site']['domain_puny']}/{quote(rel[:-len('index.html')])}"
             if rel.endswith("index.html") else f"https://{cfg['site']['domain_puny']}/{quote(rel)}")
    base = "../" * rel.count("/")
    write(out, rel, page(rel, title, desc, body, base, canon, ld, og_img, noindex))

# ---------- компоненты ----------
def product_img(p: dict, thumb: bool = False) -> str:
    sku = quote(p["sku"])
    route = "thumb" if thumb else "img"
    return (f'<div class="img-wrap"><div class="ph-fallback" aria-hidden="true"><span></span></div>'
            f'<img src="/{route}/{sku}.jpg" alt="{escape(p["title"])}" loading="lazy" '
            f'onload="this.parentElement.classList.add(\'ok\')" onerror="this.remove()"></div>')

def price_line(p: dict) -> str:
    return "цена у дистрибьютора"

def product_card(cfg: dict, cat_slug: str, p: dict) -> str:
    url = f"{p['slug']}/"
    pr = p.get("price") or {}
    badge = ('<span class="badge ok live-badge" data-sku="{sku}">в наличии</span>'.format(sku=escape(p["sku"]))
             if pr.get("stock_total") else
             f'<span class="badge live-badge" data-sku="{escape(p["sku"])}">под заказ</span>')
    return f"""<article class="card">
  <a class="card-img" href="{url}">{product_img(p, thumb=True)}{badge}</a>
  <div class="sku">{escape(p['sku'])}</div>
  <h3><a href="{url}">{escape(p['title'])}</a></h3>
  <div class="row"><span class="price">{price_line(p)}</span><span class="more">{icon("arrow", 17)}</span></div>
</article>"""

def feats_html(p: dict) -> str:
    et = p.get("etim_features") or []
    if et:
        rows = "".join(
            f"<li>{escape(f['n'])}: <strong>{escape(f['v'])}</strong>"
            + (f" {escape(f['u'])}" if f.get("u") else "") + "</li>"
            for f in et[:18])
        return f"<ul class='feats'>{rows}</ul>"
    return "<ul class='feats'>" + "".join(f"<li>{escape(f)}</li>" for f in p["features"]) + "</ul>"


def partner_stock_html(p: dict) -> str:
    ps = p.get("partner_stock") or []
    if not ps:
        return ""
    rows = "".join(
        f"<li>{escape(s['source'])} — <strong>{s['qty']} шт</strong>"
        + (f" <span class=\"note\">(на {escape(s['updated'])})</span>" if s.get("updated") else "")
        + "</li>" for s in ps)
    return (f"<section class='partner-stock'><h2>Наличие у дистрибьюторов-партнёров</h2>"
            f"<ul class='pstock'>{rows}</ul></section>")

# ---------- страницы ----------
def build_home(out: Path, cfg: dict, cats: list, dists: list) -> None:
    tree = ddp_tree(cats)
    n_products = sum(len(c["products"]) for c in cats)
    n_points = sum(len(d.get("locations") or []) for d in dists)
    l1_rows = "".join(
        f'<a class="row-item" href="catalog/{quote(slugify(k["title"])[:40])}-{l1}/">'
        f'<span class="ticon">{icon(k["icon"], 24)}</span>'
        f'<span class="rt">{escape(k["title"])}</span>'
        f'<span class="chip">{len(k["l2"])} групп · {sum(len(c["products"]) for g in k["l2"].values() for c in g["groups"])} поз.</span>'
        f'<span class="go-arrow">{icon("arrow", 18)}</span></a>'
        for l1, k in sorted(tree.items())
    )
    body = f"""
<section class="hero">
  <div class="wrap">
    <div>
      <div class="mark" aria-hidden="true"></div>
      <h1>Продукция ИЭК в Беларуси — заказ у официальных дистрибьюторов</h1>
      <p class="lead">Официальный портал ПАО «ИЭК ХОЛДИНГ» в Республике Беларусь. Соберите корзину — запрос уйдёт выбранному дистрибьютору, счёт выставят по вашим реквизитам. Без посредников и переплат.</p>
      <div class="cta-row">
        <a class="btn btn-primary btn-lg" href="catalog/">Открыть каталог</a>
        <a class="btn btn-ghost btn-lg" href="order/">Быстрый заказ по артикулу</a>
      </div>
    </div>
    <aside class="hero-stats">
      <div class="hcell"><span class="hicon">{icon("bolt", 26)}</span><span class="num">{n_products}+</span><span class="lbl">позиций с характеристиками и документами</span></div>
      <div class="hcell"><span class="hicon">{icon("pin", 26)}</span><span class="num">{n_points}</span><span class="lbl">точек дистрибьюторов по всей Беларуси</span></div>
      <div class="hcell"><span class="hicon">{icon("clock", 26)}</span><span class="num">1 день</span><span class="lbl">на выставление счёта после запроса</span></div>
    </aside>
  </div>
</section>
<section class="sec"><div class="wrap">
  <div class="sec-head"><div><p class="overline">каталог</p><h2>Направления продукции</h2></div><a class="link all" href="catalog/">Весь каталог →</a></div>
  <div class="rows">{l1_rows}</div>
</div></section>
<section class="sec"><div class="sec-tint" style="padding:48px 40px">
  <div class="wrap" style="padding:0">
    <p class="overline">как заказать</p>
    <div class="sec-head" style="margin-bottom:30px"><h2 style="font-size:clamp(20px,2.4vw,26px)">Три шага до счёта</h2></div>
    <div class="steps">
      <div class="step"><span class="stnum">01</span><strong>Выберите товар</strong><p>В каталоге или через поиск по артикулу — все позиции оригинальные, производство ИЭК.</p></div>
      <div class="step"><span class="stnum">02</span><strong>Отправьте запрос</strong><p>Корзина уходит выбранному дистрибьютору. Остальные партнёры тоже видят запрос и могут предложить условия.</p></div>
      <div class="step"><span class="stnum">03</span><strong>Получите счёт</strong><p>Дистрибьютор выставляет счёт по вашим реквизитам и связывается по самовывозу или доставке.</p></div>
    </div>
  </div>
</div></section>
<section class="sec"><div class="wrap">
  <div class="sec-head"><div><p class="overline">преимущества</p><h2>Почему иэк.бел</h2></div></div>
  <div class="usp">
    <div class="tile"><span class="ticon">{icon("shield", 24)}</span><h3>Официально</h3><p>Портал ведёт представительство ПАО «ИЭК ХОЛДИНГ» — только оригинальная продукция с гарантией производителя.</p><span class="go-arrow">Гарантия до 10 лет</span></div>
    <div class="tile"><span class="ticon">{icon("tag", 24)}</span><h3>Прямые цены</h3><p>Запрос уходит дистрибьюторам напрямую — счёт без розничных наценок перекупщиков.</p><span class="go-arrow">Счёт по вашим реквизитам</span></div>
    <div class="tile"><span class="ticon">{icon("truck", 24)}</span><h3>Вся страна</h3><p>Заказы маршрутизируются ближайшему к вам дистрибьютору — самовывоз или доставка.</p><span class="go-arrow">Вся Республика Беларусь</span></div>
  </div>
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><div><p class="overline">по всей стране</p><h2>Дистрибьюторы в вашем городе</h2></div><a class="link all" href="distributors/map/">Карта сети →</a></div>
  <div class="city-chips">{"".join(f'<span class="chip">{escape(str(L.get("city")))}</span>' for d in dists for L in (d.get("locations") or []) if L.get("city"))}</div>
  <div class="cta-band">
    <div class="t">Готовы заказать? Соберите корзину — дистрибьюторы выставят счёт по вашим реквизитам.</div>
    <a class="btn btn-dark btn-lg" href="cart/">{icon("cart", 18)} Перейти в корзину</a>
  </div>
</div></section>
"""
    write_page(out, cfg, "index.html",
               "ИЭК в Беларуси — купить продукцию ИЭК у официальных дистрибьюторов",
               "Официальный портал заказа продукции ИЭК в Республике Беларусь: автоматические выключатели, УЗО, щиты, светодиодное освещение. Заказ напрямую у официальных дистрибьюторов.",
               body, org_ld(cfg) + website_ld(cfg))

def build_catalog(out: Path, cfg: dict, cats: list) -> None:
    """Каталог как на iek.ru: плитки направлений с номерами и фото товаров."""
    tree = ddp_tree(cats)
    total = sum(len(c["products"]) for c in cats)

    def first_sku(k: dict) -> str:
        for _k2, l2 in sorted(k["l2"].items()):
            for c in l2["groups"]:
                if c["products"]:
                    return c["products"][0]["sku"]
        return ""

    tiles = []
    for l1, k in sorted(tree.items()):
        sku = first_sku(k)
        photo = ""
        if sku:
            photo = '<img src="/thumb/' + quote(sku) + '.jpg" alt="" loading="lazy" onerror="this.remove()">'
        tiles.append(
            '<a class="dir-tile" href="/catalog/' + quote(slugify(k["title"])[:40]) + "-" + l1 + '/">'
            '<span class="dnum">' + str(l1) + '.</span>'
            '<span class="dtitle">' + escape(k["title"]) + '</span>'
            '<span class="dphoto">' + photo + '</span></a>')

    body = ('<div class="wrap">'
            + breadcrumbs_html([("", "Главная"), ("", "Каталог")])
            + '<h1 class="catalog-h">Каталог товаров</h1>'
            + '<div class="dir-grid">' + "".join(tiles) + '</div></div>')
    write_page(out, cfg, "catalog/index.html",
               "Каталог продукции ИЭК в Беларуси — все направления | иэк.бел",
               f"Полный каталог ГК IEK: {total} позиций по направлениям ДДП. Заказ у официальных дистрибьюторов в РБ.",
               body, breadcrumbs_ld(f"https://{DOMAIN}/", [("", "Главная"), ("catalog/", "Каталог")]))

    # страницы направлений: плитки групп с фото (уровень 2 иек-структуры)
    for l1, k in sorted(tree.items()):
        l1slug = f"{slugify(k['title'])[:40]}-{l1}"
        gtiles = []
        for l2, g in sorted(k["l2"].items()):
            for c in g["groups"]:
                fs = c["products"][0]["sku"] if c["products"] else ""
                photo = f'<img src="/thumb/{quote(fs)}.jpg" alt="" loading="lazy" onerror="this.remove()">' if fs else ""
                gtiles.append(
                    f'<a class="dir-tile" href="/catalog/{quote(c["slug"])}/">'
                    f'<span class="dnum">{escape(c.get("ddp_id", ""))}</span>'
                    f'<span class="dtitle">{escape(c["title"])}</span>'
                    f'<span class="dphoto">{photo}</span></a>')
        kbody = f"""<div class="wrap">
{breadcrumbs_html([("../", "Главная"), ("../catalog/", "Каталог"), ("", k["title"])])}
<h1 class="catalog-h">{escape(k["title"])}</h1>
<div class="dir-grid">{"".join(gtiles)}</div>
</div>"""
        write_page(out, cfg, f"catalog/{l1slug}/index.html",
                   f"{k['title']} ИЭК — каталог по разделам ДДП | иэк.бел",
                   f"{k['title']}: полный каталог продукции ИЭК по разделам ДДП, наличие и заказ у дистрибьюторов в Беларуси.",
                   kbody, breadcrumbs_ld(f"https://{DOMAIN}/", [("", "Главная"), ("catalog/", "Каталог"), ("", k["title"])]))

def build_category(out: Path, cfg: dict, cat: dict) -> None:
    PER = 60
    prods = cat["products"]
    pages = max(1, (len(prods) + PER - 1) // PER)
    crumbs = breadcrumbs_html([("../", "Главная"), ("../catalog/", "Каталог"), ("", cat["title"])])
    ld = breadcrumbs_ld(f"https://{DOMAIN}/", [("", "Главная"), ("catalog/", "Каталог"), ("", cat["title"])])
    kw = escape(cat.get("keywords", f"{cat['title'].lower()} ИЭК купить Беларусь"))
    for pg in range(1, pages + 1):
        chunk = prods[(pg - 1) * PER: pg * PER]
        cards = "".join(product_card(cfg, cat["slug"], pr) for pr in chunk)
        pg_links = ""
        if pages > 1:
            items = "".join(
                f'<a class="pgn{" cur" if n == pg else ""}" href="/catalog/{cat["slug"]}/{"" if n == 1 else f"page/{n}/"}">{n}</a>'
                for n in range(1, pages + 1))
            pg_links = f'<nav class="pgn-wrap">Страница {pg} из {pages}: {items}</nav>'
        title = f"{cat['title']} ИЭК — купить в Беларуси{f', страница {pg}' if pages > 1 else ''} | иэк.бел"
        body = f"""<div class="wrap">
{crumbs}
<h1>{escape(cat["title"])} ИЭК — купить в Беларуси</h1>
<div class="cat-layout">
  <aside class="filters" id="cat-filters">
    <div class="f-block">
      <h4>Раздел каталога</h4>
      {breadcrumbs_html([("../", "Главная"), ("../catalog/", "Катalog"), ("", cat["title"])])}
    </div>
    <div class="f-block">
      <h4>Наличие</h4>
      <label class="f-check"><input type="checkbox" id="f-stock"> Только в наличии на складах ИЭК</label>
    </div>
    <div class="f-block">
      <h4>Поиск внутри раздела</h4>
      <input type="search" id="f-q" class="f-q" placeholder="Артикул или название…">
    </div>
    <p class="note">Фильтры работают мгновенно на этой странице. Полный фильтр по ETIM-характеристикам — следующий этап.</p>
  </aside>
  <div class="cat-main">
    <div class="cat-toolbar">
      <button class="btn btn-ghost f-btn" id="f-toggle">{icon("gear", 17)} Фильтр</button>
      <span class="chip ok">{len(prods)} позиций</span>
      <label class="sort-lbl">Сортировка:
        <select id="sort-sel" class="sort-sel">
          <option value="sku">По артикулу А→Я</option>
          <option value="sku-d">По артикулу Я→А</option>
          <option value="name">По названию</option>
          <option value="stock">Сначала в наличии</option>
        </select>
      </label>
    </div>
    <div class="grid" id="cat-grid">{cards}</div>
    {pg_links}
    <section class="seo-text"><h2>Как купить {escape(cat["title"].lower())} ИЭК в Беларуси</h2>
    <p>На иэк.бел вы заказываете напрямую у официальных дистрибьюторов ИЭК: заявка уходит авторизованному партнёру, что исключает подделки и лишние наценки. Для проектных организаций — оптовые условия и спецификации.</p>
    <p>Популярные запросы: {kw}. Не нашли позицию? Отправьте <a href="/order/">быстрый запрос по артикулу</a> — дистрибьютор подберёт аналог.</p></section>
  </div>
</div>
</div>"""
        rel_path = f"catalog/{cat['slug']}/index.html" if pg == 1 else f"catalog/{cat['slug']}/page/{pg}/index.html"
        write_page(out, cfg, rel_path, title,
                   (cat["intro"] or "")[:160],
                   body, ld)

def build_product(out: Path, cfg: dict, cat: dict, p: dict) -> None:
    pr = p.get("price") or {}
    m_series = re.match(r"^(ARMAT|MASTER|KARAT|UNION|GENERICA)", p.get("title", ""))
    series = m_series.group(1) if m_series else ""

    # гарантия и срок службы — подписанные плитки (как на БП);
    # мусорные значения («нет данных», пусто) — прочерк
    warranty, service_life = "", ""
    for f in p.get("features", []):
        if f.startswith("Гарантия"):
            warranty = f.split(":", 1)[1].strip()
        if f.startswith("Срок службы"):
            service_life = f.split(":", 1)[1].strip()
    for _i, _v in (("w", warranty), ("s", service_life)):
        bad = (not _v) or _v.lower().startswith(("нет", "не указан", "не задан")) or _v == "—"
        if bad:
            if _i == "w":
                warranty = "—"
            else:
                service_life = "—"
        elif _v.lower().endswith("лет") and len(_v.split()) == 2:
            pass  # «15 лет» — ок
        elif _v.isdigit():
            if _i == "w":
                warranty = f"{_v} лет"
            else:
                service_life = f"{_v} лет"

    # ETIM: «Основные характеристики» = первые 6 позиций В ПОРЯДКЕ ИЭК (PIM
    # сортирует характеристики по классу товара, коммерчески главные — первыми;
    # ровно так же на bp.iek.ru — сверено с живой карточкой ВА47-29).
    et = p.get("etim_features") or []
    if et:
        spec_val = lambda f: escape(f["v"]) + ((" " + escape(f["u"])) if f.get("u") else "")
        spec_rows = "".join(
            f'<div class="spec-row"><span class="k">{escape(f["n"])}</span>'
            f'<span class="v">{spec_val(f)}</span></div>'
            for f in et)
        spec_short = "".join(
            f'<div class="spec-row"><span class="k">{escape(f["n"])}</span>'
            f'<span class="v">{spec_val(f)}</span></div>'
            for f in et[:6])
    else:
        spec_rows = "".join(
            f'<div class="spec-row"><span class="k">{escape(str(f).split(":")[0])}</span>'
            f'<span class="v">{escape(str(f).split(":", 1)[-1].strip())}</span></div>'
            for f in p.get("features", []) if ":" in str(f))
        spec_short = spec_rows

    # документы
    # параметрический переключатель: «Другие варианты» (индекс из main).
    # Пересечение осей: чип значения доступен, только если в группе есть товар
    # с этим значением И текущими значениями остальных осей; иначе — серый,
    # некликабельный («нет в этой комплектации»).
    switcher_html = ""
    pidx = cat.get("param_index") or {}
    if pidx:
        my = {f["n"]: str(f["v"]) for f in (p.get("etim_features") or [])}
        # оси подбора: 1) приоритетные (ток, полюса, характеристика…) — всегда;
        # 2) прочие параметры с 2-12 значениями; шум (масса/габариты) — исключён
        PRIO = ["Номинальный ток", "Количество полюсов", "Характеристика срабатывания",
                "Количество модулей", "Номинальное рабочее напряжение"]

        def prio(n):
            for i, key in enumerate(PRIO):
                if key.lower() in n.lower():
                    return i
            return len(PRIO)

        used_axes = []
        for param, values in sorted(pidx.items(), key=lambda x: (prio(x[0]), len(x[1]))):
            if prio(param) >= len(PRIO) and not 2 <= len(values) <= 12:
                continue  # неприоритетные оси — только с небольшим числом значений
            # дубли-оси («Общ количество полюсов» при «Количество полюсов») — пропускаем
            if any(param.lower() in u.lower() or u.lower() in param.lower()
                   for u in used_axes):
                continue
            used_axes.append(param)

        # O(1)-индекс combos группы: ключ = кортеж значений всех осей → товар.
        # Строится один раз на группу (build_product вызывается для каждого товара).
        cidx = cat.get("_combo_index")
        if cidx is None:
            cidx = cat["_combo_index"] = {}
            for tp in cat["products"]:
                tm = tp.get("_etim_map")
                if tm is None:
                    tm = tp["_etim_map"] = {f["n"]: str(f["v"])
                                            for f in (tp.get("etim_features") or [])}
                cidx.setdefault(tuple(tm.get(q) for q in used_axes), tp)

        def combo_product(param, val):
            """Товар группы: axis=value, остальные оси — как у текущего."""
            return cidx.get(tuple(val if q == param else my.get(q) for q in used_axes))

        blocks = []
        for param in used_axes:
            values = pidx[param]
            chips = []
            try:
                ordered = sorted(values, key=lambda x: float(str(x).replace(",", ".")))
            except ValueError:
                ordered = sorted(values, key=lambda x: (len(x), x))
            for val in ordered:
                disp = val[:-2] if val.endswith(".0") else val
                if my.get(param) == val:
                    chips.append(f'<span class="pchip pchip-on">{escape(disp)}</span>')
                    continue
                tp = combo_product(param, val)
                if tp is not None:
                    chips.append(f'<a class="pchip" href="/catalog/{quote(cat["slug"])}/{tp["slug"]}/" title="{escape(param)}: {escape(val)}">{escape(disp)}</a>')
                else:
                    chips.append(f'<span class="pchip pchip-off" title="Нет в этой комплектации">{escape(disp)}</span>')
            if len(chips) > 1:
                blocks.append(f'<div class="pblock"><span class="pk">{escape(param)}</span>'
                              f'<span class="pchips">{"".join(chips)}</span></div>')
        if blocks:
            switcher_html = ('<div class="pswitch"><h4>Другие варианты — подбор по параметрам</h4>'
                             + "".join(blocks[:4]) + '</div>')
    docs = p.get("docs") or []
    docs_html = ""
    if docs:
        lis = "".join(
            f"<li><span class='doc-ic'>{escape((d.get('type') or 'документ')[:3].upper())}</span>"
            f"<a href='/docs/{quote(d['file'])}' target='_blank' rel='noopener'>{escape(d['name'])}</a> "
            f"<span class='note'>{escape(d.get('type', 'документ'))}</span></li>"
            for d in docs[:12])
        docs_html = f"<h2 id='docs' class='h-sec'>Документация</h2><ul class='docs'>{lis}</ul>"

    # преимущества: нумерованный список 01./02. (как на БП)
    adv_lines = [x.strip(" -–—") for x in (p.get("advantages") or "").splitlines()
                 if x.strip(" -–—") and len(x.strip()) > 3]
    adv_html = ""
    if adv_lines:
        lis = "".join(f"<li><span class='an'>{i:02d}.</span>{escape(x)}</li>"
                      for i, x in enumerate(adv_lines[:10], 1))
        adv_html = (f"<h2 id='adv' class='h-sec'>Преимущества</h2>"
                    f"<ol class='adv-list'>{lis}</ol>")

    stock_badge = (f'<span class="badge ok live-badge" data-sku="{escape(p["sku"])}">'
                   f'В наличии · {pr.get("stock_total", 0)} шт</span>'
                   if pr.get("stock_total") else
                   f'<span class="badge live-badge" data-sku="{escape(p["sku"])}">под заказ</span>')

    # таблица наличия: дистрибьюторы + склады ИЭК в РФ (живое обновление live.js)
    STORE_RU = {"Щ": "Щёлково", "Кув": "Кувекино", "Я": "Ярославль",
                "БЛБ": "БЛБ", "др.": "Другие склады"}
    def fmt_qty(n):
        return f"{n:,}".replace(",", " ") + " шт"

    def stock_table() -> str:
        rows = []
        partners = {}
        for s in (p.get("partner_stock") or []):
            partners[s["source"]] = partners.get(s["source"], 0) + s["qty"]
        if partners:
            rows.append('<tr class="grp"><td colspan="2">У дистрибьюторов</td></tr>')
            for name, q in sorted(partners.items(), key=lambda x: -x[1]):
                rows.append(f'<tr><td>{escape(name)}</td><td>{fmt_qty(q)}</td></tr>')
        stores = p.get("res_stores") or {}
        if stores:
            rows.append('<tr class="grp"><td colspan="2">Склады ИЭК (РФ)</td></tr>')
            for a, q in sorted(stores.items(), key=lambda x: -x[1]):
                rows.append(f'<tr><td>{escape(STORE_RU.get(a, a))}</td><td>{fmt_qty(q)}</td></tr>')
            rows.append(f'<tr class="sum"><td>Итого на складах ИЭК</td><td>{fmt_qty(sum(stores.values()))}</td></tr>')
        if not rows:
            return ""
        return (f'<div class="stock-tbl-wrap" data-live-stock="{escape(p["sku"])}">'
                f'<h4>Наличие</h4><table class="stock-tbl">{"".join(rows)}</table></div>')

    stock_table_html = stock_table()

    body = f"""<div class="wrap">
{breadcrumbs_html([("../../", "Главная"), ("../../catalog/", "Каталог"), (f"../../catalog/{cat['slug']}/", cat["title"]), ("", p["title"])])}
<div class="bp-head">
<h1>{escape(p["title"])}</h1>
<div class="series-chip">Серия: {escape(series)}</div>
<div class="ptabs">
  <a class="pt-active" href="#desc">Описание</a><a href="#features">Характеристики</a><a href="#docs">Документация</a><a href="#order">Заказ</a>
</div>
</div>
<article class="product">
  <div class="p-grid">
    <div class="p-left">
      <div class="p-photo">{product_img(p)}<button class="sku-copy p-copy" data-copy="{escape(p["sku"])}" title="Скопировать артикул">⧉</button></div>
      <div class="p-plates">
        <div class="plate py"><span class="pl"><span class="pl-t">Срок службы</span><span class="pl-v">{escape(service_life or "—")}</span></span>{icon("clock", 30)}</div>
        <div class="plate pd"><span class="pl"><span class="pl-t">Гарантия</span><span class="pl-v">{escape(warranty or "—")}</span></span>{icon("shield", 30)}</div>
      </div>
    </div>
    <div class="p-right">
      <div class="stock-row">
        {stock_badge}
        <span class="art-chip">Артикул: <b>{escape(p["sku"])}</b> <button class="sku-copy" data-copy="{escape(p["sku"])}" aria-label="Скопировать артикул">⧉</button></span>
      </div>
      {stock_table_html}
      <div class="price-card">
        <div class="pc-row"><span class="pc-l">Цена</span><span class="pc-v">у дистрибьютора</span></div>
        <p class="note">Счёт с актуальной ценой выставит дистрибьютор по вашим реквизитам после запроса.</p>
      </div>
      <div class="qty-box">
        <h4>Добавление в корзину</h4>
        <div class="qty-stepper">
          <button class="qs-minus" type="button">−</button>
          <input class="qty-val" type="number" min="1" value="1">
          <button class="qs-plus" type="button">+</button>
        </div>
        <button class="btn btn-primary add-to-cart-qty" data-sku="{escape(p["sku"])}" data-title="{escape(p["title"])}">Добавить в корзину</button>
      </div>
      <div class="spec-short">
        <div class="ss-head"><h4>Основные характеристики</h4><a class="ss-all" href="#features">Все характеристики</a></div>
        {spec_short or '<p class="note">уточняйте у дистрибьютора</p>'}
      </div>
      {switcher_html}
    </div>
  </div>
  <div class="desc-grid">
    <div class="desc-col">
      <h2 id="desc" class="h-sec">Описание</h2>
      <p class="lead">{escape(p["desc"])}</p>
    </div>
    <div class="adv-col">{adv_html}</div>
  </div>
  <h2 id="features" class="h-sec">Технические характеристики</h2>
  <div class="spec-table">{spec_rows or '<p class="note">уточняйте у дистрибьютора</p>'}</div>
  {docs_html}
  <div class="order-box" id="order">
    <h2>Заказ у дистрибьютора</h2>
    <p class="stock">Наличие обновляется онлайн; ниже — данные последней выгрузки.</p>
    <div data-live-stock="{escape(p["sku"])}" class="live-detail"></div>
    <p class="note">Оформите корзину — заявка уйдёт выбранному дистрибьютору, счёт придёт по вашим реквизитам.</p>
  </div>
</article>
</div>"""
    write_page(out, cfg, f"catalog/{cat['slug']}/{p['slug']}/index.html",
               f"{p['title']} — купить в Беларуси | иэк.бел",
               f"{p['title']} ({p['sku']}) — характеристики, наличие и заказ у официальных дистрибьюторов ИЭК в Беларуси.",
               body, product_ld(cfg, cat, p),
               og_img=f"https://{DOMAIN}/img/{quote(p['sku'])}.jpg" if p.get("img", True) else "")

def build_distributors(out: Path, cfg: dict, dists: list) -> None:
    cards = ""
    for d in dists:
        cls, txt = STATUS_CHIP.get(d.get("iek_status") or "declared", ("mid", "дистрибьютор"))
        lis = []
        for L in (d.get("locations") or []):
            phone = f' <span class="c-row">{icon("phone", 15)} {escape(str(L["phone"]))}</span>' if L.get("phone") else ""
            hours = f' · {escape(str(L["hours"]))}' if L.get("hours") else ""
            approx = ' <span class="note">(≈)</span>' if L.get("approx") else ""
            yamap = (f' <a class="more" rel="nofollow" target="_blank" '
                     f'href="https://yandex.ru/maps/?pt={L["lon"]},{L["lat"]}&z=17">Яндекс.Карты ↗</a>'
                     if isinstance(L.get("lat"), (int, float)) else "")
            lis.append(f"<li class='loc-line'><span class='chip t'>{escape(str(L.get('type') or 'точка'))}</span> "
                       f"<strong>{escape(str(L.get('city') or ''))}</strong>, "
                       f"{escape(str(L.get('address') or ''))}{phone}{hours}{approx}{yamap}</li>")
        site = f' · <a href="{escape(d["site"])}" rel="nofollow">{escape(d["site"])}</a>' if d.get("site") else ""
        email = f' · <span class="c-row">{icon("mail", 14)} {escape(d["email"])}</span>' if d.get("email") else ""
        spec = f"<p>{escape(d['specialization'])}</p>" if d.get("specialization") else ""
        legal = f"<p class='note'>{escape(d.get('legalName') or '')}{site}{email}</p>" if (d.get("legalName") or site or email) else ""
        cards += f"""<div class="dist">
<h3>{escape(d['name'])} <span class="chip {cls}">{txt}</span></h3>
{legal}{spec}
<ul class="locs">{''.join(lis) or '<li class="note">данные уточняются</li>'}</ul>
</div>"""
    body = f"""<div class="wrap">
{breadcrumbs_html([("", "Главная"), ("", "Дистрибьюторы")])}
<h1>Официальные дистрибьюторы ИЭК в Беларуси</h1>
<p>Заказы с портала маршрутизируются авторизованным партнёрам. Все точки на одной странице — <a href="map/">карта Яндекс</a>.</p>
{cards}
<p class="note">Статусы собраны из открытых источников и проверяются представительством. «≈» — координата приблизительная. Обновлено: {escape(str(cfg.get('dist_updated', '')))}</p>
</div>"""
    write_page(out, cfg, "distributors/index.html",
               "Официальные дистрибьюторы ИЭК в Беларуси — адреса, магазины, склады | иэк.бел",
               "Дистрибьюторы продукции ИЭК в Республике Беларусь: адреса офисов, магазинов и складов, телефоны, статусы. Карта партнёрской сети на Яндекс.Картах.",
               body, distributors_ld(cfg, dists))

def build_map(out: Path, cfg: dict, dists: list) -> None:
    pt_parts = []
    for d in dists:
        for L in (d.get("locations") or []):
            lat, lon = L.get("lat"), L.get("lon")
            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                lt = (L.get("type") or "").lower()
                style = ("pm2gnm" if ("склад" in lt or "филиал" in lt) else
                         "pm2ylm" if ("магазин" in lt or "выдач" in lt) else
                         "pm2orm" if ("производ" in lt or "завод" in lt) else "pm2blm")
                pt_parts.append(f"{lon},{lat},{style}")
    if pt_parts:
        src = f"https://yandex.ru/map-widget/v1/?pt={'~'.join(pt_parts)}&l=map&z=7"
    else:
        src = "https://yandex.ru/map-widget/v1/?ll=27.95,53.7&z=7&l=map"
    body = f"""<div class="wrap">
{breadcrumbs_html([("../", "Главная"), ("../distributors/", "Дистрибьюторы"), ("", "Карта")])}
<h1>Дистрибьюторы ИЭК на карте Беларуси</h1>
<p>Офисы, магазины и склады партнёрской сети ({len(pt_parts)} точек). Список с контактами — <a href="../">на странице дистрибьюторов</a>.</p>
<iframe class="yamap" src="{src}" allowfullscreen title="Карта дистрибьюторов ИЭК в Беларуси (Яндекс.Карты)"></iframe>
<p class="note">Яндекс.Карты. Точки, помеченные «≈», показаны приблизительно — точная геолокация уточняется.</p>
</div>"""
    write_page(out, cfg, "distributors/map/index.html",
               "Карта дистрибьюторов ИЭК в Беларуси (Яндекс.Карты) | иэк.бел",
               "Карта офисов, магазинов и складов официальных дистрибьюторов продукции ИЭК в Республике Беларусь на Яндекс.Картах.",
               body, distributors_ld(cfg, dists))

def build_cart(out: Path, cfg: dict, dists: list) -> None:
    names = json.dumps([d["name"] for d in dists if d.get("iek_status") in ("confirmed", "declared")], ensure_ascii=False)
    body = f"""<div class="wrap">
{breadcrumbs_html([("", "Главная"), ("", "Корзина")])}
<h1>Корзина запроса</h1>
<p>Соберите позиции, выберите дистрибьютора — заказ уйдёт напрямую, остальные партнёры тоже увидят запрос и смогут предложить свои условия.</p>
<div id="cart-root"><p class="note">Загружаю корзину…</p></div>
<button class="linklike" id="cart-clear">Очистить корзину</button>
<script>window.IEK_DISTRIBUTORS = {names};</script>
</div>"""
    write_page(out, cfg, "cart/index.html",
               "Корзина — запрос счёта у дистрибьюторов ИЭК | иэк.бел",
               "Оформление запроса: выберите позиции и дистрибьютора ИЭК в Беларуси — заказ уйдёт напрямую, счёт выставят по вашим реквизитам.",
               body, noindex=True)

def build_search(out: Path, cfg: dict) -> None:
    body = """<div class="wrap">
<nav class="crumbs"><a href="../">Главная</a> › <span>Поиск</span></nav>
<h1>Поиск по каталогу ИЭК</h1>
<p>Ищите по артикулу (MVA20-1-006-C) или названию (автомат ВА47-29, УЗО, щит, прожектор).</p>
<div class="searchbig">
  <input type="search" id="q" placeholder="Артикул или название…" autofocus>
</div>
<div id="results" aria-live="polite"></div>
</div>
<script src="../assets/js/search.js?v={BUILD}" defer></script>"""
    write_page(out, cfg, "search/index.html",
               "Поиск по каталогу продукции ИЭК | иэк.бел",
               "Поиск по артикулам и названиям продукции ИЭК: автоматические выключатели, УЗО, дифавтоматы, щиты, светотехника.",
               body, noindex=True)

def build_search_index(out: Path, cfg: dict, cats: list) -> None:
    idx = []
    for c in cats:
        for p in c["products"]:
            idx.append({"s": p["sku"], "n": p["title"][:120],
                        "u": f"catalog/{c['slug']}/{p['slug']}/", "c": c["title"]})
    (out / "search-index.json").write_text(
        json.dumps(idx, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

def build_404(out: Path, cfg: dict) -> None:
    body = """<section class="hero" style="padding:56px 20px">
  <div class="mark" aria-hidden="true"></div>
  <h1>404 — страница не найдена</h1>
  <p class="lead">Такой страницы нет, но каталог ИЭК на месте.</p>
  <a class="btn btn-primary btn-lg" href="/catalog/">Открыть каталог</a>
  <a class="btn btn-ghost btn-lg" href="/">На главную</a>
</section>"""
    write_page(out, cfg, "404.html",
               "Страница не найдена | иэк.бел",
               "Страница не найдена. Перейдите в каталог продукции ИЭК.",
               body, noindex=True)

def build_order(out: Path, cfg: dict) -> None:
    body = f"""<div class="wrap">
{breadcrumbs_html([("", "Главная"), ("", "Быстрый заказ")])}
<h1>Быстрый заказ по артикулу</h1>
<p>Знаете артикул ИЭК, но не хотите собирать корзину? Оставьте артикул — запрос уйдёт представительству, дистрибьютор подберёт позицию и выставит счёт.</p>
<form class="order-form" id="quick-form">
  <label>Артикул ИЭК / что нужно<input name="sku" required placeholder="Например: MVA20-1-025C или «щит на 36 модулей IP65»"></label>
  <label>Количество<input name="qty" type="number" min="1" value="1"></label>
  <label>Контактное лицо (ФИО)<input name="name" required></label>
  <label>Телефон<input name="phone" type="tel" required></label>
  <label>Email<input name="email" type="email" required></label>
  <label>Комментарий<textarea name="comment" rows="2"></textarea></label>
  <button class="btn btn-primary btn-lg" type="submit">Отправить запрос</button>
  <div id="quick-result"></div>
</form>
<p class="note">Для запроса сразу нескольким дистрибьюторам воспользуйтесь <a href="/cart/">корзиной</a>.</p>
<script>
document.getElementById("quick-form").addEventListener("submit", function (e) {{
  e.preventDefault();
  var fd = new FormData(e.target);
  var payload = {{
    created: new Date().toISOString(),
    distributor: "Представительство иэк.бел (быстрый заказ)",
    client: {{ name: fd.get("name"), phone: fd.get("phone"), email: fd.get("email"),
              type: "—", org: null, requisites: null, city: null }},
    comment: fd.get("comment") || null,
    items: [{{ sku: fd.get("sku"), title: "Быстрый заказ по артикулу", qty: +fd.get("qty") || 1 }}],
  }};
  var out = document.getElementById("quick-result");
  out.innerHTML = '<p class="note">Отправляю…</p>';
  fetch("/api/order", {{ method: "POST", headers: {{"Content-Type": "application/json"}}, body: JSON.stringify(payload) }})
    .then(function (r) {{ return r.json(); }})
    .then(function (j) {{
      out.innerHTML = '<div class="order-ok"><h3>✓ Запрос принят. Номер: ' + (j.orderId || "—") + '</h3>' +
        '<p>Представительство свяжется с вами и передаст запрос дистрибьюторам.</p></div>';
      e.target.reset();
    }})
    .catch(function () {{
      out.innerHTML = '<p class="note">Сервис временно недоступен — напишите нам: {SITE_EMAIL}</p>';
    }});
}});
</script>
</div>"""
    write_page(out, cfg, "order/index.html",
               "Быстрый заказ по артикулу ИЭК | иэк.бел",
               "Быстрый запрос по артикулу ИЭК: укажите позицию и контакты — дистрибьютор подберёт товар и выставит счёт.",
               body, noindex=True)

def build_aux(out: Path, cfg: dict) -> None:
    d = f"https://{DOMAIN}/"
    (out / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + d + "sitemap.xml\n", encoding="utf-8")
    urls = [p.replace("index.html", "") for p in PAGES
            if not p.startswith("cart/") and p != "404.html"]
    parts = [urls] if len(urls) <= 40000 else [urls[i:i + 40000] for i in range(0, len(urls), 40000)]
    if len(parts) == 1:
        body = "\n".join(f"  <url><loc>{d}{quote(s)}</loc></url>" for s in parts[0])
        (out / "sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n',
            encoding="utf-8")
    else:
        idx = ""
        for i, part in enumerate(parts, 1):
            fn = f"sitemap-{i}.xml"
            idx += f"  <sitemap><loc>{d}{fn}</loc></sitemap>\n"
            body = "\n".join(f"  <url><loc>{d}{quote(s)}</loc></url>" for s in part)
            (out / fn).write_text(
                f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n',
                encoding="utf-8")
        (out / "sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{idx}</sitemapindex>\n',
            encoding="utf-8")

STATUS_CHIP = {
    "confirmed": ("ok", "дистрибьютор IEK подтверждён"),
    "declared": ("mid", "IEK заявлен в ассортименте/партнёрах"),
    "unconfirmed": ("bad", "статус IEK публично не подтверждён"),
    "none": ("mid", "завод-производитель (связь с IEK уточняется)"),
}

def main() -> None:
    if len(sys.argv) != 4:
        sys.exit("usage: build.py <catalog.json> <distributors.json> <out_dir>")
    catalog_path, dist_path, out_dir = map(Path, sys.argv[1:])
    cfg = json.loads(catalog_path.read_text(encoding="utf-8"))
    _dist = json.loads(dist_path.read_text(encoding="utf-8"))
    dists = _dist["distributors"]
    cfg["dist_updated"] = _dist.get("updated", "")
    cats = cfg["categories"]

    # ETIM-характеристики: _downloads/lk_etim.json (если выгружены)
    etimdb = out_dir.parent / "data" / "etim.db"
    if etimdb.exists():
        import sqlite3 as _sq
        con = _sq.connect(str(etimdb))
        cur = con.cursor()
        n_et = 0
        for c in cats:
            for p in c["products"]:
                row = cur.execute("SELECT features FROM etim WHERE sku=?",
                                  (p["sku"].upper(),)).fetchone()
                if row:
                    p["etim_features"] = json.loads(row[0])
                    n_et += 1
        con.close()
        print(f"ETIM: характеристики подключены к {n_et} товарам")

        # параметрический индекс группы: {param: {value: [индексы продуктов]}}
        for c in cats:
            pm = {}
            for i, p in enumerate(c["products"]):
                for f in p.get("etim_features") or []:
                    pm.setdefault(f["n"], {}).setdefault(str(f["v"]), []).append(i)
            c["param_index"] = {k: v for k, v in pm.items() if len(v) > 1}

    # статические фиды остатков партнёров: data/stock/{партнёр}.json
    stock_dir = out_dir.parent / "data" / "stock"
    if stock_dir.is_dir():
        bysku = {}
        for f in sorted(stock_dir.glob("*.json")):
            try:
                feed = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            pname = feed.get("partner", f.stem)
            upd = feed.get("updated", "")
            for sku, q in (feed.get("items") or {}).items():
                if q:
                    bysku.setdefault(sku.upper(), []).append(
                        {"source": pname, "qty": q, "updated": upd})
        if bysku:
            for c in cats:
                for p in c["products"]:
                    pp = bysku.get(p["sku"].upper())
                    if pp:
                        p["partner_stock"] = pp

    # остатки по складам ИЭК (последняя выгрузка ЛК) — для таблицы наличия
    resfile = out_dir.parent / "_downloads" / "lk_residues.json"
    if resfile.exists():
        res_raw = json.loads(resfile.read_text(encoding="utf-8"))
        res_abbr = {g: (s.get("abbr") or "др.")
                    for g, s in (res_raw.get("stores") or {}).items()}
        resmap = {}
        for it in res_raw.get("shopItems", []):
            stores = {}
            for g, q in (it.get("residues") or {}).items():
                if not q:
                    continue
                a = res_abbr.get(g, "др.")
                stores[a] = stores.get(a, 0) + q
            if stores:
                resmap[it["sku"].upper()] = stores
        for c in cats:
            for p in c["products"]:
                st = resmap.get(p["sku"].upper())
                if st:
                    p["res_stores"] = st
        print(f"Остатки по складам: {len(resmap)} SKU")

    global DOMAIN, SITE_PHONE, SITE_EMAIL, BUILD
    DOMAIN = cfg["site"]["domain_puny"]
    SITE_PHONE = cfg["site"]["phone"]
    SITE_EMAIL = cfg["site"]["email"]
    BUILD = str(int(_time.time()))

    for c in cats:
        for p in c["products"]:
            p["slug"] = slugify(p["sku"])

    out = out_dir
    out.mkdir(parents=True, exist_ok=True)
    for p_ in out.rglob("*.html"):
        p_.unlink()
    PAGES.clear()

    build_home(out, cfg, cats, dists)
    build_catalog(out, cfg, cats)
    for c in cats:
        build_category(out, cfg, c)
        for p in c["products"]:
            build_product(out, cfg, c, p)
    build_distributors(out, cfg, dists)
    build_map(out, cfg, dists)
    build_cart(out, cfg, dists)
    build_search(out, cfg)
    build_search_index(out, cfg, cats)
    build_404(out, cfg)
    build_order(out, cfg)
    build_aux(out, cfg)
    # ассеты: CSS и JS — источники в tools/assets, в site/ попадают при сборке
    (out / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (out / "assets" / "style.css").write_text(CSS.replace("__BASE__", "/"), encoding="utf-8")
    js_src = Path(__file__).with_name("assets") / "js"
    for js in js_src.glob("*.js"):
        (out / "assets" / "js" / js.name).write_text(js.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"OK: {len(PAGES)} страниц → {out}/")

if __name__ == "__main__":
    main()
