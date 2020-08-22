import logging
from functools import wraps
from timeit import default_timer


def timer(function):
    logger = logging.getLogger("bot_performance_logger")

    @wraps(function)
    def wrapper(*args, **kwargs):
        bef = default_timer()
        ret = function(*args, **kwargs)
        aft = default_timer()
        # Version that logs args, kwargs but really bloats up the log file. Used for deeeeep inspection.
        #logger.info('{:s} took {:0.4f}ms:args{}:kwargs{}'.format(function.__name__, ((aft - bef) * 1000), args, kwargs))
        logger.info('{:s} took {:0.6f}ms'.format(function.__name__, ((aft - bef) * 1000), args, kwargs))
        return ret
    return wrapper