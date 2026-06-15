
import sys
import os
import logging
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from producers.churn_producer import ChurnProducer
from producers.config.producer_config import ProducerConfig
from utils.kafka_client import KafkaProducerClient
from utils.data_cleaner import DataCleaner


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():

    load_dotenv()
    config = ProducerConfig.from_env()
    logger.info(f"Configuration loaded: topic={config.kafka_topic}, servers={config.kafka_bootstrap_servers}")
    kafka_client = KafkaProducerClient(
        bootstrap_servers=config.kafka_bootstrap_servers,
        topic=config.kafka_topic,
        request_timeout_ms=config.request_timeout_ms,
        acks=config.acks,
        retries=config.retries
    )
    
    data_cleaner = DataCleaner()
    producer = ChurnProducer(
        kafka_client=kafka_client,
        data_cleaner=data_cleaner,
        batch_size=config.batch_size
    )
    try:
        producer.stream_data(config.csv_path)
    except KeyboardInterrupt:
        logger.info("Streaming interrupted by user")
    except Exception as e:
        logger.error(f"Streaming failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()