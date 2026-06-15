import pandas as pd

class DataCleaner:
    """Handle data cleaning and preprocessing"""
    DROP_COLUMNS = ['RowNumber', 'CustomerId', 'Surname']
    
    @classmethod
    def clean_churn_data(cls, df):
        """
        Clean churn data by removing unnecessary columns
        
        Args:
            df: pandas DataFrame with raw churn data
            
        Returns:
            Cleaned pandas DataFrame
        """
        columns_to_drop = [col for col in cls.DROP_COLUMNS if col in df.columns]
        
        if columns_to_drop:
            df_cleaned = df.drop(columns=columns_to_drop, errors='ignore')
            print(f"Dropped columns: {columns_to_drop}")
        else:
            df_cleaned = df.copy()
            
        print(f"Data cleaned: {len(df_cleaned.columns)} columns remaining")
        return df_cleaned
    
    @classmethod
    def validate_data(cls, df):
        """
        Validate data quality
        
        Args:
            df: pandas DataFrame to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        
        required_cols = ['CreditScore', 'Age', 'Exited']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"Warning: Missing required columns: {missing_cols}")
            return False
            
        return True