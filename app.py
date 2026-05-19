from flask import Flask, request
import requests
import random
import os

app = Flask(__name__)

# ===================================
# ENV VARIABLES
# ===================================

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

GRAPH_API_VERSION = "v25.0"

# ===================================
# SETTINGS
# ===================================

TRIGGERS = {
    "17878276398591244": {
        "keyword": "link",
        "link": "https://yourwebsite.com"
    }
}

COMMENT_REPLIES = [
    "Check DM 👀",
    "Sent in your DM 📩",
    "Check your inbox ✨",
    "Done ✅",
    "Link sent in DM 🚀"
]

# ===================================
# HOME
# ===================================

@app.route("/")
def home():
    return "Instagram Webhook Running"

# ===================================
# DEBUG TOKEN
# ===================================

@app.route("/debug-token")
def debug_token():

    if PAGE_ACCESS_TOKEN:
        return {
            "exists": True,
            "starts_with": PAGE_ACCESS_TOKEN[:10],
            "length": len(PAGE_ACCESS_TOKEN)
        }

    return {
        "exists": False
    }

# ===================================
# TEST TOKEN
# ===================================

@app.route("/test-token")
def test_token():

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/me/accounts"

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    response = requests.get(
        url,
        params=params
    )

    return response.text

# ===================================
# WEBHOOK VERIFY
# ===================================

@app.route("/webhook", methods=["GET"])
def verify():

    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print("TOKEN FROM META:", token)
    print("VERIFY_TOKEN:", VERIFY_TOKEN)

    if token == VERIFY_TOKEN:
        return challenge, 200

    return "verification failed", 403

# ===================================
# COMMENT REPLY
# ===================================

def reply_to_comment(comment_id, message):

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/"
        f"{comment_id}/replies"
    )

    params = {
        "access_token": PAGE_ACCESS_TOKEN,
        "message": message
    }

    response = requests.post(
        url,
        params=params
    )

    print("===== COMMENT REPLY =====")
    print(response.status_code)
    print(response.text)

# ===================================
# SEND DM
# ===================================

def send_dm_button(user_id):

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/me/messages"
    )

    headers = {
        "Content-Type": "application/json"
    }

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    payload = {
        "recipient": {
            "id": user_id
        },
        "message": {
            "text": "Here is your link 👇",
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "Click Here",
                    "payload": "GET_LINK"
                }
            ]
        }
    }

    response = requests.post(
        url,
        headers=headers,
        params=params,
        json=payload
    )

    print("===== BUTTON DM =====")
    print(response.status_code)
    print(response.text)

# ===================================
# FINAL LINK
# ===================================

def send_final_link(user_id, link):

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/me/messages"
    )

    headers = {
        "Content-Type": "application/json"
    }

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    payload = {
        "recipient": {
            "id": user_id
        },
        "message": {
            "text": f"Here is your link 🚀\n{link}"
        }
    }

    response = requests.post(
        url,
        headers=headers,
        params=params,
        json=payload
    )

    print("===== FINAL LINK =====")
    print(response.status_code)
    print(response.text)

# ===================================
# WEBHOOK RECEIVER
# ===================================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    print("===== WEBHOOK =====")
    print(data)

    try:

        if data.get("object") == "instagram":

            for entry in data.get("entry", []):

                for change in entry.get("changes", []):

                    if change.get("field") == "comments":

                        comment = (
                            change["value"]
                            .get("text", "")
                            .lower()
                        )

                        user_id = (
                            change["value"]
                            ["from"]["id"]
                        )

                        media_id = (
                            change["value"]
                            ["media"]["id"]
                        )

                        comment_id = (
                            change["value"]
                            ["id"]
                        )

                        print("===== COMMENT =====")
                        print("TEXT:", comment)
                        print("USER:", user_id)
                        print("MEDIA:", media_id)

                        if media_id in TRIGGERS:

                            trigger = (
                                TRIGGERS[media_id]
                            )

                            if (
                                trigger["keyword"]
                                in comment
                            ):

                                random_reply = (
                                    random.choice(
                                        COMMENT_REPLIES
                                    )
                                )

                                reply_to_comment(
                                    comment_id,
                                    random_reply
                                )

                                send_dm_button(
                                    user_id
                                )

        if data.get("object") == "page":

            for entry in data.get("entry", []):

                for messaging_event in (
                    entry.get(
                        "messaging", []
                    )
                ):

                    sender_id = (
                        messaging_event
                        ["sender"]["id"]
                    )

                    if (
                        "message"
                        in messaging_event
                        and
                        "quick_reply"
                        in messaging_event
                        ["message"]
                    ):

                        payload = (
                            messaging_event
                            ["message"]
                            ["quick_reply"]
                            ["payload"]
                        )

                        if payload == "GET_LINK":

                            send_final_link(
                                sender_id,
                                "https://yourwebsite.com"
                            )

    except Exception as e:

        print("===== ERROR =====")
        print(str(e))

    return "ok", 200

# ===================================
# RUN SERVER
# ===================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
