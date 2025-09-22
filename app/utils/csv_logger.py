# app/utils/csv_logger.py
import csv
import os
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CSVLogger:
    def __init__(self, csv_file_path: str = "analysis_results.csv"):
        self.csv_file_path = csv_file_path
        self._ensure_csv_headers()
    
    def _ensure_csv_headers(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'timestamp', 'comment_id', 'draft_id', 'comment_text',
                    'sentiment_label', 'sentiment_score', 'summary', 
                    'keywords', 'wordcloud_path', 'model_version', 'analyzed_at'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            logger.info(f"Created new CSV file: {self.csv_file_path}")
    
    def log_analysis_result(self, comment_id: int, draft_id: str, comment_text: str, analysis_result: Dict[str, Any]):
        """Log a single analysis result to CSV"""
        try:
            # Prepare CSV row data
            csv_row = {
                'timestamp': datetime.now().isoformat(),
                'comment_id': comment_id,
                'draft_id': draft_id,
                'comment_text': str(comment_text)[:500],
                'sentiment_label': analysis_result.get("sentiment_label", ""),
                'sentiment_score': analysis_result.get("sentiment_score", ""),
                'summary': str(analysis_result.get("summary", ""))[:300],
                'keywords': '|'.join(analysis_result.get("keywords", [])),
                'wordcloud_path': analysis_result.get("wordcloud_path", ""),
                'model_version': analysis_result.get("model_version", ""),
                'analyzed_at': analysis_result.get("analyzed_at", "").isoformat() if hasattr(analysis_result.get("analyzed_at"), 'isoformat') else str(analysis_result.get("analyzed_at", ""))
            }
            
            # Write to CSV
            with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = csv_row.keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(csv_row)
            
            logger.info(f"Logged analysis for comment {comment_id} to CSV")
            
        except Exception as e:
            logger.error(f"Failed to log analysis to CSV: {e}")

csv_logger = CSVLogger()