
import os
import logging
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-20b"
history = {}

SYSTEM = """
Sen gelişmiş bir yapay zeka asistanısın.
Adın Bahar AI.
Her zaman Türkçe cevap ver.
Doğal, akıllı, samimi ve yardımcı ol.
Soruları tekrar etme.
Her mesaja bağlama uygun, özgün cevap ver.
Kod yazabilir, matematik çözebilir,
çeviri yapabilir, metin yazabilir,
fikir üretebilir ve açıklamalar yapabilirsin.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Merhaba! Ben Bahar AI 🤖\n"
        "Sana nasıl yardımcı olabilirim?\n\n"
        "/clear - Sohbet geçmişini temizle"
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history.pop(update.effective_user.id, None)
    await update.message.reply_text("Sohbet geçmişi temizlendi! ✅")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    question = update.message.text

    if user_id not in history:
        history[user_id] = []

    history[user_id].append({
        "role": "user",
        "content": question
    })

    history[user_id] = history[user_id][-16:]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                *history[user_id]
            ],
            temperature=0.7,
            max_tokens=2000
        )

        answer = response.choices[0].message.content
        history[user_id].append({
            "role": "assistant",
            "content": answer
        })

        for i in range(0, len(answer), 4000):
            await update.message.reply_text(answer[i:i+4000])

    except Exception:
        logging.exception("AI error")
        await update.message.reply_text(
            "Şu anda cevap oluşturamadım. Biraz sonra tekrar dene."
        )

def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("BAHAR AI AKTİF!")
    app.run_polling()

if __name__ == "__main__":
    main()
