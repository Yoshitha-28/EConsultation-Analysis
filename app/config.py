import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    mongodb_uri: str = os.getenv("MONGODB_URI")
    mongo_db: str = os.getenv("MONGO_DB")
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND")
    s3_endpoint: str = os.getenv("S3_ENDPOINT")
    s3_access_key: str = os.getenv("S3_ACCESS_KEY")
    s3_secret_key: str = os.getenv("S3_SECRET_KEY")
    s3_bucket: str = os.getenv("S3_BUCKET")
    model_version: str = os.getenv("MODEL_VERSION", "default-v1")

settings = Settings()