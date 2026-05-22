"""
Prediction routes — diabetes, heart disease, parkinsons, history, and PDF.
"""
import os
import json

from flask import Blueprint, request, jsonify, send_file, current_app

from backend.models.db_models import db, PredictionHistory
from backend.routes.auth import token_required
from backend.ml.predict import predict_diabetes, predict_heart, predict_parkinsons
from backend.ml.audio_processing import extract_features_from_bytes
from backend.services.pdf_service import generate_prediction_pdf

prediction_bp = Blueprint('prediction', __name__, url_prefix='/api')


@prediction_bp.route('/predict/diabetes', methods=['POST'])
@token_required
def diabetes_prediction(current_user):
    """Predict diabetes with smart input handling."""
    data = request.get_json(silent=True) or {}

    try:
        result = predict_diabetes(data)
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

    # Save to history
    record = PredictionHistory(
        user_id=current_user.id,
        disease_type='diabetes',
        input_data=data,
        prediction_result=result['prediction'],
        confidence=result['confidence'],
    )
    db.session.add(record)
    db.session.commit()

    result['id'] = record.id
    return jsonify(result), 200


@prediction_bp.route('/predict/heart', methods=['POST'])
@token_required
def heart_prediction(current_user):
    """Predict heart disease with smart input handling."""
    data = request.get_json(silent=True) or {}

    try:
        result = predict_heart(data)
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

    record = PredictionHistory(
        user_id=current_user.id,
        disease_type='heart',
        input_data=data,
        prediction_result=result['prediction'],
        confidence=result['confidence'],
    )
    db.session.add(record)
    db.session.commit()

    result['id'] = record.id
    return jsonify(result), 200


@prediction_bp.route('/predict/parkinsons', methods=['POST'])
@token_required
def parkinsons_prediction(current_user):
    """Predict Parkinson's disease from uploaded audio."""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    if not audio_file.filename:
        return jsonify({'error': 'Empty audio filename'}), 400

    try:
        audio_bytes = audio_file.read()
        features = extract_features_from_bytes(audio_bytes, audio_file.filename)
        result = predict_parkinsons(features)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

    record = PredictionHistory(
        user_id=current_user.id,
        disease_type='parkinsons',
        input_data=features,
        prediction_result=result['prediction'],
        confidence=result['confidence'],
    )
    db.session.add(record)
    db.session.commit()

    result['id'] = record.id
    return jsonify(result), 200


@prediction_bp.route('/predictions/history', methods=['GET'])
@token_required
def prediction_history(current_user):
    """Get current user's prediction history."""
    records = (
        PredictionHistory.query
        .filter_by(user_id=current_user.id)
        .order_by(PredictionHistory.created_at.desc())
        .all()
    )
    return jsonify({'predictions': [r.to_dict() for r in records]}), 200


@prediction_bp.route('/predictions/<int:pred_id>/pdf', methods=['GET'])
@token_required
def download_pdf(current_user, pred_id):
    """Generate and download PDF report for a prediction."""
    record = PredictionHistory.query.get(pred_id)
    if record is None:
        return jsonify({'error': 'Prediction not found'}), 404
    if record.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403

    try:
        pdf_path = generate_prediction_pdf(record, current_user)
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'prediction_report_{pred_id}.pdf',
        )
    except Exception as e:
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500
