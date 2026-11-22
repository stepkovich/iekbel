# DEVELOPER.md — Инструкции для разработчиков

## 📋 Содержание
- [Установка и запуск](#установка-и-запуск)
- [Структура проекта](#структура-проекта)
- [API](#api)
- [Основные задачи](#основные-задачи)
- [Создание нового товара](#создание-нового-товара)
- [Создание новости](#создание-новости)
- [Изменение дизайна](#изменение-дизайна)
- [Troubleshooting](#troubleshooting)

## Установка и запуск

### Требования
- Python 3.12+
- pip
- mmenv (выбранная виртуальная среда)
- Доступ к интернету (для API lk.iek.ru)

### Шаги установки

1. **Клонирование репозитория**
   ```bash
   git clone <repository-url>
   cd иэк.бел
   ```

2. **Установка зависимостей**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # или
   .venv\Scripts\activate  # Windows

   pip install django==6.1.3 pillow
   ```

3. **Настройка базы данных**
   ```bash
   python manage.py migrate
   ```

4. **Загрузка данных каталога (опционально)**
   ```bash
   python tools/import_lk.py --kind "Модульное оборудование"
   ```

5. **Запуск dev server**
   ```bash
   python tools/devserver.py 8090
   ```

### Запуск

**Dev server (локальная разработка)**
```bash
# Запуск на порту 8090 (по умолчанию)
python tools/devserver.py

# Запуск на другом порту
python tools/devserver.py 8091
```

**Статический сайт (сборка)**
```bash
python tools/build.py data/lk-catalog.json data/distributors.json site
```

## Структура проекта

```
иэк.бел/
├── catalog/               # Django приложение
│   ├── models.py         # Модели данных (Product, Distributor, Order, News и др.)
│   ├── admin.py          # Админка Django
│   ├── views.py          # Views (если используются)
│   └── __init__.py       # Пакет
├── config/                # Django конфигурация
│   ├── settings.py       # Основные настройки проекта
│   ├── urls.py           # URL маршруты
│   ├── wsgi.py           # WSGI приложение
│   └── asgi.py           # ASGI приложение
├── tools/                 # Инструменты и скрипты
│   ├── build.py          # Сборка статического сайта
│   ├── devserver.py      # Dev server с прокси API lk.iek.ru
│   ├── import_lk.py      # Импорт каталога из API lk.iek.ru
│   ├── split_catalog.py  # Потоковая разбивка каталога
│   ├── fetch_etim.py     # Выгрузка ETIM данных
│   ├── etim_to_sqlite.py # Конвертация ETIM в SQLite
│   ├── check_links.py    # Проверка ссылок на сайте
│   ├── style.css         # Глобальный CSS
│   └── assets/           # Статические ассеты (CSS, JS)
├── data/                  # Данные проекта
│   ├── catalog.json      # Оригинальный каталог товаров
│   ├── distributors.json # Дистрибьюторы
│   ├── news.json         # Новости
│   ├── lk-catalog.json   # Импортированный каталог (размер ~136 МБ)
│   ├── lk-cats/          # Разбитый каталог (по группам)
│   │   ├── _site.json    # Блок site из lk-catalog.json
│   │   ├── _index.json   # Метаданные групп
│   │   └── 001-*.json    # Файлы групп (по одной группе в файле)
│   ├── news_photos/      # Фотографии новостей
│   └── orders/           # Заказы пользователей
├── site/                  # Сгенерированный статический сайт
│   ├── index.html        # Главная страница
│   ├── catalog/          # Каталог товаров
│   ├── news/             # Новости
│   ├── distributors/     # Дистрибьюторы
│   ├── cart/             # Корзина
│   ├── order/            # Быстрый заказ
│   ├── search/           # Поиск
│   └── assets/           # Статические файлы
├── docs/                  # Документация
├── db.sqlite3            # SQLite база данных (Django)
├── manage.py             # Django CLI утилита
├── requirements.txt      # Python зависимости
└── .env                  # Конфигурация (API ключи lk.iek.ru)
```

## API

Проект использует API личного кабинета lk.iek.ru для получения данных о товарах, документах и остатках.

### API Endpoints (Dev server)

**Фотографии товаров**
- `GET /img/{sku}.jpg` — фото товара из lk.iek.ru
- `GET /thumb/{sku}.jpg` — уменьшенная версия фото (480px)

**Документы**
- `GET /docs/{file}` — документы товара (сертификаты, паспорта, схемы)

**API Метаданные**
- `GET /api/docs?sku=ВА47-29` — получить метаданные документов товара

**Остатки на складах**
- `GET /api/stock?sku=A,B,C` — получить остатки со складов ИЭК

**Заказы**
- `POST /api/order` — создать заявку на покупку

### API Примеры

**Получить метаданные документов**
```bash
curl "http://127.0.0.1:8090/api/docs?sku=MVA20-1-006-C"
```

**Ответ:**
```json
{
  "sku": "MVA20-1-006-C",
  "docs": [
    {
      "name": "Сертификат соответствия",
      "type": "сертификат",
      "url": "/docs/certificate_MVA20-1-006-C.pdf"
    },
    {
      "name": "Паспорт",
      "type": "паспорт",
      "url": "/docs/passport_MVA20-1-006-C.pdf"
    }
  ]
}
```

**Получить остатки**
```bash
curl "http://127.0.0.1:8090/api/stock?sku=MVA20-1-006-C,MVA20-2-032-C"
```

**Создать заказ**
```bash
curl -X POST http://127.0.0.1:8090/api/order \
  -H "Content-Type: application/json" \
  -d '{
    "created": "2026-11-17T10:00:00Z",
    "distributor": "Представительство иэк.бел",
    "client": {
      "name": "Иван Иванов",
      "phone": "+375291234567",
      "email": "ivan@example.com",
      "type": "Юр.лицо",
      "org": "ООО Пример",
      "requisites": "P/C 123456789",
      "city": "Минск"
    },
    "comment": "Тестовый заказ",
    "items": [
      {
        "sku": "MVA20-1-006-C",
        "title": "KARAT Автоматический выключатель",
        "qty": 10
      }
    ]
  }'
```

**Ответ:**
```json
{
  "ok": true,
  "orderId": "IEK-241117-A1B2C3",
  "routed": [
    {
      "target": "local-demo",
      "ok": true
    }
  ]
}
```

## Основные задачи

### Добавить новый товар

**Вариант 1: Через админку**
1. Открыть http://localhost:8090/admin/catalog/product/add/
2. Заполнить поля: SKU, название, описание, характеристики
3. Сохранить товар
4. Пересобрать сайт (опционально)

**Вариант 2: Через скрипт импорта**
```bash
# Импортировать конкретное направление
python tools/import_lk.py --kind "Светотехника" --limit 100

# Или весь каталог
python tools/import_lk.py --kind "__ALL__"
```

### Добавить новость

1. Открыть http://localhost:8090/admin/catalog/news/add/
2. Заполнить поля:
   - **Title** — заголовок новости
   - **Slug** — URL (автогенерируется из заголовка, можно оставить пустым)
   - **Kind** — рубрика: news (новость), event (мероприятие), company (о нас)
   - **Date** — дата публикации
   - **Announcement** — анонс (для списка на главной)
   - **Body** — полный текст новости
   - **Photo** — фото (опционально)
3. Сохранить новость
4. Сайт автоматически обновится при следующей сборке

### Обновить каталог

```bash
# 1. Обновить данные из API lk.iek.ru
python tools/import_lk.py --kind "Модульное оборудование"

# 2. Разбить каталог на файлы (если lk-catalog.json большой)
python tools/split_catalog.py

# 3. Пересобрать сайт
python tools/build.py data/lk-catalog.json data/distributors.json site

# 4. Проверить ссылки (опционально)
python tools/check_links.py
```

## Создание нового товара

**Через API lk.iek.ru (рекомендуемый способ):**

1. **Получить API ключи**
   - Логин и пароль берутся из файла `.env`:
     ```
     LK_API_LOGIN='503-20261027-121210-318'
     LK_API_PASSWORD=';Kt1_2Lyq4?VyQ_8'
     ```

2. **Импортировать товары**
   ```bash
   # Импортировать конкретное направление
   python tools/import_lk.py --kind "Щитовое оборудование"

   # Импортировать с лимитом (для тестирования)
   python tools/import_lk.py --kind "Автоматические выключатели" --limit 50

   # Импортировать весь каталог (медленно)
   python tools/import_lk.py --kind "__ALL__"
   ```

3. **Пересобрать сайт**
   ```bash
   python tools/build.py data/lk-catalog.json data/distributors.json site
   ```

**Через админку Django:**

1. **Установить необходимые данные**
   - В админке создать дистрибьюторов
   - Загрузить `data/distributors.json`

2. **Добавить товар вручную**
   - Открыть http://localhost:8090/admin/catalog/product/add/
   - Заполнить обязательные поля:
     - **SKU** — артикул (уникальный)
     - **Name** — название товара
     - **Ddp** — группа ДДП (выбор из выпадающего списка)
     - **Description** — описание
   - Необязательные поля:
     - **Features** — характеристики (JSON поле)
     - **Price** — базовая цена
     - **RRC** — РРЦ (розничная цена по курсу НБРБ)
     - **Stock total** — остаток на складах
   - Сохранить

3. **Пересобрать сайт**
   ```bash
   python tools/build.py data/lk-catalog.json data/distributors.json site
   ```

## Создание новости

**Через админку Django:**

1. Открыть http://localhost:8090/admin/catalog/news/add/
2. Заполнить поля:

   **Основное:**
   - **Title** — заголовок новости
   - **Slug** — URL (опционально, автогенерируется)
   - **Kind** — рубрика:
     - `news` — новость
     - `event` — мероприятие
     - `company` — о представлении
   - **Date** — дата публикации
   - **Is published** — опубликовать сразу

   **Контент:**
   - **Announcement** — анонс (до 500 символов, отображается в списке)
   - **Body** — полный текст (абзацы с новой строки, HTML допустим)

   **Фото:**
   - **Photo** — загрузить файл изображения
   - **Photo caption** — подпись к фото (опционально)

3. Сохранить новость
4. После сохранения сайт автоматически обновится при следующей сборке
   или можно пересобрать принудительно:
   ```bash
   python tools/build.py data/lk-catalog.json data/distributors.json site
   ```

**Через JSON файл (для массовой загрузки):**

1. Создать файл `data/news.json` с структурой:
   ```json
   [
     {
       "title": "Заголовок новости",
       "slug": "url-news",
       "date": "2026-11-17",
       "kind": "news",
       "announcement": "Анонс новости",
       "body": "Полный текст новости\nс новой строки",
       "photo": "photo.jpg",
       "photo_caption": "Подпись к фото"
     }
   ]
   ```

2. Перезаписать `data/news.json`

3. Пересобрать сайт:
   ```bash
   python tools/build.py data/lk-catalog.json data/distributors.json site
   ```

## Изменение дизайна

Дизайн состоит из трёх частей:

### 1. CSS (tools/style.css)

Основной файл стилей. Изменения в нём влияют на весь сайт.

Пример изменения цвета кнопки:
```css
.btn-primary {
  background-color: #007bff;
  color: white;
}
```

Пример изменения шрифта:
```css
body {
  font-family: 'Roboto', sans-serif;
}
```

### 2. HTML шаблоны (tools/build.py)

Генерация HTML происходит в `tools/build.py`:

- **Главная страница**: функция `build_home()`
- **Каталог**: функции `build_catalog()` и `build_category()`
- **Товар**: функция `build_product()`
- **Новости**: функции `build_news()`
- **Дистрибьюторы**: функции `build_distributors()` и `build_map()`

Для изменения дизайна:
1. Отредактируйте HTML в соответствующей функции в `build.py`
2. Добавьте/измените CSS в `tools/style.css`
3. Пересоберите сайт:
   ```bash
   python tools/build.py data/lk-catalog.json data/distributors.json site
   ```

### 3. Статические файлы (tools/assets)

- **CSS**: `tools/assets/css/`
- **JavaScript**: `tools/assets/js/`

Изменения в этих файлах также требуют пересборки.

## Troubleshooting

### Ошибка: Port already in use

**Ошибка:**
```
OSError: [Errno 98] Address already in use
```

**Решение 1: Остановить старый процесс**
```bash
# Найти процесс
lsof -ti:8090

# Остановить процесс
kill -9 <PID>

# Или использовать другой порт
python tools/devserver.py 8091
```

**Решение 2: Найти и остановить все процессы на порту**
```bash
# Linux/Mac
lsof -ti:8090 | xargs kill -9

# Windows
netstat -ano | findstr :8090
taskkill /PID <PID> /F
```

### Ошибка: Ошибка сборки

**Ошибка:**
```
Error building site
```

**Причины:**
- Отсутствует `data/lk-catalog.json`
- Невалидный JSON
- Проблемы в коде сборки
- Многофайловый JSON превышает доступную память (для `lk-catalog.json`)

**Решение:**
```bash
# 1. Проверить JSON
python -m json.tool data/lk-catalog.json

# 2. Разбить каталог на файлы (если каталог большой)
python tools/split_catalog.py

# 3. Проверить структуру
ls -lh data/lk-cats/

# 4. Пересобрать сайт
python tools/build.py data/lk-catalog.json data/distributors.json site

# 5. Или точечная сборка конкретных групп
python tools/build.py data/lk-catalog.json data/distributors.json site --cats catalog,news
```

### Ошибка: Нет данных в админке

**Причина:**
- JSON файлы не скопированы в папку `data/`
- База данных не инициализирована

**Решение:**
```bash
# 1. Проверить наличие файлов
ls -lh data/*.json

# 2. Импортировать данные из API lk.iek.ru
python tools/import_lk.py --kind "Модульное оборудование"

# 3. Разбить каталог
python tools/split_catalog.py

# 4. Перезапустить админку
python tools/devserver.py
```

### Ошибка: Ошибка ETIM характеристики

**Причина:**
- Отсутствует ETIM API ключ
- Ошибка в данных API
- Нет файла `data/etim.db`

**Решение:**
```bash
# 1. Выгрузить данные ETIM из lk.iek.ru
python tools/fetch_etim.py

# 2. Конвертировать в SQLite
python tools/etim_to_sqlite.py

# 3. Проверить базу данных
sqlite3 data/etim.db "SELECT COUNT(*) FROM etim;"

# 4. Пересобрать сайт
python tools/build.py data/lk-catalog.json data/distributors.json site
```

### Ошибка: ImportError: No module named 'PIL'

**Причина:**
- Не установлен модуль Pillow

**Решение:**
```bash
pip install pillow
```

### Ошибка: Out of memory при сборке каталога

**Причина:**
- Слишком большой файл `lk-catalog.json` (136 МБ) не помещается в память

**Решение:**
```bash
# 1. Разбить каталог на файлы
python tools/split_catalog.py

# 2. Сборка автоматически будет использовать разбитый каталог
python tools/build.py data/lk-catalog.json data/distributors.json site
```

### Не работает карта дистрибьюторов

**Причина:**
- Ошибка в `data/distributors.json`
- Отсутствует Leaflet.js
- Нет координат в данных

**Решение:**
```bash
# 1. Проверить координаты в JSON
python -c "import json; print(json.load(open('data/distributors.json')))"

# 2. Проверить структуру координат
grep -A 5 "lat" data/distributors.json

# 3. Проверить наличие Leaflet.js
ls -la tools/assets/vendor/leaflet.*

# 4. Пересобрать сайт
python tools/build.py data/lk-catalog.json data/distributors.json site
```

### Не импортируются фото

**Причина:**
- Отсутствует интернет-соединение
- Неверные API ключи
- Проблемы с папкой для сохранения

**Решение:**
```bash
# 1. Проверить интернет
ping lk.iek.ru

# 2. Проверить .env файл
cat .env

# 3. Создать папку для фото
mkdir -p site/assets/img

# 4. Перезапустить импорт с опцией --no-images
python tools/import_lk.py --kind "Модульное оборудование" --no-images
```

### Не отображаются товары в админке

**Причина:**
- Модель Product не зарегистрирована в админке
- Нет данных в базе данных

**Решение:**
```bash
# 1. Проверить регистрацию модели
grep "ProductAdmin" catalog/admin.py

# 2. Импортировать данные
python tools/import_lk.py --kind "__ALL__"

# 3. Перезапустить админку
python tools/devserver.py
```

### API возвращает ошибку 502

**Причина:**
- Проблемы с API lk.iek.ru
- Неверные API ключи
- Срок действия ключей истёк

**Решение:**
```bash
# 1. Проверить логи
tail -f logs_etim.log

# 2. Проверить API ключи в .env
cat .env | grep LK_API_

# 3. Перезапустить dev server
python tools/devserver.py
```

## Дополнительные команды

```bash
# Очистить кэш
rm -rf _downloads/cache

# Показать структуру каталога
tree -L 2 data/lk-cats/

# Проверить количество товаров
python -c "import json; cats = json.load(open('data/lk-catalog.json')); print(sum(len(c.get('products', [])) for c in cats.get('categories', [])))"

# Показать количество страниц в сайте
find site -name "*.html" | wc -l

# Обновить ETIM базу данных
python tools/fetch_etim.py
python tools/etim_to_sqlite.py
python tools/build.py data/lk-catalog.json data/distributors.json site
```

## Полезные ссылки

- [Django документация](https://docs.djangoproject.com/)
- [LK API lk.iek.ru](https://lk.iek.ru)
- [Leaflet.js](https://leafletjs.com/)
- [Pillow](https://pillow.readthedocs.io/)
