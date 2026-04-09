"""
WSGI config for document_tracker project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'document_tracker.settings')

application = get_wsgi_application()
