from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import os
from fastapi import FastAPI
import uvicorn
import threading

# Load env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Telegram bot code here (same as before)
main_menu = [["🌍 Translate"], ["ℹ️ Help", "🔐 Privacy"]]
reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! I can translate any text to Amharic.\nChoose an option:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 Translate - Translate any text to Amharic\nℹ️ Help - Show this message\n🔐 Privacy - Privacy info"
    )

async def privacy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Your messages are private. I do not store or share them.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🌍 Translate":
        await update.message.reply_text("Send me any text and I will translate it to Amharic:")
        context.user_data["translate_mode"] = True
    elif text == "ℹ️ Help":
        await help_command(update, context)
    elif text == "🔐 Privacy":
        await privacy_command(update, context)
    elif context.user_data.get("translate_mode"):
        try:
            translated = GoogleTranslator(source='auto', target='am').translate(text)
            await update.message.reply_text(f"Translated:\n{translated}")
        except Exception as e:
            await update.message.reply_text(f"Translation failed: {e}")
        finally:
            context.user_data["translate_mode"] = False
    else:
        await update.message.reply_text("Please choose an option from the menu.", reply_markup=reply_markup)

# Run Telegram bot in background
def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling()

threading.Thread(target=run_bot).start()

# Dummy FastAPI server to satisfy Render
web_app = FastAPI()

@web_app.get("/")
async def root():
    return {"status": "Bot is running"}

if __name__ == "__main__":
    uvicorn.run(web_app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))