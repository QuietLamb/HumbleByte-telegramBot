from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import random

# get quote from API
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    data = response.json()[0]
    return f'"{data["q"]}"\n— {data["a"]}'

# get bible verse from API
def get_bible_verse():
    try:
        books = ["John", "Matthew", "Romans", "Psalms", "Proverbs"]
        chapters = list(range(1, 10))
        verses = list(range(1, 20))

        book = random.choice(books)
        chapter = random.choice(chapters)
        verse = random.choice(verses)

        url = f"https://bible-api.com/{book}+{chapter}:{verse}"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        text = data["text"].strip()
        reference = data["reference"]

        return f"{reference} - {text}"
    except Exception as e:
        return f"❌ Error fetching verse: {e}"

# Handle /quote command
async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    quote = get_quote()
    msg = await update.message.reply_text(quote)
    user_messages.setdefault(user_id, []).append(msg.message_id)

# Handle /verse command
async def verse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    verse = get_bible_verse()
    msg = await update.message.reply_text(verse)
    user_messages.setdefault(user_id, []).append(msg.message_id)

# Track message ID of user
user_messages = {}

# Handle /empty command
def empty(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Delete all tracked messages for user
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except:
                pass
    user_messages[user_id] = []

# Add command handlers
if __name__ == "__main__":
    app = ApplicationBuilder().token("8190306917:AAF7lRTQqbor1bg6aUlOWO2mmw2U16WpDwQ").build()
    app.add_handler(CommandHandler("quote", quote_command))
    app.add_handler(CommandHandler("verse", verse_command))
    app.add_handler(CommandHandler("empty", empty))  

    print("🤖 Bot is running...")
    app.run_polling()