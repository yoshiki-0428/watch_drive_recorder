import time
from loguru import logger


def time_elapsed(func):
    """関数の実行時間を計測し、ログに出力するデコレータ"""

    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # より高精度な時間計測
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        logger.info(f"{func.__name__} took {elapsed_time:.4f} seconds to complete.")
        return result

    return wrapper
