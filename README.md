# AI Medical Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.18-FF6F00?logo=tensorflow&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?logo=tailwindcss&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**Multi-disease risk assessment powered by artificial neural networks (ANN).**  
Predicts diabetes, heart disease, and Parkinson's disease from clinical parameters and voice recordings.

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Datasets](#datasets)
- [Model Performance](#model-performance)
- [Risk Classification](#risk-classification)
- [Project Structure](#project-structure)
- [Development](#development)
- [License](#license)

---

## Overview

AI Medical Assistant is a full-stack web application that uses artificial neural networks to assess disease risk from clinical data. It serves three distinct prediction pipelines:

| Disease | Modality | Input | Model |
|---------|----------|-------|-------|
| **Diabetes** | Clinical parameters | HbA1c, blood glucose, BMI, demographics | ANN (8 features, 100K training rows) |
| **Heart Disease** | Clinical parameters | Chest pain type, ECG, BP, cholesterol, age | ANN (11 base + 6 engineered features, 918 rows) |
| **Parkinson's Disease** | Voice recording | Sustained vowel phonation (22 acoustic features) | ANN (22 features, 195 rows) |

The system includes JWT-based authentication, user prediction history, and downloadable PDF reports.

---

## Features

- **Three disease models** — Diabetes, heart disease, Parkinson's disease under one interface
- **Voice-based Parkinson's screening** — Record or upload a `.wav` file; extracts all 22 standard UCI acoustic features via librosa + parselmouth + nolds
- **Feature engineering** — Heart model augments 11 base features with 6 derived interactions (`age_maxhr`, `oldpeak_restingbp`, `restingbp_chol`, `maxhr_sq`, `oldpeak_sq`, `chol_zero`)
- **Threshold-tuned predictions** — Each model uses an optimal probability threshold (maximizing recall on validation) instead of the default 0.5 cutoff
- **Risk level stratification** — Probability output mapped to Low / Moderate / High risk bands
- **JWT authentication** — Register, login, and secured endpoints (24h token expiry)
- **Prediction history** — Per-user audit trail of all past assessments
- **PDF export** — Download individual prediction reports
- **Admin panel** — User management, global prediction overview, model retraining trigger
- **Responsive UI** — React 19 with Tailwind CSS 4, dark theme, animated components

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Frontend (React + Vite)                      │
│  localhost:5173                                                     │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌──────────────────────┐ │
│  │Prediction│ │Dashboard │ │  History   │ │    Admin Panel       │ │
│  │  Forms   │ │          │ │            │ │                      │ │
│  └────┬─────┘ └──────────┘ └────────────┘ └──────────────────────┘ │
│       │                    axios                                    │
└───────┼─────────────────────────────────────────────────────────────┘
        │  HTTP / JSON / FormData (audio)
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Backend (Flask, port 5000)                        │
│                                                                     │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────────────┐  │
│  │  Routes  │  │   ML Engine  │  │  Database (SQLite)            │  │
│  │          │  │              │  │  ┌──────────┐ ┌─────────────┐ │  │
│  │ /auth    │  │ predict.py   │  │  │  Users   │ │ Predictions │ │  │
│  │ /predict │──│ train.py     │──│  └──────────┘ └─────────────┘ │  │
│  │ /admin   │  │ audio_proc.. │  └──────────────────────────────┘  │
│  └──────────┘  └──────┬───────┘                                    │
│                       │                                            │
│              ┌────────┴────────┐                                   │
│              │  ml_assets/     │  (.keras models, scalers, meta)   │
│              └─────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────┘
```

### Request Flow

1. User fills form (or records audio) on the frontend
2. Frontend sends POST request with `Authorization: Bearer <jwt>` header
3. Flask route validates token via `@token_required` decorator
4. Route delegates to `predict.py` which:
   - Loads the cached model (`.keras`) and scaler (`.pkl`) from `ml_assets/`
   - Encodes categorical features using saved mappings from `meta.json`
   - Computes engineered features (heart only)
   - Scales input and runs inference
   - Applies tuned threshold and risk classification
5. Result is saved to `PredictionHistory` table in SQLite
6. JSON response returned to frontend

---

## Tech Stack

### Backend

| Component | Technology |
|-----------|-----------|
| Framework | Flask 3.x |
| ORM | Flask-SQLAlchemy |
| Auth | PyJWT (HS256) |
| Deep Learning | TensorFlow 2.18 / Keras |
| Audio Processing | librosa, parselmouth (Praat wrapper), nolds |
| Data | pandas, NumPy, scikit-learn |
| PDF | reportlab |
| CORS | Flask-CORS |

### Frontend

| Component | Technology |
|-----------|-----------|
| Framework | React 19 |
| Build Tool | Vite 6 |
| Styling | Tailwind CSS 4 |
| Animation | Framer Motion 11 |
| Charts | Recharts 2 |
| HTTP | Axios 1.7 |
| Audio Recording | Web Audio API + wavesurfer.js |

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### 1. Clone and Install Backend

```bash
# Create virtual environment
python -m venv .venv

# Activate
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Edit backend/.env if needed (defaults work out of the box)
SECRET_KEY=medical-ai-secret-key-2024
DATABASE_URL=sqlite:///medical_ai.db
JWT_EXPIRATION_HOURS=24
```

### 3. (Optional) Train Models

Pre-trained models are included. To retrain from scratch:

```bash
python -m backend.ml.train
```

Training outputs `.keras` model, `.pkl` scaler, and `meta.json` for each disease into `backend/static/ml_assets/`.

### 4. Start the Backend

```bash
python -m backend.app
```

Server starts at `http://127.0.0.1:5000`.

### 5. Install and Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

App opens at `http://localhost:5173`.

---

## API Reference

### Authentication

All prediction endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

#### Register

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123"
}
```

Response `201`:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": { "id": 1, "username": "johndoe", "email": "john@example.com", "role": "user" }
}
```

#### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepass123"
}
```

Response `200` — same shape as register.

### Predictions

#### Diabetes

```http
POST /api/predict/diabetes
Authorization: Bearer <token>
Content-Type: application/json

{
  "gender": "Male",
  "age": 55,
  "hypertension": 1,
  "heart_disease": 0,
  "smoking_history": "former",
  "bmi": 28.5,
  "HbA1c_level": 6.8,
  "blood_glucose_level": 150
}
```

#### Heart Disease

```http
POST /api/predict/heart
Authorization: Bearer <token>
Content-Type: application/json

{
  "Age": 55,
  "Sex": "M",
  "ChestPainType": "ASY",
  "RestingBP": 140,
  "Cholesterol": 240,
  "FastingBS": 1,
  "RestingECG": "LVH",
  "MaxHR": 110,
  "ExerciseAngina": "Y",
  "Oldpeak": 2.0,
  "ST_Slope": "Flat"
}
```

#### Parkinson's

```http
POST /api/predict/parkinsons
Authorization: Bearer <token>
Content-Type: multipart/form-data

# Field: audio (file, .wav format, max 2MB, max 10 seconds)
```

#### Response (all prediction endpoints)

```json
{
  "prediction": 1,
  "confidence": 0.9321,
  "risk_level": "High",
  "disease": "heart",
  "id": 42
}
```

| Field | Type | Description |
|-------|------|-------------|
| `prediction` | int | 0 = negative, 1 = positive |
| `confidence` | float | Raw probability output (0–1) |
| `risk_level` | string | `"Low"`, `"Moderate"`, or `"High"` |
| `disease` | string | `"diabetes"`, `"heart"`, or `"parkinsons"` |
| `id` | int | Prediction history record ID |

### History & Reporting

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/predictions/history` | Returns all predictions for the authenticated user |
| GET | `/api/predictions/<id>/pdf` | Downloads a PDF report for a specific prediction |

### Admin Endpoints

Require `role: "admin"` in the JWT payload.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users` | List all users |
| GET | `/api/admin/predictions` | List all predictions across all users |
| POST | `/api/admin/retrain/<disease>` | Trigger model retraining for `diabetes`, `heart`, or `parkinsons` |

---

## Datasets

| Disease | Source | Rows | Features | Target |
|---------|--------|------|----------|--------|
| **Diabetes** | [Kaggle — iammustafatz](https://www.kaggle.com/datasets/iammustafatz/diabetes-prediction-dataset) | 100,000 | gender, age, hypertension, heart_disease, smoking_history, bmi, HbA1c_level, blood_glucose_level | `diabetes` (binary) |
| **Heart** | [Kaggle — fedesoriano](https://www.kaggle.com/datasets/fedesoriano/heart-failure-prediction) | 918 | Age, Sex, ChestPainType, RestingBP, Cholesterol, FastingBS, RestingECG, MaxHR, ExerciseAngina, Oldpeak, ST_Slope + 6 engineered | `HeartDisease` (binary) |
| **Parkinson's** | [UCI ML Repository](https://archive.ics.uci.edu/dataset/174/parkinsons) | 195 | 22 acoustic features (fundamental frequency, jitter, shimmer, NHR, HNR, RPDE, DFA, etc.) | `status` (binary: 1 = Parkinson's) |

### Notes

- **Cholesterol = 0** is preserved in the heart dataset rather than imputed. 88.4% of zero-cholesterol rows are positive for heart disease — a clinically meaningful signal. An additional `chol_zero` flag feature is added.
- **RestingBP = 0** is corrected via median imputation (anomalous entries only).
- **Categorical encoding** uses scikit-learn `LabelEncoder` with saved `.classes_` mappings for deterministic inference.

---

## Model Performance

Metrics on held-out test sets (20% split) after threshold tuning:

| Disease | Accuracy | Recall | Precision | F1 Score | AUC | Threshold |
|---------|----------|--------|-----------|----------|-----|-----------|
| Diabetes | 97.22% | 97.09% | 96.67% | 96.88% | 0.995 | 0.87 |
| Heart | 90.22% | 94.74% | 88.89% | 91.72% | 0.940 | 0.44 |
| Parkinson's | 97.44% | 100.0% | 94.44% | 97.14% | 0.995 | 0.50 |

### Design Notes

- **Threshold tuning** maximizes recall (sensitivity) to minimize false negatives, which is the clinically preferred trade-off for screening applications.
- **95%+ across all four metrics is not achievable** for all diseases with real healthcare data:
  - Diabetes: ~34% of true-positive patients present normal biomarker values (HbA1c < 5.7, glucose < 100), creating irreducible class overlap in feature space.
  - Heart: limited sample size (918 rows) and intrinsic overlap in ECG/blood pressure values between positive and negative classes cap the ceiling near 90%.
  - Parkinson's: very small sample (195 rows) with high-dimensional (22) features; high accuracy but limited generalizability.
- **Heart model uses 5-fold cross-validation** and engineered features to extract maximum signal from the 918-row dataset.
- Models were trained with class weighting to address imbalance where present.

### Architecture Details

| Disease | Architecture | Hidden Units | Activation | Epochs | Batch |
|---------|-------------|--------------|------------|--------|-------|
| Diabetes | 3 hidden layers | 64 → 32 → 16 | ReLU → Sigmoid | 50 | 32 |
| Heart | 3 hidden layers | 64 → 32 → 16 | ReLU → Sigmoid | 100 | 16 |
| Parkinson's | 3 hidden layers | 128 → 64 → 32 | ReLU → Sigmoid | 100 | 8 |

---

## Risk Classification

The raw probability output is mapped to one of three risk levels:

| Level | Probability Range | Display |
|-------|------------------|---------|
| **Low** | < 0.40 | Green badge |
| **Moderate** | 0.40 – 0.79 | Yellow badge |
| **High** | ≥ 0.80 | Red badge |

These thresholds balance providing early warning (Moderate catches borderline cases) while reserving High for high-confidence predictions.

---

## Project Structure

```
AI Medical Assistant/
├── backend/
│   ├── app.py                      # Flask app factory and blueprint registration
│   ├── config.py                   # Environment-based configuration
│   ├── .env                        # Environment variables (SECRET_KEY, DB, etc.)
│   ├── ml/
│   │   ├── train.py                # Model training pipeline for all 3 diseases
│   │   ├── predict.py              # Inference functions with categorical encoding
│   │   └── audio_processing.py     # 22 acoustic feature extraction from voice
│   ├── models/
│   │   └── db_models.py            # SQLAlchemy User and PredictionHistory models
│   ├── routes/
│   │   ├── auth.py                 # Register, login, profile, token_required decorator
│   │   ├── prediction.py           # Diabetes/heart/parkinsons predict + history + PDF
│   │   └── admin.py                # Admin user/prediction listing, retrain trigger
│   ├── services/
│   │   └── pdf_service.py          # PDF report generation via reportlab
│   ├── static/
│   │   └── ml_assets/              # Trained models (.keras), scalers (.pkl), meta (.json)
│   └── uploads/                    # Uploaded audio files (temporary)
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Prediction.jsx      # Main prediction forms (diabetes/heart/parkinsons)
│   │   │   ├── Dashboard.jsx       # User dashboard with statistics
│   │   │   ├── History.jsx         # Prediction history table
│   │   │   ├── AdminDashboard.jsx  # Admin panel
│   │   │   ├── LandingPage.jsx     # Public landing page
│   │   │   ├── LoginPage.jsx       # Login form
│   │   │   └── RegisterPage.jsx    # Registration form
│   │   ├── components/
│   │   │   ├── UI/                 # GlassCard, RiskBadge, ConfidenceBar, NeonButton, etc.
│   │   │   └── Layout/            # Navbar, Sidebar
│   │   ├── services/
│   │   │   └── api.js             # Axios API client
│   │   ├── context/
│   │   │   └── AuthContext.jsx    # Authentication context provider
│   │   └── utils/
│   │       └── audioRecorder.js    # Web Audio API recording utility
│   ├── package.json
│   └── vite.config.js
├── datasets/
│   ├── diabetes.csv                # 100K rows
│   ├── heart.csv                   # 918 rows
│   └── Parkinsons disease.csv      # 195 rows, 22 features
├── requirements.txt                # Python dependencies
└── README.md
```

---

## Development

### Running Tests

```bash
# Test heart model inference (standalone)
python _test_heart.py
```

### Training Individual Models

```python
# From train.py:
# train_diabetes()   — trains and saves diabetes model
# train_heart()      — trains and saves heart model (5-fold CV)
# train_parkinsons() — trains and saves Parkinsons model
```

Run all three sequentially:

```bash
python -m backend.ml.train
```

### Adding a New Dataset

1. Place CSV in `datasets/`
2. Add training function in `train.py` following the existing pattern
3. Add prediction function in `predict.py`
4. Register a new route in `routes/prediction.py`
5. Add form in `pages/Prediction.jsx`

### Categorical Encoding (Important)

The `encode_categoricals()` function uses `LabelEncoder` which sorts classes alphabetically. The saved mapping must use `le.classes_` to build the dictionary, not the original input list order. This was a resolved bug — see `train.py` for the correct implementation.

---

## License

MIT

---

## Acknowledgments

- UCI Machine Learning Repository for the Parkinson's dataset
- Kaggle users iammustafatz and fedesoriano for the diabetes and heart datasets
- The librosa, parselmouth, and nolds open-source projects
