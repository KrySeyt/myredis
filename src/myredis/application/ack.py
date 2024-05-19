from myasync import Coroutine


class Ack:
    def __call__(self) -> Coroutine[tuple[str, str]]:
        yield None
        return "REPLCONF", "ACK"
