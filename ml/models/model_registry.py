import joblib
import io
from datetime import datetime
from typing import Dict, Any
import logging

from utils.minio_client import get_minio_client
from config.settings import settings

logger = logging.getLogger(__name__)

class ModelRegistry:
    """Manage model versioning and storage"""
    
    def __init__(self):
        self.minio_client = get_minio_client()
        self.bucket = settings.MINIO_BUCKET
        self.model_path = "models/"
    
    def save_model(self, model, metrics: Dict[str, Any], version: str = None):
        """Save model to MinIO with metadata"""
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        model_name = f"bank_churn_rf_{version}.pkl"
        model_bytes = io.BytesIO()
        joblib.dump(model, model_bytes)
        model_bytes.seek(0)
        
        self.minio_client.put_object(
            self.bucket,
            f"{self.model_path}{model_name}",
            model_bytes,
            length=model_bytes.getbuffer().nbytes
        )
        
        metadata = {
            'version': version,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'model_type': 'RandomForestClassifier'
        }
        
        import json
        metadata_bytes = io.BytesIO(json.dumps(metadata).encode())
        self.minio_client.put_object(
            self.bucket,
            f"{self.model_path}metadata_{version}.json",
            metadata_bytes,
            length=metadata_bytes.getbuffer().nbytes
        )
        
        self.minio_client.copy_object(
            self.bucket,
            f"{self.model_path}bank_churn_rf_latest.pkl",
            f"{self.bucket}/{self.model_path}{model_name}"
        )
        
        logger.info(f"Model saved: {model_name} with accuracy {metrics['accuracy']:.2%}")
        return model_name
    
    def load_latest_model(self):
        """Load the latest model from MinIO"""
        try:
            response = self.minio_client.get_object(
                self.bucket,
                f"{self.model_path}bank_churn_rf_latest.pkl"
            )
            model = joblib.load(response)
            logger.info("Latest model loaded successfully")
            return model
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return None