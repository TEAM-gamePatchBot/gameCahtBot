import os, boto3
from typing import Generic
from boto3.dynamodb.conditions import Key
from flask import Flask, request
from fbmessenger import BaseMessenger, MessengerClient
from fbmessenger.templates import GenericTemplate #OneTimeNotifTemplate
from fbmessenger.elements import Text, Button, Element
from fbmessenger import quick_replies
from fbmessenger.attachments import Image, Video
from fbmessenger.thread_settings import (
    GreetingText,
    GetStartedButton,
    PersistentMenuItem,
    PersistentMenu,
)

''' Template에 Button을 넣을 때 쓰면 됩니다.
def get_button(ratio, link):
    return Button(
        button_type='web_url',
        title = ,
        url=link,
        webview_height_ratio=ratio,
    )'''

def get_element(title, subtitle, image_url, item_url):
    return Element(
        title=title,
        subtitle = subtitle,
        image_url = image_url,
        item_url = f"https://kart.nexon.com/Kart/News/Patch/view.aspx?n4articlesn={item_url}",
    )


def make_qrs_set():
    qr1 = quick_replies.QuickReply(title='최신 패치 내역', payload="PATCH_LIST_PAYLOAD")
    qr2 = quick_replies.QuickReply(title='패치 내역 링크', payload='PATCH_LINK_PAYLOAD')
    qr3 = quick_replies.QuickReply(title='기능 설명', payload='FUNC_DESC_PAYLOAD')
    return quick_replies.QuickReplies(quick_replies=[qr1, qr2, qr3])  




def save_customer_data(sender):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("gamePatchBot")
    table.put_item(
        Item={"dataType": "customer", "notification_id": int(sender),}
    )


def process_message(message):
    print(message)
    qrs = make_qrs_set()

    sender = message['sender']['id']
    save_customer_data(sender)
    
    if 'text' in message['message']:
        msg = message['message']['text']
        if msg == "최신 패치 내역":
            # DB에서 패치 내역 불러와서 contents 처럼 한 str로 처리해주면 됨
            contents = "\n".join(patch_contents)
            response = Text(text = contents, quick_replies=qrs)
        elif msg == "패치 내역 링크":
            # DB에서 title, subtitle, image_url, item_url(게시글 id 만 가져오면 됨)
            elem = get_element(link)
            response = GenericTemplate(elements=[elem], quick_replies=qrs)
        elif msg == "기능 설명":
            contents = "입력창 위의 버튼을 눌러\n⚡최신 패치 내역⚡을 보거나\n📢카트라이더 패치 안내 게시판📢으로 이동할 수 있습니다😍"
            response = Text(text = contents, quick_replies=qrs)
        else:
            contents = "버튼을 눌러 내용을 확인해주세요!😊"
            response = Text(text = contents, quick_replies=qrs)

        ''' 일회성 알림 쓰는 방법
        elif msg == "알림 설정":
            title="Notify me"
            payload="OTN_PAYLOAD"
            response = OneTimeNotifTemplate(title, payload) '''
        
        return response.to_dict()


def process_optin(message):
    qrs = make_qrs_set()
    contents = "감사합니다!"
    response = Text(text=contents, quick_replies=qrs)
    return response.to_dict()


class Messenger(BaseMessenger):
    def __init__(self, page_access_token):
        self.page_access_token = page_access_token
        super(Messenger, self).__init__(self.page_access_token)
        self.client = MessengerClient(self.page_access_token)

    def message(self, message):
        action = process_message(message)
        res = self.send(action, 'RESPONSE')
        app.logger.debug('Response: {}'.format(res))

    ''' 일회성 알림 쓰는 방법
    def optin(self, message):
        sender = message['sender']['id']
        otn_token = message['optin']['one_time_notif_token']
        action = process_optin(message)
        res = self.send(action, 'RESPONSE')
        app.logger.debug('Response: {}'.format(res)) '''


    def init_bot(self):
        self.add_whitelisted_domains('https://facebook.com/')
        greeting = GreetingText(text='카트라이더 패치 내역에 관한 알림을 받으세요!')
        self.set_messenger_profile(greeting.to_dict())

        get_started = GetStartedButton(payload='start')
        res = self.set_messenger_profile(get_started.to_dict())

        app.logger.debug('Response: {}'.format(res))

    def delivery(self, message):
        pass

    def read(self, message):
        pass

    def account_linking(self, message):
        pass

    def postback(self, message):
        payload = message['postback']['payload']
        if 'start' in payload:
            txt = ('안녕하세요~!')
            self.send({'text': txt}, 'RESPONSE')


