"""
WSGI config for the legacy documenttracker package path.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'documenttracker.settings')

application = get_wsgi_application()
