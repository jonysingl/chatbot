import os
from pathlib import Path


def create_project_structure(base_path):
    """创建FastAPI项目目录结构"""
    dirs = [
        # 主应用目录
        "app",
        "app/api",
        "app/api/endpoints",
        "app/core",
        "app/db",
        "app/models",
        "app/schemas",
        "app/services",
        "app/templates",
        "app/static/css",
        "app/static/js",
        # 其他目录
        "migrations",
        "tests",
    ]

    files = {
        # 应用文件
        "app/__init__.py": "",
        "app/main.py": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get(\"/\")\ndef read_root():\n    return {\"message\": \"Hello World\"}",
        "app/api/__init__.py": "",
        "app/api/endpoints/__init__.py": "",
        "app/api/endpoints/user.py": "from fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get(\"/users/\")\ndef read_users():\n    return [{\"username\": \"user1\"}, {\"username\": \"user2\"}]",
        "app/core/__init__.py": "",
        "app/core/config.py": "from pydantic import BaseSettings\n\nclass Settings(BaseSettings):\n    app_name: str = \"Awesome API\"\n    admin_email: str\n    items_per_user: int = 50\n\n    class Config:\n        env_file = \".env\"",
        "app/core/security.py": "from fastapi.security import OAuth2PasswordBearer\n\noauth2_scheme = OAuth2PasswordBearer(tokenUrl=\"token\")",
        "app/db/__init__.py": "",
        "app/db/base.py": "# 数据库基类",
        "app/db/session.py": "from sqlalchemy import create_engine\nfrom sqlalchemy.ext.declarative import declarative_base\nfrom sqlalchemy.orm import sessionmaker\n\nSQLALCHEMY_DATABASE_URL = \"sqlite:///./sql_app.db\"\n\nengine = create_engine(\n    SQLALCHEMY_DATABASE_URL, connect_args={\"check_same_thread\": False}\n)\nSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)\n\nBase = declarative_base()",
        "app/models/__init__.py": "",
        "app/models/user.py": "from sqlalchemy import Boolean, Column, Integer, String\n\nfrom .base import Base\n\nclass User(Base):\n    __tablename__ = \"users\"\n\n    id = Column(Integer, primary_key=True, index=True)\n    username = Column(String, unique=True, index=True)\n    email = Column(String, unique=True, index=True)\n    hashed_password = Column(String)\n    is_active = Column(Boolean, default=True)",
        "app/schemas/__init__.py": "",
        "app/schemas/user.py": "from pydantic import BaseModel\n\nclass UserBase(BaseModel):\n    username: str\n    email: str\n\nclass UserCreate(UserBase):\n    password: str\n\nclass User(UserBase):\n    id: int\n    is_active: bool\n\n    class Config:\n        orm_mode = True",
        "app/services/__init__.py": "",
        "app/services/user_service.py": "from sqlalchemy.orm import Session\n\nfrom ..models.user import User\nfrom ..schemas.user import UserCreate\n\ndef get_user(db: Session, user_id: int):\n    return db.query(User).filter(User.id == user_id).first()\n\ndef create_user(db: Session, user: UserCreate):\n    db_user = User(username=user.username, email=user.email)\n    db.add(db_user)\n    db.commit()\n    db.refresh(db_user)\n    return db_user",
        "app/templates/base.html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>{% block title %}{% endblock %}</title>\n    <link rel=\"stylesheet\" href=\"{{ url_for('static', path='/css/style.css') }}\">\n</head>\n<body>\n    {% block content %}{% endblock %}\n    <script src=\"{{ url_for('static', path='/js/script.js') }}\"></script>\n</body>\n</html>",
        "app/templates/index.html": "{% extends \"base.html\" %}\n\n{% block title %}Home{% endblock %}\n\n{% block content %}\n<h1>Welcome to FastAPI</h1>\n{% endblock %}",
        "app/static/css/style.css": "body {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n}",
        "app/static/js/script.js": "console.log(\"Hello from FastAPI!\");",

        # 测试文件
        "tests/__init__.py": "",
        "tests/test_api.py": "from fastapi.testclient import TestClient\n\nfrom app.main import app\n\nclient = TestClient(app)\n\ndef test_read_root():\n    response = client.get(\"/\")\n    assert response.status_code == 200\n    assert response.json() == {\"message\": \"Hello World\"}",

        # 配置文件
        ".env": "ADMIN_EMAIL=admin@example.com",
        ".gitignore": "__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nbuild/\ndevelop-eggs/\ndist/\ndownloads/\neggs/\n.eggs/\nlib/\nlib64/\nparts/\nsdist/\nvar/\nwheels/\n*.egg-info/\n.installed.cfg\n*.egg\nMANIFEST\n\n# Unit test / coverage reports\nhtmlcov/\n.tox/\n.nox/\n.coverage\n.coverage.*\n.cache\nnosetests.xml\ncoverage.xml\n*.cover\n*.py,cover\n.hypothesis/\n.pytest_cache/\n\n# Environments\n.env\n.venv\nenv/\nvenv/\nENV/\nenv.bak/\nvenv.bak/\n\n# Database\n*.sqlite\n*.sql\n\n# IDE\n.vscode/\n.idea/\n*.swp\n*.swo\n*.sublime-workspace\n\n# Logs\n*.log\n\n# OS\n.DS_Store\n\n# FastAPI specific\nmigrations/\n",
        "requirements.txt": "fastapi\nuvicorn\npython-multipart\npython-jose[cryptography]\npasslib\nbcrypt\npython-dotenv\nsqlalchemy\nalembic\npytest\n",
        "run.py": "import uvicorn\n\nif __name__ == \"__main__\":\n    uvicorn.run(\"app.main:app\", host=\"0.0.0.0\", port=8000, reload=True)"
    }

    # 创建目录
    for directory in dirs:
        Path(base_path, directory).mkdir(parents=True, exist_ok=True)
        # 在每个目录中添加__init__.py文件
        if "__init__.py" not in os.listdir(Path(base_path, directory)):
            with open(Path(base_path, directory, "__init__.py"), "w") as f:
                f.write("")

    # 创建文件
    for file_path, content in files.items():
        full_path = Path(base_path, file_path)
        with open(full_path, "w") as f:
            f.write(content)

    print(f"项目结构已创建在: {base_path}")


if __name__ == "__main__":
    project_name = "testtomcat-fastapi"
    create_project_structure(project_name)