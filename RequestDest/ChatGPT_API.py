"""
ChatGPTと会話を行うクラス
内部ではOpenAIのAPI経由で行う
"""
from revChatGPT.V3 import Chatbot
from revChatGPT.typings import APIConnectionError
class bot:
    #スレッドIDとChatGPTのconversation_idを対応付け
    def __init__(self, api_key, model='gpt-3.5-turbo') -> None:
        self.thread_id_dict = {}
        self.chatbot = Chatbot(api_key=api_key, engine=model)
    def add_thread(self, thread_id):
        self.thread_id_dict[thread_id] = thread_id
    def request(self, message):
        response = ""
        try:
            if not message.channel.id in self.thread_id_dict:
                response = self.chatbot.ask(prompt=message.content)
                self.thread_id_dict[message.channel.id] = message.channel.id
            else:
                response = self.chatbot.ask(prompt=message.content
                                            ,convo_id=self.thread_id_dict[message.channel.id])
        except APIConnectionError as e:
            response = e
        return response