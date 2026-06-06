import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Bot Token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Log startup info
logger.info(f"BOT_TOKEN loaded: {'Yes' if BOT_TOKEN else 'No'}")
logger.info(f"GEMINI_API_KEY loaded: {'Yes' if GEMINI_API_KEY else 'No'}")
logger.info(f"GEMINI_API_KEY starts with: {GEMINI_API_KEY[:10]}..." if GEMINI_API_KEY else "No key")

def ask_ai(user_message):
    """Call Google Gemini API using requests."""
    # Try v1beta first, then v1
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": user_message}
                ]
            }
        ]
    }
    
    logger.info(f"Calling Gemini API...")
    response = requests.post(url, headers=headers, json=data, timeout=30)
    logger.info(f"Gemini API response status: {response.status_code}")
    
    result = response.json()
    logger.info(f"Gemini API response: {str(result)[:500]}")
    
    if "candidates" in result:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    elif "error" in result:
        error_msg = result['error'].get('message', 'Unknown error')
        logger.error(f"Gemini API error: {error_msg}")
        # If v1beta fails, try v1 with gemini-1.5-flash
        url2 = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        logger.info(f"Trying fallback model gemini-1.5-flash...")
        response2 = requests.post(url2, headers=headers, json=data, timeout=30)
        result2 = response2.json()
        logger.info(f"Fallback response: {str(result2)[:500]}")
        if "candidates" in result2:
            return result2["candidates"][0]["content"]["parts"][0]["text"]
        return f"API Error: {error_msg}"
    else:
        logger.error(f"Unexpected response: {result}")
        return "Sorry, I could not get a response."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! I am an AI bot powered by Google Gemini. Send me a message and I will reply."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Just send me a message and I will respond using AI!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    logger.info(f"User ({update.effective_user.id}) said: {user_message}")

    try:
        ai_reply = ask_ai(user_message)
        await update.message.reply_text(ai_reply)
        logger.info(f"AI replied: {ai_reply[:100]}...")
    except Exception as e:
        logger.error(f"Error in echo handler: {type(e).__name__}: {e}")
        await update.message.reply_text(f"Sorry, I encountered an error: {type(e).__name__}")

def main() -> None:
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set!")
        return
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not set!")
        return
        
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("Bot is running...")
    logger.info("Bot started successfully!")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
