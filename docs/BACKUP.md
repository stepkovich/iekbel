# BACKUP.md — Инструкции по резервному копированию

## 📋 Что бэкапится

### Обязательные бэкапы
- data/catalog.json — каталог товаров
- data/distributors.json — дистрибьюторы
- data/news.json — новости
- data/orders/ — заявки клиентов
- data/lk-cats/ — категориальный каталог

### Опциональные бэкапы
- data/etim.db — ETIM характеристики
- data/import_partial.json — частичный импорт

### Не бэкапится
- site/ — сгенерированный сайт
- .git/ — есть в репозитории
- node_modules/ — есть в репозитории
- _downloads/ — можно скачать заново
- config/ — конфигурация (не критична)

## 📦 Структура бэкапов

```
backups/
├── 2026-11-18_00-11-45/
│   ├── catalog.json.gz
│   ├── distributors.json.gz
│   ├── news.json.gz
│   ├── orders.tar.gz
│   ├── lk-cats.tar.gz
│   ├── etim.db.gz
│   ├── import_partial.json.gz
│   └── manifest.json
├── 2026-11-17_23-59-32/
│   └── ...
└── ...
```

## 🚀 Использование

### Обычный бэкап
```bash
cd /home/home/Документы/иэк.бел
python tools/backup.py
```

### Указать количество бэкапов
```bash
python tools/backup.py --keep 7
```

### Пробный запуск (без создания бэкапа)
```bash
python tools/backup.py --dry-run
```

### Список существующих бэкапов
```bash
python tools/backup.py --list
```

### Просмотреть список бэкапов
```bash
ls -lht backups/
```

### Просмотреть manifest последнего бэкапа
```bash
cat backups/2026-11-18_00-11-45/manifest.json | python -m json.tool
```

## 🔧 Восстановление

### Из архива JSON файла
```bash
# Распаковать
gunzip -c backups/2026-11-18_00-11-45/catalog.json.gz > data/catalog.json

# Проверить
python -m json.tool data/catalog.json
```

### Восстановить папку orders
```bash
# Распаковать архив
tar -xzf backups/2026-11-18_00-11-45/orders.tar.gz -C data/

# Или в отдельную директорию
tar -xzf backups/2026-11-18_00-11-45/orders.tar.gz -C /tmp
```

### Восстановить папку lk-cats
```bash
tar -xzf backups/2026-11-18_00-11-45/lk-cats.tar.gz -C data/
```

### Проверка данных
```bash
# Проверить JSON
python -m json.tool data/catalog.json

# Перезапустить админку
python tools/devserver.py
```

## ⏰ Автоматизация (cron)

### Ежедневный бэкап (каждое утро в 2 ночи)
```bash
0 2 * * * cd /home/home/Документы/иэк.бел && python tools/backup.py --keep 30 >> logs/cron.log 2>&1
```

### Еженедельный бэкап (каждое воскресенье в 2 ночи)
```bash
0 2 * * 0 cd /home/home/Документы/иэк.бел && python tools/backup.py --keep 4 >> logs/cron.log 2>&1
```

### Проверить cron задачи
```bash
crontab -e
```

## 📊 Мониторинг

### Размер бэкапов
```bash
du -sh backups/
```

### Количество бэкапов
```bash
ls -d backups/*/ | wc -l
```

### Последний бэкап
```bash
ls -lht backups/ | head -5
```

### Размер каждого файла в бэкапе
```bash
du -h backups/2026-11-18_00-11-45/*
```

## ✅ Тест восстановления

### 1. Создать тестовый бэкап
```bash
python tools/backup.py
```

### 2. Проверить данные в админке
Открыть: http://localhost:8090/admin

### 3. Удалить данные (для теста)
```bash
mv data/catalog.json data/catalog.json.backup
```

### 4. Восстановить
```bash
gunzip -c backups/2026-11-18_00-11-45/catalog.json.gz > data/catalog.json
```

### 5. Проверить данные
Открыть админку — данные должны восстановиться

## 🔄 Полное восстановление из бэкапа

