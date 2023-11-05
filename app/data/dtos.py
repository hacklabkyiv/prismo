from dataclasses import dataclass


@dataclass
class UserDto:
    key: str
    name: str

    def __init__(self, user_key, user_name):
        self.key = user_key
        self.name = user_name


@dataclass
class OperationDto:
    time: int
    type: str

    def __init__(self, operation_time, operation_type):
        self.time = operation_time
        self.type = operation_type
