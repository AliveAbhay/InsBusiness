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
# REEL / POST SETTINGS
# ===================================

TRIGGERS = {
    "17878276398591244": {
        "keyword": "link",
        "link": "https://yourwebsite.com"
    }
}

# ===================================
# RANDOM PUBLIC REPLIES
# ===================================

COMMENT_REPLIES = [
    "Link sent 📩",
    "Check DM 👀",
    "Done ✅",
    "Sent in inbox ✨"
]

# ===================================
# HOME
# ===================================

@app.route("/")
def home():
    return "Instagram Bot Running"


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

    print(
        "\n===== COMMENT REPLY ====="
    )

    print(
        response.status_code
    )

    print(
        response.text
    )


# ===================================
# SEND BUTTON DM
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
            "id":
            user_id
        },
        "message": {
            "text":
            "Tap button below 👇",

            "quick_replies": [
                {
                    "content_type":
                    "text",

                    "title":
                    "Send Link 🔗",

                    "payload":
                    "send link"
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

    print(
        "\n===== BUTTON DM ====="
    )

    print(
        response.status_code
    )

    print(
        response.text
    )


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
            "id":
            user_id
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

    print(
        "\n===== FINAL LINK ====="
    )

    print(
        response.status_code
    )

    print(
        response.text
    )


# ===================================
# WEBHOOK RECEIVER
# ===================================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    print(
        "\n===== WEBHOOK ====="
    )

    print(data)

    try:

        # ===================================
        # INSTAGRAM EVENTS
        # ===================================

        if data.get(
            "object"
        ) == "instagram":

            for entry in data.get(
                "entry", []
            ):

                for change in entry.get(
                    "changes", []
                ):

                    field = change.get(
                        "field"
                    )

                    value = change.get(
                        "value", {}
                    )

                    # ===================================
                    # COMMENT EVENT
                    # ===================================

                    if field == "comments":

                        comment = (
                            value.get(
                                "text", ""
                            )
                            .strip()
                            .lower()
                        )

                        user_id = (
                            value.get(
                                "from", {}
                            )
                            .get("id")
                        )

                        media_id = (
                            value.get(
                                "media", {}
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

                        # STOP BOT LOOP
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
                                .strip()
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

                                # SEND BUTTON DM
                                if user_id:

                                    send_dm_button(
                                        user_id
                                    )

                    # ===================================
                    # MESSAGE EVENT
                    # ===================================

                    elif field == "messages":

                        sender_id = (
                            value.get(
                                "sender", {}
                            )
                            .get("id")
                        )

                        message = (
                            value.get(
                                "message", {}
                            )
                        )

                        text = (
                            message.get(
                                "text", ""
                            )
                            .strip()
                            .lower()
                        )

                        print(
                            "\n===== DM ====="
                        )

                        print(
                            "TEXT:",
                            text
                        )

                        # USER CLICKED BUTTON
                        # -> SEND LINK
                        if text == "send link":

                            send_final_link(
                                sender_id,
                                "https://yourwebsite.com"
                            )

    except Exception as e:

        print(
            "\n===== ERROR ====="
        )

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
