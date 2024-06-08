from dataclasses import dataclass
from datetime import datetime

@dataclass
class Observation:
    id: int
    time: datetime
    value: float

@dataclass
class Sensor:
    id: int
    name: str
    description: str
    model: str
    unit: str
    unit_pretty: str
    depth: float
    observations: list[Observation]

@dataclass
class Device:
    id: int
    name: str
    description: str
    latitude: float
    longtitude: float
    sensors: list[Sensor]
