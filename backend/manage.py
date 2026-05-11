#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def should_skip_migrate() -> bool:
    if len(sys.argv) < 2 or sys.argv[1] != 'migrate':
        return False

    skip_migrations = os.environ.get('SKIP_MIGRATIONS_ON_RENDER', '').lower() in {'1', 'true', 'yes', 'on'}
    running_on_render = bool(
        os.environ.get('RENDER')
        or os.environ.get('RENDER_SERVICE_ID')
        or os.environ.get('RENDER_SERVICE_NAME')
        or os.environ.get('RENDER_EXTERNAL_URL')
    )

    return skip_migrations or running_on_render


def main():
    """Run administrative tasks."""
    if should_skip_migrate():
        print('Skipping migrations during Render startup.')
        return

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'document_tracker.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
