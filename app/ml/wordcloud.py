# app/ml/wordcloud.py
from wordcloud import WordCloud
import boto3
import io
from ..config import settings

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)

def ensure_bucket_exists():
    """Create the bucket if it doesn't exist"""
    try:
        s3_client.head_bucket(Bucket=settings.S3_BUCKET)
        print(f"Bucket {settings.S3_BUCKET} already exists")
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            # Bucket doesn't exist, create it
            try:
                s3_client.create_bucket(Bucket=settings.S3_BUCKET)
                print(f"Bucket {settings.S3_BUCKET} created successfully")
            except Exception as create_error:
                print(f"Failed to create bucket: {create_error}")
        else:
            print(f"Error checking bucket: {e}")

# Check and create bucket on module import
ensure_bucket_exists()

def generate_and_upload_wordcloud(draft_id: str, text: str) -> str:
    try:
        # Generate wordcloud
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
        buffer = io.BytesIO()
        wordcloud.to_image().save(buffer, format="PNG")
        buffer.seek(0)
        
        # Upload to S3
        file_key = f"wordclouds/{draft_id}/{__import__('uuid').uuid4()}.png"
        s3_client.put_object(
            Bucket=settings.S3_BUCKET, 
            Key=file_key, 
            Body=buffer, 
            ContentType="image/png"
        )
        
        return f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{file_key}"
    except Exception as e:
        print(f"Failed to generate or upload wordcloud: {e}")
        return ""