
from services.data_pipeline import load_bronze_layer, transform_silver_layer, transform_gold_layer
from services.ml_pipeline import train_churn_model  


load_bronze = PythonOperator(task_id='load_bronze_layer', python_callable=load_bronze_layer)
transform_silver = PythonOperator(task_id='transform_silver_layer', python_callable=transform_silver_layer)
transform_gold = PythonOperator(task_id='transform_gold_layer', python_callable=transform_gold_layer)
train_model = PythonOperator(task_id='train_ml_model', python_callable=train_churn_model)

load_bronze >> transform_silver >> transform_gold >> train_model