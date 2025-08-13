"""
WSGI config for atelier_management project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

# In atelier_management/atelier_management/wsgi.py and asgi.py
import os
from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atelier_management.settings.development') # Changed this line
application = get_wsgi_application()
