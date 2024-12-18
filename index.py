from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os

# Configure Flask app
app = Flask(__name__)
CORS(app)  # Optional: Enable CORS if required for cross-domain requests

# Configure logging to a file
log_file = os.environ.get("WEBHOOK_LOG", "webhook.log")  # Log file path from environment variable
logging.basicConfig(
    filename=log_file,          # Log file name
    level=logging.INFO,         # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
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
    try:
        # Capture JSON data
        data = request.json
        if not data:
            logger.error("No JSON data received")
            return jsonify({"status": "error", "message": "No JSON data received"}), 400

        logger.info("Received Signal: %s", data)

        # Validate incoming data
        is_valid, error = validate_signal(data)
        if not is_valid:
            logger.error("Validation Error: %s", error)
            return jsonify({"status": "error", "message": error}), 400

        # Extract and log signal details
        action = data.get("action")
        symbol = data.get("symbol")
        price = float(data.get("price"))
        lot_size = float(data.get("lot_size"))

        logger.info(f"Action: {action}, Symbol: {symbol}, Price: {price}, Lot Size: {lot_size}")

        # Placeholder for processing the signal (e.g., trigger trading action)
        process_signal(action, symbol, price, lot_size)

        return jsonify({"status": "success", "message": "Signal received and validated"}), 200

    except Exception as e:
        logger.exception("Error processing webhook")
        return jsonify({"status": "error", "message": str(e)}), 500

# Function to process the signal
def process_signal(action, symbol, price, lot_size):
    """
    Process trading signals further, such as executing trades, saving to a database, or forwarding to another platform.
    """
    logger.info("Processing Signal: Action=%s, Symbol=%s, Price=%s, Lot Size=%s", action, symbol, price, lot_size)
    # Add your actual processing logic here
    # For example: Save to a database, forward to another service, or trigger a trading API

if __name__ == "__main__":
    # Get port from environment variable for scalability
    port = int(os.environ.get("PORT", 8080))
    logger.info("Starting Webhook Server on port %s", port)
    app.run(host="0.0.0.0", port=port)
