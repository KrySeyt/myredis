from typing import Any

from myredis.application.gateways.values import ValuesStorage


class Echo:
    def __call__(self, value: str) -> str:
        return value
