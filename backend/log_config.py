﻿import logging
import uvicorn

class ColorFormatter(logging.Formatter):
    COLOR_MAP = {
        "DEBUG": "\033[0;36m",     # ciano
        "INFO": "\033[0;32m",      # verde
        "WARNING": "\033[0;33m",   # amarelo
        "ERROR": "\033[0;31m",     # vermelho
        "CRITICAL": "\033[1;41m",  # fundo vermelho
    }

    RESET = "\033[0m"

    def format(self, record):
        color = self.COLOR_MAP.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": ColorFormatter,
            "format": "[%(levelname)s] - %(name)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "colored",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"],
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
