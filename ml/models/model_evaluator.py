import numpy as np
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
import logging

logger = logging.getLogger(__name__)

class ModelEvaluator:
    """Evaluate model performance"""
    
    def evaluate(self, y_true, y_pred, y_proba=None):
        """Calculate comprehensive metrics"""
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred),
            'recall': recall_score(y_true, y_pred),
            'f1_score': f1_score(y_true, y_pred),
            'classification_report': classification_report(y_true, y_pred),
            'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
        }
        
        if y_proba is not None:
            metrics['roc_auc'] = roc_auc_score(y_true, y_proba)
        
        return metrics
    
    def log_metrics(self, metrics, stage='training'):
        """Log metrics for monitoring"""
        logger.info(f"=== {stage.upper()} METRICS ===")
        logger.info(f"Accuracy: {metrics['accuracy']:.2%}")
        logger.info(f"Precision: {metrics['precision']:.2%}")
        logger.info(f"Recall: {metrics['recall']:.2%}")
        logger.info(f"F1-Score: {metrics['f1_score']:.2%}")
        if 'roc_auc' in metrics:
            logger.info(f"ROC-AUC: {metrics['roc_auc']:.3f}")