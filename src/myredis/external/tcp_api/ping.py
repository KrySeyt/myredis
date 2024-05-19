from myasync import Coroutine

from myredis.application.ping import Ping


def ping() -> Coroutine[bytes]:
    interactor = Ping()
    value = yield from interactor()
    return f"+{value}\r\n".encode()
