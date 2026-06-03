#!/bin/bash
cd ~
git clone https://github.com/ktint81/telegram-ai-bot.git 2>/dev/null || (cd ~/telegram-ai-bot && git pull)
cd ~/telegram-ai-bot
pip install -r requirements.txt
echo "Bot installed. Please set environment variables and run:"
echo "export BOT_TOKEN='your_token_here'"
echo "export OPENAI_API_KEY='your_key_here'"
echo "python bot.py"
