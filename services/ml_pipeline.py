import logging
from utils.bigquery_client import get_bq_client
from ml.trainers.random_forest_trainer import RandomForestTrainer
from ml.models.model_registry import ModelRegistry
from config.settings import settings

logger = logging.getLogger(__name__)

def train_churn_model(**kwargs):
    """Orchestrate model training"""
    logger.info("Starting ML model training pipeline...")
    
    bq_client = get_bq_client()
    query = f"""
    SELECT * FROM `{settings.PROJECT_ID}.{settings.DATASET}.gold_bank_churn_features`
    """
    df = bq_client.query(query).to_dataframe()
    logger.info(f"Loaded {len(df)} rows for training")
    
    trainer = RandomForestTrainer()
    model, metrics = trainer.train(df)
    
    return {
        'status': 'success',
        'accuracy': metrics['accuracy'],
        'model_version': kwargs.get('execution_date')
    }

def predict_churn(features):
    """Make predictions using latest model"""
    registry = ModelRegistry()
    model = registry.load_latest_model()
    
    if model is None:
        raise Exception("No model available for prediction")
    
    predictions = model.predict(features)
    probabilities = model.predict_proba(features)
    
    return predictions, probabilities