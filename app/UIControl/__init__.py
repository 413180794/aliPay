import logging.config
from profile import profile
logging.config.dictConfig(profile.LOGGING_SETTING)
logger = logging.getLogger()
