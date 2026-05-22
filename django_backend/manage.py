#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
from urllib.parse import urlparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from shared.config import settings

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    if len(sys.argv) == 1 or sys.argv[1] == 'runserver':
        django_url = settings.DJANGO_BACKEND_URL
        parsed_url = urlparse(django_url)
        port = parsed_url.port or 8000
        host = parsed_url.hostname or '127.0.0.1'
        sys.argv = ['manage.py', 'runserver', f'{host}:{port}']
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
