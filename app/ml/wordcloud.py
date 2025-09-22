from wordcloud import WordCloud
import boto3
import io
from ..config import settings

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)

def generate_and_upload_wordcloud(draft_id: str, text: str) -> str:
    try:
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
        buffer = io.BytesIO()
        wordcloud.to_image().save(buffer, format="PNG")
        buffer.seek(0)
        file_key = f"wordclouds/{draft_id}/{__import__('uuid').uuid4()}.png"
        s3_client.put_object(Bucket=settings.S3_BUCKET, Key=file_key, Body=buffer, ContentType="image/png")
        return f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{file_key}"
    except Exception as e:
        print(f"Failed to generate or upload wordcloud: {e}")
        return None