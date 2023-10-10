from dataclasses import dataclass


@dataclass
class DeviceDto:
    id: str
    name: str

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
