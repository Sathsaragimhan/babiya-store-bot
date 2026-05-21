import os
import logging
import requests
from threading import Thread
from flask import Flask  # Render Free එකට මේක ඕනේ
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# --- Render Free එක රැකගන්න පුංචි Web Server එකක් ---
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Babiya Bot is Alive!"

def run_flask():
    # Render එකෙන් දෙන Port එක ගන්නවා, නැත්නම් 8080 පාවිච්චි කරනවා
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --- BOT CONFIGURATION ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Sathsaragimhan/babiya-store-bot/refs/heads/main/data.txt"

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! මම Babiya Store එකේ AI Assistant. ඔයාට මොනවද දැනගන්න ඕනේ?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    try:
        response_github = requests.get(GITHUB_RAW_URL)
        business_info = response_github.text if response_github.status_code == 200 else "ඔයා Babiya Store එකේ ඇසිස්ටන්ට්."
    except Exception:
        business_info = "ඔයා Babiya Store එකේ ඇසිස්ටන්ට්."
    
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_text,
            config=types.GenerateContentConfig(system_instruction=business_info),
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Gemini Error: {e}")
        await update.message.reply_text("💡 සිස්ටම් එකේ පොඩි කාර්යබහුලත්වයක් තියෙනවා. කරුණාකර නැවත උත්සාහ කරන්න!")

def main():
    # Flask සර්වර් එක Background එකේ රන් කරනවා
    Thread(target=run_flask).start()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Telegram Bot එක ලයිව් වෙනවා...")
    application.run_polling()

if __name__ == '__main__':
    main()