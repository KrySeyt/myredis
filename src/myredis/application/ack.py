from myasync import Coroutine


class Ack:
    def __call__(self) -> Coroutine[None]:
        yield None
