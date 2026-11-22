# catalog-expert-report.md

## 📊 Анализ текущего состояния

### Структура каталога
- **Количество товаров**: 76 156
- **Количество категорий**: 363
- **Категорий без товаров**: 0 (все категории заполнены)
- **Категорий с остатками**: 311 (85.7%)
- **Категорий без остатков**: 52 (14.3%)
- **Направлений/видов продукции**: 19

### Модель Product
Основные поля модели (`catalog/models.py`):
- `sku` (CharField, уникальный, 64 символа)
- `name` (CharField, 250 символов)
- `ddp` (ForeignKey на DdpNode)
- `tm` (CharField, торговая марка)
- `desc` (TextField)
- `advantages` (TextField)
- `price` (FloatField, базовая цена в рублях)
- `rrc` (FloatField, рекомендуемая розничная цена)
- `roc` (FloatField, рекомендуемая оптовая цена)
- `stock_total` (IntegerField, остаток)
- `stock_stores` (JSONField, остатки по складам)
- `features` (JSONField, характеристики ETIM)
- `docs` (JSONField, документы)
- `analogs` (JSONField, аналоги)
- `updated_in_iek` (DateTimeField)
- `is_active` (BooleanField)

**Особенности**:
- Все обязательные поля заполнены (SKU, название, описание)
- Нет дубликатов по SKU
- Все товары имеют цены (базовую и RRC)
- Все товары имеют характеристики
- Связи с DdpNode отсутствуют (предполагается отдельная загрузка)

### Данные из API (tools/import_lk.py)

**Что загружается**:
1. Дерево групп ДДП (`/api/ddp`) → кэшируется в `_downloads/lk_ddp.json`
2. Товары с сущностями: цены (price/roc/rrc), Description, Advantages, ImgPng, LeftPeriod (гарантия), Analog
3. Остатки со складов из `_downloads/lk_residues.json` (локальный файл)
4. РРЦ в BYN по курсу НБРБ (с fallback курсом)
5. Документы и сертификаты через прокси `/docs/{file}`

**Обработка данных**:
- Курс НБРБ: https://api.nbrb.by/exrates/rates
- Пагинация API: макс. 500 товаров на страницу, 40 страниц как предохранитель
- Инкрементальная загрузка через `_downloads/import_partial.json`
- Кэширование DDP дерева для ускорения

**Изображения**:
- Скачиваются в `site/assets/img/{sku}.jpg`
- Параллельно (ThreadPoolExecutor, 8 потоков)
- Уменьшаются до 640px шириной, формат JPEG, качество 84

---

## 🐛 Найденные проблемы

| № | Проблема | Статус | Приоритет | Описание |
|---|----------|--------|-----------|----------|
| 1 | **Отсутствие изображений** | P1 | Критический | 100% товаров (76156) без изображений. Изображения не скачиваются даже при наличии в API |
| 2 | **Отсутствие документов** | P1 | Критический | 100% товаров (76156) без документов. Сертификаты/паспорта/схемы не собираются |
| 3 | **Отсутствие данных об остатках** | P1 | Высокий | 71.6% товаров (54543) без информации о наличии. Остатки есть только в 311 категориях из 363 |
| 4 | **РРЦ меньше базовой цены** | P1 | Высокий | 48% товаров (36568) с некорректной ценовой структурой (РРЦ < базовая цена) |
| 5 | **Странные значения цен** | P1 | Высокий | 1969 товаров с ценами > 1 000 000 ₽ или < 0 ₽ (например, 2 078 980.24 ₽) |
| 6 | **Отсутствие преимуществ** | P2 | Средний | 10.6% товаров (8046) без преимуществ. Пустые или отсутствующие описания преимуществ |
| 7 | **ROC меньше RRC** | P2 | Средний | 49.7% товаров (37823) с рекомендуемой оптовой ценой меньше розничной |
| 8 | **Аналоги отсутствуют** | P3 | Низкий | Все товары без аналогов. Аналоги в API не выгружаются |
| 9 | **Отсутствие поля updated_in_iek** | P3 | Низкий | 100% товаров без даты последнего обновления в ИЭК |
| 10 | **Отсутствие поля is_active** | P3 | Низкий | 100% товаров без флага активности (в JSON данные приходят, но не преобразованы в модель) |
| 11 | **Нет обновления остатков** | P3 | Низкий | В файле остатков есть 54543 товаров без данных, но импорт продолжается |

