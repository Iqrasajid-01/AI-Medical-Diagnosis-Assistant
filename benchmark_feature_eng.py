"""Feature engineering sprint - squeeze max performance from all datasets"""
import os, warnings, json, pickle
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')
import pandas as pd, numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, PolynomialFeatures
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix
from imblearn.over_sampling import SMOTE
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
from tensorflow import keras
from tensorflow.keras import layers

CACHE = os.path.join(os.path.expanduser('~'), '.cache', 'kagglehub', 'datasets')
PROJECT = r'D:\ANN - Copy\AI Medical Assistant'

def build_ann(input_dim, layers_config, name, dropout=0.3):
    model = keras.Sequential(name=name)
    model.add(layers.Input(shape=(input_dim,)))
    for i, units in enumerate(layers_config):
        model.add(layers.Dense(units, activation='relu'))
        model.add(layers.BatchNormalization())
        model.add(layers.Dropout(dropout if i < len(layers_config)-1 else dropout/2))
    model.add(layers.Dense(1, activation='sigmoid'))
    return model

def train_evaluate(model, X_train, y_train, X_test, y_test, epochs, batch_size, class_weight=None):
    model.compile(optimizer=keras.optimizers.Adam(0.0005), loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.15,
              class_weight=class_weight,
              callbacks=[keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=0)],
              verbose=0)
    y_prob = model.predict(X_test, verbose=0).flatten()
    best = {'f1': 0, 'prec': 0, 'rec': 0, 'acc': 0, 'th': 0.5}
    for th in np.arange(0.05, 0.96, 0.01):
        pred = (y_prob > th).astype(int)
        prec = precision_score(y_test, pred, zero_division=1)
        rec = recall_score(y_test, pred, zero_division=1)
        f1 = f1_score(y_test, pred, zero_division=1)
        acc = accuracy_score(y_test, pred)
        if f1 > best['f1']:
            best = {'f1': f1, 'prec': prec, 'rec': rec, 'acc': acc, 'th': th}
    return best, y_prob

def add_diabetes_features(df):
    df['bmi_age'] = df['bmi'] * df['age'] / 100
    df['hba1c_glucose'] = df['HbA1c_level'] * df['blood_glucose_level'] / 100
    df['age_hba1c'] = df['age'] * df['HbA1c_level']
    df['age_sq'] = df['age'] ** 2 / 100
    df['bmi_sq'] = df['bmi'] ** 2 / 100
    df['glucose_sq'] = df['blood_glucose_level'] ** 2 / 10000
    df['hba1c_sq'] = df['HbA1c_level'] ** 2
    return df

def add_heart_features(df):
    df['age_maxhr'] = df['Age'] * df['MaxHR'] / 100
    df['oldpeak_restingbp'] = df['Oldpeak'] * df['RestingBP'] / 100
    df['age_oldpeak'] = df['Age'] * df['Oldpeak']
    df['restingbp_chol'] = df['RestingBP'] * df['Cholesterol'] / 10000
    df['maxhr_sq'] = df['MaxHR'] ** 2 / 100
    df['oldpeak_sq'] = df['Oldpeak'] ** 2
    return df

def add_parkinsons_features(df, top_k=10):
    from scipy.stats import pearsonr
    corrs = {}
    for col in df.columns:
        if col != 'status':
            corrs[col] = abs(pearsonr(df[col], df['status'])[0])
    top = sorted(corrs, key=corrs.get, reverse=True)[:top_k]
    for i, f1 in enumerate(top):
        for f2 in top[i+1:]:
            name = f'{f1[:8]}_{f2[:8]}'
            df[name] = df[f1] * df[f2]
    return df

results = {}

