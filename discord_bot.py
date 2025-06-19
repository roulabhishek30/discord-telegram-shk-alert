import discord
import json
import requests
from config import DISCORD_TOKEN, TELEGRAM_BOT_TOKEN, REGISTRY_FILE

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = discord.Client(intents=intents)

def load_registry():
    try:
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def send_to_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text})

@bot.event
async def on_ready():
    print(f"Discord bot logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    server_name = message.guild.name if message.guild else "DM"
    registry = load_registry()

    for discord_name, telegram_id in registry.items():
        mention = f"@{discord_name}"
        if mention in message.content:
            telegram_msg = f"[{server_name}] {message.content}"
            send_to_telegram(telegram_id, telegram_msg)
            print(f"Sent to {discord_name} on Telegram")
            break

bot.run(DISCORD_TOKEN)