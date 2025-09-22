from fastapi import FastAPI
from app.database import Base, engine

from app.routes import users, drafts, comments, analysis

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SIH eConsultation Backend")

# Register routes
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(drafts.router, prefix="/drafts", tags=["Drafts"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])
app.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
