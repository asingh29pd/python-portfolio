from datetime import date, timedelta

import pytest

from tasktracker.domain.task import Priority
from tasktracker.services.task_service import TaskNotFoundError

TODAY = date.today()
TOMORROW = TODAY + timedelta(days=1)
YESTERDAY = TODAY - timedelta(days=1)


# ---------- adding ----------
def test_add_task_assigns_id_and_stores_values(service):
    task = service.add_task("Write report", Priority.HIGH, TOMORROW)

    assert task.id is not None
    assert task.title == "Write report"
    assert task.priority == Priority.HIGH
    assert task.due_date == TOMORROW
    assert task.done is False


def test_add_task_strips_whitespace_from_title(service):
    task = service.add_task("  Review logs  ", Priority.LOW, None)

    assert task.title == "Review logs"


@pytest.mark.parametrize("bad_title", ["", "   "])
def test_add_task_rejects_empty_title(service, bad_title):
    with pytest.raises(ValueError, match="empty"):
        service.add_task(bad_title, Priority.MEDIUM, None)


def test_add_task_rejects_past_due_date(service):
    with pytest.raises(ValueError, match="past"):
        service.add_task("Old task", Priority.MEDIUM, YESTERDAY)


def test_add_task_allows_due_date_today(service):
    task = service.add_task("Due today", Priority.MEDIUM, TODAY)

    assert task.due_date == TODAY


def test_ids_are_not_reused_after_delete(service):
    service.add_task("One", Priority.LOW, None)
    second = service.add_task("Two", Priority.LOW, None)
    service.delete_task(second.id)

    third = service.add_task("Three", Priority.LOW, None)

    assert third.id == second.id + 1


# ---------- listing ----------
def test_list_hides_completed_tasks_by_default(service):
    first = service.add_task("A", Priority.LOW, None)
    service.add_task("B", Priority.LOW, None)
    service.complete_task(first.id)

    titles = [task.title for task in service.list_tasks()]

    assert titles == ["B"]


def test_list_with_include_done_puts_completed_last(service):
    first = service.add_task("A", Priority.LOW, None)
    service.add_task("B", Priority.LOW, None)
    service.complete_task(first.id)

    titles = [task.title for task in service.list_tasks(include_done=True)]

    assert titles == ["B", "A"]


# ---------- completing ----------
def test_complete_task_marks_it_done(service):
    task = service.add_task("Finish me", Priority.MEDIUM, None)

    service.complete_task(task.id)

    all_tasks = service.list_tasks(include_done=True)
    assert all_tasks[0].done is True


def test_complete_unknown_task_raises(service):
    with pytest.raises(TaskNotFoundError):
        service.complete_task(999)


# ---------- deleting ----------
def test_delete_task_removes_it(service):
    task = service.add_task("Remove me", Priority.MEDIUM, None)

    service.delete_task(task.id)

    assert service.list_tasks(include_done=True) == []


def test_delete_unknown_task_raises(service):
    with pytest.raises(TaskNotFoundError):
        service.delete_task(999)
