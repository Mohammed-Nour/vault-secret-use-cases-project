# app/main.py
import os
from urllib.parse import urlsplit

import requests
from flask import Flask, jsonify, request, abort

app = Flask(__name__)
REQUEST_TIMEOUT = (3.05, 10)  # Connect and read timeout, in seconds.


def fetch_api_data(api_url):
    try:
        resp = requests.get(api_url, timeout=REQUEST_TIMEOUT, allow_redirects=False)
        if 300 <= resp.status_code < 400:
            abort(502, description="Upstream redirects are not allowed")
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        abort(504, description="Upstream API timed out")
    except requests.exceptions.RequestException:
        app.logger.warning("Upstream API request failed")
        abort(502, description="Upstream API request failed")


@app.route("/", methods=["GET"])
def root():
    # Vault configuration is trusted; callers cannot choose a destination.
    api_url = os.getenv("API_URL")
    if not api_url:
        return jsonify({"error": "Missing API URL"}), 400

    try:
        parsed = urlsplit(api_url)
        valid_url = (
            parsed.scheme in ("http", "https")
            and parsed.hostname
            and not parsed.username
            and not parsed.password
            and not parsed.fragment
        )
        parsed.port  # Reject malformed port numbers before making a request.
    except ValueError:
        valid_url = False
    if not valid_url:
        abort(500, description="API_URL must be an HTTP(S) URL without credentials or a fragment")

    if any(value != api_url for value in request.args.getlist("api_url")):
        abort(400, description="api_url must match the configured API_URL")

    data = fetch_api_data(api_url)
    return jsonify(data)


if __name__ == "__main__":
    # Port 8080 matches the Helm chart’s service port
    app.run(host="0.0.0.0", port=8080)
