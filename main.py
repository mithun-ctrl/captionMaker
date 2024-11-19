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
from script import START_TEXT, HELP_TEXT, SUPPORT_TEXT, ABOUT_TEXT,MOVIE_TEXT
from fetchMovieData import fetch_movie_data, omdb_api_key
import random
import motor.motor_asyncio
from pymongo import MongoClient
import datetime

# Get environment variables
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
log_channel = int(os.getenv('LOG_CHANNEL'))
target_channel = int(os.getenv('TARGET_CHANNEL'))
tmdb_api_key= os.getenv("YOUR_TMDB_API_KEY")
mongo_uri = os.getenv("MONGO_URI")

YOUR_TMDB_API_KEY = tmdb_api_key
MONGO_URI = mongo_uri
DATABASE_NAME = "movie_bot_db"
GENERATED_MOVIES_COLLECTION = "generated_movies"

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]
generated_movies_collection = db[GENERATED_MOVIES_COLLECTION]

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
     InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    [InlineKeyboardButton("🍿 Movie-Anime", callback_data="movie")]
    
])

async def download_image(url):
    """Download image from URL"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
    return None

async def is_movie_already_generated(movie_title):
    """Check if a movie has been previously generated"""
    existing_movie = await generated_movies_collection.find_one({"movie_title": movie_title})
    return existing_movie is not None

async def record_generated_movie(movie_title, movie_data):
    """Record a generated movie in the database"""
    await generated_movies_collection.insert_one({
        "movie_title": movie_title,
        "generated_at": datetime.datetime.now(datetime.timezone.utc),
        "movie_data": movie_data
    })

async def download_poster(poster_url):
    """Download movie poster from URL"""
    if poster_url and poster_url != 'N/A':
        async with aiohttp.ClientSession() as session:
            async with session.get(poster_url) as response:
                if response.status == 200:
                    return await response.read()
    return None

def format_caption(movie, year, audio, genre, imdbRating, runTime, rated, synopsis):
    """Format the caption with Markdown"""
    
    try:
        # Extract the number from the "Runtime" string (e.g., "57 min")
        minutes = int(runTime.split()[0])  # Get the numeric part
        if minutes > 60:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            formatted_runtime = f"{hours}h {remaining_minutes}min"
        elif minutes==60:
            hours = minutes // 60
            formatted_runtime = f"{hours}h"
        else:
            formatted_runtime = runTime
    except (ValueError, IndexError):
        formatted_runtime = runTime  # Use the raw value if parsing fails
    
    
    caption = f""" {movie}（{year}）
    
» 𝗔𝘂𝗱𝗶𝗼: {audio}（Esub）
» 𝗤𝘂𝗮𝗹𝗶𝘁𝘆: 480p | 720p | 1080p |
» 𝗚𝗲𝗻𝗿𝗲: {genre}
» 𝗜𝗺𝗱𝗯 𝗥𝗮𝘁𝗶𝗻𝗴: {imdbRating}/10
» 𝗥𝘂𝗻𝘁𝗶𝗺𝗲: {formatted_runtime}
» 𝗥𝗮𝘁𝗲𝗱: {rated}

» 𝗦𝘆𝗻𝗼𝗽𝘀𝗶𝘀
> {synopsis}

@Teamxpirates
>[𝗜𝗳 𝗬𝗼𝘂 𝗦𝗵𝗮𝗿𝗲 𝗢𝘂𝗿 𝗙𝗶𝗹𝗲𝘀 𝗪𝗶𝘁𝗵𝗼𝘂𝘁 𝗖𝗿𝗲𝗱𝗶𝘁, 𝗧𝗵𝗲𝗻 𝗬𝗼𝘂 𝗪𝗶𝗹𝗹 𝗯𝗲 𝗕𝗮𝗻𝗻𝗲𝗱]"""
    return caption

def format_series_caption(movie, year, audio, genre, imdbRating, totalSeason, type, synopsis):
    """Format the caption with Markdown"""
    
    season_count = ""
    
    try:
        totalSeason = int(totalSeason)
        for season in range(1, totalSeason+1):
            season_count += f"\n│S{season}) [𝟺𝟾𝟶ᴘ]  [𝟽𝟸𝟶ᴘ]  [𝟷𝟶𝟾𝟶ᴘ]\n"
    except ValueError:
        season_count = "N/A"
        
    
    caption = f""" {movie} ({year})
