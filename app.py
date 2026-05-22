from flask import (
    Flask,
    request
)

from config import (
    VERIFY_TOKEN,
    MY_USERNAME
)

from database import (
    load_automations,
    save_comment_log
)

from automation import (
    reply_to_comment
)

app = Flask(__name__)

# ======================
# MEMORY ROUTING
# ======================

USER_CONTEXT = {}

# ======================
# WEBHOOK VERIFY
# ======================

@app.route(
    "/webhook",
    methods=["GET"]
)
def verify():

    token = request.args.get(
        "hub.verify_token"
    )

    challenge = request.args.get(
        "hub.challenge"
    )

    if token == VERIFY_TOKEN:
        return challenge, 200

    return (
        "verification failed",
        403
    )

# ======================
# WEBHOOK RECEIVER
# ======================

@app.route(
    "/webhook",
    methods=["POST"]
)
def webhook():

    data = request.json

    print(data)

    automations = (
        load_automations()
    )

    try:

        # ==================
        # COMMENT DETECTION
        # ==================

        if (
            data.get("object")
            == "instagram"
        ):

            for entry in data.get(
                "entry",
                []
            ):

                for change in entry.get(
                    "changes",
                    []
                ):

                    field = (
                        change.get(
                            "field"
                        )
                    )

                    # ----------------
                    # COMMENTS
                    # ----------------

                    if field == "comments":

                        value = (
                            change.get(
                                "value",
                                {}
                            )
                        )

                        username = (
                            value.get(
                                "from",
                                {}
                            ).get(
                                "username",
                                ""
                            )
                        )

                        # avoid bot loop
                        if (
                            username.lower()
                            == MY_USERNAME
                        ):
                            continue

                        media_id = str(
                            value.get(
                                "media",
                                {}
                            ).get("id")
                        )

                        comment_text = (
                            value.get(
                                "text",
                                ""
                            )
                            .strip()
                            .lower()
                        )

                        comment_id = (
                            value.get("id")
                        )

                        user_id = (
                            value.get(
                                "from",
                                {}
                            ).get("id")
                        )

                        print(
                            "COMMENT:",
                            comment_text
                        )

                        if (
                            media_id
                            in automations
                        ):

                            config = (
                                automations[
                                    media_id
                                ]
                            )

                            keyword = (
                                config[
                                    "keyword"
                                ]
                                .lower()
                            )

                            if (
                                keyword
                                in comment_text
                            ):

                                # Public reply
                                reply_to_comment(
                                    comment_id,
                                    config[
                                        "public_reply"
                                    ]
                                )

                                # Save context
                                USER_CONTEXT[
                                    str(user_id)
                                ] = {
                                    "media_id":
                                    media_id,

                                    "final_link":
                                    config[
                                        "final_link"
                                    ]
                                }

                                # Log
                                save_comment_log({
                                    "user":
                                    username,

                                    "comment":
                                    comment_text,

                                    "media_id":
                                    media_id
                                })

                                print(
                                    "META DM "
                                    "AUTOMATION "
                                    "WILL HANDLE"
                                )

                    # ----------------
                    # MESSAGE EVENTS
                    # ----------------

                    elif (
                        field
                        == "messages"
                    ):

                        value = (
                            change.get(
                                "value",
                                {}
                            )
                        )

                        sender_id = str(
                            value.get(
                                "sender",
                                {}
                            ).get("id")
                        )

                        message = (
                            value.get(
                                "message",
                                {}
                            )
                        )

                        text = (
                            message.get(
                                "text",
                                ""
                            )
                            .strip()
                            .lower()
                        )

                        print(
                            "MESSAGE:",
                            text
                        )

                        # user clicked
                        # meta button

                        if (
                            sender_id
                            in USER_CONTEXT
                        ):

                            user_data = (
                                USER_CONTEXT[
                                    sender_id
                                ]
                            )

                            final_link = (
                                user_data[
                                    "final_link"
                                ]
                            )

                            print(
                                "SEND:",
                                final_link
                            )

                            # OPTIONAL:
                            # call Graph API
                            # send message

    except Exception as e:

        print(e)

    return "ok", 200

@app.route("/")
def home():
    return (
        "Hybrid Automation Running"
    )

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
