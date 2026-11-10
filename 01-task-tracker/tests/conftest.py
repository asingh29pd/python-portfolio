import pytest

from tasktracker.repositories.json_task_repository import JsonTaskRepository
from tasktracker.repositories.task_repository import TaskRepository
from tasktracker.services.task_service import TaskService


@pytest.fixture(params=["sqlite", "json"])
def repository(request, tmp_path):
    """Runs every test that uses it twice: once per storage backend."""
    if request.param == "sqlite":
        return TaskRepository(tmp_path / "test.db")
    return JsonTaskRepository(tmp_path / "test.json")


@pytest.fixture
def service(repository):
    return TaskService(repository)
