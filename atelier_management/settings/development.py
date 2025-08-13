from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*'] # Allows access from any host during dev

# Database (using django-environ to parse DATABASE_URL from docker-compose)
import environ
env = environ.Env()
environ.Env.read_env() # reads .env file
DATABASES = {
    'default': env.db('DATABASE_URL')
}

# Django Debug Toolbar
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    "127.0.0.1",
]
