#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""иэк.бел — ЕДИНАЯ точка запуска (PyCharm Run / `python run.py`).

Сам делает всё по порядку и только то, что действительно нужно:
  1. окружение:  .venv + Django/Pillow, если в текущем python их нет
  2. данные:     import_lk из API ИЭК (нужен .env) → split_catalog — если данных нет
  3. сборка:     если site/ отсутствует или устарела относительно данных/кода
  4. база:       migrate + суперюзер admin (если db.sqlite3 ещё нет)
  5. серверы:    сайт :8090 + админка :8091
  6. браузер:    открывает сам

Останов: Ctrl+C / красный квадрат PyCharm — гасит оба сервера.
"""
import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
ENV_FILE = ROOT / ".env"


def venv_python():
    exe = "python.exe" if os.name == "nt" else "python"
    return VENV / ("Scripts" if os.name == "nt" else "bin") / exe


def sh(cmd, cwd=None):
    print("→", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], cwd=str(cwd or ROOT), check=True)


def ensure_python():
    """Django нужен админке. Если в текущем интерпретаторе его нет —
    создаём .venv, ставим requirements и перезапускаем себя под .venv."""
    try:
        import django  # noqa: F401
        return sys.executable
    except ImportError:
        pass
    if os.environ.get("IEK_VENV") == "1":
        sys.exit("! .venv есть, но Django не импортируется — pip install -r requirements.txt")
    if not venv_python().exists():
        print("→ окружение: создаю .venv и ставлю Django + Pillow (один раз)…", flush=True)
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
        subprocess.run([str(venv_python()), "-m", "pip", "install", "-q", "-r",
                        str(ROOT / "requirements.txt")], check=True)
    else:
        print("→ окружение: .venv есть, доустанавливаю requirements…", flush=True)
        subprocess.run([str(venv_python()), "-m", "pip", "install", "-q", "-r",
                        str(ROOT / "requirements.txt")], check=True)
    env = dict(os.environ, IEK_VENV="1")
    print("→ перезапуск под .venv…", flush=True)
    os.execve(str(venv_python()), [str(venv_python()), str(Path(__file__).resolve())], env)


def have_env_keys():
    if not ENV_FILE.exists():
        return False
    text = ENV_FILE.read_text(encoding="utf-8")
    return "LK_API_LOGIN=" in text and "LK_API_PASSWORD=" in text


def ensure_data():
    """Каталог: снапшот из гита → без сети; API+ .env — только для обновления."""
    # характеристики ETIM: в гите только сжатая копия (5 МБ вместо 155).
    # Без etim.db карточки товаров теряют «Другие варианты» (фильтры по
    # параметрам) и ETIM-характеристики. Распаковка ДО ранних return:
    # раньше блок стоял после них и на машинах со снапшотом не выполнялся
    # никогда. Появление etim.db сбрасывает манифест инкремента —
    # следующая сборка полная, фильтры оказываются на всех карточках.
    gz = ROOT / "data" / "etim.db.gz"
    if gz.exists() and not (ROOT / "data" / "etim.db").exists():
        import gzip
        print("→ характеристики: распаковываю data/etim.db.gz…", flush=True)
        with gzip.open(gz, "rb") as fin, open(ROOT / "data" / "etim.db", "wb") as fout:
            fout.write(fin.read())
        mf = ROOT / "data" / ".incbuild.json"
        if mf.exists():
            mf.unlink()
            print("→ манифест инкремента сброшен — будет полная пересборка", flush=True)
        print("→ характеристики: готово", flush=True)
    cats = ROOT / "data" / "lk-cats" / "_index.json"
    if cats.exists():
        return
    snap = ROOT / "data" / "lk-cats.tar.gz"
    if snap.exists():
        print("→ данные: разворачиваю снапшот каталога data/lk-cats.tar.gz…", flush=True)
        import tarfile
        with tarfile.open(snap) as tf:
            tf.extractall(ROOT / "data")
        print("→ данные: готово", flush=True)
        return
    catalog = ROOT / "data" / "lk-catalog.json"
    if not catalog.exists():
        if not have_env_keys():
            sys.exit("! Нет данных каталога и нет .env.\n"
                     "  Положи .env (LK_API_LOGIN=…, LK_API_PASSWORD=…) в корень проекта\n"
                     "  и запусти ещё раз — каталог скачается из API ИЭК автоматически.")
        print("→ данные: качаю каталог из API ИЭК (первый раз ~20–40 мин)…", flush=True)
        sh([sys.executable, "tools/import_lk.py", "--kind", "__ALL__", "--no-images"])
    if not cats.exists():
        print("→ данные: разрезаю каталог на группы…", flush=True)
        sh([sys.executable, "tools/split_catalog.py"])


def newest_mtime(paths):
    newest = 0.0
    for p in paths:
        p = Path(p)
        if p.exists():
            newest = max(newest, p.stat().st_mtime)
    return newest


def build_if_needed():
    index = ROOT / "site" / "index.html"
    n_pages = sum(1 for _ in (ROOT / "site").rglob("*.html")) if (ROOT / "site").is_dir() else 0
    sources = [ROOT / "tools" / "build.py", ROOT / "tools" / "style.css",
               ROOT / "tools" / "assets", ROOT / "data" / "lk-cats" / "_index.json",
               ROOT / "data" / "distributors.json", ROOT / "data" / "news.json"]
    stale = (not index.exists() or n_pages < 70000
             or newest_mtime(sources) > index.stat().st_mtime)
    if stale:
        print(f"→ сборка сайта ({n_pages} страниц сейчас, полная ~8 мин)…", flush=True)
        sh([sys.executable, "tools/build.py", "data/lk-catalog.json",
            "data/distributors.json", "site"])
    else:
        print(f"→ сборка не нужна: сайт актуален ({n_pages} страниц)", flush=True)


def ensure_db(py):
    db = ROOT / "db.sqlite3"
    fresh = not db.exists()
    sh([py, "manage.py", "migrate"], cwd=ROOT)
    # заявки из data/orders/*.json (пишет devserver) → в админку; идемпотентно
    if (ROOT / "data" / "orders").is_dir():
        try:
            sh([py, "manage.py", "load_orders"], cwd=ROOT)
        except Exception:
            pass
    if fresh:
        env = dict(os.environ,
                   DJANGO_SUPERUSER_USERNAME="admin",
                   DJANGO_SUPERUSER_EMAIL="admin@iek-bel.local",
                   DJANGO_SUPERUSER_PASSWORD="iekbel-admin-2026")
        subprocess.run([py, "manage.py", "createsuperuser", "--noinput"],
                       cwd=str(ROOT), env=env, check=True)
        print("→ база создана, суперюзер: admin / iekbel-admin-2026", flush=True)


def port_busy(port):
    s = socket.socket()
    s.settimeout(1)
    try:
        s.bind(("127.0.0.1", port))
        s.close()
        return False
    except OSError:
        return True


def serve(py):
    procs = []
    if port_busy(8090):
        print("→ :8090 уже занят — считаю, что сайт запущен", flush=True)
    else:
        procs.append(subprocess.Popen([py, "tools/devserver.py"], cwd=str(ROOT)))
    if port_busy(8091):
        print("→ :8091 уже занят — считаю, что админка запущена", flush=True)
    else:
        procs.append(subprocess.Popen([py, "manage.py", "runserver", "127.0.0.1:8091"],
                                      cwd=str(ROOT)))
    for _ in range(30):
        time.sleep(1)
        try:
            socket.create_connection(("127.0.0.1", 8090), timeout=1).close()
            break
        except OSError:
            pass
    print("", flush=True)
    print("✓ Сайт:    http://127.0.0.1:8090", flush=True)
    print("✓ Админка: http://127.0.0.1:8091/admin/  (admin / iekbel-admin-2026)", flush=True)
    print("  Останов: Ctrl+C / красный квадрат PyCharm", flush=True)
    try:
        webbrowser.open("http://127.0.0.1:8090/")
    except Exception:
        pass
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\n→ останавливаю серверы…", flush=True)
    finally:
        for p_ in procs:
            p_.terminate()


def main():
    py = ensure_python()          # может перезапустить скрипт под .venv
    (ROOT / "media" / "news").mkdir(parents=True, exist_ok=True)
    ensure_data()
    build_if_needed()
    ensure_db(py)
    serve(py)


if __name__ == "__main__":
    main()
