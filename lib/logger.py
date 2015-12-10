import logging
import logging.config
import sys

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
            "maxBytes": 2*1024*1024,
            "backupCount": 5,
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
        "handlers": ["debug_file_handler"]
    }
})

def get_default_logger(name):
    """ Unless you have a good reason not to, pass in `__name__` """
    logger = logging.getLogger(name)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logger.setLevel(logging.DEBUG)
    def excepthook(excType, excValue, traceback, logger=logger):
        logger.error("Logging an uncaught exception",
                     exc_info=(excType, excValue, traceback))

    sys.excepthook = excepthook
    return logger
