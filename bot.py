
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Bot Token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client with explicit base_url as requested
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.openai.com/v1"
)

# Define the AI model to use
AI_MODEL = "gpt-4o-mini"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! I am an AI bot. Send me a message and I will reply."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Just send me a message and I will respond using AI!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message using AI."""
    user_message = update.message.text
    logger.info(f"User ({update.effective_user.id}) said: {user_message}")

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        ai_reply = response.choices[0].message.content
        await update.message.reply_text(ai_reply)
        logger.info(f"AI replied: {ai_reply}")
    except Exception as e:
        logger.error(f"Error communicating with AI model: {e}")
        await update.message.reply_text("Sorry, I encountered an error trying to generate a response.")

def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN:
        logger.error("No BOT_TOKEN found in environment variables!")
        return
    
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # On non command i.e. message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
