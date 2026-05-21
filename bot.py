import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# --- CONFIGURATION (Render එකෙන් Keys ගන්න විදිහ) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Sathsaragimhan/babiya-store-bot/refs/heads/main/data.txt"

# Gemini Client එක හදනවා
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Logging Setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! මම Babiya Store එකේ AI Assistant. ඔයාට මොනවද දැනගන්න ඕනේ?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    
    # GitHub එකෙන් data.txt කියවීම
    try:
        response_github = requests.get(GITHUB_RAW_URL)
        if response_github.status_code == 200:
            business_info = response_github.text
        else:
            business_info = "ඔයා Babiya Store එකේ ඇසිස්ටන්ට්."
    except Exception as e:
        business_info = "ඔයා Babiya Store එකේ ඇසිස්ටන්ට්."
    
    # Gemini එකට Request එක යැවීම (Error handling එක්ක)
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=business_info,
            ),
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Gemini Error: {e}")
        await update.message.reply_text("💡 සිස්ටම් එකේ පොඩි කාර්යබහුලත්වයක් තියෙනවා. කරුණාකර විනාඩියකින් නැවත උත්සාහ කරන්න!")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Telegram Bot එක ලයිව් වෙනවා...")
    application.run_polling()

if __name__ == '__main__':
    main()