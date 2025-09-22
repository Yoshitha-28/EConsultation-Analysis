# SIH - eConsultation Analysis API
## A FastAPI-based system for analyzing public comments on policy drafts using machine learning. The system processes comments to extract sentiment, generate summaries, identify keywords, and create visualizations.

## Features
1) Sentiment Analysis: Uses DistilBERT model to classify comments as positive, negative, or neutral
2) Text Summarization: Automatically generates concise summaries of comments
3) Keyword Extraction: Identifies important keywords and phrases
4) WordCloud Generation: Creates visual word clouds from comment text
5) RESTful API: FastAPI endpoints for comment submission and analysis retrieval
6) Background Processing: Celery workers for asynchronous analysis
7) PostgreSQL Database: Persistent storage for comments and analysis results
8) Dockerized: Complete containerization with Docker Compose

## Architecture
```bash
SIH/
├── app/
│   ├── ml/              # Machine Learning components
│   │   ├── sentiment.py    # Sentiment analysis
│   │   ├── summarizer.py   # Text summarization
│   │   ├── keywords.py     # Keyword extraction
│   │   └── wordcloud.py    # WordCloud generation
│   ├── routes/          # API routes
│   │   └── comments.py     # Comment endpoints
│   ├── workers/         # Celery tasks
│   │   └── tasks.py        # Background processing tasks
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   └── main.py          # FastAPI application
├── docker-compose.yml   # Multi-container setup
└── requirements.txt     # Python dependencies
```
## Prerequisites
1) Docker
2) Docker Compose
3) Python 3.8+ (for local development)

## Installation & Setup
### Clone the repository

```bash
git clone https://github.com/Yoshitha-28/SIH.git
cd SIH
```
### Create environment file

```bash
cp .env.example .env
```
### Edit .env with your configuration:

```bash
env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=econsult
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# MinIO/S3
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=econsult-artifacts

# Model
MODEL_VERSION=hf-distilbert-v1
```
### Start the application

```bash
docker-compose up --build
```
## Usage
### 1. Submit Comments for Analysis
bash
curl -X POST "http://localhost:8000/api/v1/comments/bulk" \
     -H "Content-Type: application/json" \
     -d '{
         "draft_id": "National_AI_Strategy_2025",
         "comments": [
             "The ethical guidelines section is comprehensive but lacks clear enforcement mechanisms.",
             "I support the initiative to fund public research, but the allocation for startups is insufficient.",
             "There is no mention of data sovereignty or the protection of citizen data from foreign entities."
         ]
     }'
Response:

json
{
    "message": "Successfully received and queued 3 comments for analysis.",
    "draft_id": "National_AI_Strategy_2025",
    "comments_received": 3,
    "task_ids": ["task-uuid-1", "task-uuid-2", "task-uuid-3"]
}
### 2. Retrieve Comment with Analysis
bash
curl "http://localhost:8000/api/v1/comments/1"
Response:

json
{
    "id": 1,
    "draft_id": "National_AI_Strategy_2025",
    "text": "The ethical guidelines section is comprehensive but lacks clear enforcement mechanisms.",
    "user_id": null,
    "status": "processed",
    "submitted_at": "2025-09-22T17:01:37.672874",
    "analysis": {
        "id": 1,
        "comment_id": 1,
        "sentiment_label": "negative",
        "sentiment_score": 0.9985,
        "summary": "The ethical guidelines section is comprehensive but lacks clear enforcement mechanisms.",
        "keywords": ["ethical guidelines", "enforcement mechanisms", "critical oversight"],
        "wordcloud_path": "http://localhost:9000/econsult-artifacts/wordcloud_1.png",
        "model_version": "hf-distilbert-v1",
        "analyzed_at": "2025-09-22T17:01:45.123456"
    }
}
### 3. Get Analysis Results Only
bash
curl "http://localhost:8000/api/v1/comments/1/analysis"
🔧 API Endpoints
Method	Endpoint	Description
POST	/api/v1/comments/bulk	Submit multiple comments for analysis
GET	/api/v1/comments/{id}	Get comment with analysis results
GET	/api/v1/comments/{id}/analysis	Get only analysis results

## ML Models Used
Sentiment Analysis: distilbert-base-uncased-finetuned-sst-2-english

Text Summarization: Custom extractive summarization

Keyword Extraction: TF-IDF based keyword extraction

WordCloud: Python wordcloud library

## Docker Services
The application consists of 5 main services:

api: FastAPI application (port 8000)

worker: Celery worker for background processing

postgres: PostgreSQL database (port 5432)

redis: Message broker for Celery (port 6379)

minio: Object storage for wordclouds (port 9000)

## Project Structure Details
Core Components
app/main.py: FastAPI application setup and routing

app/models.py: Database models (Comment, CommentAnalysis)

app/schemas.py: Pydantic schemas for request/response validation

app/database.py: Database connection and session management

Machine Learning Pipeline
app/ml/sentiment.py: Sentiment analysis with DistilBERT

app/ml/summarizer.py: Text summarization

app/ml/keywords.py: Keyword extraction

app/ml/wordcloud.py: WordCloud generation and storage

app/ml/pipeline.py: Orchestrates the complete analysis pipeline

Background Processing
app/workers/tasks.py: Celery tasks for async processing

app/celery_app.py: Celery application configuration

## Monitoring
Check service status:

bash
docker-compose ps
View API logs:

bash
docker-compose logs api
View worker logs:

bash
docker-compose logs worker
## Troubleshooting
Common Issues
WordCloud bucket errors: Ensure MinIO is running and bucket exists

Database connection issues: Check PostgreSQL credentials in .env

Celery task failures: Verify Redis connection and worker logs

Health Checks
API: http://localhost:8000/health

MinIO: http://localhost:9000/minio/health/live

🤝 Contributing
Fork the repository

Create a feature branch

Commit your changes

Push to the branch

Open a Pull Request

📄 License
This project is licensed under the MIT License.

🙏 Acknowledgments
FastAPI for the excellent web framework

Hugging Face for pre-trained models

Celery for background task processing

SQLAlchemy for database ORM

Note: This is a prototype system developed for the Smart India Hackathon. For production use, additional security measures, error handling, and scalability improvements would be needed.
