import pandas as pd
import time
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseProducer(ABC):
    """Abstract base class for data producers"""
    
    def __init__(self, kafka_client, data_cleaner, batch_size=500):
        self.kafka_client = kafka_client
        self.data_cleaner = data_cleaner
        self.batch_size = batch_size
        
    @abstractmethod
    def load_data(self, source_path):
        """Load data from source"""
        pass
    
    @abstractmethod
    def prepare_record(self, row):
        """Prepare a single record for sending"""
        pass
    
    def stream_data(self, source_path):
        """Main streaming logic"""
        # Load and clean data
        df = self.load_data(source_path)
        df = self.data_cleaner.clean_churn_data(df)
        
        if not self.data_cleaner.validate_data(df):
            logger.warning("Data validation failed, continuing anyway...")
        
        # Connect to Kafka
        if not self.kafka_client.connect():
            raise Exception("Failed to connect to Kafka")
        
        # Stream data
        total_rows = len(df)
        logger.info(f"Starting streaming of {total_rows} rows...")
        start_time = time.time()
        
        for i in range(0, total_rows, self.batch_size):
            batch = df.iloc[i:i+self.batch_size]
            
            # Prepare batch records
            records = []
            for _, row in batch.iterrows():
                record = self.prepare_record(row)
                records.append(record)
            
            # Send batch
            self.kafka_client.send_batch(records)
            self.kafka_client.flush()
            
            # Progress log
            progress = min(i + self.batch_size, total_rows) / total_rows * 100
            elapsed = time.time() - start_time
            logger.info(f"Progress: {progress:.1f}% ({min(i+self.batch_size, total_rows)}/{total_rows}) | {elapsed:.1f}s")
        
        # Cleanup
        self.kafka_client.close()
        logger.info(f"Streaming completed in {time.time() - start_time:.1f} seconds!")