app = Flask(__name__)
app.debug = True
messenger = Messenger(os.environ.get('FB_PAGE_TOKEN'))


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == os.environ.get('FB_VERIFY_TOKEN'):
            if request.args.get('init') == 'true':
                messenger.init_bot()
                return ''
            return request.args.get('hub.challenge')
        raise ValueError('FB_VERIFY_TOKEN does not match.')
    elif request.method == 'POST':
        messenger.handle(request.get_json(force=True))
    return ''



@app.route("/notification", methods=["POST"])
def notification():
    qrs = make_qrs_set()
    data = request.get_json()
    print(data)
    error = data["error"]
    patchList = data["patchList"]

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("gamePatchBot")

    patchContents = list(
        map(
            lambda patchId: table.get_item(Key={"dataType": "kart", "notification_id": patchId})[
                "Item"
            ],
            patchList,
        )
    )

    patchContents = list(
        map(
            lambda patch: get_element(patch["subject"], patch["patchTime"], patch["thumbnail_src"], patch["notification_id"]),
            patchContents,
        )
    )
    



    # {
    #     "subject": " 1/28(목) 업데이트 안내",
    #     "content": {
    #         "patch_list": [
    #             {
    #                 "patch_subject": "1. 시즌 패스 시즌 4가 오픈됩니다.",
    #                 "patch_content": ["▶ 시즌 패스 시즌 4 오픈", "▶ 시즌 패스 시즌 4 관련 아이템 판매"],
    #             },
    #             {"patch_subject": "2. 스노우 모빌-R이 출시됩니다.", "patch_content": ["▶ 스노우 모빌-R이 판매됩니다."]},
    #             {
    #                 "patch_subject": "3. 다양한 이벤트가 진행됩니다.",
    #                 "patch_content": ["▶ 겨울 맞이 아이템 복불복", "▶ 기다리면 열리는 상자가 오픈됩니다."],
    #             },
    #             {
    #                 "patch_subject": "4. 다양한 퀘스트가 진행됩니다.",
    #                 "patch_content": [
    #                     "▶ 시즌  패스 시즌 4 OPEN (하루 한 번만 완료 가능)",
    #                     "▶ 눈사람 요정 케로의 마법 (하루 한 번만 완료 가능)",
    #                 ],
    #             },
    #             {"patch_subject": "5. 기타 시스템 변경사항", "patch_content": ["▶ 네이버 채널링 서비스 종료"]},
    #         ]
    #     },
    #     "date": "2021-01-27",
    #     "dataType": "kart",
    #     "notification_id": Decimal("75190"),
    #     "patchTime": "2021년 1월 28일(목) 오전 0시",
    #     "thumbnail_src": "https://file.nexon.com/NxFile/Download/FileDownloader.aspx?oidFile=4908963554209564999",
    # }

    customerIdList = table.query(KeyConditionExpression=Key("dataType").eq("customer"))["Items"]
    results = []
    for patch in patchContents:
        action = GenericTemplate(elements=[patch], quick_replies=qrs).to_dict()
        result = list(
            map(
                lambda customer: messenger.send(action, int(customer["notification_id"])),
                customerIdList,
            )
        )
        results.append(result)

    return results





if __name__ == '__main__':
    app.run(threaded=True, port=5000)


    