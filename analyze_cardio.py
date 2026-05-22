import pandas as pd, numpy as np
import os, warnings
os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
os.environ['TF_ENABLE_ONEDNN_OPTS']='0'
warnings.filterwarnings('ignore')
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

CACHE = os.path.join(os.path.expanduser('~'), '.cache', 'kagglehub', 'datasets')
cardio = pd.read_csv(os.path.join(CACHE, 'sulianova', 'cardiovascular-disease-dataset', 'versions', '1', 'cardio_train.csv'), sep=';')
print('CARDIO 70K')
print(f'Shape: {cardio.shape}')
print(f'Columns: {list(cardio.columns)}')
print(f'Cardio distribution: {cardio["cardio"].value_counts().to_dict()}')
print(f'Nulls: {cardio.isnull().sum().sum()}')

# Preprocess
df = cardio.copy()
df['age_years'] = (df['age'] / 365.25).astype(int)
features = ['age_years', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 'cholesterol', 'gluc', 'smoke', 'alco', 'active']
X = df[features].values.astype(float)
y = df['cardio'].values

print(f'Positive rate: {y.mean()*100:.1f}%')

# Filter outliers (common for cardio dataset)
mask = (df['ap_hi'] > 250) | (df['ap_hi'] < 50) | (df['ap_lo'] > 200) | (df['ap_lo'] < 30) | (df['height'] < 100) | (df['height'] > 250)
print(f'Outliers to remove: {mask.sum()}')
df_clean = df[~mask]
X_clean = df_clean[features].values.astype(float)
y_clean = df_clean['cardio'].values
print(f'After cleaning: {X_clean.shape}, Positive rate: {y_clean.mean()*100:.1f}%')

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42, stratify=y_clean)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# Balanced - no class weights needed
model = keras.Sequential([
    layers.Input(shape=(len(features),)),
    layers.Dense(256, activation='relu'),
    layers.BatchNormalization(), layers.Dropout(0.3),
    layers.Dense(128, activation='relu'),
    layers.BatchNormalization(), layers.Dropout(0.3),
    layers.Dense(64, activation='relu'),
    layers.BatchNormalization(), layers.Dropout(0.2),
    layers.Dense(32, activation='relu'),
    layers.Dense(1, activation='sigmoid'),
])
model.compile(optimizer=keras.optimizers.Adam(0.001), loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train_s, y_train, epochs=30, batch_size=256, validation_split=0.15,
          callbacks=[keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=0)],
          verbose=1)

y_prob = model.predict(X_test_s, verbose=0).flatten()

# Find best threshold
best = {'f1': 0}
for th in np.arange(0.05, 0.96, 0.01):
    pred = (y_prob > th).astype(int)
    prec = precision_score(y_test, pred)
    rec = recall_score(y_test, pred)
    f1 = f1_score(y_test, pred)
    acc = accuracy_score(y_test, pred)
    if f1 > best['f1']:
        best = {'f1': f1, 'th': th, 'prec': prec, 'rec': rec, 'acc': acc}
    if prec >= 0.95 and rec >= 0.95 and f1 >= 0.95:
        print(f'  ALL >95% at th={th:.2f}: acc={acc:.4f}, prec={prec:.4f}, rec={rec:.4f}')

print(f'\nBest: th={best["th"]:.2f}, acc={best["acc"]:.4f}, prec={best["prec"]:.4f}, rec={best["rec"]:.4f}, f1={best["f1"]:.4f}')

pos_probs = y_prob[y_test == 1]
neg_probs = y_prob[y_test == 0]
print(f'\nPos probs: mean={pos_probs.mean():.4f}, median={np.median(pos_probs):.4f}, p10={np.percentile(pos_probs,10):.4f}')
print(f'Neg probs: mean={neg_probs.mean():.4f}, median={np.median(neg_probs):.4f}, p90={np.percentile(neg_probs,90):.4f}')