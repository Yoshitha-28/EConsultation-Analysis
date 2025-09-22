from fastapi import FastAPI
from .routes import comments

app = FastAPI(
    title="eConsultation Analysis API",
    description="An AI model to predict sentiments and analyze suggestions from stakeholders.",
    version="1.0.0"
)

app.include_router(comments.router, prefix="/api/v1", tags=["Comments"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the eConsultation Analysis API"}