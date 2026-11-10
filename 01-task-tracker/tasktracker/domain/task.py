from dataclasses import dataclass
from datetime import date
from enum import Enum


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    title: str
    priority: Priority = Priority.MEDIUM
    due_date: date | None = None
    done: bool = False
    id: int | None = None
