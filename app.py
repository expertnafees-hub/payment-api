from flask import Flask, jsonify, request
import os
import uuid
import time

app = Flask(__name__)

# System metadata
SERVICE_NAME = os.getenv("SERVICE_NAME", "payment-api")
VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": SERVICE_NAME,
        "version": VERSION,
        "status": "online",
        "timestamp": int(time.time())
    }), 200

# 1. Critical Health Check Endpoint for AWS ALB & ECS
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": SERVICE_NAME,
        "environment": ENVIRONMENT
    }), 200

# 2. Payment Processing Endpoint
@app.route("/api/v1/payments", methods=["POST"])
def process_payment():
    data = request.get_json(silent=True) or {}
    amount = data.get("amount", 0)
    currency = data.get("currency", "USD")

    if amount <= 0:
        return jsonify({"error": "Invalid amount. Must be greater than 0"}), 400

    # Simulate transaction processing
    transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
    return jsonify({
        "transaction_id": transaction_id,
        "amount": amount,
        "currency": currency,
        "status": "APPROVED",
        "processed_at": int(time.time())
    }), 201

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
