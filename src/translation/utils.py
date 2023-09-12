#!/usr/bin/env python3
"""
This file contains utility functions that are commonly used for translation unit.
"""
from src.common.logger import Logger


def get_logger(name="TranslationUnit"):
    if name in Logger._loggers:
        return Logger._loggers[name]
    else:
        logger = Logger(name=name)
        logger.add_file_handler("translation.log")
        Logger._loggers[name] = logger
        return logger
