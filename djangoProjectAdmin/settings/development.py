# djangoProjectAdmin/settings/development.py

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allow all hosts during development
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# HTTPS settings
# All set to False for development
# All set to True for development
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Development-specific database settings (optional)
# For example, using SQLite for development
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Additional development-specific settings can be added here
