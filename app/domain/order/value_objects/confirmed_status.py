from enum import Enum, unique


@unique
class ConfirmedStatus(Enum):
    YES = "YES"
    NO = "NO"
    NOT_PROCESSED = "NOT_PROCESSED"
