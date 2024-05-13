from myredis.application.gateways.values import ValuesStorage


class Get:
    def __init__(self, values_storage: ValuesStorage) -> None:
        self._values_storage = values_storage

    def __call__(self, key: str) -> object | None:
        return self._values_storage.get(key)