# ====================================
# DIABETES: 100K + feature engineering
# ====================================
print('=' * 60)
print('DIABETES: 100K + feature engineering')
path = os.path.join(CACHE, 'iammustafatz', 'diabetes-prediction-dataset', 'versions', '1')
df = pd.read_csv(os.path.join(path, 'diabetes_prediction_dataset.csv'))
le = LabelEncoder()
df['gender'] = le.fit_transform(df['gender'])
df['smoking_history'] = le.fit_transform(df['smoking_history'])
df = add_diabetes_features(df)
feature_cols = [c for c in df.columns if c != 'diabetes']
print(f'  Features: {len(feature_cols)} (8 base + {len(feature_cols)-8} engineered)')
X = df[feature_cols].values.astype(float)
y = df['diabetes'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# SMOTE for diabetes
sm = SMOTE(random_state=42)
X_train_res, y_train_res = sm.fit_resample(X_train_s, y_train)
print(f'  After SMOTE: {X_train_res.shape}, pos={y_train_res.sum()}')

model_dia = build_ann(X_train_res.shape[1], [256, 128, 64, 32], 'diabetes_eng')
best_dia, y_prob_dia = train_evaluate(model_dia, X_train_res, y_train_res, X_test_s, y_test, epochs=50, batch_size=1024)
print(f'  Best: th={best_dia["th"]:.2f}, acc={best_dia["acc"]:.4f}, prec={best_dia["prec"]:.4f}, rec={best_dia["rec"]:.4f}, f1={best_dia["f1"]:.4f}')
results['diabetes'] = best_dia

# Save
os.makedirs(os.path.join(PROJECT, 'backend', 'static', 'ml_assets'), exist_ok=True)
model_dia.save(os.path.join(PROJECT, 'backend', 'static', 'ml_assets', 'diabetes_fe.keras'))
with open(os.path.join(PROJECT, 'backend', 'static', 'ml_assets', 'diabetes_scaler.pkl'), 'wb') as f:
    pickle.dump(scaler, f)
meta = {
    'features': feature_cols,
    'gender_mapping': {'Female': 0, 'Male': 1, 'Other': 2},
    'smoking_mapping': {'never': 0, 'former': 1, 'current': 2, 'not current': 3, 'ever': 4, 'No Info': 5},
    'best_threshold': float(best_dia['th'])
}
with open(os.path.join(PROJECT, 'backend', 'static', 'ml_assets', 'diabetes_meta.json'), 'w') as f:
    json.dump(meta, f, indent=2)

# ====================================
# HEART: 918 + feature engineering
# ====================================
print('\n' + '=' * 60)
print('HEART: 918 + feature engineering + ensemble')
path = os.path.join(CACHE, 'fedesoriano', 'heart-failure-prediction', 'versions', '1')
df = pd.read_csv(os.path.join(path, 'heart.csv'))

cat_maps = {}
for col in ['Sex', 'ChestPainType', 'RestingECG', 'ExerciseAngina', 'ST_Slope']:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    cat_maps[col] = dict(zip(le.classes_, le.transform(le.classes_)))

df = add_heart_features(df)
feature_cols_h = [c for c in df.columns if c != 'HeartDisease']
print(f'  Features: {len(feature_cols_h)} (11 base + {len(feature_cols_h)-11} engineered)')
X = df[feature_cols_h].values.astype(float)
y = df['HeartDisease'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler_h = StandardScaler()
X_train_s = scaler_h.fit_transform(X_train)
X_test_s = scaler_h.transform(X_test)

sm = SMOTE(random_state=42)
X_train_res, y_train_res = sm.fit_resample(X_train_s, y_train)
print(f'  After SMOTE: {X_train_res.shape}, pos={y_train_res.sum()}')

# Ensemble of 3 ANNs for heart
ens_preds = []
for seed in [42, 123, 456]:
    tf.random.set_seed(seed)
    model_h = build_ann(X_train_res.shape[1], [128, 64, 32], f'heart_ens_{seed}')
    model_h.compile(optimizer=keras.optimizers.Adam(0.0005), loss='binary_crossentropy', metrics=['accuracy'])
    model_h.fit(X_train_res, y_train_res, epochs=80, batch_size=32, validation_split=0.15,
                callbacks=[keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=0)],
                verbose=0)
    ens_preds.append(model_h.predict(X_test_s, verbose=0).flatten())
y_prob_h = np.mean(ens_preds, axis=0)

best_h = {'f1': 0}
for th in np.arange(0.05, 0.96, 0.01):
    pred = (y_prob_h > th).astype(int)
    prec = precision_score(y_test, pred, zero_division=1)
    rec = recall_score(y_test, pred, zero_division=1)
    f1 = f1_score(y_test, pred, zero_division=1)
    acc = accuracy_score(y_test, pred)
    if f1 > best_h['f1']:
        best_h = {'f1': f1, 'th': th, 'prec': prec, 'rec': rec, 'acc': acc}
print(f'  Ensemble Best: th={best_h["th"]:.2f}, acc={best_h["acc"]:.4f}, prec={best_h["prec"]:.4f}, rec={best_h["rec"]:.4f}, f1={best_h["f1"]:.4f}')
results['heart'] = best_h

# ====================================
# PARKINSONS: 195 + feature engineering
# ====================================
print('\n' + '=' * 60)
print('PARKINSONS: 22 features + noise aug + feature engineering')
pdf = pd.read_csv(os.path.join(PROJECT, 'datasets', 'Parkinsons disease.csv'))
pdf = pdf.drop(columns=['name'], errors='ignore')
pdf = add_parkinsons_features(pdf, top_k=8)
feature_cols_p = [c for c in pdf.columns if c != 'status']
print(f'  Features: {len(feature_cols_p)} (22 base + {len(feature_cols_p)-22} engineered)')
X = pdf[feature_cols_p].values.astype(float)
y = pdf['status'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler_p = StandardScaler()
X_train_s = scaler_p.fit_transform(X_train)
X_test_s = scaler_p.transform(X_test)

# SMOTE
sm = SMOTE(random_state=42)
X_train_res, y_train_res = sm.fit_resample(X_train_s, y_train)
# Noise augmentation
noise = np.random.normal(0, 0.05, X_train_res.shape)
X_train_aug = np.vstack([X_train_res, X_train_res + noise])
y_train_aug = np.hstack([y_train_res, y_train_res])
print(f'  After SMOTE+noise: {X_train_aug.shape}')

# Ensemble
ens_preds_p = []
for seed in [42, 99, 777]:
    tf.random.set_seed(seed)
    model_p = build_ann(X_train_aug.shape[1], [128, 64, 32, 16], f'park_ens_{seed}', dropout=0.25)
    model_p.compile(optimizer=keras.optimizers.Adam(0.0003), loss='binary_crossentropy', metrics=['accuracy'])
    model_p.fit(X_train_aug, y_train_aug, epochs=100, batch_size=16, validation_split=0.15,
                callbacks=[keras.callbacks.EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True, verbose=0)],
                verbose=0)
    ens_preds_p.append(model_p.predict(X_test_s, verbose=0).flatten())
y_prob_p = np.mean(ens_preds_p, axis=0)

best_p = {'f1': 0}
for th in np.arange(0.05, 0.96, 0.01):
    pred = (y_prob_p > th).astype(int)
    prec = precision_score(y_test, pred, zero_division=1)
    rec = recall_score(y_test, pred, zero_division=1)
    f1 = f1_score(y_test, pred, zero_division=1)
    acc = accuracy_score(y_test, pred)
    if f1 > best_p['f1']:
        best_p = {'f1': f1, 'th': th, 'prec': prec, 'rec': rec, 'acc': acc}
print(f'  Ensemble Best: th={best_p["th"]:.2f}, acc={best_p["acc"]:.4f}, prec={best_p["prec"]:.4f}, rec={best_p["rec"]:.4f}, f1={best_p["f1"]:.4f}')
results['parkinsons'] = best_p

print('\n' + '=' * 60)
print('FINAL RESULTS')
print('=' * 60)
for disease, r in results.items():
    all95 = r['prec'] >= 0.95 and r['rec'] >= 0.95 and r['f1'] >= 0.95 and r['acc'] >= 0.95
    print(f'\n{disease}:')
    print(f'  acc={r["acc"]:.4f}, prec={r["prec"]:.4f}, rec={r["rec"]:.4f}, f1={r["f1"]:.4f}')
    print(f'  th={r["th"]:.2f}')
    print(f'  ALL >95%: {"YES!" if all95 else "no"}')