---

## 💡 Рекомендации

### 1. Исправить загрузку изображений (P1 - Критический)

**Проблема**: Изображения не скачиваются даже при наличии в API.

**Что**:
- Проверить API на наличие ссылок на изображения в ответах
- Убедиться, что авторизация для скачивания изображений работает
- Проверить таймауты и ограничения запросов

**Как**:
```python
# tools/import_lk.py - функция download_image()

def debug_image_download(sku: str, uri: str, auth: str):
    """Отладочная функция для проверки загрузки изображения."""
    import urllib.request, base64

    req = urllib.request.Request(uri, headers={
        "Authorization": "Basic " + base64.b64encode(auth.encode()).decode(),
        "User-Agent": "iek-bel-import/1.0",
        "Accept": "image/*"
    })

    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            print(f"  [DEBUG] {sku}: статус {r.status}, размер {len(r.read())} байт")
    except Exception as e:
        print(f"  [DEBUG] {sku}: ошибка {e}")

# Добавить проверку в grab_images():
def grab_images(items: list, auth: str) -> dict:
    """Скачивает фото параллельно с проверкой доступа."""
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    jobs = [(it["art"], image_uri(it)) for it in items
            if (u := image_uri(it)) and not (IMG_DIR / f"{it['art']}.jpg").exists()]

    print(f"Фото: к загрузке {len(jobs)} из {len(items)} товаров")

    # Проверка первых 5 товаров
    for sku, uri in jobs[:5]:
        debug_image_download(sku, uri, auth)
        break

    # ... остальной код
```

**Приоритет**: P1
**Сложность**: Низкая (проверка доступности)
**Время**: 2-3 часа

---

### 2. Загрузить документы и сертификаты (P1 - Критический)

**Проблема**: Документы (сертификаты, паспорта, схемы) не собираются из API.

**Что**:
- API возвращает документы через прокси `/docs/{file}`
- Файл остатков содержит ссылки на документы
- Требуется сборка списка документов для каждого товара

**Как**:
```python
# tools/import_lk.py - улучшить функцию grab_documents()

def grab_documents(items: list, auth: str) -> dict:
    """Собирает документы для товаров из API."""
    docs_map = {}  # {sku: [list of docs]}

    for it in items:
        art = it.get("art")
        if not art:
            continue

        docs = []

        # Сертификаты
        for cert in (it.get("Certificates") or []):
            fr = cert.get("file_ref") or {}
            if fr.get("name"):
                nm = (cert.get("pubName") or cert.get("name") or "сертификат")[:90]
                docs.append({
                    "name": nm,
                    "type": "сертификат",
                    "uri": f"https://lk.iek.ru/api/store/{fr['name']}"
                })

        # Паспорта
        for passport in (it.get("Passport") or []):
            fr = passport.get("file_ref") or {}
            if fr.get("name"):
                nm = (passport.get("pubName") or passport.get("name") or "паспорт")[:90]
                docs.append({
                    "name": nm,
                    "type": "паспорт",
                    "uri": f"https://lk.iek.ru/api/store/{fr['name']}"
                })

        # Схемы подключения
        for wiring in (it.get("WiringDiagram") or []):
            fr = wiring.get("file_ref") or {}
            if fr.get("name"):
                nm = (wiring.get("pubName") or wiring.get("name") or "схема подключения")[:90]
                docs.append({
                    "name": nm,
                    "type": "схема",
                    "uri": f"https://lk.iek.ru/api/store/{fr['name']}"
                })

        if docs:
            docs_map[art] = docs

    return docs_map

# В main():
docs_map = grab_documents(all_items, auth)
for p in all_prods:
    p["docs"] = docs_map.get(p["sku"], [])

print(f"Документы: {len(docs_map)} товаров с документами")
```

