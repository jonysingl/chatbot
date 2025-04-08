from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import logging
from datetime import datetime

from app.db.database import get_db
from app.schemas.user import UserCreate
from app.services import user_service

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 配置模板路径
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))


# 注册页面
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# 注册处理
@router.post("/register")
async def register(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(..., alias="confirm-password"),
        db: Session = Depends(get_db)
):
    # 记录请求信息，帮助调试
    logger.info(f"处理注册请求: 用户名={username}, 邮箱={email}")

    # 检查两次密码是否一致
    if password != confirm_password:
        logger.warning("注册失败: 两次输入的密码不一致")
        return RedirectResponse(
            url=f"/register?error=两次输入的密码不一致",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 检查用户名是否已存在
    if user_service.get_user_by_username(db, username):
        logger.warning(f"注册失败: 用户名 '{username}' 已存在")
        return RedirectResponse(
            url=f"/register?error=用户名已被注册",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 检查邮箱是否已存在
    if user_service.get_user_by_email(db, email):
        logger.warning(f"注册失败: 邮箱 '{email}' 已存在")
        return RedirectResponse(
            url=f"/register?error=邮箱已被注册",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 创建用户
    try:
        user_data = UserCreate(
            username=username,
            email=email,
            password=password
        )
        user = user_service.create_user(db, user_data)
        logger.info(f"用户注册成功: user_id={user.user_id}, username={user.username}")

        # 注册成功，重定向到登录页
        return RedirectResponse(
            url="/login?registerSuccess=true",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as e:
        # 记录详细错误信息
        logger.error(f"注册时发生错误: {str(e)}", exc_info=True)
        # 注册失败
        return RedirectResponse(
            url=f"/register?error=注册失败: {str(e)}",
            status_code=status.HTTP_303_SEE_OTHER
        )


# 登录页面
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# 登录处理
@router.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    # 记录登录尝试
    logger.info(f"处理登录请求: 用户名={username}")

    # 验证用户
    user = user_service.authenticate_user(db, username, password)

    if not user:
        # 登录失败
        logger.warning(f"登录失败: 用户名 '{username}' 密码验证不通过")
        return RedirectResponse(
            url="/login?error=用户名或密码错误",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 登录成功，记录信息
    logger.info(f"登录成功: user_id={user.user_id}, username={user.username}")

    # 重定向到聊天页面
    return RedirectResponse(
        url="/chatbot",
        status_code=status.HTTP_303_SEE_OTHER
    )


# 聊天页面 (之前的dashboard)
@router.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    try:
        return templates.TemplateResponse("chatbot.html", {
            "request": request,
            "username": "jonysingl",  # 这里可以设置用户名
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        logger.error(f"加载聊天页面出错: {e}", exc_info=True)
        return HTMLResponse(content=f"<h1>无法加载聊天页面</h1><p>错误信息: {str(e)}</p>", status_code=500)