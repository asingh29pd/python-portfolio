from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "tasks.db"
JSON_PATH = BASE_DIR / "tasks.json"

STORAGE_BACKEND = "json"  # change to "sqlite" to switch storage
