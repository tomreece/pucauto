import logging
import logging.config

class SeleniumFilter(logging.Filter):
    def filter(self, record):
        selenium_log = 'selenium.webdriver.remote.remote_connection'
        return selenium_log not in record.getMessage()

# much of this taken from http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python
# reference -- https://docs.python.org/2/library/logging.config.html
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "console": {
            "format": "%(message)s"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "console",
            "stream": "ext://sys.stdout"
        },

        "debug_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": "debug.log",
            "maxBytes": 400000,
            "backupCount": 20,
            "encoding": "utf8"
        },

        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "info.log",
            "maxBytes": 100000,
            "backupCount": 20,
            "encoding": "utf8"
        },

        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "simple",
            "filename": "error.log",
            "maxBytes": 50000,
            "backupCount": 20,
            "encoding": "utf8"
        }
    },

    "loggers": {
        "__main__": {
            "level": "INFO",
            "handlers": ["console"]
        }
    },

    "root": {
        "level": "DEBUG",
        "handlers": ["debug_file_handler", "info_file_handler", "error_file_handler"]
    }
})

def get_default_logger(name):
    """ Unless you have a good reason not to, pass in `__name__` """
    logger = logging.getLogger(name)
    logger.addFilter(SeleniumFilter())
    logger.setLevel(logging.DEBUG)
    return logger
