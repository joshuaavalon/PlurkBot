import logging

logger = logging.getLogger(__name__)


class CatchAndLog:
    def __init__(self, rethrow: bool = False, default=None):
        self.rethrow = rethrow  # type:bool
        self.default = default

    def __call__(self, f):
        def decorated(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(e)
                if self.rethrow:
                    raise e
                else:
                    return self.default

        return decorated


def check_type(variable, types, default=None):
    if not isinstance(types, list):
        types = [types]
    for t in types:
        try:
            if isinstance(variable, t):
                return variable
        except TypeError:
            continue
    return default


def try_get(try_dict: dict, key, default=None):
    if not isinstance(try_dict, dict):
        return default
    if key in try_dict:
        return try_dict[key]
    else:
        return default
