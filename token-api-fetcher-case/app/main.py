import os
import requests
from flask import Flask, jsonify, abort, request

app = Flask(__name__)

# === CONFIGURATION ===
# For simplicity we store it here. In prod you’d want an env var.
API_URL = os.getenv("API_URL")
EXPECTED_TOKEN = os.getenv("EXPECTED_TOKEN")


@app.route("/healthz", methods=["GET"])
def healthz():
    # a simple check—could also do real checks here
    return "", 200


@app.route("/", methods=["GET"])
def root():
    token = request.headers.get("X-API-Token")
    if token != EXPECTED_TOKEN:
        abort(401, "Invalid or missing API token")

    try:
        resp = requests.get(API_URL)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException as e:
        app.logger.error(f"Upstream fetch failed: {e}")
        abort(502, "Failed to fetch API data")


if __name__ == "__main__":
    # you can also set FLASK_ENV=development to get the debugger
    app.run(host="0.0.0.0", port=8080)
