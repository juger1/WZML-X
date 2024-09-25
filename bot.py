from pyrogram import Client, filters
import aiohttp
from config import API_ID, API_HASH, BOT_TOKEN, API_URL, SUPPORT_GROUP, UPDATES_CHANNEL, DATABASE_URL, DATABASE_NAME
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import Database  # Import the Database class

# Initialize the database
db = Database(DATABASE_URL, DATABASE_NAME)

# Initialize the bot client
bot = Client('AdlinkFly shortener bot',
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN,
             workers=50,
             sleep_threshold=10)

print("Developer: @StupidBoi69")
print("Bot is Started Now")

@bot.on_message(filters.command('start') & filters.private)
async def start(client, message):
    btn = [[
        InlineKeyboardButton('Updates Channel', url=UPDATES_CHANNEL),
        InlineKeyboardButton('Support Chat', url=SUPPORT_GROUP)]]
    text = """**Just send me a link and get a short link. You can also send multiple links separated by a space or enter.**"""
    await message.reply(f"👋 Hello {message.from_user.mention},\n\nI'm Adlinkfly Shortner bot. {text}", reply_markup=InlineKeyboardMarkup(btn))

@bot.on_message(filters.command('set_api') & filters.private)
async def set_api(client, message):
    if len(message.command) < 2:
        await message.reply("⚠️ Please provide your API key. Usage: /set_api <your_api_key>")
        return

    api_key = message.command[1]
    user_id = message.from_user.id

    if db.set_api_key(user_id, api_key):
        await message.reply("✅ Your API key has been set successfully!")
    else:
        await message.reply("❌ Error while setting your API key.")

@bot.on_message(filters.command('me') & filters.private)
async def me(client, message):
    user_id = message.from_user.id
    username = message.from_user.username if message.from_user.username else "Not set"
    
    # Retrieve the user's API key from MongoDB
    api_key = db.get_api_key(user_id) or "None"

    response_text = (
        f"🔍 **Your Information**:\n"
        f"**User ID**: `{user_id}`\n"
        f"**Username**: `{username}`\n"
        f"**API URL**: `{API_URL}`\n"
        f"**API Key**: `{api_key}`"
    )

    await message.reply(response_text)

@bot.on_message(filters.regex(r'https?://[^\s]+') & filters.private)
async def link_handler(client, message):
    links = [match.group(0) for match in message.matches]

    processing_message = await message.reply("🔄 Processing your links...")

    try:
        short_links = await get_bulk_shortlinks(links, message.from_user.id)
        replaced_text = message.text
        for orig_link, short_link in zip(links, short_links):
            replaced_text = replaced_text.replace(orig_link, short_link)
        await client.send_message(message.chat.id, replaced_text)
    except Exception as e:
        await message.reply(f'❌ Error: {e}', quote=True)
    finally:
        await processing_message.delete()

async def get_bulk_shortlinks(links, user_id):
    try:
        api_key = db.get_api_key(user_id)
        if not api_key:
            raise ValueError("⚠️ API key not set. Please set it using /set_api command.")

        short_links = []
        for link in links:
            short_link = await get_shortlink(link, api_key)
            short_links.append(short_link)

        return short_links
    except Exception as e:
        raise ValueError(f"Error retrieving short links: {e}")

async def get_shortlink(link, api_key):
    params = {'api': api_key, 'url': link}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, raise_for_status=True) as response:
                data = await response.json()
                if 'shortenedUrl' not in data:
                    raise ValueError("⚠️ Invalid response from the shortening service.")
                return data["shortenedUrl"]
    except aiohttp.ClientError as e:
        raise ValueError(f"Network error: {e}")
    except Exception as e:
        raise ValueError(f"Error shortening the URL: {e}")

# Run the bot
bot.run()
