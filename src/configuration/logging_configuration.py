import logging
import logging.config
import os
import sys


def setup_logging(env: str = "development", app_root = ""):

    print(app_root)

    is_production = env.lower() == "production"
    os.makedirs(f"{app_root}/logs/",exist_ok = True)
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "human_readable": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "line": %(lineno)d, "message": "%(message)s"}',
                "datefmt": "%Y-%m-%dT%H:%M:%SZ",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "json" if is_production else "human_readable",
                "level": "INFO" if is_production else "DEBUG",
            },
            "file_debug":{
                "class" : "logging.handlers.RotatingFileHandler",
                "filename" : f"{app_root}/logs/app_debug.log",
                "maxBytes" : 5_000_000,
                "backupCount" : 4,
                "formatter" : "json" if is_production else "human_readable",
                "level" : "DEBUG",
                "encoding" : "utf-8"
            }
        },
        ""
        "loggers": {
            "": {
                "handlers": ["console","file_debug"],
                "level": "INFO" if is_production else "DEBUG",
                "propagate": True,
            },
            "urllib3": {
                "level": "WARNING",
            },
            "aiosqlite": {
                "level": "WARNING",
            },
            "asyncio": {
              "level": "WARNING",
            },
            "docker":{
                "level" : "WARNING"
            },
            "PIL":{
                "level" : "WARNING"
            }
        },
    }

    logging.config.dictConfig(logging_config)