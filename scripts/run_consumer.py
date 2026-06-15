
import sys
import os
import logging
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from consumers.churn_consumer import ChurnConsumer
from consumers.config.consumer_config import ConsumerConfig
from utils.kafka_client import KafkaConsumerClient
from storage.minio_client import MinioClient
from storage.data_writer import DataWriter


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    
    load_dotenv()
    

    config = ConsumerConfig.from_env()
    logger.info(f"Configuration loaded: topic={config.kafka_topic}, bucket={config.minio_bucket}")
    

    minio_client = MinioClient(
        endpoint=config.minio_endpoint,
        access_key=config.minio_access_key,
        secret_key=config.minio_secret_key,
        bucket=config.minio_bucket,
        use_ssl=config.use_ssl
    )
    
  
    if not minio_client.connect():
        logger.error("Failed to connect to MinIO")
        sys.exit(1)
    
   
    if not minio_client.ensure_bucket_exists():
        logger.error("Failed to ensure bucket exists")
        sys.exit(1)
    
   
    data_writer = DataWriter(minio_client)
    
   
    kafka_client = KafkaConsumerClient(
        topic=config.kafka_topic,
        bootstrap_servers=config.kafka_bootstrap_servers,
        group_id=config.kafka_group_id,
        auto_offset_reset=config.auto_offset_reset
    )
    

    consumer = ChurnConsumer(kafka_client, data_writer)
    

    try:
        stats = consumer.consume_for_airflow(minio_path=config.minio_file_path)
        
        if stats['total_received'] == 0:
            logger.warning("No messages received. Check that the producer ran successfully.")
            sys.exit(0)
        
        logger.info(f"Success! {stats['total_saved']} messages saved to MinIO")
        logger.info(f"   Time: {stats['elapsed_time']:.1f}s")
        logger.info(f"   Rate: {stats['messages_per_second']:.1f} msg/s")
        
    except KeyboardInterrupt:
        logger.info("Consumption interrupted by user")
    except Exception as e:
        logger.error(f"Consumption failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()