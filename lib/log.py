import time
from contextlib import contextmanager


@contextmanager
def time_log(msg: str) -> None:
    """with構文で使うことにより、処理時間を print 出力するための関数
    例：
    with time_log(l"処理A"):
        proc_A()

    とすると、proc_A()の処理時間をprint出力する。
    """
    print(f"{msg}:start")
    st_tm: float = time.time()
    yield
    ed_tm: float = time.time()
    print(f"{msg}:end:process time {ed_tm-st_tm:.3f} [sec]")
