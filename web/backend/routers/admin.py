import uuid
import os
import sys
from fastapi import APIRouter, HTTPException, UploadFile, File
from models import DomainCreate, EntryCreate, EntryUpdate
from database import get_db, PROJECT_ROOT

router = APIRouter(prefix="/api/admin", tags=["admin"])

DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# Lazy import file watcher
_file_watcher = None
_WATCHDOG_AVAILABLE = False


def _get_file_watcher():
    global _file_watcher, _WATCHDOG_AVAILABLE
    if _file_watcher is None:
        try:
            sys.path.insert(0, PROJECT_ROOT)
            from utils.file_watcher import file_watcher, WATCHDOG_AVAILABLE
            _file_watcher = file_watcher
            _WATCHDOG_AVAILABLE = WATCHDOG_AVAILABLE
        except ImportError:
            _WATCHDOG_AVAILABLE = False
    return _file_watcher


# ── Domains ──

@router.get("/domains")
def list_domains():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM domains ORDER BY created_at").fetchall()
    return [dict(r) for r in rows]


@router.post("/domains")
def create_domain(req: DomainCreate):
    did = str(uuid.uuid4())
    cname = f"domain_{req.name}"
    ddir = f"data/domains/{req.name}"
    os.makedirs(os.path.join(PROJECT_ROOT, ddir), exist_ok=True)
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO domains (id, name, description, collection_name, prompt_template, data_dir) VALUES (?,?,?,?,?,?)",
                (did, req.name, req.description, cname, req.prompt_template, ddir)
            )
        except Exception:
            raise HTTPException(400, "领域已存在")
    return {"id": did, "name": req.name, "collection_name": cname, "data_dir": ddir}


@router.delete("/domains/{domain_id}")
def delete_domain(domain_id: str):
    if domain_id == "default":
        raise HTTPException(400, "不能删除默认领域")
    with get_db() as conn:
        conn.execute("DELETE FROM knowledge_entries WHERE domain_id=?", (domain_id,))
        conn.execute("DELETE FROM knowledge_files WHERE domain_id=?", (domain_id,))
        conn.execute("DELETE FROM domains WHERE id=?", (domain_id,))
    return {"ok": True}


# ── Knowledge Entries ──

@router.get("/domains/{domain_id}/entries")
def list_entries(domain_id: str):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM knowledge_entries WHERE domain_id=? ORDER BY updated_at DESC", (domain_id,)
        ).fetchall()
    return [dict(r) for r in rows]


@router.post("/domains/{domain_id}/entries")
def add_entry(domain_id: str, req: EntryCreate):
    eid = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute(
            "INSERT INTO knowledge_entries (id, domain_id, title, content) VALUES (?,?,?,?)",
            (eid, domain_id, req.title, req.content)
        )
    return {"id": eid, "title": req.title}


@router.put("/entries/{entry_id}")
def update_entry(entry_id: str, req: EntryUpdate):
    with get_db() as conn:
        if req.title is not None:
            conn.execute("UPDATE knowledge_entries SET title=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                         (req.title, entry_id))
        if req.content is not None:
            conn.execute("UPDATE knowledge_entries SET content=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                         (req.content, entry_id))
    return {"ok": True}


@router.delete("/entries/{entry_id}")
def delete_entry(entry_id: str):
    with get_db() as conn:
        conn.execute("DELETE FROM knowledge_entries WHERE id=?", (entry_id,))
    return {"ok": True}


# ── Knowledge Files ──

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}


@router.get("/domains/{domain_id}/files")
def list_files(domain_id: str):
    with get_db() as conn:
        domain = conn.execute("SELECT data_dir FROM domains WHERE id=?", (domain_id,)).fetchone()
        if not domain:
            raise HTTPException(404, "领域不存在")

        db_files = conn.execute(
            "SELECT * FROM knowledge_files WHERE domain_id=? ORDER BY uploaded_at DESC", (domain_id,)
        ).fetchall()

    db_filenames = {r["filename"] for r in db_files}
    result = [dict(r) for r in db_files]

    scan_dir = os.path.join(PROJECT_ROOT, domain["data_dir"])
    if os.path.isdir(scan_dir):
        for fname in sorted(os.listdir(scan_dir)):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                continue
            if fname in db_filenames:
                continue
            result.append({
                "id": None,
                "domain_id": domain_id,
                "filename": fname,
                "file_path": os.path.join(scan_dir, fname),
                "md5_hex": "",
                "status": "disk_only",
                "uploaded_at": None,
            })

    return result


@router.post("/domains/{domain_id}/files/upload")
async def upload_file(domain_id: str, file: UploadFile = File(...)):
    import hashlib
    content = await file.read()
    md5_hex = hashlib.md5(content).hexdigest()

    with get_db() as conn:
        domain = conn.execute("SELECT data_dir FROM domains WHERE id=?", (domain_id,)).fetchone()
        if not domain:
            raise HTTPException(404, "领域不存在")

    save_dir = os.path.join(PROJECT_ROOT, domain["data_dir"])
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, file.filename)
    with open(save_path, "wb") as f:
        f.write(content)

    fid = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute(
            "INSERT INTO knowledge_files (id, domain_id, filename, file_path, md5_hex) VALUES (?,?,?,?,?)",
            (fid, domain_id, file.filename, save_path, md5_hex)
        )
    return {"id": fid, "filename": file.filename, "md5": md5_hex}


@router.delete("/files/{file_id}")
def delete_file(file_id: str):
    with get_db() as conn:
        conn.execute("DELETE FROM knowledge_files WHERE id=?", (file_id,))
    return {"ok": True}


@router.post("/domains/{domain_id}/reindex")
def reindex(domain_id: str):
    with get_db() as conn:
        domain = conn.execute("SELECT collection_name, data_dir FROM domains WHERE id=?", (domain_id,)).fetchone()
    if not domain:
        raise HTTPException(404, "领域不存在")

    try:
        sys.path.insert(0, PROJECT_ROOT)
        from rag.vector_store import VectorStoreService
        from database import get_db as _get_db

        vs = VectorStoreService(collection_name=domain["collection_name"], data_path=domain["data_dir"])
        with _get_db() as conn:
            indexed = {r["md5_hex"] for r in conn.execute("SELECT md5_hex FROM knowledge_files").fetchall()}
        count = vs.load_documents(indexed_md5_set=indexed)
        return {"indexed": count}
    except Exception as e:
        raise HTTPException(500, f"索引失败: {str(e)}")


# ── File Watcher ──


@router.get("/system/watcher")
def get_watcher_status():
    fw = _get_file_watcher()
    return {
        "available": _WATCHDOG_AVAILABLE,
        "running": fw.is_running if fw else False,
    }


@router.post("/system/watcher/start")
def start_watcher():
    fw = _get_file_watcher()
    if not _WATCHDOG_AVAILABLE:
        raise HTTPException(400, "watchdog 未安装，无法使用文件监听")
    if fw.is_running:
        return {"ok": True, "message": "文件监听已在运行"}
    abs_data = os.path.join(PROJECT_ROOT, "data")
    fw.start(abs_data, lambda evt, path: None)
    return {"ok": True, "message": "文件监听已启动"}


@router.post("/system/watcher/stop")
def stop_watcher():
    fw = _get_file_watcher()
    if not _WATCHDOG_AVAILABLE:
        raise HTTPException(400, "watchdog 未安装")
    fw.stop()
    return {"ok": True, "message": "文件监听已停止"}
