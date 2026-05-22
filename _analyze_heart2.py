import pandas as pd
import numpy as np

df = pd.read_csv('datasets/heart.csv')

print('Cholesterol=0 by HeartDisease:')
print(df[df['Cholesterol']==0]['HeartDisease'].value_counts())
print()

print('Cholesterol median by target:')
print(df.groupby('HeartDisease')['Cholesterol'].median())
print()

# Before vs after imputation effect on correlation
from sklearn.preprocessing import LabelEncoder
df_c = df.copy()
for c in df_c.columns:
    if pd.api.types.is_string_dtype(df_c[c]):
        le = LabelEncoder()
        df_c[c] = le.fit_transform(df_c[c])

print('Cholesterol vs target BEFORE imputation:', df_c['Cholesterol'].corr(df_c['HeartDisease']))

# After imputation
df2 = df.copy()
chol_med = df2.groupby('HeartDisease')['Cholesterol'].transform('median')
df2['Cholesterol'] = df2['Cholesterol'].replace(0, np.nan).fillna(chol_med)
df2_c = df2.copy()
for c in df2_c.columns:
    if pd.api.types.is_string_dtype(df2_c[c]):
        le = LabelEncoder()
        df2_c[c] = le.fit_transform(df2_c[c])
print('Cholesterol vs target AFTER imputation:', df2_c['Cholesterol'].corr(df2_c['HeartDisease']))

# Also check: what was the original correlation with zero-chol rows vs without
print()
print('Zero-chol rows HeartDisease distribution:', df[df['Cholesterol']==0]['HeartDisease'].value_counts(normalize=True).round(3))
print('Non-zero-chol rows HeartDisease distribution:', df[df['Cholesterol']!=0]['HeartDisease'].value_counts(normalize=True).round(3))
