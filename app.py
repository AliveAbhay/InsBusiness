from flask import Flask, request
import requests

app = Flask(__name__)

# VERIFY TOKEN
VERIFY_TOKEN = "InsBiz7062"

# PAGE ACCESS TOKEN
PAGE_ACCESS_TOKEN = "EAA8F6lrFvUABRRptMYFGwlMxyyOVRLU01o80QnW6AxZB2SWM699TRqqN08us12GGb7A4bD9Uk6Q0If8uoUxThAIMT2b1UQ8hFGNmE8CcuUA90vyZBAqERrtzsfc4hqReNSZBTwzRZB40y1k1dRnMa55ZB9Pk7zbWd7QqTY72fv7zZBBJCeRUAPzz4rh8CEiSNF1PtbkgKS6iXPgvJsxUvaG6S7bFXeRZC5T7ZCUWTJP4UAlTZCtGi"


# -----------------------------------
# REEL/POST AUTOMATION SETTINGS
# -----------------------------------

TRIGGERS = {

    # REEL/POST 1
    "17878276398591244": {
        "keyword": "link",
        "message": "Here is your website link:\nhttps://yourwebsite.com"
    },

    # REEL/POST 2
    "17892345678999999": {
        "keyword": "course",
        "message": "Here is your course link:\nhttps://course.com"
    },

    # REEL/POST 3
    "17892345678111111": {
        "keyword": "preset",
        "message": "Download preset here:\nhttps://preset.com"
    }

}


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

    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    payload = {
        "recipient": {"id": user_id},
        "message": {
            "text": message
        }
    }

    response = requests.post(url, json=payload)

    print(response.text)


# -----------------------------------
# WEBHOOK EVENT RECEIVER
# -----------------------------------

@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json

    print(data)

    try:

        for entry in data['entry']:

            for change in entry['changes']:

                if change['field'] == 'comments':

                    comment = change['value']['text'].lower()

                    user_id = change['value']['from']['id']

                    media_id = change['value']['media']['id']

                    print("COMMENT:", comment)
                    print("MEDIA ID:", media_id)

                    # CHECK IF THIS REEL/POST EXISTS
                    if media_id in TRIGGERS:

                        trigger = TRIGGERS[media_id]

                        # CHECK KEYWORD
                        if trigger["keyword"] in comment:

                            send_dm(
                                user_id,
                                trigger["message"]
                            )

    except Exception as e:
        print(e)

    return "ok", 200


# -----------------------------------
# RUN SERVER
# -----------------------------------

app.run(host="0.0.0.0", port=10000)