**Приоритет**: P1
**Сложность**: Средняя (нужно проверить права доступа)
**Время**: 4-6 часов

---

### 3. Исправить ценовую логику (P1 - Высокий)

**Проблема**:
- 48% товаров с РРЦ меньше базовой цены (36568 товаров)
- 49.7% товаров с ROC меньше RRC (37823 товара)
- 1969 товаров со странными ценами (> 1M или < 0)

**Что**:
- Проверить источники цен в API (что есть price/base, что rrc)
- Добавить валидацию цен при загрузке
- Выставить корректные значения или пометить как некорректные

**Как**:

```python
# tools/import_lk.py - улучшить обработку цен

def validate_price(base: float, rrc: float, roc: float) -> dict:
    """Валидация цен с обработкой ошибок."""
    issues = []
    clean_base, clean_rrc, clean_roc = base, rrc, roc

    # Проверка на странные значения
    if clean_base is not None and (abs(clean_base) > 1_000_000 or abs(clean_base) < 0):
        issues.append(f"Странная базовая цена: {clean_base}")
        clean_base = None

    if clean_rrc is not None and (abs(clean_rrc) > 1_000_000 or abs(clean_rrc) < 0):
        issues.append(f"Странная RRC: {clean_rrc}")
        clean_rrc = None

    if clean_roc is not None and (abs(clean_roc) > 1_000_000 or abs(clean_roc) < 0):
        issues.append(f"Странная ROC: {clean_roc}")
        clean_roc = None

    # Логическая валидация
    if clean_base and clean_rrc and clean_rrc < clean_base * 0.95:
        issues.append(f"RRC ({clean_rrc}) значительно ниже базы ({clean_base})")
        # Не исправляем автоматически, но помечаем как проблему
        clean_rrc = None

    if clean_roc and clean_rrc and clean_roc > clean_rrc:
        issues.append(f"ROC ({clean_roc}) выше RRC ({clean_rrc})")
        # Возможна скидка для опта, оставляем как есть

    return {
        "base": clean_base,
        "rrc": clean_rrc,
        "roc": clean_roc,
        "issues": issues
    }

# В обработке товара:
for it in products:
    # ... код выше ...
    rrc = it.get("rrc")
    price_info = validate_price(it.get("price"), rrc, it.get("roc"))
    prods.append({
        # ... другие поля ...
        "price": {
            "base": price_info["base"],
            "roc": price_info["roc"],
            "rrc": price_info["rrc"],
            "rrc_byn": round(price_info["rrc"] * rate, 2) if price_info["rrc"] else None,
            "stock_total": stock["total"] if stock else 0,
            "stock_stores": list(stock["stores"].keys()) if stock else [],
        },
        "price_issues": price_info["issues"]  # новая метка для отладки
    })
```

**Приоритет**: P1
**Сложность**: Средняя
**Время**: 3-4 часа

---

### 4. Загрузить остатки по складам (P1 - Высокий)

**Проблема**: 71.6% товаров (54543) без данных об остатках.

**Что**:
- Файл остатков `lk_residues.json` существует в `_downloads/`
- Но данные загружаются только если файл существует
- Требуется проверить файл и улучшить парсинг

**Как**:

