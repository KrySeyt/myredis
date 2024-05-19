from myasync import Coroutine

from myredis.application.ack import Ack


def ack() -> Coroutine[bytes]:
    first, second = yield from Ack()()
    return f"*2\r\n${len(first)}\r\n{first}\r\n${len(second)}\r\n{second}\r\n".encode()
