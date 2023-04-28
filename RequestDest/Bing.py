"""
BingChatと会話を行うクラス
"""
import asyncio
import json
from EdgeGPT import Chatbot, ConversationStyle
class bot:
    def __init__(self) -> None:
        with open('../cookies.json', 'r') as f:
            cookies = json.load(f)
        self.chatbot = Chatbot(cookies=cookies)
    async def request(self, message):
        response = await self.chatbot.ask(prompt=message, conversation_style=ConversationStyle.creative, wss_link="wss://sydney.bing.com/sydney/ChatHub")
        return response['item']['messages'][1]['text']

async def main():
    chatbot = bot()
    while True:    
        print(await chatbot.request(message=input()))

if __name__ == "__main__":
    asyncio.run(main())
    