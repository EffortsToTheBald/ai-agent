import uuid
import json
import sys
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models import SessionCreate, SessionRename, MessageCreate, ChatRequest
from database import get_db, PROJECT_ROOT

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Lazy import agent to avoid DASHSCOPE_API_KEY error at startup
_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        sys.path.insert(0, PROJECT_ROOT)
        from agent.react_agent import ReactAgent
        _agent = ReactAgent()
    return _agent


# ── Sessions ──

@router.post("/sessions")
def create_session(req: SessionCreate, user_id: str):
    sid = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute(
            "INSERT INTO sessions (id, user_id, title, domain) VALUES (?,?,?,?)",
            (sid, user_id, req.title, req.domain)
        )
    return {"id": sid, "title": req.title, "domain": req.domain}


@router.get("/sessions")
def list_sessions(user_id: str, domain: str = None):
    with get_db() as conn:
        if domain:
            rows = conn.execute(
                "SELECT id, title, domain, created_at, updated_at FROM sessions WHERE user_id=? AND domain=? ORDER BY updated_at DESC",
                (user_id, domain)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, title, domain, created_at, updated_at FROM sessions WHERE user_id=? ORDER BY updated_at DESC",
                (user_id,)
            ).fetchall()
    return [dict(r) for r in rows]


@router.put("/sessions/{session_id}/rename")
def rename_session(session_id: str, req: SessionRename):
    with get_db() as conn:
        conn.execute("UPDATE sessions SET title=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (req.title, session_id))
    return {"ok": True}


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    with get_db() as conn:
        conn.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE id=?", (session_id,))
    return {"ok": True}


# ── Messages ──

@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: str):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id=? ORDER BY id ASC",
            (session_id,)
        ).fetchall()
    return [dict(r) for r in rows]


@router.post("/sessions/{session_id}/messages")
def add_message(session_id: str, user_id: str, req: MessageCreate):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?,?,?)",
            (session_id, req.role, req.content)
        )
        conn.execute("UPDATE sessions SET updated_at=CURRENT_TIMESTAMP WHERE id=?", (session_id,))
    return {"ok": True}


# ── Chat (SSE streaming) ──

@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    def generate():
        full_response = ""
        try:
            agent = _get_agent()
            for token in agent.excute_stream(req.message):
                full_response += token
                yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
            return

        with get_db() as conn:
            conn.execute("INSERT INTO messages (session_id, role, content) VALUES (?,?,?)",
                         (req.session_id, "user", req.message))
            conn.execute("INSERT INTO messages (session_id, role, content) VALUES (?,?,?)",
                         (req.session_id, "assistant", full_response))
            conn.execute("UPDATE sessions SET updated_at=CURRENT_TIMESTAMP WHERE id=?", (req.session_id,))

        yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
