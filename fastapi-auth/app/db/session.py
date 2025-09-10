# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from app.core.config import settings

# engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
# AsyncSessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=AsyncSession)

# async def get_session() -> AsyncSession:
#     async with AsyncSessionLocal() as session:
#         yield session


# app/db/session.py
import ssl, certifi
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from app.core.config import settings

ssl_ctx = ssl.create_default_context(cafile=certifi.where())

# Serverless-friendly engine: no long-lived pools, TLS on asyncpg, pre-ping
engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,        # do not hold connections between invocations
    pool_pre_ping=True,        # validate before use
    connect_args={"ssl": ssl_ctx, "statement_cache_size": 0},# asyncpg TLS
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Use this as your FastAPI dependency
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

get_session = get_db