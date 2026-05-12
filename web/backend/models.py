from pydantic import BaseModel
from typing import Optional


class UserRegister(BaseModel):
    username: str
    password: str
    role: str = "user"
    admin_code: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    role: str


class SessionCreate(BaseModel):
    title: str = "新对话"
    domain: str = "default"


class SessionRename(BaseModel):
    title: str


class MessageCreate(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    session_id: str
    message: str


class DomainCreate(BaseModel):
    name: str
    description: str = ""
    prompt_template: str = ""


class EntryCreate(BaseModel):
    title: str
    content: str


class EntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
