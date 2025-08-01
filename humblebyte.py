from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
from telegram import Update
import time

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    data = response.json()[0]
    return f'"{data["q"]}"\n— {data["a"]}'

def get_bible_verse():
    try:
        url = f"https://beta.ourmanna.com/api/v1/get/?format=json&timestamp={int(time.time())}"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        verse = data["verse"]["details"]
        text = verse["text"]
        reference = verse["reference"]

        return f"{reference} - {text}"
    except Exception as e:
        return f"❌ Error fetching verse: {e}"

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_quote())

async def verse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    verse = get_bible_verse()
    await update.message.reply_text(verse)

if __name__ == "__main__":
    app = ApplicationBuilder().token("8190306917:AAF7lRTQqbor1bg6aUlOWO2mmw2U16WpDwQ").build()
    app.add_handler(CommandHandler("quote", quote_command))
    app.add_handler(CommandHandler("verse", verse_command))
    print("🤖 Bot with /quote and /verse is running...")
    app.run_polling()