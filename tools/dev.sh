#!/bin/bash
# Одна кнопка: пересборка сайта + статика 8090 + Django-админка 8091
cd "$(dirname "$0")/.." || exit 1
PY="${PYTHON:-/home/home/mmenv/bin/python}"

# гасим старые экземпляры (не убивая себя: скобки в паттерне)
pkill -f "devserver[.]py" 2>/dev/null
pkill -f "runserver 127[.]0[.]0[.]1:8091" 2>/dev/null
sleep 1

echo "→ сборка статики..."
"$PY" tools/build.py data/lk-catalog.json data/distributors.json site

echo "→ статический сайт :8090..."
nohup "$PY" tools/devserver.py 8090 > logs_dev.log 2>&1 &

echo "→ Django админка :8091..."
nohup "$PY" manage.py runserver 127.0.0.1:8091 > logs_django.log 2>&1 &

sleep 2
echo ""
echo "✓ Сайт:      http://127.0.0.1:8090"
echo "✓ Админка:   http://127.0.0.1:8091/admin/  (admin / iekbel-admin-2026)"
echo "Логи: logs_dev.log, logs_django.log"
