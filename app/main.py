from fastapi import FastAPI
from .database import Base, async_engine
from .routes import comments

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(title="eConsultation Analysis API (PostgreSQL)")

@app.on_event("startup")
async def on_startup():
    await create_tables()

app.include_router(comments.router, prefix="/api/v1", tags=["Comments"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the eConsultation Analysis API (PostgreSQL)"}