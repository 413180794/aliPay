import os

basedir = os.path.abspath(os.path.dirname(__file__))  #


class Profile:
    SECRET_KEY = "1996/06/18"
    LOG_FILE_URL = os.path.join(basedir, "static", "log")
    INFO_LOG_URL = os.path.join(LOG_FILE_URL, "info.log")
    ERROR_LOG_URL = os.path.join(LOG_FILE_URL, "errors.log")
    UI_QSS_URL = os.path.join(basedir,"static", "style", "ui.qss")
    CONFIG_INI_URL = os.path.join(basedir,"static","config","config.ini")
    ENCODING = "utf-8"
    DECODING = ENCODING

    LOGGING_SETTING = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            },
            "info_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filename": INFO_LOG_URL,
                "maxBytes": 10485760,
                "backupCount": 20,
                "encoding": "utf8"
            },
            "error_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "simple",
                "filename": ERROR_LOG_URL,
                "maxBytes": 10485760,
                "backupCount": 20,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "my_module": {
                "level": "ERROR",
                "handlers": [
                    "info_file_handler"
                ],
                "propagate": "no"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": [
                "console",
                "info_file_handler",
                "error_file_handler"
            ]
        }
    }


profile = Profile
