from tasktracker import config
from tasktracker.repositories.json_task_repository import JsonTaskRepository
from tasktracker.repositories.task_repository import TaskRepository
from tasktracker.services.task_service import TaskService


def build_service() -> TaskService:
    if config.STORAGE_BACKEND == "sqlite":
        repository = TaskRepository(config.DB_PATH)
    else:
        repository = JsonTaskRepository(config.JSON_PATH)
    return TaskService(repository)
