import logging
from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

logger = logging.getLogger(__name__)

ViewT = TypeVar("ViewT")


class WrongCommand(Generic[ViewT]):
    def __init__(self, view: Callable[[], ViewT]) -> None:
        self._view = view

    def __call__(self, command: list[str]) -> Coroutine[ViewT]:
        yield None

        logger.error(f"Unknown command - {command}")
        return self._view()
