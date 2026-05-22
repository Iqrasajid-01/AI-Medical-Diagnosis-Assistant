"""Download larger datasets - attempt 2 with better URLs."""
import os
import sys
import csv
import io

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(SCRIPT_DIR, 'datasets')

def try_download(urls, filename):
    path = os.path.join(DATASETS_DIR, filename)
    for url in urls:
        try:
            print(f"Trying: {url}")
            import urllib.request
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if len(data) > 100:
                    with open(path, 'wb') as f:
                        f.write(data)
                    print(f"  Downloaded {len(data)} bytes -> {path}")
                    return path
                else:
                    print(f"  Too small: {len(data)} bytes")
        except Exception as e:
            print(f"  Failed: {e}")
    return None

def main():
    results = {}

    # --- HEART: Fedesoriano Heart Failure Prediction ---
    print("\n=== HEART ===")
    heart_path = try_download([
        "https://raw.githubusercontent.com/fedesoriano/heart-failure-prediction/main/heart.csv",
        "https://raw.githubusercontent.com/fedesoriano/heart-failure-prediction/master/heart.csv",
        "https://media.githubusercontent.com/media/fedesoriano/heart-failure-prediction/main/heart.csv",
    ], "heart_fedesoriano.csv")
    if heart_path:
        import pandas as pd
        df = pd.read_csv(heart_path)
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        results['heart'] = {'path': heart_path, 'shape': list(df.shape), 'columns': list(df.columns)}
    else:
        results['heart'] = {'error': 'Failed all URLs'}

    # --- DIABETES: Try Kaggle mirror on GitHub ---
    # The Pima dataset is the most common - but we need a LARGER one.
    # Try the CDC dataset from Hugging Face's raw parquet or another source
    print("\n=== DIABETES ===")
    
    # Try CDC dataset from AMS-AHEAD (CSV download) or other mirrors
    diabetes_path = try_download([
        # Mendeley DOI direct download (try with proper API)
        "https://data.mendeley.com/api/datasets/rn9m3zb7nt/files/8ff1a061-3c20-43e4-8d79-1e1acd29ae05",
        # Try the raw file without the API
        "https://prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com/rn9m3zb7nt-1.zip",
    ], "diabetes_mendeley2.csv")
    
    if diabetes_path:
        import pandas as pd
        df = pd.read_csv(diabetes_path)
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        results['diabetes'] = {'path': diabetes_path, 'shape': list(df.shape), 'columns': list(df.columns)}
    else:
        results['diabetes'] = {'error': 'Failed all URLs'}

    # --- PARKINSONS: Try UCI repository ---
    print("\n=== PARKINSONS ===")
    park_path = try_download([
        "https://archive.ics.uci.edu/static/public/470/parkinson+disease+classification.zip",
        "https://archive.ics.uci.edu/static/public/489/parkinson+dataset+with+replicated+acoustic+features.zip",
    ], "parkinsons_uci.zip")
    if park_path:
        import zipfile
        import pandas as pd
        with zipfile.ZipFile(park_path) as z:
            print(f"  Files in zip: {z.namelist()}")
            for name in z.namelist():
                if name.endswith('.csv'):
                    with z.open(name) as f:
                        df = pd.read_csv(f)
                        print(f"  CSV ({name}): Shape={df.shape}, Columns={list(df.columns)[:10]}...")
                        results['parkinsons'] = {'path': name, 'shape': list(df.shape), 'columns': list(df.columns)}
                    break
    else:
        results['parkinsons'] = {'error': 'Failed all URLs'}

    print("\n\n=== RESULTS ===")
    import json
    print(json.dumps(results, indent=2, default=str))

if __name__ == '__main__':
    main()
