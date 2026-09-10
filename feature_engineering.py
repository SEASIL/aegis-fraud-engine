import pandas as pd
from sqlalchemy import create_engine
import numpy as np

def perform_feature_engineering():
    db_user = 'fraud_user'
    db_password = 'fraud_password'
    db_host = 'localhost'
    db_port = '5432'
    db_name = 'fraud_db'
    
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

    print("Fetching raw data from PostgreSQL...")
    # Fetch a subset of columns necessary for the engineering to save memory
    # Using card1 as the main card identifier, TransactionAmt for amounts, P_emaildomain for categorical
    query = """
        SELECT "TransactionID", "isFraud", "TransactionDT", "TransactionAmt", 
               "card1", "card4", "P_emaildomain", "ProductCD"
        FROM raw_transactions
    """
    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        print("Failed to fetch data. Have you run load_data_to_postgres.py?")
        print(e)
        return

    print("Starting feature engineering...")
    
    # 1. Frequency encoding for categorical fields
    for col in ['P_emaildomain', 'card4', 'ProductCD']:
        freq = df[col].value_counts(normalize=True)
        df[f'{col}_freq'] = df[col].map(freq)

    # 2. Amount z-scores per card
    # Group by card1 and calculate z-score of TransactionAmt
    card_group = df.groupby('card1')['TransactionAmt']
    df['card1_amt_mean'] = card_group.transform('mean')
    df['card1_amt_std'] = card_group.transform('std')
    df['amt_z_score_card1'] = (df['TransactionAmt'] - df['card1_amt_mean']) / (df['card1_amt_std'] + 1e-5) # add epsilon to avoid div by zero

    # 3. Time-based aggregates
    # TransactionDT is in seconds from a reference point.
    # Convert to hours.
    df['TransactionHour'] = np.floor(df['TransactionDT'] / 3600)
    
    # Since we can't easily do a rolling window over non-datetime index efficiently in raw pandas without sorting,
    # we'll approximate "transactions per card in last 24h" by counting transactions in the same 24h block.
    df['TransactionDay'] = np.floor(df['TransactionDT'] / 86400)
    
    df['card_tx_count_24h'] = df.groupby(['card1', 'TransactionDay'])['TransactionID'].transform('count')

    # Drop intermediate columns if desired, but we'll keep them for simplicity.
    features_to_save = [
        "TransactionID", "isFraud", "TransactionAmt", "card1", 
        "P_emaildomain_freq", "card4_freq", "ProductCD_freq", 
        "amt_z_score_card1", "card_tx_count_24h"
    ]
    
    engineered_df = df[features_to_save].copy()
    
    # Fill NAs
    engineered_df.fillna(0, inplace=True)

    print(f"Engineered dataset size: {engineered_df.shape}")
    
    print("Saving engineered features to PostgreSQL...")
    engineered_df.to_sql('engineered_features', engine, if_exists='replace', index=False)
    print("Feature engineering complete.")

if __name__ == "__main__":
    perform_feature_engineering()
