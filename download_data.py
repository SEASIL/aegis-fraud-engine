import os
from kaggle.api.kaggle_api_extended import KaggleApi
import zipfile

def download_data():
    data_dir = "data/raw"
    os.makedirs(data_dir, exist_ok=True)
    
    print("Authenticating with Kaggle API...")
    try:
        api = KaggleApi()
        api.authenticate()
    except Exception as e:
        print(f"Failed to authenticate with Kaggle API: {e}")
        print("Please ensure your kaggle.json is present in ~/.kaggle/")
        return

    competition_name = "ieee-fraud-detection"
    print(f"Downloading dataset {competition_name}...")
    api.competition_download_files(competition_name, path=data_dir)
    
    zip_path = os.path.join(data_dir, f"{competition_name}.zip")
    if os.path.exists(zip_path):
        print("Extracting files...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        print("Extraction complete.")
        os.remove(zip_path)
    else:
        print("Download failed or files not found.")

if __name__ == "__main__":
    download_data()