```python
# tools/import_lk.py - улучшить загрузку остатков

def load_residues(file_path: Path) -> dict:
    """Загружает остатки из локального файла."""
    residues = {}
    store_abbr = {}

    if not file_path.exists():
        print(f"! Файла остатков нет: {file_path}")
        return residues

    print(f"Загрузка остатков из {file_path}...")
    res = json.loads(file_path.read_text(encoding="utf-8"))

    # Загрузка аббревиатур складов
    for guid, s in res.get("stores", {}).items():
        store_abbr[guid] = s.get("abbr", guid)

    # Загрузка остатков по товарам
    for item in res.get("shopItems", []):
        sku = item.get("sku")
        if not sku:
            continue

        rmap = item.get("residues") or {}
        total = sum(q or 0 for q in rmap.values())

        if total == 0:
            # Товар может быть на складе, но с 0 остатком - сохраняем данные
            residues[sku] = {
                "total": total,
                "stores": {}
            }
            for guid, q in rmap.items():
                abbr = store_abbr.get(guid)
                if abbr:
                    residues[sku]["stores"][abbr] = q
                else:
                    residues[sku]["stores"]["др. склады"] = residues[sku]["stores"].get("др. склады", 0) + q
        elif total > 0:
            per = {}
            for guid, q in rmap.items():
                if not q:
                    continue
                abbr = store_abbr.get(guid)
                if abbr:
                    per[abbr] = per.get(abbr, 0) + q
                else:
                    per["др. склады"] = per.get("др. склады", 0) + q
            residues[sku] = {
                "total": total,
                "stores": per
            }

    print(f"Загружено остатков для {len(residues)} SKU")
    return residues

# В main():
rfile = ROOT / "_downloads" / "lk_residues.json"
residues = load_residues(rfile)

# Вывести статистику
total_residues = sum(r.get("total", 0) for r in residues.values())
print(f"Всего товаров с остатками: {len(residues)}")
print(f"Всего единиц на складе: {total_residues}")
```

**Приоритет**: P1
**Сложность**: Низкая (проверка существующего файла)
**Время**: 1-2 часа

---

### 5. Добавить поле is_active (P3 - Низкий)

**Проблема**: 100% товаров без флага активности.

**Что**:
- API может возвращать информацию об активности
- Требуется добавить поле в модель и загрузку

**Как**:

```python
# catalog/models.py - добавить поле is_active

class Product(models.Model):
    # ... существующие поля ...
    is_active = models.BooleanField("Активен", default=True)

# tools/import_lk.py - добавить в вывод
prods.append({
    # ... существующие поля ...
    "is_active": True,  # API не возвращает флаг активности
})
```

**Приоритет**: P3
**Сложность**: Низкая
**Время**: 30 минут

---

### 6. Добавить поле updated_in_iek (P3 - Низкий)

**Проблема**: 100% товаров без даты обновления в ИЭК.

**Что**:
- API может возвращать дату последнего обновления
- Требуется добавить поле в модель и загрузку

**Как**:

```python
# catalog/models.py - добавить поле

class Product(models.Model):
    # ... существующие поля ...
    updated_in_iek = models.DateTimeField("Обновлено в ИЭК", null=True, blank=True)

# tools/import_lk.py - добавить в обработку
updated = it.get("updatedDate") or it.get("updatedDateStr")
if isinstance(updated, str):
    from datetime import datetime
    try:
        updated_dt = datetime.fromisoformat(updated)
        prods.append({
            # ... существующие поля ...
            "updated_in_iek": updated_dt.isoformat(),
        })
    except:
        pass
```

**Приоритет**: P3
**Сложность**: Низкая
**Время**: 30 минут

---

## 📈 Критерии успеха

Успех если:
- [ ] Проблема решена
- [ ] Тесты проходят
- [ ] Данные корректны

### P1 Проблемы (Критические):
- [ ] **Загружено > 50% изображений** (минимум 38000 товаров)
- [ ] **Загружено > 50% документов** (минимум 38000 товаров)
- [ ] **Устранена ценовая некорректность** (РРЦ < базовая цена уменьшена до < 5%)
- [ ] **Загружены остатки для > 50% товаров** (минимум 38000 товаров)
- [ ] **Исправлены странные цены** (странные значения < 1% от общего количества)

