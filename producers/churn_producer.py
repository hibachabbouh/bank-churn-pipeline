import pandas as pd
from producers.base_producer import BaseProducer

class ChurnProducer(BaseProducer):
    """Producer for bank churn data"""
    
    def load_data(self, csv_path):
        """Load churn data from CSV"""
        logger.info(f"Loading dataset: {csv_path}")
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} rows with {len(df.columns)} columns")
        return df
    
    def prepare_record(self, row):
        """Prepare a churn record for Kafka"""
        return row.to_dict()