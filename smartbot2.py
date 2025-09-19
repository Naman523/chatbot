import os
import asyncio
import pyjokes
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import aiohttp
from ollama import chat as ollama_chat

# ========== Async API Calls ==========

async def get_ollama_response(user_input: str):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: ollama_chat(model="llama3", messages=[{"role": "user", "content": user_input}])
    )
    return response["message"]["content"]

async def get_weather(city: str):
    api_key = "4d24dfe149b7e8ac7f9a11d8c0b198ed"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            j = await r.json()
            if j.get("main"):
                return f"🌡 Weather in {city.title()}:\n{j['main']['temp']}°C, {j['weather'][0]['description']}"
            return "❌ City not found."

async def get_news():
    api_key = "8ce87eac61a844fa9500965424d8f110"
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            j = await r.json()
            articles = j.get("articles", [])[:5]
            return "\n\n".join([f"• {a['title']}" for a in articles]) if articles else "No headlines."

# ========== Command Handlers ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm your Smart Bot 🤖\n\n"
        "You can chat with me or use these commands:\n"
        "/weather <city>\n/news\n/joke\n"
        "/monitor_risk <asset> <size> <threshold>\n"
        "/auto_hedge <strategy> <threshold>\n"
        "/hedge_now <asset> <size>\n"
        "/hedge_status <asset>\n"
        "/hedge_history <asset> <timeframe>\n"
        "/analytics"
    )

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(pyjokes.get_joke())

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Please provide a city: /weather <city>")
        return
    city = " ".join(context.args)
    response = await get_weather(city)
    await update.message.reply_text(response)

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = await get_news()
    await update.message.reply_text(response)

# ======= Placeholder Trading Commands =======
async def monitor_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Monitoring risk (placeholder response).")

async def auto_hedge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Automated hedging started (placeholder response).")

async def hedge_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💹 Executed hedge immediately (placeholder response).")

async def hedge_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Current hedge status (placeholder response).")

async def hedge_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 Hedge history (placeholder response).")

async def analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Portfolio-level risk report (placeholder response).")

# ========== Message Handler for Chat ==========
async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response = await get_ollama_response(user_text)
    await update.message.reply_text(response)

# ========== Main Bot ==========
def main():
    token = "8015391053:AAFAjvMhoylUrU4iGfNrSjmz3_WzjrJmwPQ"  # Add your bot token in environment variables
    app = Application.builder().token(token).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("monitor_risk", monitor_risk))
    app.add_handler(CommandHandler("auto_hedge", auto_hedge))
    app.add_handler(CommandHandler("hedge_now", hedge_now))
    app.add_handler(CommandHandler("hedge_status", hedge_status))
    app.add_handler(CommandHandler("hedge_history", hedge_history))
    app.add_handler(CommandHandler("analytics", analytics))

    # Fallback to chat
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
