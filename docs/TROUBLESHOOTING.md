# Troubleshooting Guide

Руководство по решению типичных проблем при работе с проектом иэк.бел.

## 📋 Содержание
- [Установка и запуск](#установка-и-запуск)
- [Сборка сайта](#сборка-сайта)
- [Импорт данных](#импорт-данных)
- [Работа с API](#работа-с-api)
- [Дизайн и шаблоны](#дизайн-и-шаблоны)
- [Админка](#админка)
- [База данных](#база-данных)
- [Дополнительные проблемы](#дополнительные-проблемы)

---

## Установка и запуск

### 1. Ошибка: Port already in use

**Ошибка:**
```
OSError: [Errno 98] Address already in use
```

**Диагностика:**
```bash
# Найти процесс, занимающий порт
lsof -ti:8090

# Проверить процессы
ps aux | grep devserver
```

**Решение 1: Остановить старый процесс**
```bash
# Linux/Mac
lsof -ti:8090 | xargs kill -9

# Windows
netstat -ano | findstr :8090
taskkill /PID <PID> /F
```

**Решение 2: Использовать другой порт**
```bash
# Запуск на порту 8091
python tools/devserver.py 8091
```

**Решение 3: Автоматическое завершение процессов**
```bash
# Убить все процессы python на порту 8090
fuser -k 8090/tcp
```

---

### 2. Ошибка: ImportError: No module named 'django'

**Ошибка:**
```
ImportError: No module named 'django'
```

**Диагностика:**
```bash
# Проверить, установлена ли Django
python -c "import django; print(django.__version__)"

# Проверить список установленных пакетов
pip list | grep django
```

**Решение:**
```bash
# Установить Django
pip install django==6.1.3

# Установить Pillow
pip install pillow

# Проверить установку
python -c "import django, PIL; print('Django:', django.__version__, 'Pillow:', PIL.__version__)"
```

---

### 3. Ошибка: AttributeError: module 'tkinter' not found

**Ошибка:**
```
AttributeError: module 'tkinter' not found
```

**Причина:**
- В системах Ubuntu/Debian tkinter может быть не установлен

**Решение:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Ubuntu/Debian (full Tkinter)
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

---

### 4. Ошибка: Permission denied

**Ошибка:**
```
Permission denied: '/home/user/.venv/bin/activate'
```

**Диагностика:**
```bash
# Проверить права доступа
ls -la .venv/bin/activate
```

**Решение:**
```bash
# Изменить права
chmod +x .venv/bin/activate
chmod +x .venv/bin/python*
chmod +x .venv/bin/pip*

# Или переустановить виртуальную среду
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
```

---

## Сборка сайта

### 5. Ошибка: Ошибка сборки

**Ошибка:**
```
Error building site
```

**Диагностика:**
```bash
# Показать ошибки сборки
python tools/build.py data/lk-catalog.json data/distributors.json site 2>&1 | tee build_errors.log

# Проверить размер файла
ls -lh data/lk-catalog.json
```

**Причина 1: Отсутствует lk-catalog.json**
```bash
# Проверить наличие файла
ls -lh data/lk-catalog.json

# Если нет, импортировать данные
python tools/import_lk.py --kind "__ALL__"
```

**Причина 2: Невалидный JSON**
```bash
# Проверить JSON
python -m json.tool data/lk-catalog.json

# Если есть ошибки, восстановить из бэкапа или переимпортировать
```

**Причина 3: Многофайловый JSON (OOM)**
```bash
# Разбить каталог на файлы
python tools/split_catalog.py

# Проверить результат
ls -lh data/lk-cats/

# Пересобрать сайт
python tools/build.py data/lk-catalog.json data/distributors.json site
```

**Причина 4: Проблемы с памятью**
```bash
# Увеличить лимит памяти (если возможно)
ulimit -v 4000000

# Или использовать точечную сборку
python tools/build.py data/lk-catalog.json data/distributors.json site --cats catalog,news
```

---

### 6. Ошибка: No such file or directory: 'data/lk-catalog.json'

**Ошибка:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/lk-catalog.json'
```

**Диагностика:**
```bash
# Проверить, существует ли файл
ls -lh data/*.json

# Проверить текущую директорию
pwd
```

**Решение:**
```bash
# Импортировать данные из API lk.iek.ru
python tools/import_lk.py --kind "Модульное оборудование"

# Или импортировать весь каталог
python tools/import_lk.py --kind "__ALL__"
```

---

### 7. Слишком долгая сборка

**Проблема:**
Сборка занимает более 5 минут

**Диагностика:**
```bash
# Показать время сборки
time python tools/build.py data/lk-catalog.json data/distributors.json site
```

**Причина 1: Разбить каталог на файлы**
```bash
# Разбить каталог (уменьшит потребление памяти)
python tools/split_catalog.py

# Пересобрать (будет быстрее)
time python tools/build.py data/lk-catalog.json data/distributors.json site
```

**Причина 2: Отключить параллельную сборку**
```bash
# Использовать однопоточный режим
BUILD_SERIAL=1 python tools/build.py data/lk-catalog.json data/distributors.json site
```

**Причина 3: Точечная сборка**
```bash
# Собрать только нужные разделы
python tools/build.py data/lk-catalog.json data/distributors.json site --cats catalog,news
```

---

### 8. Не создаётся sitemap.xml

**Проблема:**
Файл `site/sitemap.xml` не создаётся

**Диагностика:**
```bash
# Проверить, есть ли HTML файлы
find site -name "*.html" | wc -l

# Проверить права на директорию
ls -la site/
```

**Решение:**
```bash
# Проверить размер сайта
du -sh site/

# Если есть файлы, пересобрать с полной очисткой
rm -rf site/*.xml
python tools/build.py data/lk-catalog.json data/distributors.json site
```

---

## Импорт данных

### 9. Ошибка: ImportError: No module named 'requests'

**Ошибка:**
```
ModuleNotFoundError: No module named 'requests'
```

**Причина:**
- Модуль requests не установлен

**Решение:**
```bash
pip install requests
```

---

### 10. Ошибка: 401 Unauthorized при импорте

**Ошибка:**
```
HTTPError: 401 Client Error: Unauthorized for url: https://lk.iek.ru/api/...
```

**Диагностика:**
```bash
# Проверить .env файл
cat .env

# Проверить API ключи
grep LK_API .env
```

**Решение:**
```bash
# Проверить формат .env
cat .env | grep LK_API_LOGIN
cat .env | grep LK_API_PASSWORD

# Перезапустить dev server
python tools/devserver.py
```

---

### 11. Ошибка: Слишком медленный импорт

**Проблема:**
Импорт каталога занимает более 1 часа

**Диагностика:**
```bash
# Показать прогресс
python tools/import_lk.py --kind "Модульное оборудование" 2>&1 | tee import.log

# Проверить логи
tail -f logs_import.log
```

**Причина 1: Ограничение API**
```bash
# Установить лимит для тестирования
python tools/import_lk.py --kind "Модульное оборудование" --limit 100
```

**Причина 2: Медленная сеть**
```bash
# Проверить скорость
ping lk.iek.ru

# Использовать другой источник данных (если доступно)
```

**Причина 3: Отсутствие кэша DDP**
```bash
# Удалить кэш и перезапустить
rm -f _downloads/lk_ddp.json
python tools/import_lk.py --kind "Модульное оборудование"
```

---

### 12. Ошибка: Кэш не очищается

**Проблема:**
После обновления данных, старые данные всё ещё отображаются

**Диагностика:**
```bash
# Проверить файлы кэша
ls -lh _downloads/cache/

# Проверить время изменения
stat _downloads/cache/ | grep Modify

# Проверить данные в JSON
python -c "import json; print(json.load(open('data/lk-catalog.json'))['categories'][0]['title'])"
```

**Решение:**
```bash
# Очистить кэш
rm -rf _downloads/cache/

# Перезапустить dev server
python tools/devserver.py

# Проверить данные
curl "http://127.0.0.1:8090/api/stock?sku=MVA20-1-006-C"
```

---

### 13. Ошибка: Недостаточно памяти при импорте

**Ошибка:**
```
MemoryError: Unable to allocate array
```

**Диагностика:**
```bash
# Проверить память системы
free -h

# Проверить размер импортируемых данных
ls -lh data/lk-catalog.json
```

**Решение:**
```bash
# Увеличить лимит памяти (если возможно)
ulimit -v 8000000

# Импортировать по направлениям
python tools/import_lk.py --kind "Модульное оборудование"
python tools/import_lk.py --kind "Светотехника"

# Разбить каталог на файлы
python tools/split_catalog.py
```

---

## Работа с API

### 14. Ошибка: API возвращает 502

**Ошибка:**
```
HTTPError: 502 Bad Gateway for url: https://lk.iek.ru/api/...
```

**Диагностика:**
```bash
# Проверить логи
tail -f logs_etim.log

# Проверить доступность API
curl -I https://lk.iek.ru/api/ddp

# Проверить API ключи
cat .env
```

**Решение:**
```bash
# Проверить сеть
ping lk.iek.ru

# Проверить API ключи
grep LK_API .env

# Проверить формат ключей
python -c "from base64 import b64encode; print(b64encode(b'test:test').decode())"

# Перезапустить dev server
python tools/devserver.py
```

---

### 15. Ошибка: API возвращает пустые данные

**Проблема:**
API lk.iek.ru возвращает пустой массив товаров

**Диагностика:**
```bash
# Проверить запрос
curl "https://lk.iek.ru/api/products?entity=Description,Advantages&format=json"

# Проверить параметры
curl "https://lk.iek.ru/api/products?groupId=0000000000&pageSize=100&entity=Description,Advantages&format=json"
```

**Решение:**
```bash
# Проверить логи
tail -f logs_import.log

# Проверить идентификаторы групп DDP
cat _downloads/lk_ddp.json | head -20

# Попробовать с другим API ключом

# Проверить параметры запроса
python -c "
import urllib.request
import json

url = 'https://lk.iek.ru/api/products?entity=Description,Advantages,ImgPng,ImgJpeg,rrc,roc,LeftPeriod,Analog&format=json'
req = urllib.request.Request(url, headers={
    'Authorization': 'Basic MTAzLTIwMjYxMDI3LTEyMTIxMTAtMzE4',
    'User-Agent': 'iek-bel-import/1.0'
})
try:
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=2)[:1000])
except Exception as e:
    print(f'Error: {e}')
"
```

---

### 16. Ошибка: Фотографии не отображаются

**Проблема:**
Фото товаров не загружаются в браузере

**Диагностика:**
```bash
# Проверить логи
tail -f logs_dev.log

# Проверить папку для фото
ls -lh site/assets/img/

# Проверить доступ к lk.iek.ru
curl -I https://lk.iek.ru/api/store/TEST.jpg

# Проверить API ключи
cat .env
```

**Решение 1: Проверить API ключи**
```bash
# Перезапустить dev server с логами
python tools/devserver.py 2>&1 | tee devserver.log
```

**Решение 2: Проверить логи**
```bash
# Показать последние ошибки
tail -100 logs_etim.log | grep -i error

# Показать доступ к фото
grep "/img/" logs_dev.log | tail -20
```

**Решение 3: Обновить фото**
```bash
# Перезапустить dev server
python tools/devserver.py

# Очистить кэш
rm -rf _downloads/cache/*

# Проверить конкретный товар
curl "http://127.0.0.1:8090/img/MVA20-1-006-C.jpg" -o test.jpg
ls -lh test.jpg
```

---

### 17. Ошибка: API /api/stock возвращает 404

**Ошибка:**
```
404 Not Found: /api/stock
```

**Диагностика:**
```bash
# Проверить, запущен ли dev server
ps aux | grep devserver

# Проверить логи
tail -f logs_dev.log
```

**Решение:**
```bash
# Перезапустить dev server
python tools/devserver.py

# Проверить доступность
curl "http://127.0.0.1:8090/api/stock?sku=MVA20-1-006-C"
```

---

## Дизайн и шаблоны

### 18. CSS не применяется

**Проблема:**
Изменения в CSS не отображаются

**Диагностика:**
```bash
# Проверить файл style.css
cat tools/style.css | grep "\.btn-primary"

# Проверить, загружается ли CSS
curl -I http://127.0.0.1:8090/assets/style.css
```

**Решение:**
```bash
# Проверить селекторы в CSS
grep "\.btn-primary" tools/style.css

# Проверить верстку HTML
grep "btn-primary" site/index.html

# Очистить кэш браузера (Ctrl+Shift+R)

# Пересобрать сайт
python tools/build.py data/lk-catalog.json data/distributors.json site
```

---

### 19. Шаблон не обновляется

**Проблема:**
Изменения в HTML шаблоне не отображаются

**Диагностика:**
```bash
# Проверить, существует ли файл
ls -lh site/index.html

# Проверить содержимое файла
grep "Главная" site/index.html

# Проверить, есть ли коммит времени сборки
grep "BUILD=" site/index.html
```

**Решение:**
```bash
# Проверить, есть ли изменения
git status site/index.html

# Показать изменения
git diff site/index.html

# Пересобрать сайт
python tools/build.py data/lk-catalog.json data/distributors.json site
```

---

### 20. Карта дистрибьюторов не работает

**Проблема:**
Карта на странице distributors/map/ не отображается

**Диагностика:**
```bash
# Проверить наличие Leaflet.js
ls -lh tools/assets/vendor/leaflet.css

# Проверить наличие данных
curl "http://127.0.0.1:8090/distributors/map/"
grep "PARTNERS" site/distributors/map/index.html

# Проверить логи
tail -f logs_dev.log | grep map
```

**Решение 1: Проверить наличие файлов**
```bash
# Проверить структуру
ls -R tools/assets/vendor/
```

**Решение 2: Проверить данные дистрибьюторов**
```bash
# Проверить JSON
python -c "import json; data = json.load(open('data/distributors.json')); print(f'Дистрибьюторов: {len(data[\"distributors\"])}')"

# Проверить координаты
python -c "import json; data = json.load(open('data/distributors.json')); dists = data['distributors']; locs = [loc for d in dists for loc in d.get('locations', []) if 'lat' in loc and 'lon' in loc]; print(f'Точек с координатами: {len(locs)}')"
```

**Решение 3: Проверить JavaScript**
```bash
# Проверить console.log в браузере
# Открыть консоль F12 и посмотреть на ошибки JavaScript
```

---

## Админка

### 21. Не открывается админка

**Проблема:**
http://localhost:8090/admin — 404 или ошибка

**Диагностика:**
```bash
# Проверить, запущен ли dev server
ps aux | grep devserver

# Проверить логи
tail -f logs_dev.log

# Проверить URL
curl "http://127.0.0.1:8090/admin"
```

**Решение:**
```bash
# Перезапустить dev server
python tools/devserver.py

# Проверить настройки Django
grep "ROOT_URLCONF" config/settings.py

# Проверить Django URL конфигурацию
cat config/urls.py
```

---

### 22. Не загружаются изображения в админке

**Проблема:**
Изображения товаров не отображаются в админке

**Диагностика:**
```bash
# Проверить наличие файлов в site/assets/img/
ls -lh site/assets/img/

# Проверить права доступа
ls -la site/assets/img/

# Проверить логи
tail -f logs_dev.log
```

**Решение:**
```bash
# Проверить права доступа
chmod -R 755 site/assets/img/

# Проверить, есть ли фото
find data/lk-catalog.json -name "*.jpg"

# Проверить, есть ли фото в данных
python -c "
import json
data = json.load(open('data/lk-catalog.json'))
products = [p for cat in data['categories'] for p in cat.get('products', []) if 'img' in p]
print(f'Товаров с фото: {len(products)}')
"
```

---

### 23. Не работает поиск в админке

**Проблема:**
Поиск по товарам не работает

**Диагностика:**
```bash
# Проверить поле search_fields в admin.py
grep "search_fields" catalog/admin.py

# Проверить количество товаров
python -c "
import json
data = json.load(open('data/lk-catalog.json'))
products = [p for cat in data['categories'] for p in cat.get('products', [])]
print(f'Всего товаров: {len(products)}')
"
```

**Решение:**
```bash
# Проверить индекс
python manage.py check

# Проверить мегамодели (если используются)
python manage.py makemigrations

# Проверить логи
tail -f logs_dev.log | grep search
```

---

## База данных

### 24. Ошибка: Database is locked

**Ошибка:**
```
Database is locked
```

**Причина:**
- База данных заблокирована другим процессом

**Решение:**
```bash
# Проверить, есть ли другие Django процессы
ps aux | grep django

# Остановить все Django процессы
pkill -f "python manage.py"

# Удалить lock файл
rm -f db.sqlite3-journal

# Перезапустить
python manage.py migrate
```

---

### 25. Ошибка: Migration error

**Ошибка:**
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Решение:**
```bash
# Очистить миграции
rm -rf migrations/

# Создать новые миграции
python manage.py makemigrations

# Применить миграции
python manage.py migrate
```

---

## Дополнительные проблемы

### 26. Проблема: Разные версии Python

**Проблема:**
Код работает на одной версии Python, но не на другой

**Диагностика:**
```bash
# Проверить версии
python --version
python3 --version

# Проверить интерпретатор в скриптах
head -1 tools/build.py
head -1 tools/devserver.py
```

**Решение:**
```bash
# Указать версию Python в скрипте
#!/usr/bin/env python3

# Или создать псевдоним
alias python='python3'

# Или установить обе версии
# Python 3.12
python3 --version
```

---

### 27. Проблема: Слишком много файлов

**Проблема:**
Проект содержит миллионы файлов

**Диагностика:**
```bash
# Проверить количество файлов
find . -type f | wc -l

# Проверить размер проекта
du -sh .

# Проверить .gitignore
cat .gitignore
```

**Решение:**
```bash
# Обновить .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".venv/" >> .gitignore
echo "site/" >> .gitignore
echo "data/" >> .gitignore
echo "logs_*.log" >> .gitignore

# Очистить кэш Python
find . -type d -name "__pycache__" -exec rm -rf {} +

# Очистить файлы .pyc
find . -name "*.pyc" -delete
```

---

### 28. Проблема: Недостаточно дискового пространства

**Проблема:**
Ошибка: No space left on device

**Диагностика:**
```bash
# Проверить диск
df -h

# Проверить использование
du -sh *

# Проверить размер каталога
du -sh data/
```

**Решение:**
```bash
# Удалить временные файлы
rm -rf _downloads/cache/

# Очистить журналы
rm -f logs_*.log

# Удалить старые бэкапы
find . -name "*.bak" -delete

# Очистить кэш Python
find . -type d -name "__pycache__" -exec rm -rf {} +

# Использовать точечную сборку
python tools/build.py data/lk-catalog.json data/distributors.json site --cats catalog
```

---

### 29. Проблема: Неправильные права доступа

**Проблема:**
Скрипты не запускаются

**Диагностика:**
```bash
# Проверить права на скрипты
ls -lh tools/*.py

# Проверить shebang
head -1 tools/*.py
```

**Решение:**
```bash
# Сделать скрипты исполняемыми
chmod +x tools/*.py

# Проверить shebang
# Должно быть: #!/usr/bin/env python3
```

---

### 30. Проблема: Нет интернета

**Проблема:**
Импорт не работает без интернета

**Диагностика:**
```bash
# Проверить доступность сайта
ping lk.iek.ru
curl -I https://lk.iek.ru/api/ddp

# Проверить DNS
nslookup lk.iek.ru
dig lk.iek.ru
```

**Решение:**
```bash
# Проверить соединение
ping -c 5 lk.iek.ru

# Проверить DNS
nslookup lk.iek.ru

# Если DNS не работает, проверьте /etc/resolv.conf

# Проверить firewall
sudo ufw status
```

---

## Полезные команды для диагностики

```bash
# Проверить статус проекта
echo "=== Статус проекта ==="
echo "Время: $(date)"
echo "Память: $(free -h | grep Mem | awk '{print $3}')"
echo "Диск: $(df -h | grep /$ | awk '{print $3}')"
echo "Процессы Django: $(ps aux | grep 'manage.py\|devserver' | grep -v grep | wc -l)"
echo "Файлов: $(find . -type f | wc -l)"
echo "Размер: $(du -sh . | awk '{print $1}')"

# Проверить структуру проекта
echo "=== Структура ==="
ls -lh data/*.json
ls -lh site/*.html | head -10
ls -lh tools/*.py

# Проверить API
echo "=== API lk.iek.ru ==="
curl -s "https://lk.iek.ru/api/ddp?format=json" | python3 -c "import json, sys; data = json.load(sys.stdin); print(f'Групп: {len(data)}')"

# Проверить данные
echo "=== Данные ==="
python -c "import json; data = json.load(open('data/lk-catalog.json')); print(f'Категорий: {len(data[\"categories\"])}'); print(f'Товаров: {sum(len(c.get(\"products\", [])) for c in data[\"categories\"])}')"

# Проверить логи
echo "=== Последние ошибки ==="
tail -20 logs_etim.log 2>/dev/null || echo "Логов нет"
tail -20 logs_import.log 2>/dev/null || echo "Логов нет"
tail -20 logs_dev.log 2>/dev/null || echo "Логов нет"
```

---

## Получение помощи

Если проблема не решена:

1. **Проверить логи**
   ```bash
   tail -100 logs_etim.log
   tail -100 logs_import.log
   tail -100 logs_dev.log
   ```

2. **Проверить документацию**
   - docs/DEVELOPER.md — инструкции для разработчиков
   - docs/API.md — документация API
   - docs/TROUBLESHOOTING.md — это руководство

3. **Проверить интернет-соединение**
   ```bash
   ping lk.iek.ru
   ```

4. **Проверить версию Python**
   ```bash
   python --version
   ```

5. **Проверить права доступа**
   ```bash
   ls -la tools/*.py
   chmod +x tools/*.py
   ```

6. **Проверить зависимости**
   ```bash
   pip list
   pip list | grep -E "django|pillow|requests"
   ```

7. **Проверить файлы проекта**
   ```bash
   ls -lh data/*.json
   ls -lh site/
   ls -lh tools/
   ```

8. **Перезапустить сервер**
   ```bash
   # Остановить
   pkill -f "python tools/devserver.py"

   # Запустить
   python tools/devserver.py 2>&1 | tee devserver.log
   ```

9. **Пересобрать сайт**
   ```bash
   python tools/build.py data/lk-catalog.json data/distributors.json site
   ```

10. **Импортировать данные**
    ```bash
    python tools/import_lk.py --kind "__ALL__"
    ```

---

## Типичные сценарии

### Сценарий 1: Первый запуск

```bash
# 1. Клонировать репозиторий
git clone <url>
cd иэк.бел

# 2. Установить зависимости
python3 -m venv .venv
source .venv/bin/activate
pip install django==6.1.3 pillow

# 3. Настроить .env
cp .env.example .env
# Заполнить LK_API_LOGIN и LK_API_PASSWORD

# 4. Импортировать данные
python tools/import_lk.py --kind "__ALL__"

# 5. Разбить каталог
python tools/split_catalog.py

# 6. Запустить dev server
python tools/devserver.py 8090

# 7. Открыть в браузере
# http://localhost:8090
```

### Сценарий 2: Обновление данных

```bash
# 1. Обновить данные из API
python tools/import_lk.py --kind "__ALL__"

# 2. Разбить каталог
python tools/split_catalog.py

# 3. Проверить изменения
git diff data/lk-catalog.json | head -50

# 4. Пересобрать сайт
python tools/build.py data/lk-catalog.json data/distributors.json site

# 5. Проверить сайт
# http://localhost:8090
```

### Сценарий 3: Добавить новость

```bash
# 1. Открыть админку
# http://localhost:8090/admin/

# 2. Добавить новость через админку
# или создать файл data/news.json

# 3. Пересобрать сайт
python tools/build.py data/lk-catalog.json data/distributors.json site

# 4. Проверить
curl "http://localhost:8090/news/"
```

### Сценарий 4: Добавить товар

```bash
# 1. Добавить через админку
# http://localhost:8090/admin/catalog/product/add/

# 2. Заполнить поля
# SKU, Name, Description, Ddp, Price

# 3. Сохранить

# 4. Пересобрать сайт
python tools/build.py data/lk-catalog.json data/distributors.json site

# 5. Проверить
curl "http://localhost:8090/catalog/автоматические-выключатели/"
```

---

## Резюме

**Основные решения проблем:**

1. **Ошибка порта** — остановить старый процесс или использовать другой порт
2. **Ошибка модулей** — установить зависимости
3. **Ошибка JSON** — проверить формат или разбить на части
4. **Ошибка памяти** — разбить каталог или использовать точечную сборку
5. **Ошибка API** — проверить ключи и сетевое соединение
6. **Ошибка CSS** — очистить кэш браузера и пересобрать
7. **Ошибка базы данных** — перезапустить или почистить миграции
8. **Проблема с дизайном** — проверить HTML/CSS файлы и пересобрать

**Полезные команды:**

```bash
# Диагностика
time python tools/build.py data/lk-catalog.json data/distributors.json site
tail -f logs_*.log
find . -type f | wc -l
du -sh .

# Очистка
rm -rf _downloads/cache/
rm -rf __pycache__/
find . -name "*.pyc" -delete

# Рестарт
pkill -f "python manage.py"
python tools/devserver.py
```

**Успешной работы с проектом!**
