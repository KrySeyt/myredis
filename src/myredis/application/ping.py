from typing import Any

from myredis.application.gateways.values import ValuesStorage


class Ping:
    def __call__(self) -> str:
        return "PONG"
