# test_settings.py

from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test_db_admin',  # Explicitly specify the test database name
        'USER': 'djangoTestUser',
        'PASSWORD': 'test_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}