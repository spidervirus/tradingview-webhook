from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import os

# Configure Flask app
app = Flask(__name__)

# Optional: Enable CORS if required
# from flask_cors import CORS
# CORS(app)

# Configure logging
log_file = os.environ.get("WEBHOOK_LOG", "webhook.log")  # Default log file
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Function to validate incoming JSON data
def validate_signal(data):
    required_fields = ["action", "symbol", "price", "lot_size"]
    missing_fields = [field for field in required_fields if field not in data or not data[field]]

    if missing_fields:
        return False, f"Missing or invalid fields: {', '.join(missing_fields)}"

    # Validate action
    if data.get("action") not in ["buy", "sell"]:
        return False, "Invalid 'action' value. Must be 'buy' or 'sell'."

    # Validate price and lot_size as floats
    try:
        float(data.get("price"))
        float(data.get("lot_size"))
    except ValueError:
        return False, "'price' and 'lot_size' must be valid numbers."

    return True, None

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handle incoming POST requests to /webhook.
    """
    try:
        # Parse JSON payload
        data = request.json
        if not data:
            logger.error("No JSON data received")
            return jsonify({"status": "error", "message": "No JSON data received"}), 400

        logger.info("Received Signal: %s", data)

        # Validate JSON payload
        is_valid, error = validate_signal(data)
        if not is_valid:
            logger.error("Validation Error: %s", error)
            return jsonify({"status": "error", "message": error}), 400

        # Extract and process the signal details
        action = data.get("action")
        symbol = data.get("symbol")
        price = float(data.get("price"))
        lot_size = float(data.get("lot_size"))

        logger.info("Action: %s, Symbol: %s, Price: %s, Lot Size: %s", action, symbol, price, lot_size)
        process_signal(action, symbol, price, lot_size)

        return jsonify({"status": "success", "message": "Signal received and validated"}), 200

    except Exception as e:
        logger.exception("Error processing webhook")
        return jsonify({"status": "error", "message": str(e)}), 500

def process_signal(action, symbol, price, lot_size):
    """
    Process the trading signal by performing necessary operations.
    """
    logger.info("Processing Signal: Action=%s, Symbol=%s, Price=%s, Lot Size=%s", action, symbol, price, lot_size)
    # Add your processing logic here, such as triggering a trade or saving the signal to a database.

# Serverless function handler for Vercel
def handler(event, context):
    """
    The entry point for Vercel's serverless environment.
    """
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    return app(event, context)
