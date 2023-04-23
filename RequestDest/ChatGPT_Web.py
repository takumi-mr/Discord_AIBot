"""
ChatGPTと会話を行うクラス
内部的にはWeb画面からの操作と同じ
実際にWebの画面で履歴が見れる
"""
from revChatGPT.V1 import Chatbot

class bot:
    #スレッドIDとChatGPTのconversation_idを対応付け
    def __init__(self, api_key) -> None:
        self.thread_id_dict = {}
        self.chatbot = Chatbot(config={"access_token":api_key})
    def add_thread(self, thread_id):
        self.thread_id_dict[thread_id] = thread_id
    def request(self, message):
        response = ''
        if not message.channel.id in self.thread_id_dict:
            for response in self.chatbot.ask(
                prompt=message.content
            ):
                pass
            self.thread_id_dict[message.channel.id] = response["conversation_id"]
        else:
            for response in self.chatbot.ask(
                prompt=message.content
                ,conversation_id=self.thread_id_dict[message.channel.id]
            ):
                pass
        return response["message"]