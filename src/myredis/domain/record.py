from dataclasses import dataclass


@dataclass
class Record:
    """
    :param expires: expire time in seconds
    """

    value: object
    expires: float | None = None
