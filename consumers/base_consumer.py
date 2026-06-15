import time
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseConsumer(ABC):
    """Abstract base class for data consumers"""
    
    def __init__(self, kafka_client, data_writer):
        self.kafka_client = kafka_client
        self.data_writer = data_writer
        
    @abstractmethod
    def process_message(self, message):
        """
        Process individual message (can be overridden for custom logic)
        
        Args:
            message: Raw message from Kafka
        
        Returns:
            Processed message (or None to skip)
        """
        return message
    
    def consume_and_save(self, minio_path, batch_report_callback=None):
        """
        Main consumer logic: consume from Kafka and save to MinIO
        
        Args:
            minio_path: Path in MinIO to save data
            batch_report_callback: Optional callback for batch reporting
        
        Returns:
            dict: Statistics about consumption
        """
        start_time = time.time()
        
    
        if not self.kafka_client.connect():
            raise Exception("Failed to connect to Kafka")
        
       
        messages_count = 0
        
        def progress_callback(count):
            nonlocal messages_count
            messages_count = count
            elapsed = time.time() - start_time
            logger.info(f"   {count} messages received | {elapsed:.1f}s")
            if batch_report_callback:
                batch_report_callback(count, elapsed)
        
    
        raw_messages = self.kafka_client.consume_messages(progress_callback)
        

        processed_messages = []
        for msg in raw_messages:
            processed = self.process_message(msg)
            if processed is not None:
                processed_messages.append(processed)
        
       
        self.kafka_client.close()
        
        
        if processed_messages:
            self.data_writer.save_to_minio(processed_messages, minio_path)
        
     
        elapsed_time = time.time() - start_time
        
        stats = {
            'total_received': len(raw_messages),
            'total_saved': len(processed_messages),
            'elapsed_time': elapsed_time,
            'messages_per_second': len(raw_messages) / elapsed_time if elapsed_time > 0 else 0
        }
        
        logger.info(f"Consumption completed: {stats}")
        return stats