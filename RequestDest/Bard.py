"""
Bardと会話を行うクラス
"""
from Bard import Chatbot
class bot:
    def __init__(self, token) -> None:
        self.chatbot = Chatbot(token)
    def request(self, message):
        response = ""
        try:
            response = self.chatbot.ask(message=message.content)
        except KeyError :
            pass
        return response["content"]
