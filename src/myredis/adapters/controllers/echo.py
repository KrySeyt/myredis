from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.echo import Echo as EchoInteractor

T_co = TypeVar("T_co", covariant=True)


class Echo(Generic[T_co]):
    def __init__(self, interactor: EchoInteractor, presenter: Callable[[str], T_co]) -> None:
        self._interactor = interactor
        self._presenter = presenter

    def __call__(self, input_str: str) -> Coroutine[T_co]:
        value = yield from self._interactor(input_str)
        return self._presenter(value)
