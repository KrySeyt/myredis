from typing import Any

from myredis.adapters.views.serializers import array_, bulk_str, int_, none, str_
from myredis.adapters.views.serializers import record as record_serializer
from myredis.adapters.views.serializers import records as records_serializer
from myredis.domain.record import Record


def ok() -> bytes:
    return b"+OK\r\n"


def get(record: Record[Any] | None) -> bytes:
    if not record:
        return not_found()

    value = record.value

    if isinstance(value, str):
        return str_(value)

    if isinstance(value, int):
        return int_(value)

    if value is None:
        return not_found()

    raise ValueError(record, f"value: {value}")


def not_found() -> bytes:
    return none()


def pong() -> bytes:
    return str_("PONG")


def echo(value: str) -> bytes:
    return bulk_str(value)


def config_param(key: str, value: str | None) -> bytes:
    if value is None:
        serialized_value = not_found()

    elif isinstance(value, str):
        serialized_value = bulk_str(value)

    else:
        raise ValueError(value)

    return array_(bulk_str(key), serialized_value)


def wait(replicas_count: int) -> bytes:
    return int_(replicas_count)


def ack() -> bytes:
    return array_(bulk_str("REPLCONF"), bulk_str("ACK"))


def records(data: dict[str, Record[Any]]) -> bytes:
    serialized_records = []
    for key, record in data.items():
        serialized_records.append(record_serializer(key, record))

    return records_serializer(*serialized_records)
