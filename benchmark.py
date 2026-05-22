"""Benchmark new datasets with ANN to verify >95% potential."""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

import tensorflow as tf
tf.get_logger().setLevel('ERROR')
from tensorflow import keras
from tensorflow.keras import layers

CACHE_DIR = os.path.join(os.path.expanduser('~'), '.cache', 'kagglehub', 'datasets')

print("=" * 60)
print("BENCHMARK: Can new datasets hit >95% with ANN?")
print("=" * 60)

def build_ann(input_dim, name='model'):
    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(32, activation='relu'),
        layers.Dense(1, activation='sigmoid'),
    ], name=name)
    model.compile(optimizer=keras.optimizers.Adam(0.001), loss='binary_crossentropy', metrics=['accuracy'])
    return model

def benchmark(name, X, y):
    safe_name = name.replace(" ", "_").replace("(", "").replace(")", "").replace(",", "")
    print(f"\n--- {name} ---")
    print(f"Shape: {X.shape}, Positives: {y.sum()}/{len(y)} ({y.mean()*100:.1f}%)")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    model = build_ann(X_train.shape[1], safe_name)
    history = model.fit(X_train, y_train, epochs=15, batch_size=256, validation_split=0.15, verbose=0)
    
    y_pred = (model.predict(X_test, verbose=0) > 0.5).astype(int).flatten()
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    print(f"  Accuracy: {acc:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall: {rec:.4f}")
    print(f"  F1: {f1:.4f}")
    print(f"  Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}")
    result = {'acc': acc, 'prec': prec, 'rec': rec, 'f1': f1}
    return result, model

results = {}

# === DIABETES ===
print("\n" + "=" * 60)
print("DIABETES: 100K Kaggle Dataset")
print("=" * 60)
try:
    path = os.path.join(CACHE_DIR, 'iammustafatz', 'diabetes-prediction-dataset', 'versions', '1')
    df = pd.read_csv(os.path.join(path, 'diabetes_prediction_dataset.csv'))
    le = LabelEncoder()
    for col in ['gender', 'smoking_history']:
        df[col] = le.fit_transform(df[col])
    feature_cols = ['gender', 'age', 'hypertension', 'heart_disease', 'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level']
    X = df[feature_cols].values
    y = df['diabetes'].values
    r, m = benchmark("Diabetes (100K)", X, y)
    results['diabetes'] = r
except Exception as e:
    print(f"ERROR: {e}")
    results['diabetes'] = {'error': str(e)}

# === HEART ===
print("\n" + "=" * 60)
print("HEART: 918-Row Fedesoriano Dataset")
print("=" * 60)
try:
    path = os.path.join(CACHE_DIR, 'fedesoriano', 'heart-failure-prediction', 'versions', '1')
    df = pd.read_csv(os.path.join(path, 'heart.csv'))
    # Encode categoricals
    le = LabelEncoder()
    for col in ['Sex', 'ChestPainType', 'RestingECG', 'ExerciseAngina', 'ST_Slope']:
        df[col] = le.fit_transform(df[col])
    feature_cols = ['Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope']
    X = df[feature_cols].values
    y = df['HeartDisease'].values
    r, m = benchmark("Heart (918)", X, y)
    results['heart'] = r
except Exception as e:
    print(f"ERROR: {e}")
    results['heart'] = {'error': str(e)}

# === PARKINSONS (keep 22-feature dataset, ANN with augmentation) ===
print("\n" + "=" * 60)
print("PARKINSONS: 22 features, ANN with SMOTE augmentation")
print("=" * 60)
try:
    datasets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets')
    df = pd.read_csv(os.path.join(datasets_dir, 'Parkinsons disease.csv'))
    df = df.drop(columns=['name'], errors='ignore')
    
    PARKINSONS_FEATURES = [
        'MDVP:Fo(Hz)', 'MDVP:Fhi(Hz)', 'MDVP:Flo(Hz)',
        'MDVP:Jitter(%)', 'MDVP:Jitter(Abs)', 'MDVP:RAP', 'MDVP:PPQ', 'Jitter:DDP',
        'MDVP:Shimmer', 'MDVP:Shimmer(dB)', 'Shimmer:APQ3', 'Shimmer:APQ5',
        'MDVP:APQ', 'Shimmer:DDA',
        'NHR', 'HNR',
        'RPDE', 'DFA', 'spread1', 'spread2', 'D2', 'PPE',
    ]
    X = df[PARKINSONS_FEATURES].values
    y = df['status'].values
    
    # Use SMOTE to augment
    from imblearn.over_sampling import SMOTE
    X_aug, y_aug = SMOTE(random_state=42, k_neighbors=3).fit_resample(X, y)
    print(f"  After SMOTE: {X_aug.shape}")
    
    r, m = benchmark("Parkinsons (195+SMOTE)", X_aug, y_aug)
    results['parkinsons'] = r
except Exception as e:
    print(f"ERROR: {e}")
    results['parkinsons'] = {'error': str(e)}

# === SUMMARY ===
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
for disease, r in results.items():
    if 'error' in r:
        print(f"  {disease}: ERROR - {r['error']}")
    else:
        print(f"  {disease}: Acc={r['acc']:.4f}, Prec={r['prec']:.4f}, Rec={r['rec']:.4f}, F1={r['f1']:.4f}")
        ok = all(v >= 0.95 for v in [r['acc'], r['prec'], r['rec'], r['f1']])
        print(f"    {'✓ PASS >95%' if ok else '✗ BELOW 95%'}")
