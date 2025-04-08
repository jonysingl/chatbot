from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.services import user_service

# 创建路由
router = APIRouter()

# 配置模板
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)


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
    # 检查两次密码是否一致
    if password != confirm_password:
        return RedirectResponse(
            url=f"/register?error=两次输入的密码不一致",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 检查用户名是否已存在
    if user_service.get_user_by_username(db, username):
        return RedirectResponse(
            url=f"/register?error=用户名已被注册",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 检查邮箱是否已存在
    if user_service.get_user_by_email(db, email):
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
        user_service.create_user(db, user_data)
        # 注册成功，重定向到登录页
        return RedirectResponse(
            url="/login?registerSuccess=true",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as e:
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
    # 验证用户
    user = user_service.authenticate_user(db, username, password)

    if not user:
        # 登录失败
        return RedirectResponse(
            url="/login?error=用户名或密码错误",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 登录成功，重定向到主页
    # 在实际应用中，这里应该设置session或cookie
    return RedirectResponse(
        url="/dashboard",
        status_code=status.HTTP_303_SEE_OTHER
    )


# 仪表盘页面 (登录后的首页)
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    # 在实际应用中，应该检查用户是否已登录
    return templates.TemplateResponse("dashboard.html", {"request": request})