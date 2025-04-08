from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import secrets
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 安全密钥，实际应用中应从环境变量获取
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 创建令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 创建会话ID
def create_session_id():
    return secrets.token_urlsafe(32)

# 用户会话存储（实际应用中应该使用Redis或数据库）
active_sessions = {}

# 创建用户会话
def create_user_session(user_id: int, username: str):
    session_id = create_session_id()
    active_sessions[session_id] = {
        "user_id": user_id,
        "username": username,
        "created_at": datetime.utcnow()
    }
    return session_id

# 获取当前用户会话
def get_current_user_session(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in active_sessions:
        return None
    return active_sessions[session_id]

# 验证会话依赖
async def get_current_user(request: Request):
    session = get_current_user_session(request)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="身份验证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return session