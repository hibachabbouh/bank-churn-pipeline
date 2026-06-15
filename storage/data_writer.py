import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataWriter:
    """Handle data writing to MinIO with formatting"""
    
    def __init__(self, minio_client):
        self.minio_client = minio_client
    
    def format_as_json_lines(self, messages):
        """Format messages as JSON lines (one JSON per line)"""
        return "\n".join([json.dumps(msg) for msg in messages])
    
    def save_to_minio(self, messages, file_path, bucket=None):
        """
        Save messages to MinIO as JSON lines
        
        Args:
            messages: List of message dictionaries
            file_path: Path in MinIO bucket (e.g., 'raw/data.json')
            bucket: Optional override for bucket name
        
        Returns:
            bool: True if successful
        """
        if not messages:
            logger.warning("No messages to save")
            return False
        
        json_data = self.format_as_json_lines(messages)
        
        target_bucket = bucket or self.minio_client.bucket
        success = self.minio_client.put_object(target_bucket, file_path, json_data)
        
        if success:
            logger.info(f"Saved {len(messages)} messages to {target_bucket}/{file_path}")
        
        return success
    
    def save_with_timestamp(self, messages, base_path, prefix='raw'):
        """
        Save messages with timestamp in filename
        
        Args:
            messages: List of message dictionaries
            base_path: Base path in MinIO (e.g., 'churn-data')
            prefix: Prefix for the file (e.g., 'raw', 'processed')
        
        Returns:
            str: Full path where data was saved
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"{prefix}/bank_churn_data_{timestamp}.json"
        
        if base_path:
            file_path = f"{base_path}/{file_path}"
        
        self.save_to_minio(messages, file_path)
        return file_path