import base64
from datetime import datetime
import json
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# ==========================================
# LIVE PRODUCTION CONFIGURATION
# ==========================================
CONSUMER_KEY = "y14tLcAAioPB48fpU883PoEhIjd14MNRPBex7hBqFA39bjUx"
CONSUMER_SECRET = "81QaAvwAFAwbLf6WrfvIc6aXHMa6LOLvNlGoCvIo2u6JTQNtBVsNWsjesqGqsctB"
PASSKEY = "d193880a84cd59e45133c944b9851b3c497881e1994e4e66b8030c992e3b296e"
BUSINESS_SHORTCODE = "5156152"
CALLBACK_URL = "https://yourdomain.com"

TOKEN_URL = "https://safaricom.co.ke"
STK_PUSH_URL = "https://safaricom.co.ke"

@app.route('/')
def home():
    return "M-Pesa POS Gateway Live Node"

@app.route('/trigger-push', methods=['GET', 'POST'])
def execute_direct_push():
    raw_credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
    encoded_credentials = base64.b64encode(raw_credentials.encode("utf-8")).decode("utf-8")
    
    token_headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(TOKEN_URL, headers=token_headers, timeout=15)
        if response.status_code != 200:
            return jsonify({"error": "Auth Failed", "details": response.text}), 400
        access_token = response.json().get("access_token")
    except Exception as e:
        return jsonify({"error": f"Connection Failed: {e}"}), 500

    # 2. TRIGGER STK PUSH PROTOCOL VIA DERIVED KEY
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    raw_password = f"{BUSINESS_SHORTCODE}{PASSKEY}{timestamp}"
    encoded_password = base64.b64encode(raw_password.encode("utf-8")).decode("utf-8")

    payload = {
        "BusinessShortCode": BUSINESS_SHORTCODE,
        "Password": encoded_password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerBuyGoodsOnline",
        "Amount": 1,
        "PartyA": "254715647500",
        "PartyB": BUSINESS_SHORTCODE,
        "PhoneNumber": "254715647500",
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "AroniumTest",
        "TransactionDesc": "Live Test",
    }

    push_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        push_response = requests.post(STK_PUSH_URL, json=payload, headers=push_headers, timeout=15)
        return jsonify(push_response.json()), push_response.status_code
    except Exception as e:
        return jsonify({"error": f"Processing Error: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
