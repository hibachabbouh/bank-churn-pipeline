import joblib
import logging
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report

from ml.models.model_registry import ModelRegistry
from ml.models.model_evaluator import ModelEvaluator
from config.settings import settings

logger = logging.getLogger(__name__)

class RandomForestTrainer:
    """Random Forest Model Trainer"""
    
    def __init__(self, model_config=None):
        self.config = model_config or settings.ML_CONFIG['random_forest']
        self.model = None
        self.registry = ModelRegistry()
        self.evaluator = ModelEvaluator()
    
    def prepare_features(self, df):
        """Préparer les features pour l'entraînement"""
        features = self.config['features']
        X = df[features]
        categorical_cols = ['Geography', 'Gender']
        X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
        
        return X
    
    def train(self, df):
    
        logger.info("Starting model training...")
        
        X = self.prepare_features(df)
        y = df['Exited']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=self.config['test_size'],
            random_state=self.config['random_state']
        )
   
        self.model = RandomForestClassifier(
            n_estimators=self.config['n_estimators'],
            max_depth=self.config.get('max_depth'),
            random_state=self.config['random_state']
        )
        self.model.fit(X_train, y_train)
        
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5)
        logger.info(f"Cross-validation scores: {cv_scores}")
        logger.info(f"Mean CV score: {cv_scores.mean():.3f}")
        

        y_pred = self.model.predict(X_test)
        metrics = self.evaluator.evaluate(y_test, y_pred)
        
        logger.info(f"Model accuracy: {metrics['accuracy']:.2%}")
        logger.info(f"Classification Report:\n{metrics['classification_report']}")
        
    
        self.registry.save_model(self.model, metrics)
        
        return self.model, metrics