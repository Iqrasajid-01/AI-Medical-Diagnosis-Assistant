import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

df = pd.read_csv('datasets/heart.csv')

print('Chol=0:', (df['Cholesterol']==0).sum())
print('BP=0:', (df['RestingBP']==0).sum())
print()
print('Cholesterol desc:')
print(df['Cholesterol'].describe())
print()

df_c = df.copy()
for c in df_c.columns:
    if pd.api.types.is_string_dtype(df_c[c]):
        le = LabelEncoder()
        df_c[c] = le.fit_transform(df_c[c])
print('Corr with target:')
corr = df_c.corr()['HeartDisease'].abs().sort_values(ascending=False)
print(corr)
print()

print('ST_Slope vs target:')
print(pd.crosstab(df['ST_Slope'], df['HeartDisease']))
print()
print('ChestPainType vs target:')
print(pd.crosstab(df['ChestPainType'], df['HeartDisease']))
print()
print('ExerciseAngina vs target:')
print(pd.crosstab(df['ExerciseAngina'], df['HeartDisease']))
print()

# Find best single thresholds
print('Oldpeak distribution by target:')
print(df.groupby('HeartDisease')['Oldpeak'].describe())
