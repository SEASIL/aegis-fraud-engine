# Classical ML System: Fraud Detection Pipeline

An end-to-end Machine Learning pipeline that detects fraudulent transactions. This project demonstrates a complete ML lifecycle: data engineering from a relational database, model training with Python, model serialization via ONNX, and deploying a REST API wrapped in a Java Spring Boot backend that logs to a NoSQL database.

## 🏗 Architecture & Tech Stack

- **Data Layer**: PostgreSQL (stores 590k+ raw transactions and engineered features)
- **Feature Engineering**: Python, Pandas, SQLAlchemy
- **Modeling Pipeline**: Scikit-Learn, XGBoost, ONNXMLTools
- **Backend API**: Java 17, Spring Boot, ONNX Runtime (JVM)
- **Inference Logging**: MongoDB (asynchronously logs requests/responses)
- **Infrastructure**: Docker & Docker Compose, Bash

## 📊 Model Performance

The pipeline evaluates Logistic Regression, Random Forest, and XGBoost baselines on the IEEE-CIS Fraud Detection dataset. 

Because the dataset is highly imbalanced (<3.5% fraud), we opted for **explicit class weighting** (`scale_pos_weight` and `class_weight='balanced'`) rather than SMOTE. SMOTE struggles to scale efficiently on datasets with millions of rows and often injects noise into highly skewed financial distributions. We optimized for **AUC-ROC** and **PR-AUC**.

| Model | Precision | Recall | F1-Score | AUC-ROC | PR-AUC |
|-------|-----------|--------|----------|---------|--------|
| **Logistic Regression** | 0.0751 | 0.6046 | 0.1335 | 0.6931 | 0.0836 |
| **Random Forest** | 0.1223 | 0.6301 | 0.2049 | 0.8172 | 0.2121 |
| **XGBoost (Winner)** | **0.1305** | **0.7343** | **0.2216** | **0.8596** | **0.2674** |

*The winning XGBoost model is serialized into `.onnx` format and hot-loaded directly into the Java backend, avoiding the need for a separate Python microservice.*

## 🚀 Local Setup & Usage

### 1. Start the Databases
Ensure Docker Desktop is running, then spin up the PostgreSQL and MongoDB instances:
```bash
docker-compose up -d
```

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

### 3. Start the Spring Boot API
The Java backend exposes the ONNX model over a REST API.
```bash
cd fraud-backend
./mvnw spring-boot:run
```

### 4. Test the API
Send a test transaction to the `/predict` endpoint:
```bash
curl -X POST http://localhost:8080/predict \
     -H "Content-Type: application/json" \
     -d '{
           "transactionAmt": 150.5, 
           "card1": 10486.0, 
           "pEmaildomainFreq": 0.05, 
           "card4Freq": 0.65, 
           "productCdFreq": 0.75, 
           "amtZScoreCard1": 1.2, 
           "cardTxCount24h": 5.0
         }'
```

**Response:**
```json
{
  "fraudProbability": 0.34381216764450073,
  "isFraud": false
}
```
*Every prediction is automatically logged into the `inference_logs` collection in MongoDB.*

## 🔄 Automation
A `retrain.sh` bash script is included to automatically pull new data, engineer features, retrain the models, convert the winner to ONNX, and hot-swap the weights into the Spring Boot resource folder.
