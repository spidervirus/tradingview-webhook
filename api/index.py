from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize Flask app
app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"message": "Hello, Vercel!"})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400
    return jsonify({"status": "success", "data": data}), 200

# Vercel serverless function handler
def handler(event, context):
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    return app(event, context)