### Если все данные потеряны
```bash
# Остановить сервер
# Ctrl+C в терминале с devserver.py

# Восстановить все файлы
gunzip -c backups/LAST_BACKUP/catalog.json.gz > data/catalog.json
gunzip -c backups/LAST_BACKUP/distributors.json.gz > data/distributors.json
gunzip -c backups/LAST_BACKUP/news.json.gz > data/news.json
gunzip -c backups/LAST_BACKUP/etim.db.gz > data/etim.db
gunzip -c backups/LAST_BACKUP/import_partial.json.gz > data/import_partial.json
tar -xzf backups/LAST_BACKUP/orders.tar.gz -C data/
tar -xzf backups/LAST_BACKUP/lk-cats.tar.gz -C data/

# Проверить
python -m json.tool data/catalog.json

# Перезапустить админку
python tools/devserver.py
```

## ⚠️ Рекомендации

1. **Храните бэкапы в 2 местах:**
   - Локально (в проекте)
   - Удалённо (Google Drive, Яндекс.Диск, FTP-сервер)

2. **Регулярно проверяйте бэкапы:**
   - Раз в неделю — проверить восстановление
   - Раз в месяц — проверить целостность
   - Проверяйте размер бэкапа (не должен расти бесконтрольно)

3. **Ведите мониторинг:**
   - Проверяйте логи при запуске
   - Количество, размер, статус бэкапов
   - Размер диска, выделенный под бэкапы

4. **План аварийного восстановления:**
   - Определите порядок восстановления файлов
   - Тестирование восстановления регулярно
   - Документируйте последовательность действий

## 📝 Важные замечания

### О размере бэкапа
- catalog.json.gz: ~3 KB
- distributors.json.gz: ~5 KB
- news.json.gz: ~1 KB
- orders.tar.gz: ~700 B (2 файла)
- lk-cats.tar.gz: ~5.8 MB (15 файлов)
- etim.db.gz: ~5.3 MB
- import_partial.json.gz: ~1.4 KB

**Общий размер:** ~10.66 MB для одного бэкапа

### О сжатии
- JSON файлы сжимаются gzip на ~80-90%
- База данных etim.db сжимается gzip на ~96%
- Папки архивируются tar.gz для сохранения структуры

### О версии
- Каждый бэкап содержит manifest с git-версией
- Позволяет отследить, какая версия данных в бэкапе

## 🆘 Аварийное восстановление

### Если каталог повреждён
```bash
# Найти последний рабочий бэкап
ls -lht backups/

# Восстановить из последнего бэкапа
gunzip -c backups/LAST_BACKUP/catalog.json.gz > data/catalog.json

# Проверить
python -m json.tool data/catalog.json

# Перезапустить
python tools/devserver.py
```

### Если все данные потеряны
```bash
# 1. Найти последний рабочий бэкап
LATEST=$(ls -dt backups/*/ | head -1)

# 2. Восстановить все файлы
gunzip -c "$LATEST/catalog.json.gz" > data/catalog.json
gunzip -c "$LATEST/distributors.json.gz" > data/distributors.json
gunzip -c "$LATEST/news.json.gz" > data/news.json
gunzip -c "$LATEST/etim.db.gz" > data/etim.db
gunzip -c "$LATEST/import_partial.json.gz" > data/import_partial.json
tar -xzf "$LATEST/orders.tar.gz" -C data/
tar -xzf "$LATEST/lk-cats.tar.gz" -C data/

# 3. Проверить
python -m json.tool data/catalog.json

# 4. Перезапустить
python tools/devserver.py
```

## 📞 Помощь

Если проблемы с бэкапами:
- Проверить права доступа: `ls -la data/ backups/`
- Проверить свободное место на диске: `df -h`
- Проверить логи: `tail -f logs/backup.log`
- Проверить cron: `crontab -l`
- Проверить Python: `python --version`

## 📚 Дополнительные ресурсы

- Версия git: `git rev-parse HEAD`
- Размеры данных: `du -sh data/*`
- Логи бэкапов: `cat logs/backup.log`
- Статус cron: `crontab -l`