╭──────────────────────
 ‣ 𝗧𝘆𝗽𝗲: {type.capitalize()}
 ‣ 𝗦𝗲𝗮𝘀𝗼𝗻: {totalSeason}
 ‣ 𝗘𝗽𝗶𝘀𝗼𝗱𝗲𝘀: 𝟬𝟭-𝟬8
 ‣ 𝗜𝗠𝗗𝗯 𝗥𝗮𝘁𝗶𝗻𝗴𝘀: {imdbRating}/10
 ‣ 𝗣𝗶𝘅𝗲𝗹𝘀: 𝟰𝟴𝟬𝗽, 𝟳𝟮𝟬𝗽, 𝟭𝟬𝟴𝟬𝗽
 ‣ 𝗔𝘂𝗱𝗶𝗼:  {audio} हिंदी
├──────────────────────
 ‣ 𝗚𝗲𝗻𝗿𝗲𝘀:{genre}
╰──────────────────────
┌────────────────────────
{season_count}
└────────────────────────
│[Click Here To Access Files]
└────────────────────────
 ‣ @TeamXPirates
> [𝗜𝗳 𝗬𝗼𝘂 𝗦𝗵𝗮𝗿𝗲 𝗢𝘂𝗿 𝗙𝗶𝗹𝗲𝘀 𝗪𝗶𝘁𝗵𝗼𝘂𝘁 𝗖𝗿𝗲𝗱𝗶𝘁, 𝗧𝗵𝗲𝗻 𝗬𝗼𝘂 𝗪𝗶𝗹𝗹 𝗯𝗲 𝗕𝗮𝗻𝗻𝗲𝗱]"""

    return caption

auto_generation_active = False
auto_generation_task = None

async def fetch_random_movies_and_series():
    """Fetch a list of random movies and series released after 2000 from IMDb Rapid API"""
    keywords = ["action", "comedy", "drama", "thriller", "horror", "romance", "sci-fi", "adventure"]
    random_keyword = random.choice(keywords)  # Pick a random keyword for search

    url = "https://imdb-top-100-movies.p.rapidapi.com/series/"
    headers = {
        "x-rapidapi-key": "55a64eed3cmsh549a490258f7e64p1dbbf4jsncf921a05a9ff",
        "x-rapidapi-host": "imdb-top-100-movies.p.rapidapi.com"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    for item in data:  # Assuming the data is a list of movies
                        title = item.get('title', "")
                        if not await is_movie_already_generated(title):
                            results.append(title)
                    return results[:20]  # Limit to top 20 unique items
                else:
                    print(f"Failed to fetch data: {response.status}")
                    return []
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []


async def generate_random_movie_poster(client):
    """
    Generate and send a random movie poster with caption
    
    Args:
        client (Client): Pyrogram client instance
    """
    global auto_generation_active

    while auto_generation_active:
        try:
            # Fetch random movies from API
            movies = await fetch_random_movies_and_series()
            
            if not movies:
                # Fallback to a predefined list if API fails
                movies = [
                    "Inception", "Interstellar", "The Matrix", 
                    "Dune", "Blade Runner 2049"
                ]
                movies = [
                    movie for movie in movies 
                    if not await is_movie_already_generated(movie)
                ]
            if not movies:
                await asyncio.sleep(60)  # Wait if no new movies
                continue
            
            # Select a random movie
            movie_name = random.choice(movies)
            
            # Fetch movie data from OMDB
            movie_data = await fetch_movie_data(movie_name)
            
            if movie_data:
                
                # Record the generated movie
                await record_generated_movie(movie_name, movie_data)
                
                if movie_data.get('type_p') == 'series':
                    caption = format_series_caption(
                        movie_data['movie_p'],
                        movie_data['year_p'],
                        movie_data['audio_p'],
                        movie_data['genre_p'],
                        movie_data['imdbRating_p'],
                        movie_data['totalSeasons_p'],
                        movie_data['type_p'],
                        movie_data['synopsis_p']
                    )                   
                else:
                    caption = format_caption(
                        movie_data['movie_p'],
                        movie_data['year_p'],
                        movie_data['audio_p'],
                        movie_data['genre_p'],
                        movie_data['imdbRating_p'],
                        movie_data['runTime_p'],
                        movie_data['rated_p'],
                        movie_data['synopsis_p']
                    )
                
                additional_message_S = f"""`[PirecyKings2] [Sseason Eepisode] {movie_data['movie_p']} ({movie_data['year_p']}) @pirecykings2`
            
                    `S01 English - Hindi [480p]`
            
                    `S01 English - Hindi [720p]`
            
                    `S01 English - Hindi [1080p]`"""
                additional_message_M = f"""`[PirecyKings2] {movie_data['movie_p']} ({movie_data['year_p']}) @pirecykings2`
            
                    `{movie_data['movie_p']} ({movie_data['year_p']}) 480p - 1080p [{movie_data['audio_p']}]`"""
                
                # Download poster
                poster_data = await download_poster(movie_data['poster'])
                
                if poster_data:
                    # Prepare poster for sending
                    poster_stream = BytesIO(poster_data)
                    poster_stream.name = "poster.jpg"
                    
                    # Send poster with caption to the specific channel
                    await client.send_photo(
                        chat_id=target_channel,
                        photo=poster_stream,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN
                    )
                if movie_data.get('type_p')=='series':
                    
                    await client.send_message(
                        chat_id=target_channel,
                        text=additional_message_S,
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await client.send_message(
                        chat_id=target_channel,
                        text=additional_message_M,
                        parse_mode=ParseMode.MARKDOWN
                    )
            
            # Wait for 1 minute before next poster
            await asyncio.sleep(60)
            
        except Exception as e:
            print(f"Random poster generation error: {str(e)}")
            # Log the error instead of just printing
            if hasattr(logger, 'log_error'):
                await logger.log_error(e)
            if not auto_generation_active:
                auto_generation_task = asyncio.create_task(generate_random_movie_poster(client))
            await asyncio.sleep(60)  # Wait before retrying

async def monitor_auto_generation(client):
    global auto_generation_active, auto_generation_task
    
    while True:
        if auto_generation_active and (auto_generation_task is None or auto_generation_task.done()):
            print("Restarting auto-generation task")
            auto_generation_task = asyncio.create_task(generate_random_movie_poster(client))
        
        await asyncio.sleep(300)


@espada.on_message(filters.command(["startautogen"]))
async def start_auto_generation(client, message):
    global auto_generation_active, auto_generation_task
    
    if not auto_generation_active:
        auto_generation_active = True
        auto_generation_task = asyncio.create_task(generate_random_movie_poster(client))
        await message.reply_text("Auto movie poster generation started!")
    else:
        await message.reply_text("Auto movie poster generation is already running.")

@espada.on_message(filters.command(["stopautogen"]))
async def stop_auto_generation(client, message):
    global auto_generation_active, auto_generation_task
    
    if auto_generation_active:
        auto_generation_active = False
        if auto_generation_task:
            auto_generation_task.cancel()
        await message.reply_text("Auto movie poster generation stopped!")
    else:
        await message.reply_text("Auto movie poster generation is not running.")


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
        elif callback_query.data == "movie":
            await callback_query.message.edit_caption(
                 caption=MOVIE_TEXT,
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
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text(
                "Please provide a movie name.\n"
                "Example: `/caption The Penguin`"
            )
            return

        movie_name = " ".join(parts[1:-1])
        include_filename = "-f" in parts or "-filename" in parts
        include_database = "-fdb" in parts or "-filenamedb" in parts

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
            movie_data['imdbRating_p'],
            movie_data['runTime_p'],
            movie_data['rated_p'],
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

        # Add additional message if -f or -filename is present
        if include_filename:
            additional_message = f"`[PirecyKings2] {movie_data['movie_p']} ({movie_data['year_p']}) @pirecykings2`"
            await client.send_message(
                chat_id=message.chat.id,
                text=additional_message,
                parse_mode=ParseMode.MARKDOWN
            )

        # Add additional message if -db or -database is present
        if include_database:
            additional_message = f"""`[PirecyKings2] {movie_data['movie_p']} ({movie_data['year_p']}) @pirecykings2`
            
            `{movie_data['movie_p']} ({movie_data['year_p']}) 480p - 1080p [{movie_data['audio_p']}]`"""
            await client.send_message(
                chat_id=message.chat.id,
                text=additional_message,
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
@espada.on_message(filters.command(["series"]))
async def series_command(client, message):
    try:
        # Extract movie name from command
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text(
                "Please provide a movie name.\n"
                "Example: `/caption Kalki 2898 AD`"
            )
            return

        series_name = " ".join(parts[1:-1])
        include_filename = "-f" in parts or "-filename" in parts
        include_database = "-fdb" in parts or "-filenamedb" in parts

        # Show "Fetching movie details..." message
        status_message = await message.reply_text("Fetching series details... Please wait!")

        # Fetch movie data from OMDB
        series_data = await fetch_movie_data(series_name)

        if not series_data:
            await status_message.edit_text("Sorry, I couldn't find information for that series. Please check the series name and try again.")
            return

        # Update status message
        await status_message.edit_text("Downloading poster...")

        # Download poster
        poster_data = await download_poster(series_data['poster'])

        if not poster_data:
            await status_message.edit_text("Sorry, couldn't fetch the series poster. Please check series name and try again.")
            return

        # Format caption
        caption = format_series_caption(
            series_data['movie_p'],
            series_data['year_p'],
            series_data['audio_p'],
            series_data['genre_p'],
            series_data['imdbRating_p'],
            series_data['totalSeasons_p'],
            series_data['type_p'],
            series_data['synopsis_p']
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

        # Add additional message if -f or -filename is present
        if include_filename:
            additional_message = f"`[PirecyKings2] [Sseason Eepisode] {series_data['movie_p']} ({series_data['year_p']}) @pirecykings2`"
            await client.send_message(
                chat_id=message.chat.id,
                text=additional_message,
                parse_mode=ParseMode.MARKDOWN
            )

        # Add additional message if -db or -database is present
        if include_database:
            additional_message = f"""`[PirecyKings2] [Sseason Eepisode] {series_data['movie_p']} ({series_data['year_p']}) @pirecykings2`
            
            `S01 English - Hindi [480p]`
            
            `S01 English - Hindi [720p]`
            
            `S01 English - Hindi [1080p]`"""
            await client.send_message(
                chat_id=message.chat.id,
                text=additional_message,
                parse_mode=ParseMode.MARKDOWN
            )

        # Delete the status message
        await status_message.delete()

        await logger.log_message(
            action="Series Command",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id,
            chat_title=f"Movie: {series_data['movie_p']}"
        )

    except Exception as e:
        await message.reply_text("An error occurred while processing your request. Please try again later.")
        print(f"Series command error: {str(e)}")

        await logger.log_message(
            action="Series Command Error",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id,
            error=e
        )
@espada.on_message(~filters.command(["start", "caption", "series"]) & ~filters.channel & ~filters.group)
async def default_response(client, message):
    try:
        # Send a default message in response
        await message.reply_text("⚠ Invaild command!")

        # Log the default response
        await logger.log_message(
            action="Default Response",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id,
        )

    except Exception as e:
        print(f"Default response error: {str(e)}")
        await logger.log_message(
            action="Default Response Error",
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

        asyncio.create_task(generate_random_movie_poster(espada))
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
