"""Download larger datasets for all three diseases."""
import requests
import os
import io
import zipfile
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(SCRIPT_DIR, 'datasets')
os.makedirs(DATASETS_DIR, exist_ok=True)

def download_file(url, filename, timeout=60):
    path = os.path.join(DATASETS_DIR, filename)
    print(f"Downloading {filename} from {url}...")
    r = requests.get(url, allow_redirects=True, timeout=timeout)
    with open(path, 'wb') as f:
        f.write(r.content)
    print(f"  Saved {len(r.content)} bytes to {path}")
    return path

def main():
    results = {}

    # --- DIABETES: Mendeley Bangladesh Dataset ---
    # DOI: 10.17632/rn9m3zb7nt.1
    print("\n=== DIABETES ===")
    diabetes_url = "https://data.mendeley.com/public-files/datasets/rn9m3zb7nt/files/8ff1a061-3c20-43e4-8d79-1e1acd29ae05/file_downloaded"
    try:
        path = download_file(diabetes_url, "diabetes_mendeley.csv", timeout=60)
        df = pd.read_csv(path)
        print(f"  Columns: {list(df.columns)}")
        print(f"  Shape: {df.shape}")
        results['diabetes'] = {'path': path, 'shape': df.shape, 'columns': list(df.columns)}
    except Exception as e:
        print(f"  Failed: {e}")
        results['diabetes'] = {'error': str(e)}

    # --- HEART: Fedesoriano Heart Failure Prediction ---
    # Try direct Kaggle download or GitHub mirror
    print("\n=== HEART ===")
    heart_urls = [
        "https://raw.githubusercontent.com/fedesoriano/heart-failure-prediction/main/heart.csv",
        "https://media.githubusercontent.com/media/fedesoriano/heart-failure-prediction/main/heart.csv",
    ]
    heart_path = None
    for url in heart_urls:
        try:
            path = download_file(url, "heart_fedesoriano.csv", timeout=30)
            df = pd.read_csv(path)
            print(f"  Columns: {list(df.columns)}")
            print(f"  Shape: {df.shape}")
            heart_path = path
            results['heart'] = {'path': path, 'shape': df.shape, 'columns': list(df.columns)}
            break
        except Exception as e:
            print(f"  Failed: {e}")

    if heart_path is None:
        print("  Could not download heart dataset")
        results['heart'] = {'error': 'Could not download'}

    # --- PARKINSONS: UCI PD Classification Dataset ---
    # https://archive.ics.uci.edu/dataset/470/parkinson+s+disease+classification
    print("\n=== PARKINSONS ===")
    parkinson_urls = [
        "https://archive.ics.uci.edu/static/public/470/parkinson+disease+classification.zip",
        "https://archive.ics.uci.edu/ml/machine-learning-databases/00470/pd_speech_features.zip",
    ]
    parkinson_path = None
    for url in parkinson_urls:
        try:
            r = requests.get(url, allow_redirects=True, timeout=60)
            if len(r.content) > 10000:
                path = os.path.join(DATASETS_DIR, "pd_speech_features.zip")
                with open(path, 'wb') as f:
                    f.write(r.content)
                print(f"  Downloaded {len(r.content)} bytes to {path}")
                with zipfile.ZipFile(path) as z:
                    z.extractall(DATASETS_DIR)
                    print(f"  Extracted files: {z.namelist()}")
                    for name in z.namelist():
                        if name.endswith('.csv'):
                            csv_path = os.path.join(DATASETS_DIR, os.path.basename(name))
                            if os.path.exists(csv_path):
                                df = pd.read_csv(csv_path)
                                print(f"  CSV columns: {list(df.columns)}")
                                print(f"  CSV shape: {df.shape}")
                                results['parkinsons'] = {'path': csv_path, 'shape': df.shape, 'columns': list(df.columns)}
                            else:
                                # Check if inside a subfolder
                                full_path = os.path.join(DATASETS_DIR, name)
                                if os.path.exists(full_path):
                                    df = pd.read_csv(full_path)
                                    print(f"  CSV columns: {list(df.columns)}")
                                    print(f"  CSV shape: {df.shape}")
                                    results['parkinsons'] = {'path': full_path, 'shape': df.shape, 'columns': list(df.columns)}
                parkinson_path = path
                break
            else:
                print(f"  Too small ({len(r.content)} bytes)")
        except Exception as e:
            print(f"  Failed: {e}")

    if parkinson_path is None:
        print("  Could not download Parkinson's dataset")
        results['parkinsons'] = {'error': 'Could not download'}

    print("\n\n=== RESULTS ===")
    print(json.dumps(results, indent=2, default=str))

if __name__ == '__main__':
    import json
    main()
