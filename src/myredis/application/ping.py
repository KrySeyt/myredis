
from myasync import Coroutine


class Ping:
    def __call__(self) -> Coroutine[str]:
        yield None
        return "PONG"
