import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score
import json
import joblib
import onnxmltools
from onnxmltools.convert.common.data_types import FloatTensorType

def train_and_evaluate():
    # 1. Connect to PostgreSQL and load data
    print("Loading engineered features from PostgreSQL...")
    engine = create_engine('postgresql://fraud_user:fraud_password@localhost:5432/fraud_db')
    
    # We will sample 100k rows if the dataset is too huge to speed up local training, 
    # but let's try loading the whole thing first. If memory is an issue, we can add LIMIT.
    df = pd.read_sql("SELECT * FROM engineered_features", engine)
    
    print(f"Dataset shape: {df.shape}")
    
    # Define features and target
    X = df.drop(columns=['TransactionID', 'isFraud'])
    y = df['isFraud']

    # 2. Train-test split (stratified due to class imbalance)
    print("Splitting data into train and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    # 3. Model Setup & Class Imbalance Handling
    # We chose class weights over SMOTE because SMOTE scales poorly to datasets with millions of rows
    # and often generates noisy synthetic samples in highly skewed transaction distributions.
    # We calculate the ratio of negative to positive samples for XGBoost.
    neg_to_pos_ratio = (len(y_train) - y_train.sum()) / y_train.sum()

    models = {
        'Logistic_Regression': LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42),
        'Random_Forest': RandomForestClassifier(n_estimators=100, class_weight='balanced', max_depth=10, random_state=42, n_jobs=-1),
        'XGBoost': XGBClassifier(scale_pos_weight=neg_to_pos_ratio, max_depth=6, random_state=42, n_jobs=-1)
    }

    results = {}
    best_auc = 0
    best_model_name = ""
    best_model = None

    # 4. Train and Evaluate Models
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        
        print(f"Evaluating {name}...")
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        auc_roc = roc_auc_score(y_test, y_prob)
        pr_auc = average_precision_score(y_test, y_prob)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        results[name] = {
            'Precision': round(precision, 4),
            'Recall': round(recall, 4),
            'F1_Score': round(f1, 4),
            'AUC_ROC': round(auc_roc, 4),
            'PR_AUC': round(pr_auc, 4)
        }

        print(f"{name} Metrics: {results[name]}")

        if auc_roc > best_auc:
            best_auc = auc_roc
            best_model_name = name
            best_model = model

    print(f"\nBest Model: {best_model_name} (AUC-ROC: {best_auc})")

    # Save metrics to JSON
    with open('metrics.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("Saved metrics to metrics.json")

    # 5. Export Best Model (.pkl and ONNX)
    print(f"Exporting {best_model_name}...")
    joblib.dump(best_model, f'{best_model_name}.pkl')
    print(f"Saved {best_model_name}.pkl")

    if best_model_name == 'XGBoost':
        # Convert XGBoost to ONNX
        initial_types = [('float_input', FloatTensorType([None, X_train.shape[1]]))]
        onnx_model = onnxmltools.convert_xgboost(best_model, initial_types=initial_types)
        onnxmltools.utils.save_model(onnx_model, f"{best_model_name}.onnx")
        print(f"Saved {best_model_name}.onnx")
    else:
        print("Note: ONNX conversion currently scripted for XGBoost. If RF won, you'll need skl2onnx.")

if __name__ == "__main__":
    train_and_evaluate()
