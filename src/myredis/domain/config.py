from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    MASTER = "master"
    SLAVE = "slave"


@dataclass
class Config:
    role: Role
