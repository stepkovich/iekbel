#!/usr/bin/env python3
"""
Скрипт создания резервных копий данных.

Использование:
    python tools/backup.py                 # Обычный бэкап
    python tools/backup.py --keep 7        # Оставить 7 бэкапов
    python tools/backup.py --gzip          # Сжать архивы (по умолчанию уже сжатые)

Структура бэкапов:
    backups/
        2026-11-17_14-30-45/
            catalog.json.gz
            distributors.json.gz
            news.json.gz
            orders.tar.gz
            lk-cats.tar.gz
            etim.db.gz
            import_partial.json.gz
            manifest.json
"""

import os
import sys
import subprocess
import tarfile
import gzip
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path


class BackupManager:
    """Управление резервными копиями данных."""

    def __init__(self, keep_days=30, dry_run=False):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / 'data'
        self.backups_dir = self.project_root / 'backups'
        self.logs_dir = self.project_root / 'logs'
        self.keep_days = keep_days
        self.dry_run = dry_run

        # Создаём необходимые директории
        self.backups_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        # Файл логов
        self.log_file = self.logs_dir / 'backup.log'

        # Источник версии
        self.git_version = self._get_git_version()

    def _get_git_version(self):
        """Получить версию из git."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()[:7]
        except Exception as e:
            return f'unknown-{datetime.now().strftime("%Y%m%d")}'

    def _log(self, message):
        """Логирование в файл и консоль."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f'[{timestamp}] {message}\n'

        # В консоль
        print(log_message.strip())

        # В файл
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message)

    def _calculate_size(self, filepath):
        """Рассчитать размер файла в байтах."""
        return os.path.getsize(filepath)

    def validate_data(self):
        """Валидация наличия данных."""
        self._log('Проверка наличия данных...')

        required_files = {
            'catalog.json': self.data_dir / 'catalog.json',
            'distributors.json': self.data_dir / 'distributors.json',
            'news.json': self.data_dir / 'news.json',
            'orders': self.data_dir / 'orders',
            'lk-cats': self.data_dir / 'lk-cats',
        }

        optional_files = {
            'etim.db': self.data_dir / 'etim.db',
            'import_partial.json': self.data_dir / 'import_partial.json',
        }

        # Проверяем обязательные файлы
        for name, path in required_files.items():
            if path.is_file():
                size = self._calculate_size(path)
                self._log(f'  ✓ {name}: {size:,} байт')
            elif path.is_dir():
                total_size = sum(self._calculate_size(f) for f in path.glob('*'))
                self._log(f'  ✓ {name}/: {total_size:,} байт')
            else:
                self._log(f'  ✗ {name}: Файл не найден')
                return False

        # Проверяем опциональные файлы
        for name, path in optional_files.items():
            if path.exists():
                size = self._calculate_size(path)
                self._log(f'  ⚠ {name}: {size:,} байт')
            else:
                self._log(f'  ⚠ {name}: Отсутствует (опционально)')

        return True

    def create_backup(self):
        """Создать резервную копию."""
        backup_id = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_path = self.backups_dir / backup_id

        self._log(f'Создание бэкапа: {backup_id}')
        self._log(f'Целевая директория: {backup_path}')

        if self.dry_run:
            self._log('DRY RUN: бэкап не создан')
            return False

        # Создаём директорию для бэкапа
        backup_path.mkdir(exist_ok=True)

        # Список файлов для бэкапа (индивидуальные файлы)
        files_to_backup = {
            'catalog.json': self.data_dir / 'catalog.json',
            'distributors.json': self.data_dir / 'distributors.json',
            'news.json': self.data_dir / 'news.json',
            'etim.db.gz': self.data_dir / 'etim.db',
            'import_partial.json.gz': self.data_dir / 'import_partial.json',
        }

        # Папки для архивирования
        folders_to_backup = {
            'orders': self.data_dir / 'orders',
            'lk-cats': self.data_dir / 'lk-cats',
        }

        # Размеры файлов в бэкапе
        file_sizes = {}
        total_size = 0

        # Архивируем отдельные файлы
        for filename, filepath in files_to_backup.items():
            if filepath and filepath.exists():
                # Сжимаем файл
                dest_file = backup_path / filename
                with open(filepath, 'rb') as f_in:
                    with gzip.open(dest_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                size = self._calculate_size(dest_file)
                file_sizes[filename] = size
                total_size += size
                self._log(f'  ✓ {filename}: {size:,} байт')
            else:
                self._log(f'  ⚠ {filename}: Пропущено')

        # Архивируем папки в tar.gz
        for tar_filename, folder_path in folders_to_backup.items():
            if folder_path.exists():
                dest_file = backup_path / f'{tar_filename}.tar.gz'
                with tarfile.open(dest_file, 'w:gz') as tar:
                    for item in folder_path.iterdir():
                        tar.add(item, arcname=item.name)

                size = self._calculate_size(dest_file)
                file_sizes[f'{tar_filename}.tar.gz'] = size
                total_size += size
                self._log(f'  ✓ {tar_filename}.tar.gz: {size:,} байт')

        # Создаём manifest.json
        manifest = {
            "backup_id": backup_id,
            "datetime": datetime.now().isoformat(),
            "source_version": self.git_version,
            "files": file_sizes,
            "size_bytes": total_size,
            "size_mb": round(total_size / (1024 * 1024), 2)
        }

        manifest_file = backup_path / 'manifest.json'
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        self._log(f'  ✓ manifest.json: {len(file_sizes)} файлов')
        self._log(f'  Общий размер: {total_size:,} байт ({manifest["size_mb"]} MB)')

        # Удаляем старые бэкапы
        self._cleanup_old_backups()

        return True

    def _cleanup_old_backups(self):
        """Удаление старых бэкапов."""
        self._log(f'Очистка старых бэкапов (хранить последние {self.keep_days} дней)...')

        cutoff_date = datetime.now().timestamp() - (self.keep_days * 24 * 60 * 60)

        deleted_count = 0
        for backup_dir in sorted(self.backups_dir.iterdir(), reverse=True):
            if backup_dir.is_dir() and backup_dir.name.isdigit():
                # Извлекаем дату из имени директории
                try:
                    backup_date = datetime.strptime(backup_dir.name, '%Y-%m-%d_%H-%M-%S')
                    if backup_date.timestamp() < cutoff_date:
                        if not self.dry_run:
                            shutil.rmtree(backup_dir)
                            self._log(f'  ✓ Удалён старый бэкап: {backup_dir.name}')
                        else:
                            self._log(f'  ⚠ DRY RUN: {backup_dir.name}')
                        deleted_count += 1
                except ValueError:
                    continue

        if deleted_count == 0:
            self._log('  Нет старых бэкапов для удаления')

    def list_backups(self):
        """Список существующих бэкапов."""
        self._log('Существующие бэкапы:')

        backups = []
        for backup_dir in sorted(self.backups_dir.iterdir(), reverse=True):
            if backup_dir.is_dir() and backup_dir.name.isdigit():
                manifest_file = backup_dir / 'manifest.json'
                if manifest_file.exists():
                    with open(manifest_file, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                    backups.append(manifest)

        if not backups:
            self._log('  Нет бэкапов')
            return

        for backup in backups:
            self._log(f'  • {backup["backup_id"]}')
            self._log(f'    Дата: {backup["datetime"]}')
            self._log(f'    Версия: {backup["source_version"]}')
            self._log(f'    Размер: {backup["size_mb"]} MB')
            self._log(f'    Файлов: {len(backup["files"])}')


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(
        description='Создание резервных копий данных проекта',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
    python tools/backup.py                # Обычный бэкап
    python tools/backup.py --keep 7       # Оставить 7 бэкапов
    python tools/backup.py --dry-run      # Пробный запуск без изменений
    python tools/backup.py --list         # Список бэкапов
        """
    )

    parser.add_argument(
        '--keep',
        type=int,
        default=30,
        help='Количество дней для хранения бэкапов (по умолчанию: 30)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Пробный запуск без создания бэкапа'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='Показать список существующих бэкапов'
    )

    args = parser.parse_args()

    # Инициализация менеджера бэкапов
    backup_manager = BackupManager(keep_days=args.keep, dry_run=args.dry_run)

    if args.list:
        backup_manager.list_backups()
        return 0

    # Валидация данных
    if not backup_manager.validate_data():
        print('\nОшибка: Не все данные найдены. Проверьте структуру проекта.', file=sys.stderr)
        return 1

    # Создание бэкапа
    success = backup_manager.create_backup()

    if success:
        print(f'\nБэкап успешно создан: {args.keep} бэкапов будут сохранены.')
        return 0
    else:
        print('\nОшибка при создании бэкапа.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
