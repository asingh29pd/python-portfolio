from datetime import date

from tasktracker.domain.task import Priority, Task
from tasktracker.repositories.base import TaskRepositoryProtocol


class TaskNotFoundError(Exception):
    pass


class TaskService:
    """Business rules live here, not in the CLI or the database code."""

    def __init__(self, repository: TaskRepositoryProtocol):
        self._repo = repository

    def add_task(self, title: str, priority: Priority, due_date: date | None) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty.")
        if due_date and due_date < date.today():
            raise ValueError("Due date cannot be in the past.")
        return self._repo.add(Task(title=title, priority=priority, due_date=due_date))

    def list_tasks(self, include_done: bool = False) -> list[Task]:
        tasks = self._repo.list_all()
        return tasks if include_done else [t for t in tasks if not t.done]

    def complete_task(self, task_id: int) -> None:
        if not self._repo.mark_done(task_id):
            raise TaskNotFoundError(f"Task #{task_id} not found.")

    def delete_task(self, task_id: int) -> None:
        if not self._repo.delete(task_id):
            raise TaskNotFoundError(f"Task #{task_id} not found.")