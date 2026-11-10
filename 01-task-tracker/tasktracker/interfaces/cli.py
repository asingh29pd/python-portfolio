from datetime import date, datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from tasktracker.bootstrap import build_service
from tasktracker.domain.task import Priority
from tasktracker.services.task_service import TaskNotFoundError

app = typer.Typer(
    help="Task Tracker: manage your tasks from the terminal.", add_completion=False
)
console = Console()

PRIORITY_STYLE = {
    Priority.HIGH: "bold red",
    Priority.MEDIUM: "yellow",
    Priority.LOW: "green",
}


def fail(message: str) -> None:
    console.print(f"[bold red]✗[/bold red] {message}")
    raise typer.Exit(code=1)


@app.command()
def add(
    title: str = typer.Argument(..., help="Task title"),
    priority: Priority = typer.Option(
        Priority.MEDIUM, "--priority", "-p", help="low, medium or high"
    ),
    due: Optional[datetime] = typer.Option(
        None, "--due", "-d", formats=["%Y-%m-%d"], help="Due date (YYYY-MM-DD)"
    ),
):
    """Add a new task."""
    try:
        task = build_service().add_task(title, priority, due.date() if due else None)
    except ValueError as error:
        fail(str(error))
    console.print(f"[bold green]✓[/bold green] Added task #{task.id}: {task.title}")


@app.command("list")
def list_tasks(
    show_all: bool = typer.Option(False, "--all", "-a", help="Include completed tasks"),
):
    """Show your tasks in a table."""
    tasks = build_service().list_tasks(include_done=show_all)
    if not tasks:
        console.print(
            '[dim]No tasks yet. Add one with:[/dim] python main.py add "My first task"'
        )
        return

    table = Table(title="Your Tasks", header_style="bold cyan", border_style="dim")
    table.add_column("ID", justify="right")
    table.add_column("Title")
    table.add_column("Priority")
    table.add_column("Due")
    table.add_column("Status")

    for task in tasks:
        overdue = bool(task.due_date and task.due_date < date.today() and not task.done)
        due_text = task.due_date.isoformat() if task.due_date else "-"
        if overdue:
            due_text = f"[bold red]{due_text} (overdue)[/bold red]"
        status = "[green]✓ Done[/green]" if task.done else "[yellow]○ Pending[/yellow]"
        title = f"[strike dim]{task.title}[/strike dim]" if task.done else task.title
        table.add_row(
            str(task.id),
            title,
            f"[{PRIORITY_STYLE[task.priority]}]{task.priority.value}[/]",
            due_text,
            status,
        )

    console.print(table)


@app.command()
def done(task_id: int = typer.Argument(..., help="ID of the task")):
    """Mark a task as done."""
    try:
        build_service().complete_task(task_id)
    except TaskNotFoundError as error:
        fail(str(error))
    console.print(f"[bold green]✓[/bold green] Task #{task_id} marked as done.")


@app.command()
def delete(task_id: int = typer.Argument(..., help="ID of the task")):
    """Delete a task."""
    try:
        build_service().delete_task(task_id)
    except TaskNotFoundError as error:
        fail(str(error))
    console.print(f"[bold green]✓[/bold green] Task #{task_id} deleted.")
