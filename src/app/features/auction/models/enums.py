import enum


class LotStatus(str, enum.Enum):
    running = "running"
    ended = "ended"
