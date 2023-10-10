from dataclasses import dataclass


@dataclass
class UserDto:
    key: str
    name: str

    def __init__(self, user_key, user_name):
        self.key = user_key
        self.name = user_name
