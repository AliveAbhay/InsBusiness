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

PAGE_ACCESS_TOKEN = "EAA8F6lrFvUABRRptMYFGwlMxyyOVRLU01o80QnW6AxZB2SWM699TRqqN08us12GGb7A4bD9Uk6Q0If8uoUxThAIMT2b1UQ8hFGNmE8CcuUA90vyZBAqERrtzsfc4hqReNSZBTwzRZB40y1k1dRnMa55ZB9Pk7zbWd7QqTY72fv7zZBBJCeRUAPzz4rh8CEiSNF1PtbkgKS6iXPgvJsxUvaG6S7bFXeRZC5T7ZCUWTJP4UAlTZCtGi"


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
