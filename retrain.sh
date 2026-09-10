#!/bin/bash

echo "======================================"
echo "    Fraud Detection ML Pipeline       "
echo "======================================"

# 1. Feature Engineering
echo "[1/4] Running Feature Engineering..."
python feature_engineering.py

# 2. Retraining Models
echo "[2/4] Retraining Models..."
python train_models.py

# 3. Converting best model to ONNX
echo "[3/4] Serializing to ONNX..."
python convert_to_onnx.py

# 4. Swapping the model for the API
echo "[4/4] Deploying new model to Backend..."
cp XGBoost.onnx fraud-backend/src/main/resources/XGBoost.onnx
cp metrics.json fraud-backend/src/main/resources/metrics.json

echo "======================================"
echo "Pipeline Complete! The new model is ready."
echo "If running in production, restart the Spring Boot container:"
echo "docker restart fraud_backend_api"
echo "======================================"
