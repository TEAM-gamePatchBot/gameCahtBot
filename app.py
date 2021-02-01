import os
from common.scraping import kartScraping
from flask import Flask, request
from fbmessenger import BaseMessenger, MessengerClient
from fbmessenger.templates import GenericTemplate, OneTimeNotifTemplate
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

def get_element(link):
    return Element(
        title="카트라이더 신규 패치 내역",
        subtitle = "카트라이더 패치 안내 게시판으로 이동🏃",
        image_url = "https://file.nexon.com/NxFile/Download/FileDownloader.aspx?oidFile=4908963554209564999",
        item_url=link,
    )


def return_qrs_set():
    qr1 = quick_replies.QuickReply(title='최신 패치 내역', payload="PATCH_LIST_PAYLOAD")
    qr2 = quick_replies.QuickReply(title='패치 내역 링크', payload='PATCH_LINK_PAYLOAD')
    qr3 = quick_replies.QuickReply(title='기능 설명', payload='FUNC_DESC_PAYLOAD')
    return quick_replies.QuickReplies(quick_replies=[qr1, qr2, qr3])  


def process_message(message):
    print("process message 함수 맨 앞의 print", message)
    qrs = return_qrs_set()
    
    if 'text' in message['message']:
        msg = message['message']['text']

        if msg == "최신 패치 내역":
            patch_contents, link = kartScraping()
            contents = "\n".join(patch_contents)
            response = Text(text = contents, quick_replies=qrs)
        elif msg == "패치 내역 링크":
            patch_contents, link = kartScraping()
            elem = get_element(link)
            response = GenericTemplate(elements=[elem], quick_replies=qrs)
        elif msg == "기능 설명":
            contents = "입력창 위의 버튼을 눌러\n⚡최신 패치 내역⚡을 보거나\n📢카트라이더 패치 안내 게시판📢으로 이동할 수 있습니다😍"
            response = Text(text = contents, quick_replies=qrs)
        elif msg == "알림 설정":
            title="Notify me"
            payload="OTN_PAYLOAD"
            response = OneTimeNotifTemplate(title, payload)
        else:
            contents = "버튼을 눌러 내용을 확인해주세요!😊"
            response = Text(text = contents, quick_replies=qrs)

        return response.to_dict()


def process_optin(message):
    qrs = return_qrs_set()
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


    def optin(self, message):
        sender = message['sender']['id']
        otn_token = message['optin']['one_time_notif_token']
        guest[sender] = otn_token
        action = process_optin(message)
        res = self.send(action, 'RESPONSE')
        app.logger.debug('Response: {}'.format(res))


    def init_bot(self):
        self.add_whitelisted_domains('https://facebook.com/')
        greeting = GreetingText(text='Welcome to the fbmessenger bot demo.')
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
            txt = ('Hey, let\'s get started! Try sending me one of these messages: '
                   'text, image, video, "quick replies", '
                   'webview-compact, webview-tall, webview-full')
            self.send({'text': txt}, 'RESPONSE')
        if 'help' in payload:
            self.send({'text': 'A help message or template can go here.'}, 'RESPONSE')


app = Flask(__name__)
app.debug = True
messenger = Messenger(os.environ.get('FB_PAGE_TOKEN'))
guest = {}


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


if __name__ == '__main__':
    app.run(threaded=True, port=5000)


    