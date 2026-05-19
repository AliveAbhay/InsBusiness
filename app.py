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

# FACEBOOK PAGE ID
PAGE_ID = "108765280484412"

# YOUR INSTAGRAM BUSINESS ACCOUNT ID
MY_IG_ID = "17841403368168872"

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
    "Link sent 📩",
    "Check DM 👀",
    "Sent in your inbox ✨",
    "Done ✅"
]

# ===================================
# HOME
# ===================================

@app.route("/")
def home():
    return "Instagram Automation Running"


# ===================================
# TEST TOKEN
# ===================================

@app.route("/test-token")
def test_token():

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/me"
    )

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

    token = request.args.get(
        "hub.verify_token"
    )

    challenge = request.args.get(
        "hub.challenge"
    )

    if token == VERIFY_TOKEN:
        return challenge, 200

    return "verification failed", 403


# ===================================
# PUBLIC COMMENT REPLY
# ===================================

def reply_to_comment(
    comment_id,
    message
):

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/"
        f"{comment_id}/replies"
    )

    params = {
        "access_token":
        PAGE_ACCESS_TOKEN,
        "message":
        message
    }

    response = requests.post(
        url,
        params=params
    )

    print("\n===== COMMENT REPLY =====")
    print(response.status_code)
    print(response.text)


# ===================================
# SEND DM BUTTON
# ===================================

def send_dm_button(
    user_id
):

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/"
        f"{PAGE_ID}/messages"
    )

    headers = {
        "Content-Type":
        "application/json"
    }

    params = {
        "access_token":
        PAGE_ACCESS_TOKEN
    }

    payload = {
        "recipient": {
            "id": user_id
        },
        "message": {
            "text":
            "Tap below to get the link 👇",
            "quick_replies": [
                {
                    "content_type":
                    "text",
                    "title":
                    "Send Link 🔗",
                    "payload":
                    "GET_LINK"
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

    print("\n===== BUTTON DM =====")
    print(response.status_code)
    print(response.text)


# ===================================
# SEND FINAL LINK
# ===================================

def send_final_link(
    user_id,
    link
):

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/"
        f"{PAGE_ID}/messages"
    )

    headers = {
        "Content-Type":
        "application/json"
    }

    params = {
        "access_token":
        PAGE_ACCESS_TOKEN
    }

    payload = {
        "recipient": {
            "id": user_id
        },
        "message": {
            "text":
            f"Here is your link 🚀\n{link}"
        }
    }

    response = requests.post(
        url,
        headers=headers,
        params=params,
        json=payload
    )

    print("\n===== FINAL LINK =====")
    print(response.status_code)
    print(response.text)


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

            for entry in data.get(
                "entry", []
            ):

                for change in entry.get(
                    "changes", []
                ):

                    if (
                        change.get(
                            "field"
                        )
                        == "comments"
                    ):

                        value = change.get(
                            "value",
                            {}
                        )

                        comment = (
                            value.get(
                                "text",
                                ""
                            )
                            .strip()
                            .lower()
                        )

                        user_id = (
                            value.get(
                                "from",
                                {}
                            )
                            .get("id")
                        )

                        media_id = (
                            value.get(
                                "media",
                                {}
                            )
                            .get("id")
                        )

                        comment_id = (
                            value.get("id")
                        )

                        print(
                            "\n===== COMMENT ====="
                        )
                        print(
                            "TEXT:",
                            comment
                        )
                        print(
                            "USER:",
                            user_id
                        )
                        print(
                            "MEDIA:",
                            media_id
                        )

                        # STOP SELF LOOP
                        if (
                            str(user_id)
                            == MY_IG_ID
                        ):
                            continue

                        if (
                            media_id
                            in TRIGGERS
                        ):

                            trigger = (
                                TRIGGERS[
                                    media_id
                                ]
                            )

                            keyword = (
                                trigger[
                                    "keyword"
                                ]
                                .lower()
                            )

                            if (
                                keyword
                                in comment
                            ):

                                # PUBLIC REPLY
                                random_reply = (
                                    random.choice(
                                        COMMENT_REPLIES
                                    )
                                )

                                reply_to_comment(
                                    comment_id,
                                    random_reply
                                )

                                # AUTO SEND BUTTON
                                if user_id:

                                    send_dm_button(
                                        user_id
                                    )

        # ==========================
        # BUTTON CLICK EVENT
        # ==========================

        if data.get("object") == "page":

            for entry in data.get(
                "entry", []
            ):

                for event in entry.get(
                    "messaging",
                    []
                ):

                    sender_id = (
                        event.get(
                            "sender",
                            {}
                        )
                        .get("id")
                    )

                    payload = (
                        event.get(
                            "message",
                            {}
                        )
                        .get(
                            "quick_reply",
                            {}
                        )
                        .get(
                            "payload"
                        )
                    )

                    print(
                        "\n===== BUTTON CLICK ====="
                    )
                    print(payload)

                    if (
                        payload
                        == "GET_LINK"
                    ):

                        send_final_link(
                            sender_id,
                            "https://yourwebsite.com"
                        )

    except Exception as e:

        print("\n===== ERROR =====")
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
