"""Deep analysis: can we hit >95% on all metrics?"""
import os, warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')
import pandas as pd, numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
from tensorflow import keras
from tensorflow.keras import layers
from scipy.stats import pearsonr

CACHE = os.path.join(os.path.expanduser('~'), '.cache', 'kagglehub', 'datasets')
PROJECT = r'D:\ANN - Copy\AI Medical Assistant'

def try_all_thresholds(y_true, y_prob):
    best = {'f1': 0, 'th': 0.5, 'prec': 0, 'rec': 0, 'acc': 0}
    for th in np.arange(0.05, 0.96, 0.01):
        pred = (y_prob > th).astype(int)
        prec = precision_score(y_true, pred, zero_division=1)
        rec = recall_score(y_true, pred, zero_division=1)
        f1 = f1_score(y_true, pred, zero_division=1)
        acc = accuracy_score(y_true, pred)
        if f1 > best['f1']:
            best = {'f1': f1, 'th': th, 'prec': prec, 'rec': rec, 'acc': acc, 'all_ok': False}
        if f1 >= 0.95 and prec >= 0.95 and rec >= 0.95:
            print(f"  OK ALL >95% at th={th:.2f}: prec={prec:.4f}, rec={rec:.4f}, f1={f1:.4f}")
            best['all_ok'] = True
    pos_probs = y_prob[y_true == 1]
    neg_probs = y_prob[y_true == 0]
    print(f"  Pos probs: mean={pos_probs.mean():.4f}, median={np.median(pos_probs):.4f}, p25={np.percentile(pos_probs,25):.4f}, p75={np.percentile(pos_probs,75):.4f}")
    print(f"  Neg probs: mean={neg_probs.mean():.4f}, median={np.median(neg_probs):.4f}, p25={np.percentile(neg_probs,25):.4f}, p75={np.percentile(neg_probs,75):.4f}")
    corr, _ = pearsonr(y_prob, y_true)
    print(f"  Correlation: {corr:.4f}")
    return best

def build_wide_ann(input_dim, name):
    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(), layers.Dropout(0.4),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(), layers.Dropout(0.4),
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(), layers.Dropout(0.3),
        layers.Dense(64, activation='relu'),
        layers.BatchNormalization(), layers.Dropout(0.3),
        layers.Dense(32, activation='relu'),
        layers.Dense(1, activation='sigmoid'),
    ], name=name)
    return model

# === DIABETES: Wide ANN with class weights ===
print("=" * 60)
print("DIABETES: Wide ANN (512-256-128-64-32)")
path = os.path.join(CACHE, 'iammustafatz', 'diabetes-prediction-dataset', 'versions', '1')
df = pd.read_csv(os.path.join(path, 'diabetes_prediction_dataset.csv'))
le = LabelEncoder()
df['gender'] = le.fit_transform(df['gender'])
df['smoking_history'] = le.fit_transform(df['smoking_history'])
X = df[['gender', 'age', 'hypertension', 'heart_disease', 'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level']].values
y = df['diabetes'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

neg, pos = np.bincount(y_train)
cw = {0: 1.0, 1: neg / pos}
print(f"  Class weight for positive: {cw[1]:.1f}")

model = build_wide_ann(X_train.shape[1], 'diabetes')
model.compile(optimizer=keras.optimizers.Adam(0.0005), loss='binary_crossentropy', metrics=['accuracy'])

history = model.fit(
    X_train_s, y_train, epochs=50, batch_size=1024,
    validation_split=0.15, class_weight=cw,
    callbacks=[keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=0)],
    verbose=1
)

y_prob = model.predict(X_test_s, verbose=0).flatten()
print("\nDiabetes probability distribution:")
best = try_all_thresholds(y_test, y_prob)
print(f"Best: th={best['th']:.2f}, acc={best['acc']:.4f}, prec={best['prec']:.4f}, rec={best['rec']:.4f}, f1={best['f1']:.4f}")

# === HEART: Try alphiree 308K dataset ===
print("\n" + "=" * 60)
print("HEART: alphiree 308K dataset")
path = os.path.join(CACHE, 'alphiree', 'cardiovascular-diseases-risk-prediction-dataset', 'versions', '3')
df2 = pd.read_csv(os.path.join(path, 'CVD_cleaned.csv'))

cat_cols2 = ['General_Health', 'Checkup', 'Exercise', 'Skin_Cancer', 'Other_Cancer',
            'Depression', 'Diabetes', 'Arthritis', 'Sex', 'Age_Category', 'Smoking_History']
for col in cat_cols2:
    df2[col] = LabelEncoder().fit_transform(df2[col].astype(str))

num_cols2 = ['Height_(cm)', 'Weight_(kg)', 'BMI', 'Alcohol_Consumption',
            'Fruit_Consumption', 'Green_Vegetables_Consumption', 'FriedPotato_Consumption']
feature_cols2 = cat_cols2 + num_cols2
X2 = df2[feature_cols2].values.astype(float)
y2 = (df2['Heart_Disease'] == 'Yes').astype(int).values
print(f"  Shape: {X2.shape}, Pos: {y2.sum()}/{len(y2)} ({y2.mean()*100:.1f}%)")

X2_train, X2_test, y2_train, y2_test = train_test_split(X2, y2, test_size=0.2, random_state=42, stratify=y2)
scaler2 = StandardScaler()
X2_train_s = scaler2.fit_transform(X2_train)
X2_test_s = scaler2.transform(X2_test)

neg2, pos2 = np.bincount(y2_train)
cw2 = {0: 1.0, 1: neg2 / pos2}
print(f"  Class weight for positive: {cw2[1]:.1f}")

model2 = build_wide_ann(X2.shape[1], 'heart_308k')
model2.compile(optimizer=keras.optimizers.Adam(0.0005), loss='binary_crossentropy', metrics=['accuracy'])
model2.fit(X2_train_s, y2_train, epochs=30, batch_size=1024, validation_split=0.15, class_weight=cw2,
           callbacks=[keras.callbacks.EarlyStopping(monitor='val_loss', patience=8, restore_best_weights=True, verbose=0)],
           verbose=1)

y2_prob = model2.predict(X2_test_s, verbose=0).flatten()
print("\nHeart (308K) probability distribution:")
best2 = try_all_thresholds(y2_test, y2_prob)
print(f"Best: th={best2['th']:.2f}, acc={best2['acc']:.4f}, prec={best2['prec']:.4f}, rec={best2['rec']:.4f}, f1={best2['f1']:.4f}")
