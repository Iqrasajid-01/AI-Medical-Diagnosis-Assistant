"""
Mock email service — logs email sends to console.

In a production environment this would integrate with an SMTP server
or service like SendGrid / AWS SES.
"""
import json
from datetime import datetime


def send_report_email(to_email, prediction_data):
    """
    Mock-send a prediction report via email.

    Parameters
    ----------
    to_email : str
        Recipient email address.
    prediction_data : dict
        Prediction result data to include in the email.

    Returns
    -------
    dict
        Status message.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print("=" * 60)
    print(f"📧 MOCK EMAIL SERVICE — {timestamp}")
    print("=" * 60)
    print(f"  To:      {to_email}")
    print(f"  Subject: AI Medical Diagnosis Report")
    print(f"  Body:")
    print(f"    Dear Patient,")
    print(f"")
    print(f"    Your medical prediction report is ready.")
    print(f"    Disease: {prediction_data.get('disease', 'N/A')}")
    print(f"    Result:  {'Positive (At Risk)' if prediction_data.get('prediction') == 1 else 'Negative (Low Risk)'}")
    print(f"    Confidence: {prediction_data.get('confidence', 0) * 100:.1f}%")
    print(f"    Risk Level: {prediction_data.get('risk_level', 'N/A')}")
    print(f"")
    print(f"    ⚠️ This is for educational purposes only.")
    print(f"    Please consult a healthcare professional.")
    print(f"")
    print(f"    — AI Medical Diagnosis Assistant")
    print("=" * 60)

    return {
        'success': True,
        'message': f'Report email sent to {to_email} (mock)',
        'timestamp': timestamp,
    }
