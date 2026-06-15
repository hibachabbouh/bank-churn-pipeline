from kafka import KafkaProducer
import json
import logging

logger = logging.getLogger(__name__)

class KafkaProducerClient:
    """Kafka producer wrapper"""
    
    def __init__(self, bootstrap_servers, topic, **kwargs):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None
        self.kwargs = kwargs
        
    def connect(self):
        """Establish connection to Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=self.kwargs.get('request_timeout_ms', 30000),
                acks=self.kwargs.get('acks', 'all'),
                retries=self.kwargs.get('retries', 3)
            )
            logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            return False
    
    def send_message(self, data):
        """Send a single message to Kafka"""
        if not self.producer:
            raise Exception("Producer not connected. Call connect() first.")
        
        future = self.producer.send(self.topic, value=data)
        return future
    
    def send_batch(self, data_batch):
        """Send a batch of messages"""
        futures = []
        for data in data_batch:
            futures.append(self.send_message(data))
        return futures
    
    def flush(self):
        """Flush all pending messages"""
        if self.producer:
            self.producer.flush()
    
    def close(self):
        """Close the producer connection"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")