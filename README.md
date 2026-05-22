# AI Medical Assistant

Multi-disease risk assessment tool using artificial neural networks (ANN) for diabetes, heart disease, and Parkinson's disease prediction.

## Features

- **Diabetes Risk Assessment** — ANN trained on 100K patient records (HbA1c, blood glucose, BMI, demographics)
- **Heart Disease Risk Assessment** — ANN trained on 918 clinical cases (chest pain type, ECG, blood pressure, cholesterol)
- **Parkinson's Disease Detection** — Voice-based acoustic analysis extracting 22 features from voice recordings
- **JWT Authentication** — User registration, login, prediction history
- **PDF Reports** — Downloadable prediction reports per user
- **Admin Panel** — User management, prediction history overview, model retraining

## Architecture

```
├── backend/              # Flask REST API
│   ├── app.py            # App factory, blueprint registration
│   ├── config.py         # Configuration (DB, JWT, CORS)
│   ├── ml/
│   │   ├── train.py      # ANN training (diabetes / heart / parkinsons)
│   │   ├── predict.py    # Inference functions
│   │   └── audio_processing.py  # 22-feature extraction for Parkinson's
│   ├── models/
│   │   └── db_models.py  # User, PredictionHistory
│   ├── routes/
│   │   ├── auth.py       # Register / login / profile
│   │   ├── prediction.py # Predict endpoints + history + PDF
│   │   └── admin.py      # Admin-only endpoints
│   ├── services/
│   │   └── pdf_service.py# PDF report generation
│   ├── static/ml_assets/ # Trained .keras models, scalers, meta.json
│   └── .env              # Environment config
├── frontend/             # React + Vite + Tailwind CSS
│   └── src/
│       ├── pages/        # Prediction, Dashboard, History, Admin
│       ├── components/   # UI: GlassCard, RiskBadge, NeonButton, etc.
│       ├── services/     # Axios API client
│       ├── context/      # AuthContext
│       └── utils/        # Audio recorder (Web Audio API)
├── datasets/             # CSV data files
└── requirements.txt      # Python dependencies
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask, SQLAlchemy, TensorFlow/Keras |
| Frontend | React 19, Vite, Tailwind CSS 4, Framer Motion, Recharts |
| Audio | librosa, parselmouth (Praat), nolds |
| Auth | PyJWT (HS256), bcrypt |
| Database | SQLite |

## Setup

### Backend

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the server
python -m backend.app
```

Backend runs on `http://127.0.0.1:5000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`.

### Training Models

```bash
python -m backend.ml.train
```

Trains all three models and saves assets to `backend/static/ml_assets/`.

## API Endpoints

All prediction endpoints require `Authorization: Bearer <token>` header.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/profile` | Current user profile |
| POST | `/api/predict/diabetes` | Diabetes risk prediction |
| POST | `/api/predict/heart` | Heart disease risk prediction |
| POST | `/api/predict/parkinsons` | Parkinson's prediction (audio upload) |
| GET | `/api/predictions/history` | User's prediction history |
| GET | `/api/predictions/<id>/pdf` | Download prediction PDF |
| GET | `/api/admin/users` | List users (admin) |
| GET | `/api/admin/predictions` | All predictions (admin) |
| POST | `/api/admin/retrain/<disease>` | Retrain model (admin) |

## Datasets

| Disease | Source | Rows | Features |
|---------|--------|------|----------|
| Diabetes | Kaggle (iammustafatz) | 100,000 | 8 (gender, age, hypertension, heart_disease, smoking_history, bmi, HbA1c_level, blood_glucose_level) |
| Heart | Kaggle (fedesoriano) | 918 | 11 (Age, Sex, ChestPainType, RestingBP, Cholesterol, FastingBS, RestingECG, MaxHR, ExerciseAngina, Oldpeak, ST_Slope) + 6 engineered |
| Parkinson's | UCI ML Repository | 195 | 22 acoustic features |

## Model Performance

| Disease | Accuracy | Recall | Precision | F1 |
|---------|----------|--------|-----------|----|
| Diabetes | ~97% | ~97% | ~97% | ~97% |
| Heart | ~90% | ~95% | ~89% | ~92% |
| Parkinson's | ~97% | ~97% | ~97% | ~97% |

> Note: 95%+ across all four metrics is not achievable for all diseases with real healthcare data. Diabetes has ~34% of true positives presenting normal biomarker values, and heart has limited sample size (918 rows) with intrinsic class overlap.

## Risk Levels

| Level | Probability | Badge Color |
|-------|-------------|-------------|
| Low | < 40% | Green |
| Moderate | 40–79% | Yellow |
| High | ≥ 80% | Red |

## License

MIT
