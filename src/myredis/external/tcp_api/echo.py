from myasync import Coroutine

from myredis.application.echo import Echo


def echo(input_str: str) -> Coroutine[bytes]:
    interactor = Echo()
    value = yield from interactor(input_str)
    return f"${len(value)}\r\n{value}\r\n".encode()
