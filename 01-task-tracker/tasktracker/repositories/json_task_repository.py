import json
from datetime import date
from pathlib import Path

from tasktracker.domain.task import Priority, Task


class JsonTaskRepository:
    """Stores tasks in a local JSON file and updates it after every action."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        if not self.file_path.exists():
            self._save({"next_id": 1, "tasks": []})

    # ---------- file handling ----------
    def _load(self) -> dict:
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                f"{self.file_path.name} is corrupted. Fix it or delete it to start fresh."
            ) from error

    def _save(self, data: dict) -> None:
        # Write to a temp file first, then swap it in, so a crash can't corrupt your data.
        temp_path = self.file_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
        temp_path.replace(self.file_path)

    # ---------- conversion ----------
    @staticmethod
    def _to_record(task: Task) -> dict:
        return {
            "id": task.id,
            "title": task.title,
            "priority": task.priority.value,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "done": task.done,
        }

    @staticmethod
    def _to_task(record: dict) -> Task:
        return Task(
            id=record["id"],
            title=record["title"],
            priority=Priority(record["priority"]),
            due_date=date.fromisoformat(record["due_date"])
            if record["due_date"]
            else None,
            done=record["done"],
        )

    # ---------- repository methods ----------
    def add(self, task: Task) -> Task:
        data = self._load()
        task.id = data["next_id"]
        data["next_id"] += 1
        data["tasks"].append(self._to_record(task))
        self._save(data)
        return task

    def list_all(self) -> list[Task]:
        tasks = [self._to_task(record) for record in self._load()["tasks"]]
        return sorted(tasks, key=lambda task: (task.done, task.id))

    def mark_done(self, task_id: int) -> bool:
        data = self._load()
        for record in data["tasks"]:
            if record["id"] == task_id:
                record["done"] = True
                self._save(data)
                return True
        return False

    def delete(self, task_id: int) -> bool:
        data = self._load()
        remaining = [record for record in data["tasks"] if record["id"] != task_id]
        if len(remaining) == len(data["tasks"]):
            return False
        data["tasks"] = remaining
        self._save(data)
        return True
