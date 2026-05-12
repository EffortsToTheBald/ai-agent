import sqlite3
import os
import uuid
from typing import Optional

from utils.path_tool import get_absolute_path


class KnowledgeManager:
    """
    知识库管理器 — 领域隔离 + Prompt 模板 + 知识条目 CRUD

    Phase 2.2: Admin 知识库管理后台
    - 领域管理：每个领域拥有独立的向量集合、Prompt 模板、知识文件
    - Prompt 模板管理：每个领域可配置独立的系统提示词
    - 知识条目 CRUD：支持条目级别的增删改查
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = get_absolute_path("data/knowledge.db")
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._ensure_writable()
        self._init_db()

    def _ensure_writable(self):
        """Ensure the database file is writable, fix permissions if needed."""
        if os.path.exists(self.db_path):
            if not os.access(self.db_path, os.W_OK):
                try:
                    os.chmod(self.db_path, 0o666)
                except OSError:
                    pass

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_conn()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS domains (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT DEFAULT '',
                    collection_name TEXT NOT NULL,
                    prompt_template TEXT DEFAULT '',
                    data_dir TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS knowledge_entries (
                    id TEXT PRIMARY KEY,
                    domain_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT DEFAULT 'manual',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (domain_id) REFERENCES domains(id)
                );

                CREATE TABLE IF NOT EXISTS knowledge_files (
                    id TEXT PRIMARY KEY,
                    domain_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    md5_hex TEXT NOT NULL,
                    status TEXT DEFAULT 'indexed',
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (domain_id) REFERENCES domains(id)
                );
            """)
            conn.commit()
            self._ensure_default_domain(conn)
        finally:
            conn.close()

    def _ensure_default_domain(self, conn):
        row = conn.execute("SELECT id FROM domains WHERE name = 'default'").fetchone()
        if not row:
            conn.execute(
                "INSERT INTO domains (id, name, description, collection_name, data_dir) VALUES (?, ?, ?, ?, ?)",
                ("default", "default", "默认领域（扫地机器人）", "agent", "data")
            )
            conn.commit()

    # ===== Domain Management =====

    def list_domains(self) -> list[dict]:
        conn = self._get_conn()
        try:
            rows = conn.execute("SELECT * FROM domains ORDER BY created_at").fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_domain(self, domain_id: str) -> Optional[dict]:
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT * FROM domains WHERE id = ?", (domain_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_domain_by_name(self, name: str) -> Optional[dict]:
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT * FROM domains WHERE name = ?", (name,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def create_domain(self, name: str, description: str = "", prompt_template: str = "") -> dict:
        domain_id = str(uuid.uuid4())
        collection_name = f"domain_{name}"
        data_dir = f"data/domains/{name}"
        conn = self._get_conn()
        try:
            os.makedirs(get_absolute_path(data_dir), exist_ok=True)
            conn.execute(
                "INSERT INTO domains (id, name, description, collection_name, prompt_template, data_dir) VALUES (?, ?, ?, ?, ?, ?)",
                (domain_id, name, description, collection_name, prompt_template, data_dir)
            )
            conn.commit()
            return {"id": domain_id, "name": name, "description": description, "collection_name": collection_name, "data_dir": data_dir}
        except sqlite3.IntegrityError:
            raise ValueError(f"领域 '{name}' 已存在")
        finally:
            conn.close()

    def update_domain(self, domain_id: str, **kwargs):
        conn = self._get_conn()
        try:
            for key, value in kwargs.items():
                if key in ("name", "description", "prompt_template"):
                    conn.execute(f"UPDATE domains SET {key} = ? WHERE id = ?", (value, domain_id))
            conn.commit()
        finally:
            conn.close()

    def delete_domain(self, domain_id: str):
        if domain_id == "default":
            raise ValueError("不能删除默认领域")
        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM knowledge_entries WHERE domain_id = ?", (domain_id,))
            conn.execute("DELETE FROM knowledge_files WHERE domain_id = ?", (domain_id,))
            conn.execute("DELETE FROM domains WHERE id = ?", (domain_id,))
            conn.commit()
        finally:
            conn.close()

    # ===== Knowledge Entries CRUD =====

    def add_entry(self, domain_id: str, title: str, content: str, source: str = "manual") -> dict:
        entry_id = str(uuid.uuid4())
        conn = self._get_conn()
        try:
            conn.execute(
                "INSERT INTO knowledge_entries (id, domain_id, title, content, source) VALUES (?, ?, ?, ?, ?)",
                (entry_id, domain_id, title, content, source)
            )
            conn.commit()
            return {"id": entry_id, "domain_id": domain_id, "title": title, "content": content}
        finally:
            conn.close()

    def update_entry(self, entry_id: str, **kwargs):
        conn = self._get_conn()
        try:
            for key, value in kwargs.items():
                if key in ("title", "content"):
                    conn.execute(f"UPDATE knowledge_entries SET {key} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (value, entry_id))
            conn.commit()
        finally:
            conn.close()

    def delete_entry(self, entry_id: str):
        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM knowledge_entries WHERE id = ?", (entry_id,))
            conn.commit()
        finally:
            conn.close()

    def list_entries(self, domain_id: str) -> list[dict]:
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM knowledge_entries WHERE domain_id = ? ORDER BY updated_at DESC",
                (domain_id,)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_entry(self, entry_id: str) -> Optional[dict]:
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT * FROM knowledge_entries WHERE id = ?", (entry_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    # ===== Knowledge Files Tracking =====

    def record_file(self, domain_id: str, filename: str, file_path: str, md5_hex: str) -> str:
        file_id = str(uuid.uuid4())
        conn = self._get_conn()
        try:
            conn.execute(
                "INSERT INTO knowledge_files (id, domain_id, filename, file_path, md5_hex) VALUES (?, ?, ?, ?, ?)",
                (file_id, domain_id, filename, file_path, md5_hex)
            )
            conn.commit()
            return file_id
        finally:
            conn.close()

    def is_file_indexed(self, md5_hex: str) -> bool:
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT id FROM knowledge_files WHERE md5_hex = ?", (md5_hex,)).fetchone()
            return row is not None
        finally:
            conn.close()

    def list_files(self, domain_id: str) -> list[dict]:
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM knowledge_files WHERE domain_id = ? ORDER BY uploaded_at DESC",
                (domain_id,)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def delete_file(self, file_id: str):
        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM knowledge_files WHERE id = ?", (file_id,))
            conn.commit()
        finally:
            conn.close()

    def get_indexed_md5_set(self) -> set:
        conn = self._get_conn()
        try:
            rows = conn.execute("SELECT md5_hex FROM knowledge_files").fetchall()
            return {r["md5_hex"] for r in rows}
        finally:
            conn.close()
