import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from tasktracker.domain.task import Priority, Task


class TaskRepository:
    """The only class that talks to the database."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._create_table()

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _create_table(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    due_date TEXT,
                    done INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    @staticmethod
    def _to_task(row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            priority=Priority(row["priority"]),
            due_date=date.fromisoformat(row["due_date"]) if row["due_date"] else None,
            done=bool(row["done"]),
        )

    def add(self, task: Task) -> Task:
        with self._connection() as conn:
            cursor = conn.execute(
                "INSERT INTO tasks (title, priority, due_date, done) VALUES (?, ?, ?, ?)",
                (
                    task.title,
                    task.priority.value,
                    task.due_date.isoformat() if task.due_date else None,
                    int(task.done),
                ),
            )
            task.id = cursor.lastrowid
        return task

    def list_all(self) -> list[Task]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY done ASC, id ASC"
            ).fetchall()
        return [self._to_task(row) for row in rows]

    def mark_done(self, task_id: int) -> bool:
        with self._connection() as conn:
            cursor = conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

    def delete(self, task_id: int) -> bool:
        with self._connection() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0
