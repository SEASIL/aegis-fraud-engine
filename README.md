# Aegis Fraud Engine

> **An end-to-end Machine Learning system for real-time financial fraud detection** — from raw transaction data to a live, production-ready REST API scoring thousands of transactions per second.

## 👉 [Click here to view the Live Demo on Render!](https://aegis-fraud-backend.onrender.com)

---

<!-- Tech Stack Badges -->
![Python](https://img.shields.io/badge/ML_Pipeline-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![XGBoost](https://img.shields.io/badge/Model-XGBoost_ONNX-189AB4?style=flat-square&logo=xgboost&logoColor=white)
![Java](https://img.shields.io/badge/Java-17-ED8B00?style=flat-square&logo=java&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Backend-Spring_Boot_4-6DB33F?style=flat-square&logo=springboot&logoColor=white)
![MongoDB](https://img.shields.io/badge/Database-MongoDB_Atlas-47A248?style=flat-square&logo=mongodb&logoColor=white)
![Docker](https://img.shields.io/badge/Deployment-Docker_+_Render-2496ED?style=flat-square&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/Data-PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)

---

## 🏦 Real-World Value: How Banks Use This

Every time you tap your card at a store or make an online payment, your bank runs a fraud score on your transaction in **under 50 milliseconds** before approving or declining it. This project implements exactly that system.

### Problems it solves for financial institutions:

| Problem | How Aegis Solves It |
|---|---|
| **Card Testing Attacks** | Detects when a fraudster makes dozens of tiny charges to verify a stolen card number |
| **Account Takeovers** | Flags transactions with amounts far above a card's normal spending pattern (Z-score) |
| **Velocity Fraud** | Catches abnormally high transaction counts within a 24-hour window |
| **Rare Domain Attacks** | Identifies transactions from email domains that are statistically unusual |
| **Real-time Decisioning** | Scores each transaction in milliseconds via a REST API — fast enough to block fraud *before* the payment clears |
| **Audit & Compliance** | Every prediction is logged to MongoDB with full request/response payload for regulatory review |

### How a real bank would integrate this:
```
Customer swipes card
      ↓
Bank's payment processor sends transaction data to Aegis API
      ↓
POST /predict  →  { "fraudProbability": 0.94, "isFraud": true }
      ↓
Bank declines the transaction in real-time
      ↓
Every decision logged to MongoDB for compliance & auditing
```

---

## 🏗 Architecture & Tech Stack

- **Data Layer**: PostgreSQL (stores 590k+ raw transactions and engineered features)
- **Feature Engineering**: Python, Pandas, SQLAlchemy
- **Modeling Pipeline**: Scikit-Learn, XGBoost, ONNXMLTools
- **Backend API**: Java 17, Spring Boot 4, ONNX Runtime (JVM)
- **Frontend UI**: Single Page Application (HTML/CSS/JS) embedded in Spring Boot
- **Inference Logging**: MongoDB Atlas (`inference_logs` collection)
- **Infrastructure**: Docker & Docker Compose, Render PaaS, MongoDB Atlas

### Why ONNX instead of a Python microservice?
Most ML systems deploy models by running a separate Python Flask/FastAPI server alongside the main backend. Aegis takes a different approach — the XGBoost model is **converted to ONNX format and embedded directly into the Java JVM**. This eliminates:
- Network round-trips between services (~10-50ms saved per request)
- Python's GIL bottleneck under concurrent load
- A second container to maintain and monitor

---

## 📁 Project Structure

```
fraud_detection_ml/
├── data/raw/ieee-fraud-detection/   # Kaggle dataset (590k transactions)
├── download_data.py                 # Kaggle API downloader
├── load_data_to_postgres.py         # Loads raw CSV → PostgreSQL
├── feature_engineering.py          # Builds 7 engineered features
├── train_models.py                  # Trains & evaluates 3 ML models
├── convert_to_onnx.py              # Converts XGBoost winner → ONNX
├── retrain.sh                      # Full pipeline automation script
├── metrics.json                    # Latest model evaluation results
├── XGBoost.onnx                    # Serialized production model
├── XGBoost.pkl                     # Scikit-learn pickle backup
├── docker-compose.yml              # Local dev stack (Postgres + Mongo + API)
├── render.yaml                     # Render Blueprint for 1-click cloud deploy
└── fraud-backend/                  # Spring Boot Java API
    ├── src/main/java/com/example/fraudbackend/
    │   ├── FraudBackendApplication.java       # App entry point
    │   ├── FraudDetectionController.java      # REST endpoints
    │   ├── FraudDetectionService.java         # ONNX inference engine
    │   ├── MongoConfig.java                   # MongoDB programmatic config
    │   ├── InferenceLog.java                  # MongoDB document model
    │   ├── InferenceLogRepository.java        # Spring Data repository
    │   ├── FraudPredictionRequest.java        # API request schema
    │   └── FraudPredictionResponse.java       # API response schema
    └── src/main/resources/
        ├── XGBoost.onnx                       # Embedded production model
        ├── metrics.json                       # Model metrics (served via API)
        └── static/                            # Web dashboard (HTML/CSS/JS)
```

---

## 📊 Model Performance

The pipeline evaluates Logistic Regression, Random Forest, and XGBoost baselines on the IEEE-CIS Fraud Detection dataset (590,000+ real bank transactions).

Because the dataset is highly imbalanced (<3.5% fraud), we opted for **explicit class weighting** (`scale_pos_weight` and `class_weight='balanced'`) rather than SMOTE. SMOTE struggles to scale efficiently on datasets with millions of rows and often injects noise into highly skewed financial distributions. We optimized for **AUC-ROC** and **PR-AUC**.

| Model | Precision | Recall | F1-Score | AUC-ROC | PR-AUC |
|-------|-----------|--------|----------|---------|--------|
| **Logistic Regression** | 0.0751 | 0.6046 | 0.1335 | 0.6931 | 0.0836 |
| **Random Forest** | 0.1223 | 0.6301 | 0.2049 | 0.8172 | 0.2121 |
| **XGBoost (Winner)** | **0.1305** | **0.7343** | **0.2216** | **0.8596** | **0.2674** |

> The winning XGBoost model is serialized into `.onnx` format and hot-loaded directly into the Java backend, eliminating the need for a separate Python microservice and reducing inference latency to under 5ms.

---

## 🔬 Engineered Features

The model does not use raw transaction fields. Instead, 7 statistical features are computed from the raw data — the same features a bank's data pipeline would generate automatically:

| Feature | Description | Fraud Signal |
|---|---|---|
| `transactionAmt` | Dollar amount of the transaction | Very high or very low amounts are suspicious |
| `card1` | Anonymized card identifier | Used for grouping card behaviour |
| `pEmaildomainFreq` | How common the buyer's email domain is (0–1) | Rare domains (near 0) are high-risk |
| `card4Freq` | How common the card network is (Visa/MC/etc.) | Rare card networks are suspicious |
| `productCdFreq` | How common the product category is | Unusual product categories flag risk |
| `amtZScoreCard1` | Standard deviations from this card's normal spend | High Z-score = unusually large purchase |
| `cardTxCount24h` | Number of transactions on this card in 24 hours | High count = velocity/card-testing attack |

---

## 🌐 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/predict` | Score a transaction and return fraud probability |
| `GET` | `/api/logs` | Retrieve the 20 most recent inference logs from MongoDB |
| `GET` | `/metrics` | Return model evaluation metrics (Precision, Recall, AUC) |
| `GET` | `/actuator/health` | Health check endpoint |

### Example — Predict
```bash
curl -X POST https://aegis-fraud-backend.onrender.com/predict \
     -H "Content-Type: application/json" \
     -d '{
           "transactionAmt": 4500,
           "card1": 1234,
           "pEmaildomainFreq": 0.0005,
           "card4Freq": 0.04,
           "productCdFreq": 0.03,
           "amtZScoreCard1": 8.7,
           "cardTxCount24h": 31
         }'
```
**Response:**
```json
{
  "fraudProbability": 0.921,
  "isFraud": true
}
```

### MongoDB Audit Log Schema
Every prediction is saved to the `inference_logs` collection:
```json
{
  "_id": "ObjectId(...)",
  "timestamp": "2026-09-12T15:35:22Z",
  "request": {
    "transactionAmt": 4500,
    "card1": 1234,
    "pEmaildomainFreq": 0.0005,
    "amtZScoreCard1": 8.7,
    "cardTxCount24h": 31
  },
  "response": {
    "fraudProbability": 0.921,
    "isFraud": true
  }
}
```

---

## 🚀 Local Setup & Usage

### Prerequisites
- Docker Desktop
- Python 3.9+
- Java 17
- Kaggle API key (`~/.kaggle/kaggle.json`)

### 1. Download the Dataset
```bash
python download_data.py
```
This uses the Kaggle API to automatically download and extract the IEEE-CIS Fraud Detection dataset into `data/raw/`.

### 2. Start the Full Stack
```bash
docker-compose up -d --build
```
Starts PostgreSQL (port 5432), MongoDB (port 27017), and the Spring Boot API (port 8080) in Docker.

### 3. Run the ML Pipeline
```bash
pip install -r requirements.txt
python load_data_to_postgres.py   # Load raw CSV → PostgreSQL
python feature_engineering.py     # Compute 7 features → write back to PostgreSQL
python train_models.py            # Train 3 models, save metrics.json + XGBoost.pkl
python convert_to_onnx.py         # Convert XGBoost → XGBoost.onnx
```

### 4. Open the Dashboard
Visit `http://localhost:8080/` to access the **Interactive Fraud Simulator**.

---

## 🔄 Retraining the Model

A single script automates the full retrain-and-deploy cycle:
```bash
bash retrain.sh
```
This script runs all 4 pipeline stages in sequence:
1. Feature engineering on fresh data
2. Model retraining (all 3 models re-evaluated)
3. Winning model converted to ONNX
4. New `XGBoost.onnx` and `metrics.json` hot-swapped into the backend resources

Then restart the container to load the new model:
```bash
docker restart fraud_backend_api
```

---

## ☁️ Cloud Deployment

A complete guide for deploying this project for free using **Render** and **MongoDB Atlas** is available in [HOSTING_GUIDE.md](HOSTING_GUIDE.md). The project includes a `render.yaml` blueprint for one-click deployment.
