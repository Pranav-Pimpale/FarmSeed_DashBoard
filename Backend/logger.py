from functools import wraps
from datetime import datetime
import json
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requests.log")

def log_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            with open(LOG_FILE, "a") as f:
                f.write(f"{datetime.now().isoformat()} - {func.__name__}\n")
        except Exception:
            pass
        return func(*args, **kwargs)
    return wrapper

# optional decorator to log returned data size (used earlier in examples)
def log_data(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        try:
            with open(LOG_FILE, "a") as f:
                f.write(f"{datetime.now().isoformat()} - {func.__name__} returned\n")
        except Exception:
            pass
        return result
    return wrapper

