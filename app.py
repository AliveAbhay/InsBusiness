from flask import Flask, request
import requests

app = Flask(__name__)

# -----------------------------------
# VERIFY TOKEN
# -----------------------------------

VERIFY_TOKEN = "InsBiz7062"

# -----------------------------------
# PAGE ACCESS TOKEN
# -----------------------------------

PAGE_ACCESS_TOKEN = "EAA8F6lrFvUABRWfZCSN8A2t8ZB6sq2vINhUtMP6FQhTOD8D01cf7HevE0iZCRLSppdZB1wNhbMbUVuXy3oYyic9YeVsPX4y2PVCt7PlTkZB6YoSKDvrfK90xCn3ZAaAjOYooatCo8bAy7BuXGeVKuefKPt63uMJzTclSZAy5HXU89ZAHXyNh4VYstf3gS6L6bsAt9i5uaeZAh0UEuw8xrTjcwjQ35BWc3SKvZAYIOcrgoKSulm8VZBLZCmLOeJpS1AZDZD"

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
# SEND DM FUNCTION
# -----------------------------------

def send_dm(user_id, message):

    url = "https://graph.facebook.com/v25.0/me/messages"

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
            "text": message
        }
    }

    response = requests.post(
        url,
        headers=headers,
        params=params,
        json=payload
    )

    print("DM RESPONSE:")
    print(response.text)


# -----------------------------------
# WEBHOOK EVENT RECEIVER
# -----------------------------------

@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json

    print("WEBHOOK DATA:")
    print(data)

    if data.get("object") == "instagram":

        try:

            for entry in data['entry']:

                for change in entry['changes']:

                    if change['field'] == 'comments':

                        comment = change['value']['text']

                        user_id = change['value']['from']['id']

                        media_id = change['value']['media']['id']

                        print("COMMENT:", comment)
                        print("USER ID:", user_id)
                        print("MEDIA ID:", media_id)

                        # -----------------------------------
                        # TEST DM
                        # -----------------------------------

                        print("SENDING TEST DM")

                        send_dm(
                            user_id,
                            "Webhook working successfully!"
                        )

        except Exception as e:

            print("ERROR:")
            print(e)

    return "ok", 200


# -----------------------------------
# RUN SERVER
# -----------------------------------

app.run(host="0.0.0.0", port=10000)
