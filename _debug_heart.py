import json, pickle, numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow import keras

meta = json.load(open('backend/static/ml_assets/heart_meta.json'))
model = keras.models.load_model('backend/static/ml_assets/heart_model.keras')
scaler = pickle.load(open('backend/static/ml_assets/heart_scaler.pkl', 'rb'))

print('Threshold:', meta['best_threshold'])
print('Cat mappings:', meta['categorical_mappings'])
print('Eng feats:', meta['engineered_features'])

cat_map = meta['categorical_mappings']
base = meta['base_features']

test_cases = [
    {'Age': 24, 'Sex': 'F', 'ChestPainType': 'NAP', 'RestingBP': 112, 'Cholesterol': 165,
     'FastingBS': 0, 'RestingECG': 'Normal', 'MaxHR': 188, 'ExerciseAngina': 'N', 'Oldpeak': 0, 'ST_Slope': 'Up'},
    {'Age': 30, 'Sex': 'F', 'ChestPainType': 'ATA', 'RestingBP': 118, 'Cholesterol': 180,
     'FastingBS': 0, 'RestingECG': 'Normal', 'MaxHR': 175, 'ExerciseAngina': 'N', 'Oldpeak': 0.2, 'ST_Slope': 'Up'},
    {'Age': 60, 'Sex': 'M', 'ChestPainType': 'ASY', 'RestingBP': 140, 'Cholesterol': 240,
     'FastingBS': 1, 'RestingECG': 'LVH', 'MaxHR': 110, 'ExerciseAngina': 'Y', 'Oldpeak': 2.0, 'ST_Slope': 'Flat'},
]

for i, input_data in enumerate(test_cases):
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
    print(f'\nTest case {i+1}: prob={prob:.4f}, th={th:.2f}, pred={prob>th}, margin={prob-th:.3f}')
    print(f'  vals: age={vals[0]}, chol={vals[4]}, maxhr={vals[7]}, oldpeak={vals[9]}')
    print(f'  eng: age_maxhr={eng["age_maxhr"]:.2f}, chol_zero={eng["chol_zero"]}')
