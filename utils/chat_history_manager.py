import sqlite3
import os
import hashlib
import secrets
from typing import Optional

from utils.path_tool import get_absolute_path


def _hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash a password with a salt using SHA-256."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return hashed, salt


def _verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify a password against a hash."""
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == hashed


class ChatHistoryManager:
    """
    会话历史持久化管理器（SQLite 实现）

    Phase 1.3: 当前使用 SQLite，后续可无缝切换至 Redis
    Phase 2.1: 新增多用户体系，每个用户拥有独立的会话历史
    Phase 2.1: 用户密码校验 + 角色权限（admin / user）
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = get_absolute_path("data/chat_history.db")
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_conn()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT DEFAULT '新对话',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                );
            """)
            conn.commit()
            self._migrate(conn)
        finally:
            conn.close()

    def _migrate(self, conn):
        """Migrate old database schema to add missing columns/tables."""
        cursor = conn.execute("PRAGMA table_info(sessions)")
        columns = {row["name"] for row in cursor.fetchall()}
        if "user_id" not in columns:
            conn.execute("ALTER TABLE sessions ADD COLUMN user_id TEXT DEFAULT ''")
            conn.commit()

        cursor = conn.execute("PRAGMA table_info(users)")
        user_cols = {row["name"] for row in cursor.fetchall()}
        if "password_hash" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT DEFAULT ''")
        if "password_salt" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN password_salt TEXT DEFAULT ''")
        if "role" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")

        conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id)")
        conn.commit()

    # ===== User Management =====

    def register_user(self, username: str, password: str, role: str = "user") -> dict:
        """Register a new user with password. Returns user dict or raises."""
        import uuid
        hashed, salt = _hash_password(password)
        user_id = str(uuid.uuid4())
        conn = self._get_conn()
        try:
            conn.execute(
                "INSERT INTO users (id, username, password_hash, password_salt, role) VALUES (?, ?, ?, ?, ?)",
                (user_id, username, hashed, salt, role)
            )
            conn.commit()
            return {"id": user_id, "username": username, "role": role}
        except sqlite3.IntegrityError:
            raise ValueError(f"用户名 '{username}' 已存在")
        finally:
            conn.close()

    def login_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate user with username and password. Returns user dict or None."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT id, username, password_hash, password_salt, role FROM users WHERE username = ?",
                (username,)
            ).fetchone()
            if not row:
                return None
            if not _verify_password(password, row["password_hash"], row["password_salt"]):
                return None
            conn.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (row["id"],)
            )
            conn.commit()
            return {"id": row["id"], "username": row["username"], "role": row["role"]}
        finally:
            conn.close()

    def get_user(self, user_id: str) -> Optional[dict]:
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT id, username, role, created_at, last_login FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def list_users(self) -> list[dict]:
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT id, username, role, created_at, last_login FROM users ORDER BY last_login DESC"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def update_user_role(self, user_id: str, role: str):
        conn = self._get_conn()
        try:
            conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
            conn.commit()
        finally:
            conn.close()

    def delete_user(self, user_id: str):
        conn = self._get_conn()
        try:
            session_ids = [r["id"] for r in conn.execute(
                "SELECT id FROM sessions WHERE user_id = ?", (user_id,)
            ).fetchall()]
            for sid in session_ids:
                conn.execute("DELETE FROM messages WHERE session_id = ?", (sid,))
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
        finally:
            conn.close()

    # ===== Session Management =====

    def get_history(self, session_id: str) -> list[dict]:
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,)
            ).fetchall()
            return [{"role": row["role"], "content": row["content"]} for row in rows]
        finally:
            conn.close()

    def add_message(self, session_id: str, user_id: str, role: str, content: str):
        conn = self._get_conn()
        try:
            conn.execute(
                "INSERT OR IGNORE INTO sessions (id, user_id, title) VALUES (?, ?, '新对话')",
                (session_id, user_id)
            )
            conn.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content)
            )
            conn.execute(
                "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,)
            )
            conn.commit()
        finally:
            conn.close()

    def get_user_sessions(self, user_id: str) -> dict[str, dict]:
        conn = self._get_conn()
        try:
            rows = conn.execute(
                """SELECT id, title, created_at, updated_at
                   FROM sessions WHERE user_id = ?
                   ORDER BY updated_at DESC""",
                (user_id,)
            ).fetchall()
            result = {}
            for row in rows:
                result[row["id"]] = {
                    "title": row["title"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
            return result
        finally:
            conn.close()

    def create_session(self, session_id: str, user_id: str, title: str = "新对话"):
        conn = self._get_conn()
        try:
            conn.execute(
                "INSERT OR IGNORE INTO sessions (id, user_id, title) VALUES (?, ?, ?)",
                (session_id, user_id, title)
            )
            conn.commit()
        finally:
            conn.close()

    def update_session_title(self, session_id: str, title: str):
        conn = self._get_conn()
        try:
            conn.execute(
                "UPDATE sessions SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (title, session_id)
            )
            conn.commit()
        finally:
            conn.close()

    def delete_session(self, session_id: str):
        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
        finally:
            conn.close()

    def clear_user_data(self, user_id: str):
        conn = self._get_conn()
        try:
            conn.execute(
                "DELETE FROM messages WHERE session_id IN (SELECT id FROM sessions WHERE user_id = ?)",
                (user_id,)
            )
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            conn.commit()
        finally:
            conn.close()

    def clear_all(self):
        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM sessions")
            conn.execute("DELETE FROM users")
            conn.commit()
        finally:
            conn.close()
