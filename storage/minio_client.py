import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class MinioClient:
    """MinIO client wrapper for S3-compatible storage"""
    
    def __init__(self, endpoint, access_key, secret_key, bucket, use_ssl=False):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.use_ssl = use_ssl
        self.client = None
        
    def connect(self):
        """Establish connection to MinIO"""
        try:
            self.client = boto3.client(
                's3',
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                use_ssl=self.use_ssl,
                region_name='us-east-1'
            )
            logger.info(f"Connected to MinIO at {self.endpoint}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MinIO: {e}")
            return False
    
    def ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        if not self.client:
            raise Exception("MinIO client not connected")
        
        try:
            self.client.head_bucket(Bucket=self.bucket)
            logger.info(f"Bucket '{self.bucket}' found")
            return True
        except ClientError:
            logger.info(f"Creating bucket '{self.bucket}'...")
            self.client.create_bucket(Bucket=self.bucket)
            logger.info(f"Bucket '{self.bucket}' created")
            return True
        except Exception as e:
            logger.error(f"Error with bucket: {e}")
            return False
    
    def put_object(self, key, data, content_type='application/json'):
        """Upload object to MinIO"""
        if not self.client:
            raise Exception("MinIO client not connected")
        
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data.encode('utf-8') if isinstance(data, str) else data,
                ContentType=content_type
            )
            logger.info(f"Object saved: {self.bucket}/{key}")
            return True
        except Exception as e:
            logger.error(f"Failed to save object: {e}")
            return False
    
    def get_object(self, key):
        """Download object from MinIO"""
        if not self.client:
            raise Exception("MinIO client not connected")
        
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response['Body'].read().decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to get object: {e}")
            return None