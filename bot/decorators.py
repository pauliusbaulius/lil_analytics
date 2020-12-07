from functools import wraps
from timeit import default_timer


def timer(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        bef = default_timer()
        ret = function(*args, **kwargs)
        aft = default_timer()
        # logger.info('{:s} took {:0.6f}ms'.format(function.__name__, ((aft - bef) * 1000), args, kwargs))
        return ret

    return wrapper
