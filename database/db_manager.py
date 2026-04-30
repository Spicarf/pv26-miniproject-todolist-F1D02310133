"""
database/db_manager.py
Mengelola koneksi dan operasi SQLite untuk Task Manager Pro.
"""

import sqlite3
import os
from datetime import datetime

DB_FILE = "tasks.db"


class DatabaseManager:
    """Mengelola semua interaksi dengan database SQLite."""

    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._init_database()

    # Inisialisasi
    def _init_database(self):
        """Membuat tabel jika belum ada."""
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    title       TEXT    NOT NULL,
                    category    TEXT    NOT NULL DEFAULT 'General',
                    priority    TEXT    NOT NULL DEFAULT 'Medium',
                    status      TEXT    NOT NULL DEFAULT 'Todo',
                    due_date    TEXT    NOT NULL,
                    description TEXT    DEFAULT '',
                    created_at  TEXT    NOT NULL
                )
            """)
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row   # akses kolom by name
        return conn

    # CREATE
    def create_task(self, data: dict) -> int:
        sql = """
            INSERT INTO tasks (title, category, priority, status, due_date, description, created_at)
            VALUES (:title, :category, :priority, :status, :due_date, :description, :created_at)
        """
        data.setdefault("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        data.setdefault("description", "")
        with self._connect() as conn:
            cur = conn.execute(sql, data)
            conn.commit()
            return cur.lastrowid

    # READ
    def get_all_tasks(self) -> list[dict]:
        """Mengembalikan semua task diurutkan by priority lalu due_date."""
        priority_order = "CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END"
        sql = f"SELECT * FROM tasks ORDER BY {priority_order}, due_date ASC"
        with self._connect() as conn:
            rows = conn.execute(sql).fetchall()
        return [dict(r) for r in rows]

    def search_tasks(self, keyword: str = "", status: str = "", priority: str = "", category: str = "") -> list[dict]:
        """Filter + search tasks."""
        conditions = []
        params = {}

        if keyword:
            conditions.append("(title LIKE :kw OR description LIKE :kw)")
            params["kw"] = f"%{keyword}%"
        if status and status != "Semua":
            conditions.append("status = :status")
            params["status"] = status
        if priority and priority != "Semua":
            conditions.append("priority = :priority")
            params["priority"] = priority
        if category and category != "Semua":
            conditions.append("category = :category")
            params["category"] = category

        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        priority_order = "CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END"
        sql = f"SELECT * FROM tasks {where} ORDER BY {priority_order}, due_date ASC"

        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def get_stats(self) -> dict:
        """Statistik ringkas untuk stat-cards."""
        with self._connect() as conn:
            total  = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            done   = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='Done'").fetchone()[0]
            prog   = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='In Progress'").fetchone()[0]
            todo   = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='Todo'").fetchone()[0]
            high   = conn.execute("SELECT COUNT(*) FROM tasks WHERE priority='High'").fetchone()[0]
        return {"total": total, "done": done, "in_progress": prog, "todo": todo, "high": high}

    def get_categories(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT DISTINCT category FROM tasks ORDER BY category").fetchall()
        return [r[0] for r in rows]

    # UPDATE
    def update_task(self, task_id: int, data: dict):
        sql = """
            UPDATE tasks
            SET title=:title, category=:category, priority=:priority,
                status=:status, due_date=:due_date, description=:description
            WHERE id=:id
        """
        data["id"] = task_id
        with self._connect() as conn:
            conn.execute(sql, data)
            conn.commit()

    # DELETE
    def delete_task(self, task_id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            conn.commit()

    def delete_all_done(self):
        """Hapus semua task yang sudah Done."""
        with self._connect() as conn:
            conn.execute("DELETE FROM tasks WHERE status='Done'")
            conn.commit()
