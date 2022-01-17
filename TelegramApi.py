import base64
import re

import requests
import time


class TelegramApi:
    def __init__(self, config, logging):
        self.method_text = config['telegram']['api_url'] + config['telegram']['token'] + "/sendMessage"
        self.method_photo = config['telegram']['api_url'] + config['telegram']['token'] + "/sendPhoto"
        self.channel_id = config['telegram']['channel_id']
        self.logging = logging

    def send_notify(self, text, tx_hash, message_type=None, photo=None):

        if text is not None:
            for i in range(5):
                try:
                    if message_type == 'nft' and photo:
                        data = photo.replace(
                            ' ', '+')
                        data = re.sub(r'data:.*base64,', '', data)
                        imgdata = base64.b64decode(data)
                        request = requests.post(self.method_photo, data={
                            "chat_id": self.channel_id,
                            "caption": text,
                            "parse_mode": 'markdown',
                            "disable_web_page_preview": 'true'
                        }, files={'photo': imgdata})
                        time.sleep(0.5)
                    elif message_type == 'nft':
                        request = requests.post(self.method_text, data={
                            "chat_id": self.channel_id,
                            "text": text,
                            "parse_mode": 'markdown',
                            "disable_web_page_preview": 'true'
                        })
                        time.sleep(0.5)
                    else:
                        request = requests.post(self.method_text, data={
                            "chat_id": self.channel_id,
                            "text": text,
                            "parse_mode": 'markdown',
                            "disable_web_page_preview": 'true'
                        })
                        time.sleep(0.5)

                    if request.status_code != 200:
                        self.logging.info(
                            "Error send telegram message, code: {}, try number {}, {}".format(request.status_code,
                                                                                              i + 1, request.text))
                        time.sleep(1.5)
                        continue

                    self.logging.info("Sent notify into Telegram about tx, hash: {}".format(tx_hash))
                    return True

                except requests.exceptions.RequestException as err:
                    self.logging.error(err)
                    continue
