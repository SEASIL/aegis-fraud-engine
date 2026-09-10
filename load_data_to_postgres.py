import pandas as pd
from sqlalchemy import create_engine
import os

def load_to_postgres():
    # Construct PostgreSQL connection string
    # Using the credentials from docker-compose.yml
    db_user = 'fraud_user'
    db_password = 'fraud_password'
    db_host = 'localhost'
    db_port = '5432'
    db_name = 'fraud_db'
    
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

    data_dir = "data/raw"
    
    # We will load a subset of columns or chunk the loading to handle memory
    transaction_file = os.path.join(data_dir, "ieee-fraud-detection", "train_transaction.csv")
    
    if not os.path.exists(transaction_file):
        print(f"File not found: {transaction_file}")
        print("Please ensure the Kaggle dataset is downloaded and extracted to data/raw/")
        return

    print("Loading train_transaction.csv into PostgreSQL... (this may take a while)")
    
    chunksize = 50000
    for i, chunk in enumerate(pd.read_csv(transaction_file, chunksize=chunksize)):
        chunk.to_sql('raw_transactions', engine, if_exists='replace' if i == 0 else 'append', index=False)
        print(f"Loaded chunk {i+1}")

    print("Data loading complete.")

if __name__ == "__main__":
    load_to_postgres()
