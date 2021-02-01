"""
도움 받은 사이트
- https://korchris.github.io/2017/06/29/FB_chatbot/
- https://parkdream.tistory.com/96 -> heroku랑 git 연동하는 방법
"""

# -*- coding:utf-8 -*-
from flask import Flask, request
from common import messaging


# from OpenSSL import SSL  -> 나중에 검수를 받을 때 보안 인증서가 필요하다고 함
app = Flask(__name__)
app.debug = True


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
        if request.args.get("hub.verify_token") == messaging.VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        else:
            return "incorrect"


@app.route("/webhook", methods=["POST"])
def talk():
    payload = request.get_json()
    print(payload)
    event = payload["entry"][0]["messaging"]
    for x in event:
        if is_user_message(x):
            text = x["message"]["text"]
            sender_id = x["sender"]["id"]
            try:
                payload = x["message"]["quick_reply"]["payload"]
            except KeyError:
                payload = None
            messaging.respond(sender_id, text, payload)
    return "ok"


@app.route("/")
def hello():
    return "Hello, World!"


if __name__ == "__main__":
    app.run(threaded=True, port=5000)