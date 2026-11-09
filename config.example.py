# config.example.py - Безопасный шаблон конфигурации
# Скопируйте этот файл в config.py или укажите токен в файле .env
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
