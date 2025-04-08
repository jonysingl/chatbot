from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.models.user import User
from app.services import user_service

# OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# 从session中获取当前用户
def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    # 尝试从session中获取用户ID
    user_id = request.session.get("user_id")
    if not user_id:
        return None

    # 根据用户ID获取用户
    return user_service.get_user_by_id(db, user_id)


# 检查是否已登录的依赖项
def require_login(current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user