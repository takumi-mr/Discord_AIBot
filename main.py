"""
外部サイトと連携するDiscord Bot
とりあえずChatGPTとBardに対応
"""
import requests
import json
import yaml
import discord
from discord.ext import commands
from discord.threads import Thread
from discord.message import MessageType
from discord.file import File
from discord.app_commands import CommandTree
#import RequestDest.ChatGPT_Web as ChatGPT_Web
import RequestDest.ChatGPT_API as ChatGPT_API
import RequestDest.Bard as Bard_API

#OpenAPIのアクセスキー
OPENAPI_ACCESS_KEY = ''
#CHATGPT_ACCESS_TOKEN = ''
#BARDのアクセストークン
BARD_ACCESS_TOKEN = ''
#SlackBotのトークン
DISCORD_BOT_TOKEN = ''
#SlackBotが応答するチャンネル
DISCORD_CHANNEL_IDS = ''
#認証・設定ファイル読み込み
with open('./config.yaml', encoding='utf-8') as file:
    obj = yaml.safe_load(file)
    OPENAPI_ACCESS_KEY = obj['OPENAI_ACCESS_KEY']
    #CHATGPT_ACCESS_TOKEN = obj['CHATGPT_ACCESS_TOKEN']
    BARD_ACCESS_TOKEN = obj['BARD_ACCESS_TOKEN']
    DISCORD_BOT_TOKEN = obj['DISCORD_BOT_TOKEN']
    DISCORD_CHANNEL_IDS = obj['CHANNEL_ID_AND_NAME']

#使えるModel名は以下URLを参照(GPT-4は順番待ちで今のところは使えない)
# https://platform.openai.com/docs/models
#chatGpt = ChatGPT_Web.bot(CHATGPT_ACCESS_TOKEN)
chatGpt3 = ChatGPT_API.bot(OPENAPI_ACCESS_KEY)
chatGpt4 = ChatGPT_API.bot(OPENAPI_ACCESS_KEY, 'gpt-4')
bard = Bard_API.bot(BARD_ACCESS_TOKEN)

class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.tree.sync()

intents = discord.Intents.default()
intents.message_content = True

bot = MyBot(command_prefix="!", intents=intents)

@bot.listen("on_message")
#メッセージ投稿時
async def on_message_received(message):
    #Bot自身の投稿には何も応答しない
    if message.author == bot.user:
        return
    #メッセージ投稿以外の内容は何も応答しない
    if message.type != MessageType.default:
        return
    #コマンドの場合はここでは処理しない
    if message.content.startswith("!"):
        return
    channel = [d for d in DISCORD_CHANNEL_IDS if d['CHANNEL_ID'] == message.channel.id]
    if channel != [] and channel[0]['CHANNEL_NAME'] == 'bard':
        async with message.channel.typing():
            await message.channel.send(bard.request(message))
        return
    #スレッド内での投稿のみChatGPTへの処理に渡す
    if not isinstance(message.channel, Thread):
        if [d for d in DISCORD_CHANNEL_IDS if d['CHANNEL_ID'] == message.channel.id] == []:
            return
        else:
            await message.channel.send('ChatGPTと会話を始めるにはスレッドを作成して下さい。')
            return
    channel = [d for d in DISCORD_CHANNEL_IDS if d['CHANNEL_ID'] == message.channel.parent_id]
    #指定チャンネル以外での投稿は何も応答しない
    if channel == []:
        return
    async with message.channel.typing():
        if channel[0]['CHANNEL_NAME'] == 'chat-gpt3':
            await message.channel.send(chatGpt3.request(message))
        elif channel[0]['CHANNEL_NAME'] == 'chat-gpt4':
            await message.channel.send(chatGpt4.request(message))
@bot.event
#スレッド作成時の処理 : スレッド毎にChatGPTとの会話を分ける
async def on_thread_create(thread):
    channel = [d for d in DISCORD_CHANNEL_IDS if d['CHANNEL_ID'] == thread.parent.id]
    if channel == []:
        return
    elif channel[0]['CHANNEL_NAME'] == 'chat-gpt3':
        chatGpt3.add_thread(thread.id)
    elif channel[0]['CHANNEL_NAME'] == 'chat-gpt4':
        chatGpt4.add_thread(thread.id)
    elif channel[0]['CHANNEL_NAME'] == 'bard':
        bard.add_thread(thread.id)

@bot.hybrid_command()
async def help_bot(ctx):
    message = "```\n\n"\
            + "**** ChatGPTとの会話方法 ****\n"\
            + "該当チャンネルでスレッドを作成してください。\n"\
            + "スレッド内で投稿すると、ChatGPTからの返信が投稿されます。\n"\
            + "スレッド毎で、会話は別の物として扱われます。\n"\
            + "\n"\
            + "**** Bardとの会話方法 ****\n"\
            + "該当チャンネルで投稿してください。\n"\
            + "Bardからの返信が投稿されます。\n"\
            + "Bardはスレッドで会話を分けられません。\n"\
            + "\n"\
            + "この内容は!help_botでも出力されます。\n"\
            + "```"
    await ctx.send(message)

@bot.hybrid_command()
async def list_openai_models(ctx):
    async with ctx.message.channel.typing():
        response = requests.get(url="https://api.openai.com/v1/models", headers={"Authorization" : "Bearer {}".format(OPENAPI_ACCESS_KEY)})
        with open('./response.json', 'w') as f:
            json.dump(response.json(), f, indent=2)
        with open('./response.json', 'rb') as f:
            await ctx.send(file=File(fp=f))

bot.run(DISCORD_BOT_TOKEN)