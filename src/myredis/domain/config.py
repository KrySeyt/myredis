from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    MASTER = "master"
    SLAVE = "slave"


@dataclass
class AppConfig:
    role: Role
