from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
from datetime import datetime
import logging

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.services import user_service
from app.utils.auth import create_user_session, get_current_user_session, get_current_user

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter()

# 配置模板路径
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))


# 注册页面和处理代码保持不变...

# 登录页面
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # 检查是否已登录
    session = get_current_user_session(request)
    if session:
        # 已登录，重定向到聊天页面
        return RedirectResponse(url="/chatbot", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("login.html", {"request": request})


# 登录处理
@router.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    # 验证用户
    user = user_service.authenticate_user(db, username, password)

    if not user:
        # 登录失败
        logger.warning(f"登录失败: 用户名 '{username}' 或密码不正确")
        return RedirectResponse(
            url="/login?error=用户名或密码错误",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 登录成功，创建会话
    session_id = create_user_session(user.user_id, user.username)

    # 设置会话cookie
    response = RedirectResponse(url="/chatbot", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=1800,  # 30分钟
        samesite="lax"
    )

    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()

    logger.info(f"登录成功: user_id={user.user_id}, username={user.username}")
    return response


# 注销
@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="session_id")
    return response


# 聊天页面 - 需要用户登录
@router.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request, current_user=Depends(get_current_user)):
    try:
        return templates.TemplateResponse("chatbot.html", {
            "request": request,
            "username": current_user["username"],
            "current_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        logger.error(f"加载聊天页面出错: {e}", exc_info=True)
        return HTMLResponse(content=f"<h1>无法加载聊天页面</h1><p>错误信息: {str(e)}</p>", status_code=500)


# 获取当前用户信息的API端点
@router.get("/api/current-user")
async def get_current_user_info(current_user=Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "user_id": current_user["user_id"],
        "logged_in_at": current_user["created_at"].strftime("%Y-%m-%d %H:%M:%S")
    }


# 用户个人资料页面
@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    # 查询完整的用户信息
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "",
        "last_login": user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else ""
    })