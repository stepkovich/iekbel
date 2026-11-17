# Community 1

> 37 nodes

## Key Concepts

- **models.py** (11 connections) — `catalog/models.py`
- **pathlib** (11 connections)
- **load_lk.py** (9 connections) — `catalog/management/commands/load_lk.py`
- **DdpNode** (9 connections) — `catalog/models.py`
- **export_news.py** (8 connections) — `catalog/management/commands/export_news.py`
- **load_orders.py** (8 connections) — `catalog/management/commands/load_orders.py`
- **News** (7 connections) — `catalog/models.py`
- **Product** (7 connections) — `catalog/models.py`
- **Order** (6 connections) — `catalog/models.py`
- **Command** (5 connections) — `catalog/management/commands/load_lk.py`
- **Command** (4 connections) — `catalog/management/commands/export_news.py`
- **.handle()** (4 connections) — `catalog/management/commands/load_lk.py`
- **Command** (4 connections) — `catalog/management/commands/load_orders.py`
- **django_core_management_base** (3 connections)
- **make()** (2 connections) — `catalog/management/commands/load_lk.py`
- **settings.py** (2 connections) — `config/settings.py`
- **shutil** (2 connections)
- **.handle()** (1 connections) — `catalog/management/commands/export_news.py`
- **BaseCommand** (1 connections)
- **Выгрузка опубликованных новостей в data/news.json (+ фото в data/news_photos/).…** (1 connections) — `catalog/management/commands/export_news.py`
- **BaseCommand** (1 connections)
- **Загрузка каталога ИЭК из выгрузок ЛК в базу Django. Запуск: python manage.py…** (1 connections) — `catalog/management/commands/load_lk.py`
- **.handle()** (1 connections) — `catalog/management/commands/load_orders.py`
- **BaseCommand** (1 connections)
- **Импорт заявок из data/orders/*.json (пишет devserver/Worker) в базу. Запуск:…** (1 connections) — `catalog/management/commands/load_orders.py`
- *... and 12 more nodes in this community*

## Relationships

- [Community 3](Community_3.md) (7 shared connections)
- [Community 2](Community_2.md) (6 shared connections)
- [Community 6](Community_6.md) (2 shared connections)
- [Community 0](Community_0.md) (2 shared connections)
- [Community 4](Community_4.md) (2 shared connections)
- [Community 5](Community_5.md) (1 shared connections)

## Source Files

- `catalog/management/commands/export_news.py`
- `catalog/management/commands/load_lk.py`
- `catalog/management/commands/load_orders.py`
- `catalog/models.py`
- `config/settings.py`

## Audit Trail

- EXTRACTED: 67 (94%)
- INFERRED: 4 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*