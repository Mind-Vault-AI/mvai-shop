"""
MindVault-AI Webhook Handler
Domain: mvai.store.nl

Handles:
- Payment webhooks (Stripe, Mollie, PayPal)
- Telegram bot updates
- General webhooks

Deploy: Vercel, Railway, or any Python host
"""

import os
import json
import hmac
import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables (set these in your deployment platform)
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
MOLLIE_WEBHOOK_SECRET = os.getenv("MOLLIE_WEBHOOK_SECRET", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")  # General webhook secret


# ============================================
# Verification Functions
# ============================================

def verify_stripe_signature(payload: bytes, signature: str) -> bool:
    """Verify Stripe webhook signature."""
    if not STRIPE_WEBHOOK_SECRET:
        logger.warning("STRIPE_WEBHOOK_SECRET not set")
        return False

    try:
        # Stripe uses timestamp.signature format
        parts = signature.split(",")
        timestamp = None
        signatures = []

        for part in parts:
            key, value = part.split("=")
            if key == "t":
                timestamp = value
            elif key == "v1":
                signatures.append(value)

        if not timestamp or not signatures:
            return False

        # Create expected signature
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        expected_sig = hmac.new(
            STRIPE_WEBHOOK_SECRET.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return any(hmac.compare_digest(expected_sig, sig) for sig in signatures)
    except Exception as e:
        logger.error(f"Stripe signature verification failed: {e}")
        return False


def verify_telegram_token(token: str) -> bool:
    """Verify Telegram bot token in URL."""
    return hmac.compare_digest(token, TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else False


def verify_general_signature(payload: bytes, signature: str) -> bool:
    """Verify general webhook HMAC signature."""
    if not WEBHOOK_SECRET:
        return True  # Skip if no secret set

    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


# ============================================
# Webhook Handlers
# ============================================

def handle_stripe_webhook(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle Stripe webhook events.

    Events:
    - checkout.session.completed
    - payment_intent.succeeded
    - customer.subscription.created
    """
    event_type = event.get("type", "")
    data = event.get("data", {}).get("object", {})

    logger.info(f"Stripe event: {event_type}")

    if event_type == "checkout.session.completed":
        # Payment successful
        customer_email = data.get("customer_email")
        amount = data.get("amount_total", 0) / 100  # Convert from cents

        logger.info(f"Payment completed: {customer_email} - €{amount}")

        # TODO:
        # 1. Send confirmation email
        # 2. Grant access to products
        # 3. Update database

        return {
            "status": "success",
            "event": event_type,
            "customer": customer_email,
            "amount": amount
        }

    elif event_type == "payment_intent.succeeded":
        payment_id = data.get("id")
        logger.info(f"Payment intent succeeded: {payment_id}")
        return {"status": "success", "payment_id": payment_id}

    elif event_type == "customer.subscription.created":
        subscription_id = data.get("id")
        logger.info(f"Subscription created: {subscription_id}")
        return {"status": "success", "subscription_id": subscription_id}

    return {"status": "ignored", "event": event_type}


def handle_mollie_webhook(payment_id: str) -> Dict[str, Any]:
    """
    Handle Mollie payment webhooks.

    Mollie sends payment ID, you need to fetch status via API.
    """
    logger.info(f"Mollie webhook: payment_id={payment_id}")

    # TODO: Fetch payment status from Mollie API
    # from mollie.api.client import Client
    # mollie = Client()
    # mollie.set_api_key(os.getenv("MOLLIE_API_KEY"))
    # payment = mollie.payments.get(payment_id)

    return {
        "status": "received",
        "payment_id": payment_id,
        "message": "Fetch payment status from Mollie API"
    }


def handle_telegram_update(update: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle Telegram bot updates.

    Update types:
    - message
    - callback_query
    - inline_query
    """
    update_id = update.get("update_id")

    # Handle message
    if "message" in update:
        message = update["message"]
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        user = message.get("from", {})

        logger.info(f"Telegram message from {user.get('username')}: {text}")

        # Command handling
        if text.startswith("/start"):
            return handle_telegram_command("start", chat_id, user)
        elif text.startswith("/challenge"):
            return handle_telegram_command("challenge", chat_id, user)
        elif text.startswith("/checkin"):
            return handle_telegram_command("checkin", chat_id, user)
        elif text.startswith("/stats"):
            return handle_telegram_command("stats", chat_id, user)

    # Handle callback query (button presses)
    if "callback_query" in update:
        callback = update["callback_query"]
        callback_data = callback.get("data", "")
        chat_id = callback.get("message", {}).get("chat", {}).get("id")

        logger.info(f"Telegram callback: {callback_data}")
        return handle_telegram_callback(callback_data, chat_id)

    return {"status": "ignored", "update_id": update_id}


def handle_telegram_command(command: str, chat_id: int, user: Dict) -> Dict[str, Any]:
    """Handle Telegram bot commands."""

    responses = {
        "start": {
            "text": f"Welkom bij MindVault-AI, {user.get('first_name', 'creator')}! 🚀\n\n"
                    "Kies een challenge:\n"
                    "• /challenge dopamine - 7 dagen Dopamine Detox\n"
                    "• /challenge gauntlet - 30 dagen The Gauntlet\n"
                    "• /challenge founder - 90 dagen Founder Fight Club\n\n"
                    "Of bekijk je stats met /stats",
            "action": "send_message"
        },
        "challenge": {
            "text": "Welke challenge wil je starten?\n\n"
                    "🧠 Dopamine Detox (7 dagen)\n"
                    "⭐ The Gauntlet (30 dagen)\n"
                    "🚀 Founder Fight Club (90 dagen)",
            "action": "send_challenge_menu"
        },
        "checkin": {
            "text": "Daily check-in ontvangen! ✅\n\n"
                    "Keep going, je bent op de goede weg!",
            "action": "record_checkin"
        },
        "stats": {
            "text": "📊 Jouw Stats:\n\n"
                    "• Actieve challenge: -\n"
                    "• Dag: 0/0\n"
                    "• Check-ins: 0\n"
                    "• Streak: 0 dagen",
            "action": "show_stats"
        }
    }

    response = responses.get(command, {"text": "Onbekend commando", "action": "none"})

    return {
        "status": "success",
        "chat_id": chat_id,
        "response": response
    }


def handle_telegram_callback(data: str, chat_id: int) -> Dict[str, Any]:
    """Handle Telegram callback queries (button presses)."""

    # Parse callback data (format: action:value)
    parts = data.split(":")
    action = parts[0] if parts else ""
    value = parts[1] if len(parts) > 1 else ""

    if action == "start_challenge":
        return {
            "status": "success",
            "chat_id": chat_id,
            "action": "start_challenge",
            "challenge": value
        }
    elif action == "checkin":
        return {
            "status": "success",
            "chat_id": chat_id,
            "action": "record_checkin"
        }

    return {"status": "ignored", "data": data}


# ============================================
# Main Handler (for serverless deployment)
# ============================================

def handler(request):
    """
    Main webhook handler for serverless platforms.

    For Vercel: Export as handler
    For AWS Lambda: Wrap with appropriate event parsing
    """

    # Parse request
    method = request.get("method", "POST")
    path = request.get("path", "/")
    headers = request.get("headers", {})
    body = request.get("body", b"")

    # Ensure body is bytes
    if isinstance(body, str):
        body = body.encode()

    # Route based on path
    if "/stripe" in path:
        # Stripe webhook
        signature = headers.get("stripe-signature", "")

        if not verify_stripe_signature(body, signature):
            return {"statusCode": 401, "body": "Invalid signature"}

        try:
            event = json.loads(body)
            result = handle_stripe_webhook(event)
            return {"statusCode": 200, "body": json.dumps(result)}
        except json.JSONDecodeError:
            return {"statusCode": 400, "body": "Invalid JSON"}

    elif "/mollie" in path:
        # Mollie webhook
        try:
            data = json.loads(body)
            payment_id = data.get("id", "")
            result = handle_mollie_webhook(payment_id)
            return {"statusCode": 200, "body": json.dumps(result)}
        except json.JSONDecodeError:
            return {"statusCode": 400, "body": "Invalid JSON"}

    elif "/telegram" in path:
        # Telegram webhook (URL should include bot token for security)
        # Example: /api/webhook/telegram/<bot_token>
        path_parts = path.split("/")
        token = path_parts[-1] if len(path_parts) > 3 else ""

        if TELEGRAM_BOT_TOKEN and not verify_telegram_token(token):
            return {"statusCode": 401, "body": "Invalid token"}

        try:
            update = json.loads(body)
            result = handle_telegram_update(update)
            return {"statusCode": 200, "body": json.dumps(result)}
        except json.JSONDecodeError:
            return {"statusCode": 400, "body": "Invalid JSON"}

    else:
        # General webhook
        signature = headers.get("x-webhook-signature", "")

        if not verify_general_signature(body, signature):
            return {"statusCode": 401, "body": "Invalid signature"}

        try:
            data = json.loads(body)
            logger.info(f"General webhook received: {data}")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "received",
                    "timestamp": datetime.utcnow().isoformat()
                })
            }
        except json.JSONDecodeError:
            return {"statusCode": 400, "body": "Invalid JSON"}


# ============================================
# Flask/FastAPI wrapper (for traditional hosting)
# ============================================

def create_flask_app():
    """Create Flask app for traditional hosting."""
    try:
        from flask import Flask, request, jsonify

        app = Flask(__name__)

        @app.route("/api/webhook/<path:webhook_type>", methods=["POST"])
        def webhook(webhook_type):
            result = handler({
                "method": request.method,
                "path": f"/api/webhook/{webhook_type}",
                "headers": dict(request.headers),
                "body": request.get_data()
            })
            return jsonify(json.loads(result["body"])), result["statusCode"]

        @app.route("/health", methods=["GET"])
        def health():
            return jsonify({"status": "healthy", "service": "mvai-webhook"})

        return app

    except ImportError:
        logger.warning("Flask not installed. Use: pip install flask")
        return None


# ============================================
# Run locally for testing
# ============================================

if __name__ == "__main__":
    app = create_flask_app()

    if app:
        print("Starting webhook server on http://localhost:5000")
        print("Endpoints:")
        print("  POST /api/webhook/stripe")
        print("  POST /api/webhook/mollie")
        print("  POST /api/webhook/telegram/<token>")
        print("  GET  /health")
        app.run(debug=True, port=5000)
    else:
        print("Install Flask to run locally: pip install flask")
