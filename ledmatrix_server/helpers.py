from datetime import datetime

from ledmatrix_server.common import log

# -------------------------
# Classes
# -------------------------

class TooManyFailsError(Exception):
    pass

# -------------------------
# Decorators
# -------------------------

FAILS = dict()

def handle_fail(critical_fails=50):
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_id = str(id(func))
            if func_id not in FAILS:
                FAILS[func_id] = 0
            
            ret = None
            try:
                ret = func(*args, **kwargs)
            except Exception:
                FAILS[func_id] += 1
                log.debug(f"Failed {FAILS[func_id]} time(s)")
            else:
                FAILS[func_id] = 0
            finally:
                if FAILS[func_id] >= critical_fails:
                    log.critical(f"Too many fails for {func_id}. Crashing.")
                    raise TooManyFailsError(f"Too mainy fails for {func_id}")
            
            return ret
        return wrapper
    return decorator


# -------------------------
# Functions
# -------------------------


def is_christmas():
    if datetime.now().month == 12:
        return True
    else:
        return False
    
