from flask import Flask, request
import requests
import random
import os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

GRAPH_API_VERSION = "v25.0"


# ==========================
# HOME ROUTE
# ==========================

@app.route("/")
def home():
    return "Instagram Webhook Running"


# ==========================
# TEST TOKEN ROUTE
# ==========================

@app.route("/test-token")
def test_token():

    url = "https://graph.facebook.com/v25.0/me"

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    response = requests.get(
        url,
        params=params
    )

    return response.text


# ==========================
# WEBHOOK VERIFY
# ==========================

@app.route("/webhook", methods=["GET"])
def verify():

    token = request.args.get(
        "hub.verify_token"
    )

    challenge = request.args.get(
        "hub.challenge"
    )

    if token == VERIFY_TOKEN:
        return challenge, 200

    return "verification failed", 403


# ==========================
# WEBHOOK RECEIVE
# ==========================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json
    print(data)

    return "ok", 200


# ==========================
# RUN SERVER
# ==========================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
