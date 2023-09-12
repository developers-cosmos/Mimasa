#!/usr/bin/env python3
"""
This file contains utility functions that are commonly used throughout the application.
"""
import glob
import logging
import os
import sys
import time
from datetime import datetime

from src.common.libraries import Config, Logger


def get_current_time():
    """Returns the current time as a string"""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def get_filename_from_path(path):
    return os.path.basename(path)


def setup_logger(logger_name: str, log_file: str, log_level: int = logging.WARNING):
    """To setup as many loggers"""
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(funcName)s: %(message)s", "%d-%m-%Y %H:%M:%S")
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.addHandler(handler)

    return logger


def track_performance(func):
    """a decorator that can be applied to any function to track its execution time"""
    logger = Logger(name="PerformanceTracker")
    logger.add_file_handler("performance.log")

    def wrapper(*args, **kwargs):
        import psutil

        # get the process information before the function is called
        process = psutil.Process()
        start_memory = process.memory_info().rss
        cpu_start = process.cpu_percent()

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        # Get the CPU utilization of all cores combined
        cpu_end = process.cpu_percent()
        end_memory = process.memory_info().rss

        execution_time = end_time - start_time
        logger.info(f"Execution time of '{func.__name__}': {execution_time:.2f} seconds")

        memory_usage_str = "Memory usage of '{}': {:.2f} MB".format(
            func.__name__, (end_memory - start_memory) / (1024**2)
        )
        logger.info(memory_usage_str)

        # Calculate the average CPU utilization by dividing by the number of cores
        num_cores = psutil.cpu_count()
        average_cpu_utilization = (cpu_end - cpu_start) / num_cores

        cpu_usage_str = "Average CPU usage of '{}': {:.2f}%".format(func.__name__, average_cpu_utilization)
        logger.info(cpu_usage_str)

        return result

    return wrapper


def setup():
    # create folder for logs storage
    if not os.path.exists(Config.LOGS_FOLDER_PATH):
        os.mkdir(Config.LOGS_FOLDER_PATH)
    else:
        logs = glob.glob(f"{Config.LOGS_FOLDER_PATH}/*")
        for log in logs:
            if os.path.exists(log):
                try:
                    os.remove(log)
                except:
                    pass

    if Config.REDIRECT_STDOUT_TO_FILE:
        global saveout
        saveout = sys.stdout
        fsock2 = open(f"{Config.LOGS_FOLDER_PATH}/stdout.log", "w")
        sys.stdout = fsock2

    if Config.REDIRECT_STDERR_TO_FILE:
        global saveerr
        saveerr = sys.stderr
        fsock1 = open(f"{Config.LOGS_FOLDER_PATH}/stderr.log", "w")
        sys.stderr = fsock1


def teardown():
    if Config.REDIRECT_STDOUT_TO_FILE:
        sys.stdout = saveout

    if Config.REDIRECT_STDERR_TO_FILE:
        sys.stderr = saveerr
