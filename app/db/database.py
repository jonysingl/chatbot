from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库连接URL - 确保正确配置
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@localhost/chatbot"

try:
    # 创建引擎，启用池回收和连接前测试
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,  # 在连接被使用前先ping一下
        pool_recycle=3600,  # 一小时后回收连接
        echo=False  # 设为True可以查看SQL语句
    )

    # 测试连接
    with engine.connect() as conn:
        logger.info("数据库连接成功")
except Exception as e:
    logger.error(f"数据库连接错误: {e}", exc_info=True)
    raise

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 添加SQL日志记录
if logger.level <= logging.DEBUG:
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        logger.debug(f"执行SQL: {statement}")
        if parameters:
            logger.debug(f"参数: {parameters}")


# 数据库依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()