import logging
from consumers.base_consumer import BaseConsumer

logger = logging.getLogger(__name__)

class ChurnConsumer(BaseConsumer):
    """Consumer for bank churn data"""
    
    def __init__(self, kafka_client, data_writer):
        super().__init__(kafka_client, data_writer)
        self.message_count = 0
    
    def process_message(self, message):
        """
        Process churn message - can add validation or transformation
        
        Args:
            message: Churn data message from Kafka
        
        Returns:
            Processed message (already cleaned by producer)
        """
    
        required_fields = ['CreditScore', 'Age', 'Exited']
        missing_fields = [f for f in required_fields if f not in message]
        
        if missing_fields:
            logger.warning(f"Message missing fields: {missing_fields}")
        
            
        self.message_count += 1
        
        
        return message
    
    def consume_for_airflow(self, minio_path='raw/bank_churn_data.json'):
        """
        Consume data and save for Airflow DAG
        
        Args:
            minio_path: Path in MinIO for the data file
        
        Returns:
            dict: Statistics about the consumption
        """
        logger.info("Starting churn data consumption for Airflow...")
        
        stats = self.consume_and_save(minio_path)
        
        logger.info(f"Data saved to MinIO at: {minio_path}")
        logger.info("You can now trigger the Airflow DAG")
        
        return stats