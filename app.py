from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "mytoken"

@app.route('/webhook', methods=['GET'])
def verify():

    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge

    return "verification failed"


@app.route('/webhook', methods=['POST'])
def webhook():

    print(request.json)

    return "ok", 200


app.run(host="0.0.0.0", port=10000)
