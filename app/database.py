from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

# For async operations (FastAPI)
async_engine = create_async_engine(settings.DATABASE_URL_ASYNC)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

# Base class for SQLAlchemy models
Base = declarative_base()