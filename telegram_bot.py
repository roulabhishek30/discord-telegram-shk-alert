import json
import telebot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_ID, REGISTRY_FILE

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def load_registry():
    try:
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_registry(data):
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, (
        "👋 Welcome to the Stronghold Kingdoms Alert Bot!\n\n"
        "Use:\n"
        "`/player <player_username>` to subscribe to alerts\n"
        "`/delete` to unsubscribe\n"
        "Admins can use `/listplayers` to view all registrations."
    ), parse_mode='Markdown')

@bot.message_handler(commands=['player'])
def register_player(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "❗ Usage: /player <player_username>")
        return
    player_name = parts[1].strip('@')
    registry = load_registry()

    # Prevent duplicate Telegram ID for different names
    if message.chat.id in registry.values():
        for k, v in list(registry.items()):
            if v == message.chat.id and k != player_name:
                del registry[k]
                break

    registry[player_name] = message.chat.id
    save_registry(registry)
    bot.reply_to(message, f"✅ Registered to receive alerts for player name: `@{player_name}`", parse_mode='Markdown')

@bot.message_handler(commands=['delete'])
def delete_player(message):
    registry = load_registry()
    for user, chat_id in list(registry.items()):
        if chat_id == message.chat.id:
            del registry[user]
            save_registry(registry)
            bot.reply_to(message, f"🗑️ Unregistered from alerts for `@{user}`", parse_mode='Markdown')
            return
    bot.reply_to(message, "❗ You are not registered.")

@bot.message_handler(commands=['listplayers'])
def list_players(message):
    if message.chat.id != TELEGRAM_ADMIN_ID:
        bot.reply_to(message, "❌ You are not authorized to view the list.")
        return
    registry = load_registry()
    if not registry:
        bot.send_message(message.chat.id, "ℹ️ No players registered.")
        return

    lines = [f"@{user} → `{chat_id}`" for user, chat_id in registry.items()]
    bot.send_message(message.chat.id, "📋 Registered Players:\n" + "\n".join(lines), parse_mode='Markdown')

bot.polling()
