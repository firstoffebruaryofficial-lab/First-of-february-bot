import os
import json
import asyncio
from datetime import datetime, timezone, timedelta
import anthropic

ROMANIA_TZ = timezone(timedelta(hours=2))
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

# Config
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Conversation history per user
user_histories = {}

SYSTEM_PROMPT = """Ești managerul personal al lui Sebi, un producător de muzică electronică (dubstep) cunoscut sub numele de scenă "First of February". 
Scopul lui Sebi este să crească și să devină popular cu muzica sa.

Personalitatea ta:
- Ești strict și motivant - îl cerți când nu face lucruri importante
- Îl lauzi când face progrese
- Ești ca un antrenor dur dar care vrea binele lui
- Vorbești în română
- Ești direct și nu te dai bătut ușor

Responsabilitățile tale zilnice:
- Îl întrebi dacă s-a trezit și a început ziua productiv
- Îi dai taskuri zilnice de promovare (TikTok, Instagram, Spotify pitching etc.)
- Îl întrebi dacă a postat conținut
- Îl motivezi să lucreze la muzică
- Îi dai idei de piese și promovare
- Seara îl întrebi ce a realizat

Când Sebi nu face taskurile, îl cerți și îl motivezi să nu renunțe la visul lui.
Când le face, îl lauzi și îi dai taskul următor.

Data și ora curentă: {datetime}
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text(
        "Salut Sebi! 🎵 Sunt managerul tău personal pentru First of February!\n\n"
        "Sunt aici să te ajut să crești și să devii popular cu muzica ta.\n"
        "Fii pregătit - o să fiu strict cu tine! 😤\n\n"
        "Spune-mi, cum a început ziua ta?"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({
        "role": "user",
        "content": user_message
    })

    # Keep only last 20 messages
    if len(user_histories[user_id]) > 20:
        user_histories[user_id] = user_histories[user_id][-20:]

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1000,
            system=SYSTEM_PROMPT.format(datetime=datetime.now(ROMANIA_TZ).strftime("%d/%m/%Y %H:%M")),
            messages=user_histories[user_id]
        )

        assistant_message = response.content[0].text

        user_histories[user_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        await update.message.reply_text(assistant_message)

    except Exception as e:
        await update.message.reply_text("Ups, ceva nu a mers. Încearcă din nou!")
        print(f"Error: {e}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Botul rulează...")
    app.run_polling()

if __name__ == "__main__":
    main()
