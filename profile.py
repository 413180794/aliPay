import os

basedir = os.path.abspath(os.path.dirname(__file__))  #


class Profile:
    SECRET_KEY = "1996/06/18"
    LOG_FILE_URL = os.path.join(basedir, "static", "log")
    INFO_LOG_URL = os.path.join(LOG_FILE_URL, "info.log")
    ERROR_LOG_URL = os.path.join(LOG_FILE_URL, "errors.log")
    UI_QSS_URL = os.path.join(basedir, "static", "style", "ui.qss")
    CONFIG_INI_URL = os.path.join(basedir, "static", "config", "config.ini")
    WEB_DRIVER_PATH = os.path.join(basedir, "static", "webDriver", "chromedriver")
    ALI_LOGIN_PATH = "https://auth.alipay.com/login/index.htm?goto=https%3A%2F%2Fwww.alipay.com%2F"
    ENCODING = "utf-8"
    DECODING = ENCODING
    BAND_CODE_ID = {
        'ABCabc101_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-abc101-3",
        'ABCabcnucc104_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2b_ebank-abcnucc104-31",
        'BJBANKbjbanknucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-bjbanknucc103-19",
        'BJRCBbjrcbnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-bjrcbnucc103-20",
        'BOCboc102_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-boc102-7",
        'BOCbocnucc104_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2b_ebank-bocnucc104-33",
        'CCBccb103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-ccb103-2",
        'CCBccb104_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2b_ebank-ccb104-30",
        'CDCBcdcbnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-cdcbnucc103-23",
        'CEBcebnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-cebnucc103-8",
        'CIBcib102_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-cib102-12",
        'CITICciticnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-citicnucc103-9",
        'CMBCcmbcnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-cmbcnucc103-11",
        'CMBcmb103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-cmb103-6",
        'CMBcmbnucc104_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2b_ebank-cmbnucc104-32",
        'COMMcommnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-commnucc103-5",
        'CSRCBcsrcbnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-csrcbnucc103-24",
        'FDBfdbnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-fdbnucc103-21",
        'GDBgdbnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-gdbnucc103-14",
        'GDBgdbnucc104_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2b_ebank-gdbnucc104-35",
        'HXBANKhxbanknucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-hxbanknucc103-25",
        'HZCBhzcbnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-hzcbnucc103-18",
        'ICBCicbc105_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-icbc105-1",
        'ICBCicbcnucc104_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2b_ebank-icbcnucc104-29",
        'NBBANKnbbanknucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-nbbanknucc103-17",
        'NJCBnjcbnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-njcbnucc103-26",
        'PSBCpsbcnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-psbcnucc103-4",
        'SHBANKshbanknucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-shbanknucc103-16",
        'SHRCBshrcbnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-shrcbnucc103-15",
        'SPABANKspabanknucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-spabanknucc103-13",
        'SPDBspdbnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-spdbnucc103-10",
        'SPDBspdbnucc104_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2b_ebank-spdbnucc104-34",
        'WJRCBwjrcbnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-wjrcbnucc103-27",
        'WZCBwzcbnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-wzcbnucc103-22",
        'ZJNXzjnxnucc103_DEPOSIT_DEBIT_EBANK_XBOX_MODEL': "J-b2c_ebank-zjnxnucc103-28"
    }
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
