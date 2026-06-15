import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
from google.oauth2 import service_account
import joblib
import os
from minio import Minio
import io

# Page configuration
st.set_page_config(
    page_title="Bank Churn Analytics Dashboard",
    
    layout="wide"
)

# Title
st.title("Bank Customer Churn Analytics & Prediction")
st.markdown("---")

# ==============================================================================
# CONNECTIONS
# ==============================================================================
@st.cache_resource
def get_bq_client():
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    return bigquery.Client(project=os.getenv('GCP_PROJECT_ID'), credentials=credentials)

@st.cache_resource
def get_minio_client():
    return Minio(
        os.getenv('MINIO_ENDPOINT'),
        access_key=os.getenv('MINIO_ACCESS_KEY'),
        secret_key=os.getenv('MINIO_SECRET_KEY'),
        secure=False
    )

@st.cache_resource
def load_model():
    """Load ML model from MinIO"""
    minio_client = get_minio_client()
    bucket = os.getenv('MINIO_BUCKET', 'spotify-data')
    
    try:
        response = minio_client.get_object(bucket, "models/bank_churn_rf_final.pkl")
        model_data = response.read()
        model = joblib.load(io.BytesIO(model_data))
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# ==============================================================================
# DATA LOADING
# ==============================================================================
st.sidebar.header("Navigation")
page = st.sidebar.selectbox(
    "Choose a page",
    ["Analytics Dashboard", "Churn Prediction", "Model Performance"]
)

# Load Gold data (cleanest)
@st.cache_data
def load_gold_data():
    try:
        bq_client = get_bq_client()
        project_id = os.getenv('GCP_PROJECT_ID')
        dataset = os.getenv('BQ_DATASET')
        
        query = f"SELECT * FROM `{project_id}.{dataset}.gold_bank_churn_features`"
        df = bq_client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"BigQuery connection error: {e}")
        return None

df = load_gold_data()

# ==============================================================================
# PAGE 1: ANALYTICS DASHBOARD
# ==============================================================================
if page == "Analytics Dashboard":
    st.header("Exploratory Data Analysis")
    
    if df is not None:
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        total_customers = len(df)
        churn_rate = df['exited'].mean() * 100
        avg_age = df['age'].mean()
        avg_balance = df['balance'].mean()
        
        col1.metric("Total Customers", f"{total_customers:,}")
        col2.metric("Churn Rate", f"{churn_rate:.1f}%")
        col3.metric("Average Age", f"{avg_age:.1f} years")
        col4.metric("Average Balance", f"${avg_balance:,.0f}")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Geographic Distribution")
            geo_dist = df['Geography'].value_counts().reset_index()
            geo_dist.columns = ['Country', 'Number of Customers']
            fig_geo = px.pie(geo_dist, values='Number of Customers', names='Country', hole=0.4)
            st.plotly_chart(fig_geo, use_container_width=True)
        
        with col2:
            st.subheader("Gender Distribution")
            gender_dist = df['Gender'].value_counts().reset_index()
            gender_dist.columns = ['Gender', 'Number of Customers']
            fig_gender = px.pie(gender_dist, values='Number of Customers', names='Gender', hole=0.4)
            st.plotly_chart(fig_gender, use_container_width=True)
        
        st.markdown("---")
        
        # Churn by category
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Churn Rate by Country")
            churn_by_geo = df.groupby('Geography')['exited'].mean().reset_index() * 100
            churn_by_geo.columns = ['Country', 'Churn Rate (%)']
            fig_churn_geo = px.bar(churn_by_geo, x='Country', y='Churn Rate (%)', 
                                   color='Churn Rate (%)', color_continuous_scale='Reds')
            st.plotly_chart(fig_churn_geo, use_container_width=True)
        
        with col2:
            st.subheader("Churn Rate by Gender")
            churn_by_gender = df.groupby('Gender')['exited'].mean().reset_index() * 100
            churn_by_gender.columns = ['Gender', 'Churn Rate (%)']
            fig_churn_gender = px.bar(churn_by_gender, x='Gender', y='Churn Rate (%)',
                                      color='Churn Rate (%)', color_continuous_scale='OrRd')
            st.plotly_chart(fig_churn_gender, use_container_width=True)
        
        st.markdown("---")
        
        # Age and balance distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Age Distribution")
            fig_age = px.histogram(df, x='age', nbins=30, title="Customer Age Distribution",
                                   labels={'age': 'Age'})
            st.plotly_chart(fig_age, use_container_width=True)
        
        with col2:
            st.subheader("Balance Distribution")
            fig_balance = px.histogram(df, x='balance', nbins=30, title="Balance Distribution",
                                       labels={'balance': 'Balance ($)'})
            st.plotly_chart(fig_balance, use_container_width=True)
        
        st.markdown("---")
        
        # Raw data
        st.subheader("Data Preview")
        st.dataframe(df.head(10))
        
    else:
        st.warning("No data available. Check that the Airflow pipeline has run successfully.")

