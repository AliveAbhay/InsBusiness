from flask import Flask, request
import requests
import random

app = Flask(__name__)

# -----------------------------------
# VERIFY TOKEN
# -----------------------------------

VERIFY_TOKEN = "InsBiz7062"

# -----------------------------------
# PAGE ACCESS TOKEN
# -----------------------------------

PAGE_ACCESS_TOKEN = "IGAAkhtKou2fdBZAFowRmozeFBMd3BJckkwV1NkUXpILWFjN01Kbmk2LW9aeWJxcWFyV0lEQ2dKUlNUNG9EN181QVlVM1VpZAm5ra2RyRjZALc0tqT1R0RERJWnd3R3VqTUJZAM204ZA3FsZAWdTcUV6N2RIdUJXXy1QZATNJZA0hMX3dJTQZDZD"

# -----------------------------------
# REEL/POST SETTINGS
# -----------------------------------

TRIGGERS = {

    # REEL / POST ID
    "17878276398591244": {

        # COMMENT TRIGGER WORD
        "keyword": "link",

        # FINAL LINK
        "link": "https://yourwebsite.com"

    }

}


# -----------------------------------
# RANDOM COMMENT REPLIES
# -----------------------------------

COMMENT_REPLIES = [
    "Check DM 👀",
    "Sent in your DM 📩",
    "Check your inbox ✨",
    "Done ✅",
    "Link sent in DM 🚀"
]


# -----------------------------------
# WEBHOOK VERIFICATION
# -----------------------------------

@app.route('/webhook', methods=['GET'])
def verify():

    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge

    return "verification failed"


# -----------------------------------
# REPLY TO COMMENT
# -----------------------------------

def reply_to_comment(comment_id, message):

    url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"

    params = {
        "access_token": PAGE_ACCESS_TOKEN,
        "message": message
    }

    response = requests.post(url, params=params)

    print("COMMENT REPLY:")
    print(response.text)


# -----------------------------------
# SEND DM BUTTON
# -----------------------------------

def send_dm_button(user_id):

    url = "https://graph.facebook.com/v19.0/me/messages"

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

    print("BUTTON DM:")
    print(response.text)


# -----------------------------------
# SEND FINAL LINK
# -----------------------------------

def send_final_link(user_id, link):

    url = "https://graph.facebook.com/v19.0/me/messages"

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

    print("FINAL LINK:")
    print(response.text)


# -----------------------------------
# WEBHOOK RECEIVER
# -----------------------------------

@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json

    print("WEBHOOK:")
    print(data)

    try:

        # -----------------------------------
        # COMMENT EVENTS
        # -----------------------------------

        if data.get("object") == "instagram":

            for entry in data['entry']:

                for change in entry['changes']:

                    if change['field'] == 'comments':

                        comment = change['value']['text'].lower()

                        user_id = change['value']['from']['id']

                        media_id = change['value']['media']['id']

                        comment_id = change['value']['id']

                        print("COMMENT:", comment)

                        if media_id in TRIGGERS:

                            trigger = TRIGGERS[media_id]

                            if trigger["keyword"] in comment:

                                # RANDOM COMMENT REPLY
                                random_reply = random.choice(COMMENT_REPLIES)

                                reply_to_comment(
                                    comment_id,
                                    random_reply
                                )

                                # SEND BUTTON DM
                                send_dm_button(user_id)

        # -----------------------------------
        # BUTTON CLICK EVENTS
        # -----------------------------------

        if data.get("object") == "page":

            for entry in data['entry']:

                for messaging_event in entry['messaging']:

                    sender_id = messaging_event['sender']['id']

                    # QUICK REPLY CLICK
                    if (
                        'message' in messaging_event
                        and 'quick_reply' in messaging_event['message']
                    ):

                        payload = messaging_event['message']['quick_reply']['payload']

                        if payload == "GET_LINK":

                            # SEND FINAL LINK
                            send_final_link(
                                sender_id,
                                "https://yourwebsite.com"
                            )

    except Exception as e:

        print("ERROR:")
        print(e)

    return "ok", 200


# -----------------------------------
# RUN SERVER
# -----------------------------------

app.run(host="0.0.0.0", port=10000)
