"""
AI Model Training Script for Maternal Health Risk Prediction
This script trains a Random Forest Classifier on the Maternal Health Risk Dataset
and saves the trained model for use in production

"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os



def load_or_create_dataset():
    """
    Load dataset from CSV (NO dummy data fallback)
    """
    csv_path = os.path.join('data', 'Maternal_data.csv')

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Dataset not found at {csv_path}. "
            "Please download the dataset and place it in the data/ folder."
        )

    print(f"Loading dataset from {csv_path}")
    df = pd.read_csv(csv_path)

    # Ensure correct column names (Kaggle dataset compatible)
    df.columns = df.columns.str.strip()

    required_columns = [
        'Age', 'SystolicBP', 'DiastolicBP',
        'BS', 'BodyTemp', 'HeartRate', 'RiskLevel'
    ]

    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


def train_model():
    """
    Train Random Forest Classifier for maternal health risk prediction
    """
    print("="*60)
    print("MATERNAL HEALTH RISK PREDICTION - MODEL TRAINING")
    print("="*60)
    
    # Load dataset
    df = load_or_create_dataset()
    print(f"\nDataset loaded: {len(df)} samples")
    print(f"Features: {list(df.columns[:-1])}")
    print(f"Target: {df.columns[-1]}")
    
    # Display class distribution
    print("\nRisk Level Distribution:")
    print(df['RiskLevel'].value_counts())
    
    # Prepare features and target
    X = df.drop('RiskLevel', axis=1)
    y = df['RiskLevel']
    
    # Encode target labels (low risk=0, mid risk=1, high risk=2)
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print(f"\nEncoded classes: {label_encoder.classes_}")
    
    # Split data (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, 
        test_size=0.2, 
        random_state=42,
        stratify=y_encoded  # Maintain class distribution
    )
    
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Train Random Forest Classifier
    print("\nTraining Random Forest Classifier...")
    rf_model = RandomForestClassifier(
        n_estimators=100,        # Number of trees
        max_depth=10,            # Maximum depth of trees
        min_samples_split=5,     # Minimum samples to split a node
        min_samples_leaf=2,      # Minimum samples in leaf node
        random_state=42,
        class_weight='balanced',  # Handle class imbalance
        n_jobs=-1                # Use all CPU cores
    )
    
    rf_model.fit(X_train, y_train)
    print("✓ Model training completed!")
    
    # Evaluate model
    print("\n" + "="*60)
    print("MODEL EVALUATION")
    print("="*60)
    
    y_pred = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nAccuracy: {accuracy * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(
        y_test, 
        y_pred, 
        target_names=label_encoder.classes_
    ))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'Feature': X.columns,
        'Importance': rf_model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print("\nFeature Importance:")
    print(feature_importance.to_string(index=False))
    
    # Save the trained model and label encoder
    model_dir = 'models'
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'maternal_risk_model.pkl')
    encoder_path = os.path.join(model_dir, 'label_encoder.pkl')
    
    with open(model_path, 'wb') as f:
        pickle.dump(rf_model, f)
    
    with open(encoder_path, 'wb') as f:
        pickle.dump(label_encoder, f)
    
    print(f"\n✓ Model saved to: {model_path}")
    print(f"✓ Label encoder saved to: {encoder_path}")
    
    # Test prediction example
    print("\n" + "="*60)
    print("SAMPLE PREDICTION TEST")
    print("="*60)
    
    sample_input = pd.DataFrame({
        'Age': [30],
        'SystolicBP': [145],
        'DiastolicBP': [95],
        'BS': [12.0],
        'BodyTemp': [98.6],
        'HeartRate': [88]
    })
    
    prediction = rf_model.predict(sample_input)
    risk_level = label_encoder.inverse_transform(prediction)[0]
    
    print("\nSample Input:")
    print(sample_input.to_string(index=False))
    print(f"\nPredicted Risk Level: {risk_level}")
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)


if __name__ == '__main__':
    train_model()