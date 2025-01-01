# djangoProjectAdmin/settings/base.py

from pathlib import Path
from datetime import timedelta
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"

# Install pymysql as MySQLdb
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-default-key")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",  # For token blacklisting
    "corsheaders",
    "user.apps.UserConfig",
    "role.apps.RoleConfig",
    "menu.apps.MenuConfig",
    "core.apps.CoreConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "djangoProjectAdmin.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "djangoProjectAdmin.wsgi.application"

# Database
# Default database configuration (can be overridden in specific settings)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "db_admin"),
        "USER": os.getenv("DB_USER", "djangoProjectAdmin"),
        "PASSWORD": os.getenv("DB_PASSWORD", "12345678"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "3306"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", "English"),
    ("zh-hans", "简体中文"),
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# Media files (User uploaded content)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "user.SysUser"

# CORS settings
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# Only set to True if your frontend needs to send cookies or HTTP authentication headers
CORS_ALLOW_CREDENTIALS = True

# REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',  # Use JWTAuthentication
        "user.authentication.CookieJWTAuthentication",
    ),
}

# SIMPLE_JWT configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=50),  # Access token lifetime
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),  # Refresh token lifetime
    "ROTATE_REFRESH_TOKENS": not DEBUG,  # Rotate refresh tokens on refresh
    "BLACKLIST_AFTER_ROTATION": not DEBUG,  # Blacklist old refresh tokens
    "BLACKLIST_ENABLED": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_COOKIE": "accessToken",  # Custom access token cookie name
    "REFRESH_COOKIE": "refreshToken",  # Custom refresh token cookie name
    "AUTH_COOKIE_PATH": "/",  # Cookie path
    "REFRESH_COOKIE_PATH": "/",  # Cookie path
    "AUTH_COOKIE_HTTP_ONLY": True,  # HttpOnly flag for access token
    "REFRESH_COOKIE_HTTP_ONLY": True,  # HttpOnly flag for refresh token
    "AUTH_COOKIE_SECURE": not DEBUG,  # Ensures cookies are only sent over HTTPS (set to True in production)
    "REFRESH_COOKIE_SECURE": not DEBUG,  # Ensures cookies are only sent over HTTPS (set to True in production)
    "AUTH_COOKIE_SAMESITE": "Lax",  # SameSite attribute
    "REFRESH_COOKIE_SAMESITE": "Lax",
}


# Retrieve rate limit settings from environment variables
RATE_LIMIT_LOGIN = os.getenv("RATE_LIMIT_LOGIN", "10/m")
RATE_LIMIT_REFRESH = os.getenv("RATE_LIMIT_REFRESH", "10/m")
RATE_LIMIT_CSRF = os.getenv("RATE_LIMIT_CSRF", "10/m")

# Optionally, group rate limit for better organization
RATE_LIMITS = {
    "LOGIN": RATE_LIMIT_LOGIN,
    "REFRESH": RATE_LIMIT_REFRESH,
    "CSRF": RATE_LIMIT_CSRF,
}


# Logging configuration
# Create log directory if it doesn't exist
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Optional: Define log-related settings for easy configuration
LOG_FILE_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_FILE_BACKUP_COUNT = 10
LOG_FILE_ENCODING = "utf-8"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "core.logging.formatters.JSONFormatter",
        },
    },
    "handlers": {
        "app_file": {
            "()": "core.logging.handlers.TimedRotatingFileHandlerWithPrefix",
            "filename": BASE_DIR / "logs/app.log",
            "formatter": "json",
            "maxBytes": LOG_FILE_MAX_SIZE,  # 10 MB
            "backupCount": LOG_FILE_BACKUP_COUNT,
            "encoding": LOG_FILE_ENCODING,
        },
        "error_file": {
            "()": "core.logging.handlers.TimedRotatingFileHandlerWithPrefix",
            "filename": BASE_DIR / "logs/error.log",
            "formatter": "json",
            "maxBytes": LOG_FILE_MAX_SIZE,  # 10 MB
            "backupCount": LOG_FILE_BACKUP_COUNT,
            "level": "ERROR",
            "encoding": LOG_FILE_ENCODING,
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "loggers": {
        # Root logger - catches all unhandled logs
        "": {
            "handlers": ["app_file", "error_file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        # Django's internal loggers
        "django": {
            "handlers": ["app_file", "error_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["app_file", "error_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        # Application loggers
        "user": {
            "handlers": ["app_file", "error_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "role": {
            "handlers": ["app_file", "error_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "menu": {
            "handlers": ["app_file", "error_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Add RequestLoggingMiddleware to MIDDLEWARE
MIDDLEWARE += [
    "core.logging.middleware.RequestLoggingMiddleware",
]
