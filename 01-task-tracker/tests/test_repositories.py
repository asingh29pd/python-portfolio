import json

import pytest

from tasktracker.domain.task import Task
from tasktracker.repositories.json_task_repository import JsonTaskRepository
from tasktracker.repositories.task_repository import TaskRepository


def test_sqlite_data_persists_between_instances(tmp_path):
    db_file = tmp_path / "tasks.db"
    TaskRepository(db_file).add(Task(title="Persist me"))

    reloaded = TaskRepository(db_file).list_all()

    assert [task.title for task in reloaded] == ["Persist me"]


def test_json_data_persists_between_instances(tmp_path):
    json_file = tmp_path / "tasks.json"
    JsonTaskRepository(json_file).add(Task(title="Persist me"))

    reloaded = JsonTaskRepository(json_file).list_all()

    assert [task.title for task in reloaded] == ["Persist me"]


def test_json_file_contains_valid_structure(tmp_path):
    json_file = tmp_path / "tasks.json"
    JsonTaskRepository(json_file).add(Task(title="Check file"))

    data = json.loads(json_file.read_text(encoding="utf-8"))

    assert data["next_id"] == 2
    assert data["tasks"][0]["title"] == "Check file"


def test_corrupted_json_raises_clear_error(tmp_path):
    json_file = tmp_path / "tasks.json"
    json_file.write_text("{ this is not valid json", encoding="utf-8")
    repository = JsonTaskRepository(json_file)

    with pytest.raises(RuntimeError, match="corrupted"):
        repository.list_all()
