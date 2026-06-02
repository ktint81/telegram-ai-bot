#!/bin/bash
cd ~
git clone https://github.com/ktint81/telegram-ai-bot.git
cd telegram-ai-bot
pip install -r requirements.txt
export BOT_TOKEN="8379367068:AAH_y1qYCWCTqiw2IWHIA-qSP3_eIFrWHNI"
export OPENAI_API_KEY="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"
python bot.py