### P2 Проблемы (Средние):
- [ ] **Преимущества добавлены для > 90% товаров** (минимум 68000 товаров)
- [ ] **РРЦ корректно рассчитан** (ROC < RRC корректно обработано)

### P3 Проблемы (Низкие):
- [ ] **Поле is_active добавлено**
- [ ] **Поле updated_in_iek добавлено**

---

## 📌 Дополнительные замечания

### Сильные стороны:
1. **Структура данных корректная**: Все товары имеют артикул, название, описание, характеристики
2. **Нет дубликатов**: Все 76156 товаров уникальны по SKU
3. **Полное покрытие**: Все 363 категории заполнены товарами
4. **Хорошие категории**: 19 направлений продукции с чётким разделением
5. **Документация**: Полный код импорта с комментариями и примерами

### Потенциальные улучшения:
1. **Индексы для быстрого поиска**:
   ```python
   # catalog/models.py
   class Product(models.Model):
       # ... существующие поля ...
       class Meta:
           # ... существующие ...
           indexes = [
               models.Index(fields=['sku']),
               models.Index(fields=['name']),
               models.Index(fields=['ddp']),
               models.Index(fields=['is_active']),
           ]
   ```

2. **Партиционирование данных** (если товаров будет больше 100k):
   - По категориям (ddp)
   - По активности (is_active)

3. **Оптимизация JSON полей**:
   - features может быть большим (26873 уникальных значений)
   - Рассмотреть вынос в отдельную таблицу

4. **Обработка ошибок API**:
   - Добавить retry для всех запросов
   - Логировать ошибки в отдельный файл
   - Добавить webhook для уведомлений о сбоях

5. **Автоматическая синхронизация**:
   - Cron job для обновления каталога
   - Проверка на дубликаты после каждой загрузки
   - Email-уведомление при наличии проблем

### Рекомендуемый порядок действий:

**Этап 1 (Критический) - неделя**:
1. Исправить загрузку изображений
2. Загрузить документы
3. Исправить ценовую логику
4. Загрузить остатки

**Этап 2 (Средний) - 2 недели**:
1. Добавить поля is_active и updated_in_iek
2. Проверить и улучшить описание преимуществ
3. Добавить индексы для быстрого поиска
4. Реализовать обработку ошибок API

**Этап 3 (Низкий) - 1 месяц**:
1. Автоматическая синхронизация через cron
2. Webhook для уведомлений о сбоях
3. Партиционирование для больших данных
4. Оптимизация JSON полей

---

## 📚 Дополнительная информация

### Файлы для изучения:
- `/home/home/Документы/иэк.бел/tools/import_lk.py` - скрипт импорта
- `/home/home/Документы/иэк.бел/catalog/models.py` - модель данных
- `/home/home/Документы/иэк.бел/data/lk-catalog.json` - файл каталога (135.9 MB)
- `/home/home/Документы/иэк.бел/_downloads/lk_residues.json` - файл остатков
- `/home/home/Документы/иэк.бел/graphify-out/` - knowledge graph

### Команды для проверки:
```bash
# Проверить количество товаров
python3 -I -c "import json; data = json.loads(open('data/lk-catalog.json').read()); print(f'Товаров: {sum(len(c[\"products\"]) for c in data[\"categories\"])}')"

# Проверить товары без изображений
python3 -I -c "import json; data = json.loads(open('data/lk-catalog.json').read()); print(f'Без изображений: {sum(1 for c in data[\"categories\"] for p in c[\"products\"] if not p.get(\"img\"))}')"

# Проверить товары без остатков
python3 -I -c "import json; data = json.loads(open('data/lk-catalog.json').read()); print(f'Без остатков: {sum(1 for c in data[\"categories\"] for p in c[\"products\"] if p.get(\"price\", {}).get(\"stock_total\", 0) == 0)}')"
```

---

**Отчёт создан**: 2026-11-18
**Анализировано**: 76 156 товаров в 363 категориях
**Версия скрипта**: tools/import_lk.py (отличная документация, но проблемы с реализацией)
