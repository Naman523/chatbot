import asyncio
import pyjokes
import wikipedia
import aiohttp
import yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from ollama import chat as ollama_chat

# ================== API KEYS ==================
OPENWEATHER_KEY = "4d24dfe149b7e8ac7f9a11d8c0b198ed"
NEWSAPI_KEY = "8ce87eac61a844fa9500965424d8f110"
EXCHANGE_KEY = "591e0697847d2ea3ab10acc2"
TREFLE_TOKEN = "usr-OvZu1Ksr4ofJ4nwf4EiHvE_GId0P54JCkO3h5afVHLA"
OMDB_KEY = "987efbbf"
NASA_KEY = "PLvEiXUjgBK6Z4faUwsEFeeg7D40bewAu5H7QfIL"
BOT_TOKEN = "8015391053:AAFAjvMhoylUrU4iGfNrSjmz3_WzjrJmwPQ"

# ================== OLLAMA AI CHAT ==================
async def get_ollama_response(user_input: str):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: ollama_chat(
            model="llama3",
            messages=[{"role": "user", "content": user_input}]
        )
    )
    return response["message"]["content"]

# ================== COMMAND: /start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Smart Bot Activated!\n"
        "You can chat with me using LLaMA3.\n\n"
        "Commands:\n"
        "/joke /wiki /stock /food /apod /weather /plant /news /movie /convert"
    )

# ================== JOKE ==================
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(pyjokes.get_joke())

# ================== WIKIPEDIA ==================
async def wiki_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /wiki <query>")
    query = " ".join(context.args)
    try:
        summary = wikipedia.summary(query, sentences=3)
        await update.message.reply_text(summary)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ================== STOCK ==================
async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /stock <ticker>")
    ticker = context.args[0].upper()
    try:
        data = yf.Ticker(ticker).info
        price = data.get("currentPrice", "N/A")
        change = data.get("regularMarketChange", "N/A")
        await update.message.reply_text(f"💹 {ticker}\nPrice: {price}\nChange: {change}")
    except:
        await update.message.reply_text("❌ Unable to fetch stock data.")

# ================== FOOD INFO ==================
async def get_food_info(food_name: str):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={food_name}&search_simple=1&action=process&json=1&page_size=5"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            data = await r.json()
            items = data.get("products", [])
            if not items:
                return f"No food info found for '{food_name}'."

            p = items[0]
            name = p.get("product_name", "Unknown")
            ing = p.get("ingredients_text", "Unknown")

            msg = f"🍎 {name}\n\nIngredients:\n{ing}"
            return msg

async def food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /food <item>")
    result = await get_food_info(" ".join(context.args))
    await update.message.reply_text(result)

# ================== NASA APOD ==================
async def get_nasa_apod(date=None):
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_KEY}"
    if date:
        url += f"&date={date}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            return await r.json()

async def apod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = context.args[0] if context.args else None
    data = await get_nasa_apod(date)
    await update.message.reply_text(
        f"🌌 {data.get('title')}\n\n{data.get('explanation')}\n\n{data.get('url')}"
    )

# ================== WEATHER ==================
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /weather <city>")
    city = " ".join(context.args)

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            data = await r.json()
            if data.get("cod") != 200:
                return await update.message.reply_text("❌ City not found.")

            name = data["name"]
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            hum = data["main"]["humidity"]

            msg = (
                f"🌤 Weather in {name}:\n"
                f"Temperature: {temp}°C\n"
                f"Condition: {desc}\n"
                f"Humidity: {hum}%"
            )
            await update.message.reply_text(msg)

# ================== PLANT INFO ==================
async def plant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /plant <name>")

    name = " ".join(context.args)
    url = f"https://trefle.io/api/v1/plants/search?token={TREFLE_TOKEN}&q={name}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            data = await r.json()

            plants = data.get("data", [])
            if not plants:
                return await update.message.reply_text("❌ No plant found.")

            p = plants[0]
            msg = (
                f"🌱 {p.get('common_name', 'Unknown')}\n"
                f"Scientific: {p.get('scientific_name')}\n"
                f"Family: {p.get('family', 'Unknown')}\n"
                f"Image: {p.get('image_url')}"
            )
            await update.message.reply_text(msg)

# ================== NEWS ==================
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = context.args[0] if context.args else "latest"
    url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={NEWSAPI_KEY}&pageSize=5"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            data = await r.json()
            articles = data.get("articles", [])

            if not articles:
                return await update.message.reply_text("No news found.")

            msg = "\n\n".join(f"📰 {a['title']}" for a in articles)
            await update.message.reply_text(msg)

# ================== MOVIE ==================
async def movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /movie <name>")

    name = "+".join(context.args)
    url = f"http://www.omdbapi.com/?apikey={OMDB_KEY}&t={name}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            data = await r.json()

            if data.get("Response") == "False":
                return await update.message.reply_text("❌ Movie not found.")

            msg = (
                f"🎬 {data.get('Title')} ({data.get('Year')})\n"
                f"Genre: {data.get('Genre')}\n"
                f"Plot: {data.get('Plot')}\n"
                f"Poster: {data.get('Poster')}"
            )
            await update.message.reply_text(msg)

# ================== CURRENCY ==================
async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 3:
        return await update.message.reply_text("Usage: /convert <amount> <from> <to>")

    amt, a, b = context.args
    amt = float(amt)

    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_KEY}/latest/{a}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            data = await r.json()

            rate = data["conversion_rates"].get(b.upper())
            if not rate:
                return await update.message.reply_text("❌ Invalid currency.")

            await update.message.reply_text(f"{amt} {a} = {amt * rate} {b}")

# ================== AI CHAT HANDLER ==================
async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    reply = await get_ollama_response(user_text)
    await update.message.reply_text(reply)

# ================== MAIN (NO ASYNC) ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # add all commands
    commands = [
        CommandHandler("start", start),
        CommandHandler("joke", joke),
        CommandHandler("wiki", wiki_search),
        CommandHandler("stock", stock),
        CommandHandler("food", food),
        CommandHandler("apod", apod),
        CommandHandler("weather", weather),
        CommandHandler("plant", plant),
        CommandHandler("news", news),
        CommandHandler("movie", movie),
        CommandHandler("convert", convert)
    ]

    for c in commands:
        app.add_handler(c)

    # AI chat
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    print("🤖 Bot is running (VS Code compatible)...")
    app.run_polling()

if __name__ == "__main__":
    main()
