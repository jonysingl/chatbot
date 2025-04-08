from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
import os

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service

router = APIRouter()

# 设置模板路径
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
templates = Jinja2Templates(directory=templates_dir)


# 渲染注册页面
@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# 处理注册请求
@router.post("/register")
async def register(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(..., alias="confirm-password"),
        db: Session = Depends(get_db)
):
    try:
        # 验证数据
        user_data = UserCreate(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password
        )

        # 检查用户名是否已存在
        db_user = user_service.get_user_by_username(db, username=user_data.username)
        if db_user:
            error_message = "用户名已被使用"
            return RedirectResponse(
                url=f"/register?error={error_message}",
                status_code=status.HTTP_303_SEE_OTHER
            )

        # 检查邮箱是否已存在
        db_user = user_service.get_user_by_email(db, email=user_data.email)
        if db_user:
            error_message = "此邮箱已被注册"
            return RedirectResponse(
                url=f"/register?error={error_message}",
                status_code=status.HTTP_303_SEE_OTHER
            )

        # 创建新用户
        user_service.create_user(db=db, user_data=user_data)

        # 注册成功，重定向到登录页面
        return RedirectResponse(
            url="/login?registerSuccess=true",
            status_code=status.HTTP_303_SEE_OTHER
        )

    except ValueError as e:
        # 处理验证错误
        error_message = str(e)
        return RedirectResponse(
            url=f"/register?error={error_message}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as e:
        # 处理其他错误
        error_message = "注册过程中发生错误，请稍后重试"
        return RedirectResponse(
            url=f"/register?error={error_message}",
            status_code=status.HTTP_303_SEE_OTHER
        )


# API版本的注册端点（可与前端JS交互）
@router.post("/api/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def api_register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    db_user = user_service.get_user_by_username(db, username=user_data.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被使用"
        )

    # 检查邮箱是否已存在
    db_user = user_service.get_user_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

    # 创建新用户
    return user_service.create_user(db=db, user_data=user_data)