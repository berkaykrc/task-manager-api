from .base import *

DEBUG = True
CELERY_TASK_ALWAYS_EAGER = True
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "taskmanager",  # docker dev
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

TESTING = "test" in sys.argv

INTERNAL_IPS = ["localhost", "127.0.0.1"]

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

TEMPLATES += [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
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

WSGI_APPLICATION = "taskmanager.wsgi.application"

LOGGING["handlers"]["console"]["formatter"] = "verbose"
LOGGING["loggers"]["django"]["level"] = "INFO"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
    },
}
