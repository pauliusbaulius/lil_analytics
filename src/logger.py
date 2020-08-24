import logging
from logging import FileHandler, Formatter
from logging.handlers import TimedRotatingFileHandler

"""
    This module sets up loggers and their formatters, handlers.
    They can then be imported to other modules and be used for logging.
    If you are contributing, please create new loggers here or use existing loggers defined here.
    
    There are 3 loggers to choose:
    
    1. logger_main
        Useful information, no debug messages. See how program behaves in the long run.
    
    2. logger_performance
        Testing function performance with @timer, @resources(#TODO) decorators.
        
    3. logger_critical
        For critical times, like database deadlocks, failed writes, etc. 
        I will make this send notifications, less messages are better.
    
    
    @pauliusbaulius 24.05.2020
"""


def setup_loggers():
    # TODO setup formatting, files, rotation, decorators. Explain which one to use in the green comment above.
    # FIXME how do i log exceptions to error.log I really dont get how any of this works.
    #logging.basicConfig(filename='data/logs/error.log', level=logging.ERROR)

    # General logger for all important logs.
    formatter = logging.Formatter('%(asctime)s:%(module)s:%(funcName)s:%(lineno)d:%(levelname)s:%(message)s')
    handler = TimedRotatingFileHandler(filename="data/logs/info.log", when="midnight", backupCount=0)
    handler.setFormatter(formatter)
    logger = logging.getLogger("bot_main_logger")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Performance logger for timer decorator.
    handler = TimedRotatingFileHandler(filename="data/logs/performance.log", when="midnight", backupCount=0)
    handler.setFormatter(formatter)
    perf_logger = logging.getLogger("bot_performance_logger")
    perf_logger.addHandler(handler)
    perf_logger.setLevel(logging.INFO)