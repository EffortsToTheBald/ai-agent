import uuid
from fastapi import APIRouter, HTTPException
from database import get_db, hash_password, verify_password
from models import UserRegister, UserLogin, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

ADMIN_CODE = "admin888"


@router.post("/register", response_model=UserResponse)
def register(req: UserRegister):
    if len(req.password) < 6:
        raise HTTPException(400, "密码长度至少6位")
    if req.role == "admin" and req.admin_code != ADMIN_CODE:
        raise HTTPException(400, "管理员验证码错误")

    user_id = str(uuid.uuid4())
    hashed, salt = hash_password(req.password)

    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO users (id, username, password_hash, password_salt, role) VALUES (?,?,?,?,?)",
                (user_id, req.username, hashed, salt, req.role)
            )
        except Exception:
            raise HTTPException(400, "用户名已存在")

    return UserResponse(id=user_id, username=req.username, role=req.role)


@router.post("/login", response_model=UserResponse)
def login(req: UserLogin):
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, password_salt, role FROM users WHERE username=?",
            (req.username,)
        ).fetchone()

    if not row or not verify_password(req.password, row["password_hash"], row["password_salt"]):
        raise HTTPException(401, "用户名或密码错误")

    with get_db() as conn:
        conn.execute("UPDATE users SET last_login=CURRENT_TIMESTAMP WHERE id=?", (row["id"],))

    return UserResponse(id=row["id"], username=row["username"], role=row["role"])


@router.get("/users", response_model=list[UserResponse])
def list_users():
    with get_db() as conn:
        rows = conn.execute("SELECT id, username, role FROM users ORDER BY last_login DESC").fetchall()
    return [UserResponse(id=r["id"], username=r["username"], role=r["role"]) for r in rows]


@router.put("/users/{user_id}/role")
def update_role(user_id: str, role: str):
    with get_db() as conn:
        conn.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
    return {"ok": True}


@router.delete("/users/{user_id}")
def delete_user(user_id: str):
    with get_db() as conn:
        sids = [r["id"] for r in conn.execute("SELECT id FROM sessions WHERE user_id=?", (user_id,)).fetchall()]
        for sid in sids:
            conn.execute("DELETE FROM messages WHERE session_id=?", (sid,))
        conn.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    return {"ok": True}
