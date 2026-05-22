from flask import Flask, request
import requests
import random
import os
import json

app = Flask(__name__)

# ==================================
# CONFIG
# ==================================

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

GRAPH_API_VERSION = "v25.0"

# ==================================
# REEL / POST SETTINGS
# ==================================

TRIGGERS = {
    "17878276398591244": {
        "keyword": "link",
        "public_reply": "Link sent 📩 Check your DM"
    }
}

# ==================================
# RANDOM PUBLIC REPLIES
# ==================================

COMMENT_REPLIES = [
    "Link sent 📩 Check your DM",
    "Check your inbox 📩",
    "Sent in DM 🚀",
    "Done ✅ Check DM"
]

# ==================================
# WEBHOOK VERIFICATION
# ==================================

@app.route("/webhook", methods=["GET"])
def verify():

    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print("VERIFY TOKEN FROM META:", token)

    if token == VERIFY_TOKEN:
        return challenge, 200

    return "verification failed", 403


# ==================================
# REPLY TO COMMENT
# ==================================

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

    try:

        response = requests.post(
            url,
            params=params
        )

        print("\n===== COMMENT REPLY =====")
        print(response.status_code)
        print(response.text)

    except Exception as e:
        print("COMMENT REPLY ERROR:", e)


# ==================================
# LOG USER (OPTIONAL)
# ==================================

def save_log(data):

    try:

        with open(
            "comment_logs.txt",
            "a",
            encoding="utf-8"
        ) as f:

            f.write(
                json.dumps(
                    data,
                    ensure_ascii=False
                )
                + "\n"
            )

    except Exception as e:
        print("LOG ERROR:", e)


# ==================================
# WEBHOOK RECEIVER
# ==================================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    print("\n===== WEBHOOK =====")
    print(data)

    try:

        if data.get("object") == "instagram":

            for entry in data.get("entry", []):

                for change in entry.get(
                    "changes", []
                ):

                    field = change.get("field")

                    # =====================
                    # COMMENT DETECTION
                    # =====================

                    if field == "comments":

                        value = change.get(
                            "value", {}
                        )

                        comment_text = (
                            value.get("text", "")
                            .strip()
                            .lower()
                        )

                        username = (
                            value.get(
                                "from", {}
                            ).get(
                                "username",
                                "unknown"
                            )
                        )

                        user_id = (
                            value.get(
                                "from", {}
                            ).get("id")
                        )

                        media_id = (
                            value.get(
                                "media", {}
                            ).get("id")
                        )

                        comment_id = (
                            value.get("id")
                        )

                        print(
                            "\n===== COMMENT ====="
                        )

                        print(
                            "USER:",
                            username
                        )

                        print(
                            "TEXT:",
                            comment_text
                        )

                        print(
                            "MEDIA:",
                            media_id
                        )

                        # =====================
                        # PREVENT SELF REPLY
                        # =====================

                        if username.lower() == "aliveabhay":
                            return "ok", 200

                        # =====================
                        # TRIGGER CHECK
                        # =====================

                        if media_id in TRIGGERS:

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
                                in comment_text
                            ):

                                # Public Reply
                                reply_message = (
                                    random.choice(
                                        COMMENT_REPLIES
                                    )
                                )

                                reply_to_comment(
                                    comment_id,
                                    reply_message
                                )

                                # Save Logs
                                save_log({
                                    "username":
                                    username,

                                    "user_id":
                                    user_id,

                                    "comment":
                                    comment_text,

                                    "media_id":
                                    media_id,

                                    "comment_id":
                                    comment_id
                                })

                                print(
                                    "META AUTOMATION "
                                    "WILL HANDLE DM"
                                )

                    # =====================
                    # MESSAGE DETECTION
                    # =====================

                    elif field == "messages":

                        value = change.get(
                            "value", {}
                        )

                        sender = value.get(
                            "sender", {}
                        )

                        message = value.get(
                            "message", {}
                        )

                        text = (
                            message.get(
                                "text", ""
                            )
                        )

                        print(
                            "\n===== MESSAGE ====="
                        )

                        print(
                            "FROM:",
                            sender.get("id")
                        )

                        print(
                            "TEXT:",
                            text
                        )

    except Exception as e:

        print("\n===== ERROR =====")
        print(e)

    return "ok", 200


# ==================================
# HOME ROUTE
# ==================================

@app.route("/")
def home():
    return (
        "Instagram Hybrid "
        "Automation Running"
    )


# ==================================
# RUN SERVER
# ==================================

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
