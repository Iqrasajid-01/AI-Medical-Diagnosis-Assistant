"""Check downloaded datasets details."""
import pandas as pd
import os

cache = os.path.join(os.path.expanduser('~'), '.cache', 'kagglehub', 'datasets')

print("=== kamilpytlak Heart Dataset ===")
path = os.path.join(cache, 'kamilpytlak', 'personal-key-indicators-of-heart-disease', 'versions', '6')
for f in os.listdir(path):
    if f.endswith('.csv'):
        df = pd.read_csv(os.path.join(path, f))
        print(f"File: {f}")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"Target column: {df.columns[-1]}")
        print(f"HeartDisease values: {df['HeartDisease'].value_counts().to_dict() if 'HeartDisease' in df.columns else 'N/A'}")
        break

print("\n=== alphiree CVD Dataset ===")
path2 = os.path.join(cache, 'alphiree', 'cardiovascular-diseases-risk-prediction-dataset', 'versions', '3')
for f in os.listdir(path2):
    if f.endswith('.csv'):
        df2 = pd.read_csv(os.path.join(path2, f))
        print(f"File: {f}")
        print(f"Shape: {df2.shape}")
        print(f"Columns: {list(df2.columns)}")
        print(f"Heart_Disease values: {df2['Heart_Disease'].value_counts().to_dict()}")
        print(f"Data types:")
        for col in df2.columns:
            print(f"  {col}: {df2[col].dtype} e.g. {df2[col].iloc[0]}")
        break

print("\n=== Diabetes 100K ===")
path3 = os.path.join(cache, 'iammustafatz', 'diabetes-prediction-dataset', 'versions', '1')
df3 = pd.read_csv(os.path.join(path3, 'diabetes_prediction_dataset.csv'))
print(f"Shape: {df3.shape}")
print(f"Columns: {list(df3.columns)}")
print(f"Target distribution: {df3['diabetes'].value_counts().to_dict()}")
print(f"Smoking history values: {df3['smoking_history'].value_counts().to_dict()}")
print(f"Gender values: {df3['gender'].value_counts().to_dict()}")

print("\n=== Fedesoriano Heart ===")
path4 = os.path.join(cache, 'fedesoriano', 'heart-failure-prediction', 'versions', '1')
df4 = pd.read_csv(os.path.join(path4, 'heart.csv'))
print(f"Shape: {df4.shape}")
print(f"Columns: {list(df4.columns)}")
print(f"ChestPainType values: {df4['ChestPainType'].value_counts().to_dict()}")
print(f"RestingECG values: {df4['RestingECG'].value_counts().to_dict()}")
print(f"ExerciseAngina values: {df4['ExerciseAngina'].value_counts().to_dict()}")
print(f"ST_Slope values: {df4['ST_Slope'].value_counts().to_dict()}")
