# app/main.py
import os
import requests
import json
from flask import Flask, jsonify, request, abort

app = Flask(__name__)


def fetch_api_data(api_url):
    try:
        resp = requests.get(api_url)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching data from API: {e}")
        abort(502, description=str(e))


@app.route("/", methods=["GET"])
def root():
    # allow override via query param ?api_url=
    api_url = request.args.get("api_url") or os.getenv("API_URL")
    if not api_url:
        return jsonify({"error": "Missing API URL"}), 400

    app.logger.info(f"Fetching data from: {api_url}")
    data = fetch_api_data(api_url)
    return jsonify(data)


if __name__ == "__main__":
    # Port 8080 matches the Helm chart’s service port
    app.run(host="0.0.0.0", port=8080)
