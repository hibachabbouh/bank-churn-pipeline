import os
from dataclasses import dataclass

@dataclass
class ProducerConfig:
    """Producer configuration"""
    
    # Kafka configuration
    kafka_bootstrap_servers: str
    kafka_topic: str
    
    # Data configuration
    csv_path: str
    
    # Streaming configuration
    batch_size: int = 500
    request_timeout_ms: int = 30000
    acks: str = 'all'
    retries: int = 3
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            kafka_bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            kafka_topic=os.getenv('KAFKA_TOPIC', 'churn-events'),
            csv_path=os.getenv('CSV_PATH', 'data/bank_churn.csv'),
            batch_size=int(os.getenv('BATCH_SIZE', 500)),
            request_timeout_ms=int(os.getenv('REQUEST_TIMEOUT_MS', 30000)),
            acks=os.getenv('KAFKA_ACKS', 'all'),
            retries=int(os.getenv('KAFKA_RETRIES', 3))
        )