"""
controllers/task_controller.py
Layer bisnis: menjembatani UI dan DatabaseManager.
"""

from database.db_manager import DatabaseManager


class TaskController:
    """Mengatur alur data antara UI (MainWindow) dan Database."""

    PRIORITIES  = ["High", "Medium", "Low"]
    STATUSES    = ["Todo", "In Progress", "Done"]
    CATEGORIES  = ["General", "Work", "Personal", "Study", "Health", "Finance", "Other"]

    def __init__(self):
        self.db = DatabaseManager()

    # ── CRUD ────────────────────────────────────────────────────
    def add(self, data: dict) -> int:
        self._validate(data)
        return self.db.create_task(data)

    def edit(self, task_id: int, data: dict):
        self._validate(data)
        self.db.update_task(task_id, data)

    def delete(self, task_id: int):
        self.db.delete_task(task_id)

    def delete_done_tasks(self):
        self.db.delete_all_done()

    # ── Query ────────────────────────────────────────────────────
    def get_all(self) -> list[dict]:
        return self.db.get_all_tasks()

    def search(self, keyword: str = "", status: str = "", priority: str = "", category: str = "") -> list[dict]:
        return self.db.search_tasks(keyword, status, priority, category)

    def get_stats(self) -> dict:
        return self.db.get_stats()

    def get_dynamic_categories(self) -> list[str]:
        """Gabungkan kategori default + dari DB (tanpa duplikat)."""
        db_cats = self.db.get_categories()
        merged = list(dict.fromkeys(self.CATEGORIES + db_cats))
        return merged

    # ── Validasi ─────────────────────────────────────────────────
    @staticmethod
    def _validate(data: dict):
        if not data.get("title", "").strip():
            raise ValueError("Judul task tidak boleh kosong.")
        if data.get("priority") not in TaskController.PRIORITIES:
            raise ValueError("Prioritas tidak valid.")
        if data.get("status") not in TaskController.STATUSES:
            raise ValueError("Status tidak valid.")
