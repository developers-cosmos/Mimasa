#!/usr/bin/env python3
"""
Logger Class
------------------------------------------------
Example Usage:

log = Logger('MyLogger')

# Log messages at different levels
log.debug('This is a debug message.')
log.info('This is an info message.')
log.warning('This is a warning message.')
log.error('This is an error message.')
log.critical('This is a critical message.')

# Add a file handler to log messages to a file
log.add_file_handler('logs.txt', level='debug')

# Log an unhandled exception
try:
    1/0
except:
    log.exception('An exception occurred.')

# Disable logging for specific levels
log.disable_level('debug')

# Log messages at different levels after disabling logging for debug
log.debug('This is a debug message.') # will not be logged
log.info('This is an info message.')
log.warning('This is a warning message.')
log.error('This is an error message.')
log.critical('This is a critical message.')

# Enable logging for the debug level
log.enable_level('debug')

# Log messages at different levels after enabling logging for debug
log.debug('This is a debug message.')
log.info('This is an info message.')
log.warning('This is a warning message.')
log.error('This is an error message.')
log.critical('This is a critical message.')
"""

import logging
import sys
import traceback
from logging import handlers

from src.common.config import Config


class Logger:
    LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    # _instance = None
    # _loggers = {}

    # def __new__(cls, *args, **kwargs):
    #     if not cls._instance:
    #         cls._instance = super().__new__(cls, *args, **kwargs)
    #     return cls._instance

    def __init__(self, name, handlers=None, level=Config.LOG_LEVEL, formatter=None, disabled_levels=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.NOTSET)
        self.log_file_base = f"{Config.LOGS_FOLDER_PATH}"
        self.disabled_levels = disabled_levels or []
        if formatter is None:
            formatter = logging.Formatter(
                "[%(asctime)s] [PID: %(process)-7d][TID: %(thread)-7d] [%(levelname)-8s] [%(name)-12s] %(message)s",
                "%d-%m-%Y %H:%M:%S",
            )
        if handlers is None:
            handlers = [logging.StreamHandler()]
        for handler in handlers:
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.set_level(level)

    def add_file_handler(self, filename, level="debug", max_bytes=10485760, backup_count=5, formatter=None):
        if formatter is None:
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)-8s] [%(name)-12s] %(message)s", "%d-%m-%Y %H:%M:%S"
            )

        filename = f"{self.log_file_base}/{filename}"
        handler = handlers.RotatingFileHandler(filename, maxBytes=max_bytes, backupCount=backup_count)
        handler.setLevel(self.LEVELS.get(level.lower(), logging.NOTSET))
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log(self, message, level="debug", exc_info=False):
        level = self.LEVELS.get(level.lower(), logging.NOTSET)
        if level not in self.disabled_levels:
            self.logger.log(level, message, exc_info=exc_info)

    def debug(self, message, exc_info=False):
        self.log(message, "debug", exc_info)

    def info(self, message, exc_info=False):
        self.log(message, "info", exc_info)

    def warning(self, message, exc_info=False):
        self.log(message, "warning", exc_info)

    def error(self, message, exc_info=False):
        self.log(message, "error", exc_info)

    def critical(self, message, exc_info=False):
        self.log(message, "critical", exc_info)

    def exception(self, message=None):
        message = message or "Unhandled Exception"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_str = "".join(tb_list)
        self.log(f"{message}\n{tb_str}", "error", exc_info=True)

    def set_level(self, level):
        self.logger.setLevel(self.LEVELS.get(level.lower(), logging.NOTSET))

    def disable_level(self, level):
        self.disabled_levels.append(self.LEVELS.get(level.lower(), logging.NOTSET))

    def enable_level(self, level):
        level = self.LEVELS.get(level.lower(), logging.NOTSET)
        if level in self.disabled_levels:
            self.disabled_levels.remove(level)
