
from myasync import Coroutine


class Echo:
    def __call__(self, value: str) -> Coroutine[str]:
        yield None
        return value
