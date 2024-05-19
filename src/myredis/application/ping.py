from myasync import Coroutine


class Ping:
    def __call__(self) -> Coroutine[None]:
        yield None
