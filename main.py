from dotenv import load_dotenv
load_dotenv()
from pyrogram import Client, filters, utils
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
import os
import asyncio
import aiohttp
from io import BytesIO
from plugins.logs import Logger
from script import START_TEXT, HELP_TEXT, SUPPORT_TEXT, ABOUT_TEXT

# Get environment variables
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
omdb_api_key = os.getenv("OMDB_API_KEY")
log_channel = int(os.getenv('LOG_CHANNEL'))
if not all([api_id, api_hash, bot_token, omdb_api_key, log_channel]):
    raise ValueError("Please set the API_ID, API_HASH, BOT_TOKEN, OMDB_API_KEY, and LOG_CHANNEL environment variables")

# Initialize the bot
espada = Client("movie_caption_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
logger = Logger(espada)

# Define keyboard layouts
start_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏠 Home", callback_data="home"),
     InlineKeyboardButton("🤖 About", callback_data="about")
     ],
    [InlineKeyboardButton("💬 Support", callback_data="support"),
     InlineKeyboardButton("ℹ️ Help", callback_data="help")]
])

async def download_image(url):
    """Download image from URL"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
    return None

async def fetch_movie_data(movie_name):
    """Fetch movie data from OMDB API"""
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={omdb_api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if data.get('Response') == 'True':
                return {
                    'movie_p': data.get('Title', movie_name),
                    'year_p': data.get('Year', 'N/A'),
                    'genre_p': data.get('Genre', 'N/A'),
                    'synopsis_p': data.get('Plot', 'N/A'),
                    'audio_p': data.get('Language', 'N/A'),
                    'poster': data.get('Poster', None)
                }
            return None

async def download_poster(poster_url):
    """Download movie poster from URL"""
    if poster_url and poster_url != 'N/A':
        async with aiohttp.ClientSession() as session:
            async with session.get(poster_url) as response:
                if response.status == 200:
                    return await response.read()
    return None

def format_caption(movie, year, audio, genre, synopsis):
    """Format the caption with Markdown"""
    caption = f""" {movie} （{year}）
» 𝗔𝘂𝗱𝗶𝗼: {audio}
» 𝗤𝘂𝗮𝗹𝗶𝘁𝘆: 480p | 720p | 1080p 
» 𝗚𝗲𝗻𝗿𝗲: {genre}
» 𝗦𝘆𝗻𝗼𝗽𝘀𝗶𝘀
> {synopsis}
@Teamxpirates
[𝗜𝗳 𝗬𝗼𝘂 𝗦𝗵𝗮𝗿𝗲 𝗢𝘂𝗿 𝗙𝗶𝗹𝗲𝘀 𝗪𝗶𝘁𝗵𝗼𝘂𝘁 𝗖𝗿𝗲𝗱𝗶𝘁, 𝗧𝗵𝗲𝗻 𝗬𝗼𝘂 𝗪𝗶𝗹𝗹 𝗯𝗲 𝗕𝗮𝗻𝗻𝗲𝗱]"""
    return caption
@espada.on_message(filters.command(["start"]))
async def start_command(client, message):
    try:
        # Send loading message
        loading_message = await message.reply_text("Loading... Please wait ⌛")
        
        # Attempt to download and send the start image
        start_image = await download_image("https://jpcdn.it/img/small/682f656e6957597eebce76a1b99ea9e4.jpg")
        if start_image:
            # Convert image data to BytesIO
            image_stream = BytesIO(start_image)
            image_stream.name = "start_image.jpg"
            
            # Send image with caption and buttons
            await client.send_photo(
                chat_id=message.chat.id,
                photo=image_stream,
                caption=START_TEXT,
                reply_markup=start_keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Fallback if image download fails
            await message.reply_text(
                START_TEXT,
                reply_markup=start_keyboard,
                parse_mode=ParseMode.MARKDOWN
            )

        # Delete the loading message
        await loading_message.delete()

        # Log the start command with correct function call
        await logger.log_message(
            action="Start Command",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id
        )

    except Exception as e:
        # Try to delete loading message if it exists and there's an error
        try:
            await loading_message.delete()
        except:
            pass
            
        # Send an error message to the user and log the error
        await message.reply_text("An error occurred. Please try again later.")
        print(f"Start command error: {str(e)}")
        
        # Log the error with details
        await logger.log_message(
            action="Start Command Error",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id,
            error=e
        )


@espada.on_callback_query()
async def callback_query(client, callback_query: CallbackQuery):
    try:
        if callback_query.data == "home":
            await callback_query.message.edit_caption(
                caption=START_TEXT,
                reply_markup=start_keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        elif callback_query.data == "about":
            await callback_query.message.edit_caption(
                caption = ABOUT_TEXT,
                reply_markup = start_keyboard,
                parse_mode = ParseMode.HTML
            )
        
        elif callback_query.data == "help":
            await callback_query.message.edit_caption(
                caption=HELP_TEXT,
                reply_markup=start_keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif callback_query.data == "support":
            await callback_query.message.edit_caption(
                caption=SUPPORT_TEXT,
                reply_markup=start_keyboard,
                parse_mode=ParseMode.HTML
            )
        
        await callback_query.answer()
    except Exception as e:
        print(f"Callback query error: {str(e)}")

@espada.on_message(filters.command(["caption"]))
async def caption_command(client, message):
    try:
        # Extract movie name from command
        movie_name = " ".join(message.text.split()[1:])
        
        if not movie_name:
            await message.reply_text(
                "Please provide a movie name.\n"
                "Example: `/caption Kalki 2898 AD`"
            )
            return

        # Show "Fetching movie details..." message
        status_message = await message.reply_text("Fetching movie details... Please wait!")
        
        # Fetch movie data from OMDB
        movie_data = await fetch_movie_data(movie_name)
        
        if not movie_data:
            await status_message.edit_text("Sorry, I couldn't find information for that movie. Please check the movie name and try again.")
            return

        # Update status message
        await status_message.edit_text("Downloading poster...")

        # Download poster
        poster_data = await download_poster(movie_data['poster'])
        
        if not poster_data:
            await status_message.edit_text("Sorry, couldn't fetch the movie poster. Please check movie name and try again.")
            return

        # Format caption
        caption = format_caption(
            movie_data['movie_p'],
            movie_data['year_p'],
            movie_data['audio_p'],
            movie_data['genre_p'],
            movie_data['synopsis_p']
        )

        # Prepare poster for sending
        poster_stream = BytesIO(poster_data)
        poster_stream.name = "poster.jpg"

        # Send poster with caption
        await client.send_photo(
            chat_id=message.chat.id,
            photo=poster_stream,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN
        )

        # Delete the status message
        await status_message.delete()
        
        await logger.log_message(
            action="Caption Command",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id,
            chat_title=f"Movie: {movie_data['movie_p']}"
        )

    except Exception as e:
        await message.reply_text("An error occurred while processing your request. Please try again later.")
        print(f"Caption command error: {str(e)}")
        
        await logger.log_message(
            action="Caption Command Error",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id,
            error=e
        )

async def start_bot():
    try:
        await espada.start()
        await logger.log_bot_start()
        print("Bot Started Successfully!")

        # Keep the bot running indefinitely
        while True:
            # Check if the client is still connected every 10 seconds
            if not espada.is_connected:
                await espada.reconnect()
            await asyncio.sleep(10)

    except Exception as e:
        print(f"Bot Crashed: {str(e)}")
        await logger.log_bot_crash(e)
    finally:
        if espada.is_connected:  # Check if client is still connected before stopping
            await espada.stop()
            
if __name__ == "__main__":
    print("Bot is Starting...")
    espada.run(start_bot())