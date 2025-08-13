from .base import *

DEBUG = False

ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com'] # IMPORTANT: Change in production

# Database (using django-environ)
import environ
env = environ.Env()
# In production, env vars are usually set directly in the environment, not from .env file.
# But you might read from an explicit path if needed (e.g., K8s secrets)
DATABASES = {
    'default': env.db('DATABASE_URL')
}

# Configure static and media files for production
# STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Add more production-specific settings:
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True # If using HTTPS
# SECURE_HSTS_SECONDS = 31536000 # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# X_FRAME_OPTIONS = 'DENY' # Protects against clickjacking
