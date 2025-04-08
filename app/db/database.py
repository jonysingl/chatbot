from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import SQLALCHEMY_DATABASE_URL

# 创建引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # 避免只读应用启动时的警告
    pool_pre_ping=True,
    # 增加连接超时和重试逻辑
    pool_recycle=3600,
    pool_timeout=30,
    max_overflow=10
)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 数据库依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()