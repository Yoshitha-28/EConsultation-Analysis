from fastapi import FastAPI
from .database import Base, async_engine
from .routes import comments
import logging

logger = logging.getLogger(__name__)

async def create_tables():
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        # In production, you might want to handle this differently
        raise

app = FastAPI(title="eConsultation Analysis API (PostgreSQL)")

@app.on_event("startup")
async def on_startup():
    await create_tables()

app.include_router(comments.router, prefix="/api/v1", tags=["Comments"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the eConsultation Analysis API (PostgreSQL)"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "database": "connected"}