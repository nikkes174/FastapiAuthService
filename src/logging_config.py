import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "/var/log/app/app.log",
            "formatter": "default",
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file"],
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
