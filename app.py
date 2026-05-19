from flask import Flask, request
import requests
import random
import os

app = Flask(__name__)

# ===================================
# CONFIG
# ===================================

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

GRAPH_API_VERSION = "v25.0"

# ===================================
# POST / REEL SETTINGS
# ===================================

TRIGGERS = {
    "17878276398591244": {
        "keyword": "link",
        "link": "https://yourwebsite.com"
    }
}

# ===================================
# RANDOM COMMENT REPLIES
# ===================================

COMMENT_REPLIES = [
    "Check DM 👀",
    "Sent in your DM 📩",
    "Check your inbox ✨",
    "Done ✅",
    "Link sent in DM 🚀"
]

# ===================================
# WEBHOOK VERIFICATION
# ===================================

@app.route("/webhook", methods=["GET"])
def verify():

    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge, 200

    return "verification failed", 403


# ===================================
# REPLY TO COMMENT
# ===================================

def reply_to_comment(comment_id, message):

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/{comment_id}/replies"
    )

    params = {
        "access_token": PAGE_ACCESS_TOKEN,
        "message": message
    }

    try:
        response = requests.post(url, params=params)

        print("\n===== COMMENT REPLY =====")
        print(response.status_code)
        print(response.text)

    except Exception as e:
        print("COMMENT REPLY ERROR:", e)


# ===================================
# SEND DM BUTTON
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
                    "title": "Get Link",
                    "payload": "GET_LINK"
                }
            ]
        }
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            params=params,
            json=payload
        )

        print("\n===== BUTTON DM =====")
        print(response.status_code)
        print(response.text)

    except Exception as e:
        print("BUTTON DM ERROR:", e)


# ===================================
# SEND FINAL LINK
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

    try:

        response = requests.post(
            url,
            headers=headers,
            params=params,
            json=payload
        )

        print("\n===== FINAL LINK =====")
        print(response.status_code)
        print(response.text)

    except Exception as e:
        print("FINAL LINK ERROR:", e)


# ===================================
# WEBHOOK RECEIVER
# ===================================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    print("\n===== WEBHOOK =====")
    print(data)

    try:

        # ==========================
        # INSTAGRAM COMMENT EVENTS
        # ==========================

        if data.get("object") == "instagram":

            for entry in data.get("entry", []):

                for change in entry.get("changes", []):

                    if change.get("field") == "comments":

                        value = change.get("value", {})

                        comment = (
                            value.get("text", "")
                            .strip()
                            .lower()
                        )

                        user_id = (
                            value.get("from", {})
                            .get("id")
                        )

                        media_id = (
                            value.get("media", {})
                            .get("id")
                        )

                        comment_id = value.get("id")

                        print("\n===== COMMENT =====")
                        print("TEXT:", comment)
                        print("USER:", user_id)
                        print("MEDIA:", media_id)

                        if media_id in TRIGGERS:

                            trigger = TRIGGERS[media_id]

                            keyword = (
                                trigger["keyword"]
                                .strip()
                                .lower()
                            )

                            if keyword in comment:

                                random_reply = random.choice(
                                    COMMENT_REPLIES
                                )

                                # Reply publicly
                                reply_to_comment(
                                    comment_id,
                                    random_reply
                                )

                                # Attempt DM
                                if user_id:
                                    send_dm_button(user_id)

        # ==========================
        # QUICK REPLY EVENTS
        # ==========================

        if data.get("object") == "page":

            for entry in data.get("entry", []):

                for messaging_event in entry.get(
                    "messaging", []
                ):

                    sender_id = (
                        messaging_event.get(
                            "sender", {}
                        ).get("id")
                    )

                    message = (
                        messaging_event.get(
                            "message", {}
                        )
                    )

                    quick_reply = (
                        message.get(
                            "quick_reply", {}
                        )
                    )

                    payload = quick_reply.get(
                        "payload"
                    )

                    print("\n===== QUICK REPLY =====")
                    print(payload)

                    if payload == "GET_LINK":

                        send_final_link(
                            sender_id,
                            "https://yourwebsite.com"
                        )

    except Exception as e:
        print("\n===== ERROR =====")
        print(e)

    return "ok", 200


# ===================================
# HOME ROUTE
# ===================================

@app.route("/")
def home():
    return "Instagram Webhook Running"


# ===================================
# RUN SERVER
# ===================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
