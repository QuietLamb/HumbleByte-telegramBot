from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
import random
import json
import os

# Load data for quiz questions from JSON file
with open(os.path.join(os.path.dirname(__file__), "HumbleByte-Data.json"), "r", encoding="utf-8") as f:
    quiz_questions = json.load(f)

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

# get random life tips from API
def get_tip():
    try:
        res = requests.get("https://api.adviceslip.com/advice")
        data = res.json()
        return f'💡 Life Tip:\n"{data["slip"]["advice"]}"'
    except Exception as e:
        return f"❌ Error fetching tip: {e}"

# Handle /quote command
async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        quote = get_quote()
        msg = await update.message.reply_text(quote)
        user_messages.setdefault(user_id, []).append(msg.message_id)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# Handle /verse command
async def verse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        verse = get_bible_verse()
        msg = await update.message.reply_text(verse)
        user_messages.setdefault(user_id, []).append(msg.message_id)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# Track message ID of user
user_messages = {}

# Handle /empty command
async def empty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Delete all tracked messages for user
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except Exception as e:
                print(f"Failed to delete message {msg_id}: {e}")
        user_messages[user_id] = []

# Handle /quiz command
async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Initialize the set if it doesn't exist
    if "asked_questions" not in context.user_data:
        context.user_data["asked_questions"] = set()
    asked = context.user_data["asked_questions"]

    available_indexes = [i for i in range(len(quiz_questions)) if i not in asked]

    if not available_indexes:
        # Reset when all questions asked
        context.user_data["asked_questions"] = set()
        available_indexes = list(range(len(quiz_questions)))

    q_index = random.choice(available_indexes)
    context.user_data["asked_questions"].add(q_index)

    question = quiz_questions[q_index]
    context.user_data["quiz"] = question

    buttons = [
        [InlineKeyboardButton(opt, callback_data=opt)] for opt in question["options"]
    ]

    await update.message.reply_text(
        f"🧠 *Bible Quiz:*\n{question['question']}",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

# Handle Answer
async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected = query.data
    question = context.user_data.get("quiz")

    if not question:
        await query.edit_message_text("No active quiz. Send /quiz to start.")
        return

    correct = question["answer"]

    if selected == correct:
        text = f"✅ Correct! *{correct}* is the right answer."
    else:
        text = f"❌ Wrong. You chose *{selected}*.\nThe correct answer is *{correct}*."

    await query.edit_message_text(text, parse_mode="Markdown")
    context.user_data["quiz"] = None

# Handle /tip command
async def tip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        tip = get_tip()
        msg = await update.message.reply_text(tip)
        user_messages.setdefault(user_id, []).append(msg.message_id)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# Add command handlers
if __name__ == "__main__":
    app = ApplicationBuilder().token("8190306917:AAF7lRTQqbor1bg6aUlOWO2mmw2U16WpDwQ").build()
    app.add_handler(CommandHandler("quote", quote_command))
    app.add_handler(CommandHandler("verse", verse_command))
    app.add_handler(CommandHandler("empty", empty))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CallbackQueryHandler(handle_quiz_answer))
    app.add_handler(CommandHandler("tip", tip_command))

    print("🤖 Bot is running...")
    app.run_polling()