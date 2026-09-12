"""
Aegis Fraud Engine - Real Dataset Validation
=============================================
Pulls actual rows from the IEEE-CIS dataset (train_transaction.csv),
applies the same feature engineering used during training,
then sends them to the live API and checks predictions.
"""
import pandas as pd
import numpy as np
import urllib.request
import json

API_URL = "https://aegis-fraud-backend.onrender.com/predict"
DATA_PATH = r"data\raw\ieee-fraud-detection\train_transaction.csv"

print("Loading dataset (sampling 50,000 rows for speed)...")
df = pd.read_csv(DATA_PATH, usecols=[
    "TransactionID", "isFraud", "TransactionDT", "TransactionAmt",
    "card1", "card4", "P_emaildomain", "ProductCD"
], nrows=100000)

print(f"Loaded {len(df)} rows. Running feature engineering...")

# --- Same feature engineering as feature_engineering.py ---
for col in ['P_emaildomain', 'card4', 'ProductCD']:
    freq = df[col].value_counts(normalize=True)
    df[f'{col}_freq'] = df[col].map(freq)

card_group = df.groupby('card1')['TransactionAmt']
df['card1_amt_mean'] = card_group.transform('mean')
df['card1_amt_std'] = card_group.transform('std')
df['amt_z_score_card1'] = (df['TransactionAmt'] - df['card1_amt_mean']) / (df['card1_amt_std'] + 1e-5)
df['TransactionDay'] = np.floor(df['TransactionDT'] / 86400)
df['card_tx_count_24h'] = df.groupby(['card1', 'TransactionDay'])['TransactionID'].transform('count')
df.fillna(0, inplace=True)

# --- Pick 5 real FRAUD and 5 real LEGITIMATE rows ---
fraud_rows = df[df['isFraud'] == 1].sample(5, random_state=42)
legit_rows = df[df['isFraud'] == 0].sample(5, random_state=42)
test_df = pd.concat([legit_rows, fraud_rows]).reset_index(drop=True)

# --- Call the live API ---
def call_api(row):
    payload = {
        "transactionAmt": float(row['TransactionAmt']),
        "card1": float(row['card1']),
        "pEmaildomainFreq": float(row['P_emaildomain_freq']),
        "card4Freq": float(row['card4_freq']),
        "productCdFreq": float(row['ProductCD_freq']),
        "amtZScoreCard1": float(row['amt_z_score_card1']),
        "cardTxCount24h": float(row['card_tx_count_24h'])
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data,
                                  headers={"Content-Type": "application/json"},
                                  method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("\n" + "="*70)
print("   AEGIS FRAUD ENGINE - REAL DATASET VALIDATION")
print("="*70)
print(f"{'#':<4} {'TransactionID':<15} {'Amt($)':<10} {'Actual':<14} {'Predicted':<14} {'Prob%':<8} {'OK?'}")
print("-"*70)

passed = 0
for i, (_, row) in enumerate(test_df.iterrows(), 1):
    try:
        result = call_api(row)
        prob = result.get("fraudProbability", 0)
        is_fraud_pred = result.get("isFraud", False)
        actual_fraud = bool(row['isFraud'])

        actual_label = "FRAUD" if actual_fraud else "LEGIT"
        pred_label   = "FRAUD" if is_fraud_pred else "LEGIT"
        match = "PASS" if actual_fraud == is_fraud_pred else "FAIL"
        if match == "PASS":
            passed += 1

        print(f"{i:<4} {int(row['TransactionID']):<15} ${row['TransactionAmt']:<9.2f} {actual_label:<14} {pred_label:<14} {prob*100:<8.1f} {match}")
    except Exception as e:
        print(f"{i:<4} {int(row['TransactionID']):<15} ERROR: {e}")

print("="*70)
print(f"   SCORE: {passed}/10 correct")
if passed >= 8:
    print("   Model is working correctly on real data!")
else:
    print("   Some mismatches found (expected at 73% recall threshold).")
print("="*70)
