# Task Tracker

A task manager with **two interfaces** (a colourful command-line app and a desktop GUI) and **two interchangeable storage backends** (JSON and SQLite), built with clean architecture and covered by automated tests.

## Screenshots

**Command line (typer + rich)**

![CLI](docs/cli.png)

**Desktop GUI (Tkinter)**

![GUI](docs/gui.png)

## Features

- Add tasks with a title, priority (low / medium / high) and optional due date
- Colour-coded task list with overdue highlighting
- Mark tasks as done or delete them
- Data saved automatically after every action
- Switch storage between JSON and SQLite with one config setting
- Input validation (empty titles and past due dates are rejected)

## Tech stack

Python 3.10+, SQLite (`sqlite3`), JSON, Tkinter, typer, rich, pytest, ruff

## Getting started

```powershell
git clone https://github.com/YOUR-USERNAME/python-portfolio.git
cd python-portfolio
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
cd 01-task-tracker
```

### Command line

```powershell
python main.py --help
python main.py add "Prepare client report" -p high -d 2026-11-30
python main.py list
python main.py done 1
python main.py list --all
python main.py delete 1
```

### Desktop GUI

```powershell
python main_gui.py
```

### Switching storage

In `tasktracker/config.py`:

```python
STORAGE_BACKEND = "json"    # or "sqlite"
```

## Architecture

```
interfaces/ (CLI, GUI)  ->  services/  ->  repositories/ (JSON, SQLite)  ->  storage
 what the user sees        business rules      all data access
                  domain/ (Task, Priority) is shared by every layer
```

```
01-task-tracker/
├── tasktracker/
│   ├── domain/          # Task and Priority definitions
│   ├── services/        # Business rules (validation, completing, deleting)
│   ├── repositories/    # SQLite and JSON storage behind one interface
│   ├── interfaces/      # CLI (typer/rich) and GUI (Tkinter)
│   ├── bootstrap.py     # Chooses the storage backend
│   └── config.py        # Settings
├── tests/               # pytest suite
├── main.py              # CLI entry point
└── main_gui.py          # GUI entry point
```

### Design decisions

- **Separation of concerns:** each layer has one job, and layers only talk downward.
- **Dependency injection:** the service receives its repository, so storage can be swapped or faked in tests.
- **Replaceable interfaces:** the CLI and GUI share the same service layer, so neither contains business logic.
- **Safe SQL:** all queries are parameterised to prevent SQL injection.
- **Safe JSON writes:** data is written to a temporary file and then swapped in, so a crash can't corrupt the data file.

## Testing

```powershell
python -m pytest -v
```

30 tests cover validation rules, adding, completing and deleting, ID handling, and persistence. Service tests run against **both** storage backends.

## Possible improvements

- Edit task command
- Search and filter by priority or due date
- Web interface (Flask) as a third interface
- Export tasks to CSV

## Author

Kishan Singh