# ==============================================================================
# PAGE 2: CHURN PREDICTION
# ==============================================================================
elif page == "Churn Prediction":
    st.header("Customer Churn Prediction")
    st.markdown("Enter customer information to predict whether they will leave the bank.")
    
    model = load_model()
    
    if model is not None:
        # Input form
        col1, col2 = st.columns(2)
        
        with col1:
            credit_score = st.number_input("Credit Score", min_value=300, max_value=900, value=650)
            geography = st.selectbox("Country", ["France", "Germany", "Spain"])
            gender = st.selectbox("Gender", ["Male", "Female"])
            age = st.number_input("Age", min_value=18, max_value=100, value=35)
            tenure = st.number_input("Tenure (years)", min_value=0, max_value=20, value=5)
        
        with col2:
            balance = st.number_input("Balance ($)", min_value=0, value=50000)
            num_products = st.number_input("Number of Products", min_value=1, max_value=4, value=2)
            has_cr_card = st.selectbox("Credit Card", ["Yes", "No"])
            is_active = st.selectbox("Active Member", ["Yes", "No"])
            estimated_salary = st.number_input("Estimated Salary ($)", min_value=0, value=50000)
        
        # Prediction button
        if st.button(" Predict Churn", type="primary"):
            # Data preparation
            input_data = pd.DataFrame({
                'credit_score': [credit_score],
                'Geography': [geography],
                'Gender': [gender],
                'age': [age],
                'tenure': [tenure],
                'balance': [balance],
                'num_of_products': [num_products],
                'has_cr_card': [1 if has_cr_card == "Yes" else 0],
                'is_active_member': [1 if is_active == "Yes" else 0],
                'estimated_salary': [estimated_salary]
            })
            
            # Prediction
            prediction = model.predict(input_data)[0]
            prediction_proba = model.predict_proba(input_data)[0]
            
            # Display result
            st.markdown("---")
            if prediction == 1:
                st.error("**HIGH CHURN RISK**")
                st.write(f"Departure probability: **{prediction_proba[1]*100:.1f}%**")
            else:
                st.success("**LOYAL CUSTOMER**")
                st.write(f"Departure probability: **{prediction_proba[1]*100:.1f}%**")
            
            # Probability visualization
            fig = go.Figure(go.Pie(
                labels=["Stays", "Leaves"],
                values=[prediction_proba[0]*100, prediction_proba[1]*100],
                hole=0.4,
                marker_colors=['#10B981', '#EF4444']
            ))
            fig.update_layout(title="Churn Probability")
            st.plotly_chart(fig, use_container_width=True)
            
    else:
        st.warning("Model not available. Make sure the ML pipeline has run successfully.")

# ==============================================================================
# PAGE 3: MODEL PERFORMANCE
# ==============================================================================
elif page == "Model Performance":
    st.header("Machine Learning Model Performance")
    
    try:
        bq_client = get_bq_client()
        project_id = os.getenv('GCP_PROJECT_ID')
        dataset = os.getenv('BQ_DATASET')
        
        # Load metrics
        query = f"SELECT * FROM `{project_id}.{dataset}.model_metrics` ORDER BY training_date DESC LIMIT 1"
        metrics_df = bq_client.query(query).to_dataframe()
        
        if not metrics_df.empty:
            col1, col2, col3 = st.columns(3)
            
            col1.metric("Model Name", metrics_df['model_name'].iloc[0])
            col2.metric("Accuracy", f"{metrics_df['accuracy'].iloc[0]*100:.2f}%")
            col3.metric("Training Date", metrics_df['training_date'].iloc[0][:10])
            
            st.markdown("---")
            st.subheader("Performance History")
            
            # Full history
            query_hist = f"SELECT * FROM `{project_id}.{dataset}.model_metrics` ORDER BY training_date"
            hist_df = bq_client.query(query_hist).to_dataframe()
            
            if not hist_df.empty:
                fig = px.line(hist_df, x='training_date', y='accuracy', 
                              title="Model Accuracy Evolution",
                              labels={'accuracy': 'Accuracy', 'training_date': 'Date'})
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(hist_df)
        else:
            st.warning("No metrics available. Run the ML pipeline first.")
            
    except Exception as e:
        st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ By Hiba Chabbouh")