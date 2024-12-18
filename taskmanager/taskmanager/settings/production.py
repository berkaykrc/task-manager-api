import sentry_sdk

from .base import *

DEBUG = False
sentry_sdk.init(
    dsn=env("SENTRY_DSN"),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

ALLOWED_HOSTS = [
    env("SENTRY_DSN"),
]

TESTING = "test" in sys.argv

LOGGING["handlers"].update({
    "file": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": BASE_DIR.parent / "logs" / "app.log",
        "maxBytes": 1024*1024*50,  # 50 MB
        "backupCount": 5,
        "formatter": "verbose",
    },
    "error_file": {
        "class": "logging.FileHandler",
        "filename": BASE_DIR.parent / "logs" / "error.log",
        "formatter": "verbose",
    },
    # Sentry handler for capturing errors
    "sentry": {
        "class": "sentry_sdk.integrations.logging.EventHandler",
        "level": "ERROR",  # Only capture ERROR and above
    },
})
LOGGING["loggers"].update({
    # This ensures logs for all apps in your project are captured
    "django": {
        # Log to file and send errors to Sentry
        "handlers": ["file", "sentry"],
        "level": "WARNING",  # Capture WARNING and above for Django logs
    },
    "django.security": {
        "handlers": ["file", "sentry"],  # Capture security-related errors
        "level": "ERROR",
        "propagate": True,
    },
    "django.db.backends": {
        # You could add "sentry" if you want DB-related logs to go to Sentry too
        "handlers": ["file"],
        "level": "WARNING",
        "propagate": False,
    },
}
)
