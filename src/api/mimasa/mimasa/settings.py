"""Django settings for mimasa project."""

import os
from pathlib import Path
from urllib.parse import unquote, urlparse


BASE_DIR = Path(__file__).resolve().parent.parent


def env(name: str, default=None):
    """Read an environment variable with an optional fallback."""
    return os.getenv(name, default)


def env_bool(name: str, default: bool = False) -> bool:
    """Read a boolean environment variable."""
    raw_value = env(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    """Read a comma-separated environment variable as a list."""
    raw_value = env(name, default) or ""
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def env_int(name: str, default: int) -> int:
    """Read an integer environment variable with a fallback."""
    raw_value = env(name)
    if raw_value is None:
        return default
    return int(raw_value)


def parse_database_url(database_url: str) -> dict:
    """Parse a DATABASE_URL value into a Django DATABASES dictionary."""
    parsed = urlparse(database_url)

    if parsed.scheme in {"postgres", "postgresql", "pgsql"}:
        engine = "django.db.backends.postgresql"
    elif parsed.scheme in {"mysql", "mysql2"}:
        engine = "django.db.backends.mysql"
    elif parsed.scheme in {"sqlite", "sqlite3"}:
        db_path = unquote(parsed.path or "")
        if not db_path or db_path == "/":
            db_path = str(BASE_DIR / "db.sqlite3")
        else:
            db_path = db_path[1:] if db_path.startswith("/") else db_path

        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": db_path,
        }
    else:
        raise ValueError("Unsupported DATABASE_URL scheme. Use postgres://, mysql://, or sqlite:///")

    return {
        "ENGINE": engine,
        "NAME": unquote(parsed.path[1:]),
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname or "localhost",
        "PORT": str(parsed.port or ""),
        "CONN_MAX_AGE": env_int("DB_CONN_MAX_AGE", 60),
    }


DEBUG = env_bool("MIMASA_DEBUG", default=False)

# SECURITY WARNING: keep this secret in production.
SECRET_KEY = env("MIMASA_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-local-dev-key"
    else:
        raise RuntimeError("MIMASA_SECRET_KEY must be set when MIMASA_DEBUG is false")

ALLOWED_HOSTS = env_list("MIMASA_ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("MIMASA_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "channels",
    "translation",
    "audio_separation",
    "face_detection",
    "pipeline",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "pipeline.middleware.RequestContextMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mimasa.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "mimasa.wsgi.application"
ASGI_APPLICATION = "mimasa.asgi.application"

DATABASE_URL = env("DATABASE_URL", "sqlite:///db.sqlite3")
DATABASES = {
    "default": parse_database_url(DATABASE_URL),
}

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

LANGUAGE_CODE = "en-us"
TIME_ZONE = env("MIMASA_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Channels: in-memory for local development; Redis for shared production workers.
REDIS_URL = env("REDIS_URL", env("CELERY_BROKER_URL", "redis://localhost:6379/0"))
if DEBUG:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],
            },
        }
    }

# Celery
CELERY_BROKER_URL = env("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Security defaults tuned for production; override with env vars if required.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = env_int("MIMASA_SECURE_HSTS_SECONDS", 31536000 if not DEBUG else 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("MIMASA_SECURE_HSTS_INCLUDE_SUBDOMAINS", not DEBUG)
SECURE_HSTS_PRELOAD = env_bool("MIMASA_SECURE_HSTS_PRELOAD", False)
SECURE_SSL_REDIRECT = env_bool("MIMASA_SECURE_SSL_REDIRECT", not DEBUG)
SESSION_COOKIE_SECURE = env_bool("MIMASA_SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = env_bool("MIMASA_CSRF_COOKIE_SECURE", not DEBUG)
SECURE_CONTENT_TYPE_NOSNIFF = env_bool("MIMASA_SECURE_CONTENT_TYPE_NOSNIFF", True)
X_FRAME_OPTIONS = env("MIMASA_X_FRAME_OPTIONS", "DENY")


# Pipeline alerting thresholds
PIPELINE_ALERT_WINDOW_HOURS = env_int("PIPELINE_ALERT_WINDOW_HOURS", 24)
PIPELINE_ALERT_MAX_JOB_FAILURE_RATE_PCT = float(env("PIPELINE_ALERT_MAX_JOB_FAILURE_RATE_PCT", "10"))
PIPELINE_ALERT_MAX_STAGE_P95_SECONDS = float(env("PIPELINE_ALERT_MAX_STAGE_P95_SECONDS", "120"))
PIPELINE_ALERT_MAX_OPEN_DEAD_LETTERS = env_int("PIPELINE_ALERT_MAX_OPEN_DEAD_LETTERS", 5)
PIPELINE_ALERT_MAX_WEBHOOK_FAILURE_RATE_PCT = float(env("PIPELINE_ALERT_MAX_WEBHOOK_FAILURE_RATE_PCT", "20"))


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structured": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "structured",
        },
    },
    "loggers": {
        "mimasa.telemetry": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
