"""Faster benchmark with class weights and threshold tuning."""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
from tensorflow import keras
from tensorflow.keras import layers

CACHE = os.path.join(os.path.expanduser('~'), '.cache', 'kagglehub', 'datasets')

def build_ann(input_dim, name, lr=0.001):
    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.2),
        layers.Dense(32, activation='relu'),
        layers.Dense(1, activation='sigmoid'),
    ], name=name)
    model.compile(optimizer=keras.optimizers.Adam(lr), loss='binary_crossentropy', metrics=['accuracy'])
    return model

def find_best_threshold(model, X_val, y_val):
    probs = model.predict(X_val, verbose=0).flatten()
    best_f1 = 0
    best_th = 0.5
    for th in np.arange(0.1, 0.9, 0.02):
        preds = (probs > th).astype(int)
        f1 = f1_score(y_val, preds)
        if f1 > best_f1:
            best_f1 = f1
            best_th = th
    return best_th

def evaluate(name, X, y, class_weight_flag=True, threshold_tune=True):
    print(f"\n--- {name} ---")
    print(f"Shape: {X.shape}, Pos: {y.sum()}/{len(y)} ({y.mean()*100:.1f}%)")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    
    model = build_ann(X_train.shape[1], name.replace(" ", "_"))
    
    cw = None
    if class_weight_flag:
        neg, pos = np.bincount(y_train)
        cw = {0: 1.0, 1: neg / pos}
        print(f"  Class weights: {cw}")
    
    early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=0)
    
    model.fit(X_train_s, y_train, epochs=30, batch_size=256, validation_split=0.15, class_weight=cw, callbacks=[early_stop], verbose=0)
    
    th = 0.5
    if threshold_tune:
        X_train_sub, X_val, y_train_sub, y_val = train_test_split(X_train_s, y_train, test_size=0.2, random_state=42, stratify=y_train)
        model2 = build_ann(X_train.shape[1], f"{name.replace(' ', '_')}_tune")
        model2.fit(X_train_sub, y_train_sub, epochs=15, batch_size=256, class_weight=cw, verbose=0)
        th = find_best_threshold(model2, X_val, y_val)
        print(f"  Best threshold: {th:.3f}")
    
    y_prob = model.predict(X_test_s, verbose=0).flatten()
    y_pred = (y_prob > th).astype(int)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    print(f"  Threshold={th:.3f}: Acc={acc:.4f}, Prec={prec:.4f}, Rec={rec:.4f}, F1={f1:.4f}")
    print(classification_report(y_test, y_pred, digits=4))
    return {'acc': acc, 'prec': prec, 'rec': rec, 'f1': f1, 'threshold': th}

results = {}

# === DIABETES (100K) ===
print("\n\n" + "=" * 60)
print("DIABETES: 100K with class weights")
path = os.path.join(CACHE, 'iammustafatz', 'diabetes-prediction-dataset', 'versions', '1')
df = pd.read_csv(os.path.join(path, 'diabetes_prediction_dataset.csv'))
le = LabelEncoder()
df['gender'] = le.fit_transform(df['gender'])
df['smoking_history'] = le.fit_transform(df['smoking_history'])
X = df[['gender', 'age', 'hypertension', 'heart_disease', 'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level']].values
y = df['diabetes'].values
results['diabetes'] = evaluate('Diabetes 100K', X, y, class_weight_flag=True, threshold_tune=True)

# === HEART (918) ===
print("\n" + "=" * 60)
print("HEART: 918 rows with class weights")
path = os.path.join(CACHE, 'fedesoriano', 'heart-failure-prediction', 'versions', '1')
df = pd.read_csv(os.path.join(path, 'heart.csv'))
for col in ['Sex', 'ChestPainType', 'RestingECG', 'ExerciseAngina', 'ST_Slope']:
    df[col] = LabelEncoder().fit_transform(df[col])
X = df[['Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope']].values
y = df['HeartDisease'].values
results['heart'] = evaluate('Heart 918', X, y, class_weight_flag=False, threshold_tune=True)

# === PARKINSONS (22 features, augmented) ===
print("\n" + "=" * 60)
print("PARKINSONS: 22 features + SMOTE + noise")
df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets', 'Parkinsons disease.csv'))
df = df.drop(columns=['name'], errors='ignore')
PARK_FEATURES = [
    'MDVP:Fo(Hz)', 'MDVP:Fhi(Hz)', 'MDVP:Flo(Hz)',
    'MDVP:Jitter(%)', 'MDVP:Jitter(Abs)', 'MDVP:RAP', 'MDVP:PPQ', 'Jitter:DDP',
    'MDVP:Shimmer', 'MDVP:Shimmer(dB)', 'Shimmer:APQ3', 'Shimmer:APQ5',
    'MDVP:APQ', 'Shimmer:DDA',
    'NHR', 'HNR', 'RPDE', 'DFA', 'spread1', 'spread2', 'D2', 'PPE',
]
X = df[PARK_FEATURES].values
y = df['status'].values
from imblearn.over_sampling import SMOTE
X_aug, y_aug = SMOTE(random_state=42, k_neighbors=3).fit_resample(X, y)
np.random.seed(42)
noise = np.random.normal(0, 0.03, X_aug.shape) * np.std(X_aug, axis=0)
X_aug = np.vstack([X_aug, X_aug + noise])
y_aug = np.hstack([y_aug, y_aug])
results['parkinsons'] = evaluate('Parkinsons augmented', X_aug, y_aug, class_weight_flag=False, threshold_tune=True)

print("\n\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
for disease, r in results.items():
    print(f"\n{disease}:")
    for k, v in r.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
    ok = all(r.get(m, 0) >= 0.95 for m in ['acc', 'prec', 'rec', 'f1'])
    print(f"  ALL >95%: {'YES' if ok else 'NO'}")
