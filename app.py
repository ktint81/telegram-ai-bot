
import os
import threading
from flask import Flask
import bot

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!", 200

def run_bot():
    bot.main()

if __name__ == "__main__":
    # Start the Telegram bot in a separate thread
    threading.Thread(target=run_bot, daemon=True).start()
    # Run the Flask app
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
