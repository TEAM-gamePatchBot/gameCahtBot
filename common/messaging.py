import json, requests
from . import scraping


with open("config.json", "r") as f:
    config = json.load(f)

PAGE_ACCESS_TOKEN = config["TOKEN"]["PAGE_ACCESS_TOKEN"]
VERIFY_TOKEN = config["TOKEN"]["VERIFY_TOKEN"]
FB_API_URL = f"https://graph.facebook.com/v9.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"


def respond(sender, message, payload):
    """Formulate a response to the user and
    pass it on to a function that sends it."""
    if message == "최신 패치 내역" or payload == "PATCH_LIST_PAYLOAD":
        patch_contents, link = scraping.kartScraping()
        response = "\n".join(patch_contents)
        send_text(sender, response)
    elif message == "패치 내역 링크" or payload == "PATCH_LINK_PAYLOAD":
        patch_contents, link = scraping.kartScraping()
        send_template(sender, link)
    elif message == "기능 설명" or payload == "FUNC_DESC_PAYLOAD":
        text = "입력창 위의 버튼을 눌러\n⚡최신 패치 내역⚡을 보거나\n📢카트라이더 패치 안내 게시판📢으로 이동할 수 있습니다😍"
        send_text(sender, text)
    else:
        text = "버튼을 눌러 내용을 확인해주세요!😊"
        send_text(sender, text)


def send_template(recipient_id, link):
    reply = {
        "recipient": {"id": recipient_id},
        "message": {
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "최신 패치 내역",
                    "payload": "PATCH_LIST_PAYLOAD",
                },
                {
                    "content_type": "text",
                    "title": "패치 내역 링크",
                    "payload": "PATCH_LINK_PAYLOAD",
                },
                {
                    "content_type": "text",
                    "title": "기능 설명",
                    "payload": "FUNC_DESC_PAYLOAD",
                },
            ],
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": "카트라이더 신규 패치 내역",  # 제목 가져오기
                            "subtitle": "카트라이더 패치 안내 게시판으로 이동🏃",
                            "image_url": "https://file.nexon.com/NxFile/Download/FileDownloader.aspx?oidFile=4908963554209564999",
                            "default_action": {
                                "type": "web_url",
                                "url": link,
                                "webview_height_ratio": "full",
                            },
                        }
                    ],
                },
            },
        },
    }

    response = requests.post(FB_API_URL, json=reply)

    return response.json()


def send_text(recipient_id, text):
    """ Send a response to Facebook """

    """ 버튼으로 구현했을 때 """
    reply = {
        "recipient": {"id": recipient_id},
        "messaging_type": "RESPONSE",
        "message": {
            "text": text,
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "최신 패치 내역",
                    "payload": "PATCH_LIST_PAYLOAD",
                },
                {
                    "content_type": "text",
                    "title": "패치 내역 링크",
                    "payload": "PATCH_LINK_PAYLOAD",
                },
                {
                    "content_type": "text",
                    "title": "기능 설명",
                    "payload": "FUNC_DESC_PAYLOAD",
                },
            ],
        },
    }

    response = requests.post(FB_API_URL, json=reply)

    return response.json()


def ice_breakers():

    reply = {
        "ice_breakers": [
            {"question": "알림 수신을 허용해주세요!", "payload": "NOTIFY_ME"},
        ]
    }

    headers = {"Content-Type": "application/json; charset=utf-8"}

    response = requests.post(FB_API_URL, headers=headers, json=reply)

    return response.json


def one_time_notif():
    reply = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "one_time_notif_req",
                "title": "Notify Me",
                "payload": "NOTIFY_ME",
            },
        }
    }

    headers = {"Content-Type": "application/json; charset=utf-8"}

    response = requests.post(FB_API_URL, headers=headers, json=reply)

    return response.json
