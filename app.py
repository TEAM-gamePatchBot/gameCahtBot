"""
도움 받은 사이트
- https://korchris.github.io/2017/06/29/FB_chatbot/
- https://parkdream.tistory.com/96 -> heroku랑 git 연동하는 방법
"""

# -*- coding:utf-8 -*-
from flask import Flask, request
import json, requests
from common import scraping

# from OpenSSL import SSL  -> 나중에 검수를 받을 때 보안 인증서가 필요하다고 함
app = Flask(__name__)

with open("config.json", "r") as f:
    config = json.load(f)

PAGE_ACCESS_TOKEN = config["TOKEN"]["PAGE_ACCESS_TOKEN"]
VERIFY_TOKEN = config["TOKEN"]["VERIFY_TOKEN"]
FB_API_URL = "https://graph.facebook.com/v2.6/me/messages"


def send_message(recipient_id, text):
    """Send a response to Facebook"""

    payload = {
        "message": {"text": text},
        "recipient": {"id": recipient_id},
        "notification_type": "regular",
    }

    auth = {"access_token": PAGE_ACCESS_TOKEN}

    response = requests.post(FB_API_URL, params=auth, json=payload)

    return response.json()


def get_bot_response(message):
    """This is just a dummy function,
    returning a variation of what the user said.
    Replace this function with one connected to chatbot."""
    patch_contents = scraping.kartScraping()
    return "\n".join(patch_contents)


def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"


def respond(sender, message):
    """Formulate a response to the user and
    pass it on to a function that sends it."""

    response = get_bot_response(message)
    send_message(sender, response)


def is_user_message(message):
    """Check if the message is a message from the user"""

    return (
        message.get("message")
        and message["message"].get("text")
        and not message["message"].get("is_echo")
    )


@app.route("/webhook", methods=["GET"])
def listen():
    """This is the main function flask uses to
    listen at the `/webhook` endpoint"""
    if request.method == "GET":
        return verify_webhook(request)


@app.route("/webhook", methods=["POST"])
def talk():
    payload = request.get_json()
    event = payload["entry"][0]["messaging"]
    for x in event:
        if is_user_message(x):
            text = x["message"]["text"]
            sender_id = x["sender"]["id"]
            respond(sender_id, text)
    return "ok"


@app.route("/", methods=["POST"])
def hello():
    send = request.get_json()
    return send


if __name__ == "__main__":
    app.run(threaded=True, port=5000)