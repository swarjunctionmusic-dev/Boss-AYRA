import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parents[2] / "database" / "ayra_memory.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'general',
            created_at TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            completed_at TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_memory(content: str, category: str = "general"):
    init_db()
    connection = get_connection()
    cursor = connection.execute(
        """
        INSERT INTO memories(content, category, created_at)
        VALUES (?, ?, ?)
        """,
        (
            content.strip(),
            category.strip() or "general",
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    connection.commit()
    memory_id = cursor.lastrowid
    connection.close()
    return memory_id


def list_memories(limit: int = 100):
    init_db()
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT id, content, category, created_at
        FROM memories
        ORDER BY id DESC
        LIMIT ?
        """,
        (max(1, min(limit, 500)),),
    ).fetchall()
    connection.close()
    return [dict(row) for row in rows]


def search_memories(query: str, limit: int = 20):
    init_db()
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT id, content, category, created_at
        FROM memories
        WHERE content LIKE ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (f"%{query.strip()}%", max(1, min(limit, 100))),
    ).fetchall()
    connection.close()
    return [dict(row) for row in rows]


def delete_memory(memory_id: int):
    init_db()
    connection = get_connection()
    cursor = connection.execute(
        "DELETE FROM memories WHERE id = ?",
        (memory_id,),
    )
    connection.commit()
    deleted = cursor.rowcount > 0
    connection.close()
    return deleted


def save_conversation(role: str, content: str):
    init_db()
    connection = get_connection()
    connection.execute(
        """
        INSERT INTO conversations(role, content, created_at)
        VALUES (?, ?, ?)
        """,
        (
            role,
            content,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    connection.commit()
    connection.close()


def recent_conversations(limit: int = 10):
    init_db()
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT role, content, created_at
        FROM conversations
        ORDER BY id DESC
        LIMIT ?
        """,
        (max(1, min(limit, 50)),),
    ).fetchall()
    connection.close()
    return [dict(row) for row in reversed(rows)]


def create_task(title: str, description: str = ""):
    init_db()
    connection = get_connection()
    cursor = connection.execute(
        """
        INSERT INTO tasks(title, description, status, created_at)
        VALUES (?, ?, 'pending', ?)
        """,
        (
            title.strip(),
            description.strip(),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    connection.commit()
    task_id = cursor.lastrowid
    connection.close()
    return task_id


def list_tasks():
    init_db()
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT id, title, description, status, created_at, completed_at
        FROM tasks
        ORDER BY
            CASE WHEN status = 'pending' THEN 0 ELSE 1 END,
            id DESC
        """
    ).fetchall()
    connection.close()
    return [dict(row) for row in rows]


def complete_task(task_id: int):
    init_db()
    connection = get_connection()
    cursor = connection.execute(
        """
        UPDATE tasks
        SET status = 'completed',
            completed_at = ?
        WHERE id = ?
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            task_id,
        ),
    )
    connection.commit()
    changed = cursor.rowcount > 0
    connection.close()
    return changed


def delete_task(task_id: int):
    init_db()
    connection = get_connection()
    cursor = connection.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,),
    )
    connection.commit()
    deleted = cursor.rowcount > 0
    connection.close()
    return deleted
