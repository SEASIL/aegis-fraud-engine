# Aegis Fraud Engine

> **An end-to-end Machine Learning system for real-time financial fraud detection** — from raw transaction data to a live, production-ready REST API scoring thousands of transactions per second.

## 👉 [Click here to view the Live Demo on Render!](https://aegis-fraud-backend.onrender.com)

---

<!-- Tech Stack Badges -->
![Python](https://img.shields.io/badge/ML_Pipeline-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![XGBoost](https://img.shields.io/badge/Model-XGBoost_ONNX-189AB4?style=flat-square&logo=xgboost&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Backend-Spring_Boot_4-6DB33F?style=flat-square&logo=springboot&logoColor=white)
![MongoDB](https://img.shields.io/badge/Database-MongoDB_Atlas-47A248?style=flat-square&logo=mongodb&logoColor=white)
![Docker](https://img.shields.io/badge/Deployment-Docker_+_Render-2496ED?style=flat-square&logo=docker&logoColor=white)
![Java](https://img.shields.io/badge/Runtime-Java_17-ED8B00?style=flat-square&logo=openjdk&logoColor=white)

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
- **Backend API**: Java 17, Spring Boot, ONNX Runtime (JVM)
- **Frontend UI**: Single Page Application (HTML/CSS/JS) embedded in Spring Boot for live transaction simulation
- **Inference Logging**: MongoDB (asynchronously logs requests/responses)
- **Infrastructure**: Docker & Docker Compose, Render PaaS, MongoDB Atlas

---

## 📊 Model Performance

The pipeline evaluates Logistic Regression, Random Forest, and XGBoost baselines on the IEEE-CIS Fraud Detection dataset (590,000+ real bank transactions).

Because the dataset is highly imbalanced (<3.5% fraud), we opted for **explicit class weighting** (`scale_pos_weight` and `class_weight='balanced'`) rather than SMOTE. SMOTE struggles to scale efficiently on datasets with millions of rows and often injects noise into highly skewed financial distributions. We optimized for **AUC-ROC** and **PR-AUC**.

| Model | Precision | Recall | F1-Score | AUC-ROC | PR-AUC |
|-------|-----------|--------|----------|---------|--------|
| **Logistic Regression** | 0.0751 | 0.6046 | 0.1335 | 0.6931 | 0.0836 |
| **Random Forest** | 0.1223 | 0.6301 | 0.2049 | 0.8172 | 0.2121 |
| **XGBoost (Winner)** | **0.1305** | **0.7343** | **0.2216** | **0.8596** | **0.2674** |

> The winning XGBoost model is serialized into `.onnx` format and **hot-loaded directly into the Java backend**, eliminating the need for a separate Python microservice and reducing inference latency to under 5ms.

---

## 🚀 Local Setup & Usage

### 1. Start the Full Stack
Ensure Docker Desktop is running, then spin up the PostgreSQL, MongoDB, and the Spring Boot API backend:
```bash
docker-compose up -d --build
```
The API and Web Dashboard will instantly be available at `http://localhost:8080/`.

### 2. Data Pipeline & Modeling
Download the IEEE-CIS Fraud Detection dataset from Kaggle and extract `train_transaction.csv` into `data/raw/ieee-fraud-detection/`.

Create a Python virtual environment, install requirements, and run the pipeline:
```bash
pip install -r requirements.txt
python load_data_to_postgres.py
python feature_engineering.py
python train_models.py
python convert_to_onnx.py
```

### 3. Start the Spring Boot API (Manual Alternative)
```bash
cd fraud-backend
./mvnw spring-boot:run
```

### 4. Interactive Web Dashboard
Open your browser to `http://localhost:8080/` to access the **Interactive Fraud Simulator**. Select a real-world fraud scenario (Stolen Card, Account Takeover, Normal Purchase, etc.) and see the model score it in real-time.

### 5. Call the API directly
```bash
curl -X POST http://localhost:8080/predict \
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
*Every prediction is automatically logged into the `inference_logs` collection in MongoDB for audit compliance.*

---

## ☁️ Cloud Deployment

A complete guide for deploying this project for free using **Render** and **MongoDB Atlas** is available in [HOSTING_GUIDE.md](HOSTING_GUIDE.md). The project includes a `render.yaml` blueprint for one-click deployment.

## 🔄 Automation
A `retrain.sh` bash script is included to automatically pull new data, engineer features, retrain the models, convert the winner to ONNX, and hot-swap the weights into the Spring Boot resource folder.
