import json, pickle, numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow import keras

meta = json.load(open('backend/static/ml_assets/heart_meta.json'))
model = keras.models.load_model('backend/static/ml_assets/heart_model.keras')
scaler = pickle.load(open('backend/static/ml_assets/heart_scaler.pkl', 'rb'))

cat_map = meta['categorical_mappings']
base = meta['base_features']

def predict(input_data):
    vals = []
    for col in base:
        val = input_data.get(col)
        if cat_map and col in cat_map:
            mapping = cat_map[col]
            if val is not None and str(val) in mapping:
                val = mapping[str(val)]
            else:
                val = 0.0
        if val is None or val == '':
            val = 0.0
        vals.append(float(val))

    age, restingbp, cholesterol, maxhr, oldpeak = vals[0], vals[3], vals[4], vals[7], vals[9]
    eng = {
        'age_maxhr': age * maxhr / 100,
        'oldpeak_restingbp': oldpeak * restingbp / 100,
        'restingbp_chol': restingbp * cholesterol / 10000,
        'maxhr_sq': maxhr ** 2 / 100,
        'oldpeak_sq': oldpeak ** 2,
        'chol_zero': 1.0 if cholesterol == 0 else 0.0,
    }
    for col in meta['engineered_features']:
        vals.append(eng.get(col, 0.0))

    X = np.array([vals])
    X_scaled = scaler.transform(X)
    prob = float(model.predict(X_scaled, verbose=0)[0][0])
    th = meta['best_threshold']
    return prob, th

tests = [
    # Low risk cases
    ('Low 1', {'Age': 24, 'Sex': 'F', 'ChestPainType': 'NAP', 'RestingBP': 112, 'Cholesterol': 165,
               'FastingBS': 0, 'RestingECG': 'Normal', 'MaxHR': 188, 'ExerciseAngina': 'N', 'Oldpeak': 0, 'ST_Slope': 'Up'}),
    ('Low 2', {'Age': 30, 'Sex': 'F', 'ChestPainType': 'ATA', 'RestingBP': 118, 'Cholesterol': 180,
               'FastingBS': 0, 'RestingECG': 'Normal', 'MaxHR': 175, 'ExerciseAngina': 'N', 'Oldpeak': 0.2, 'ST_Slope': 'Up'}),
    ('Low 3', {'Age': 25, 'Sex': 'F', 'ChestPainType': 'TA', 'RestingBP': 110, 'Cholesterol': 200,
               'FastingBS': 0, 'RestingECG': 'Normal', 'MaxHR': 180, 'ExerciseAngina': 'N', 'Oldpeak': 0, 'ST_Slope': 'Up'}),
    # High risk cases
    ('High 1', {'Age': 60, 'Sex': 'M', 'ChestPainType': 'ASY', 'RestingBP': 140, 'Cholesterol': 240,
                'FastingBS': 1, 'RestingECG': 'LVH', 'MaxHR': 110, 'ExerciseAngina': 'Y', 'Oldpeak': 2.0, 'ST_Slope': 'Flat'}),
    ('High 2', {'Age': 55, 'Sex': 'M', 'ChestPainType': 'ASY', 'RestingBP': 160, 'Cholesterol': 0,
                'FastingBS': 1, 'RestingECG': 'ST', 'MaxHR': 90, 'ExerciseAngina': 'Y', 'Oldpeak': 3.5, 'ST_Slope': 'Down'}),
    ('High 3', {'Age': 65, 'Sex': 'M', 'ChestPainType': 'NAP', 'RestingBP': 150, 'Cholesterol': 280,
                'FastingBS': 0, 'RestingECG': 'LVH', 'MaxHR': 120, 'ExerciseAngina': 'Y', 'Oldpeak': 1.5, 'ST_Slope': 'Flat'}),
]

print(f'Threshold: {meta["best_threshold"]:.2f}')
for name, input_data in tests:
    prob, th = predict(input_data)
    pred = 'Heart Disease' if prob > th else 'No Heart Disease'
    if prob >= 0.80:
        risk = 'High'
    elif prob >= 0.40:
        risk = 'Moderate'
    else:
        risk = 'Low'
    print(f'{name:8s}: prob={prob:.3f} pred={pred:16s} risk={risk:8s}')
