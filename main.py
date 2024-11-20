from dotenv import load_dotenv
load_dotenv()
from pyrogram import Client, filters, utils
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery,InputMediaPhoto
from pyrogram.enums import ParseMode
import os
import asyncio
import aiohttp
from io import BytesIO
from plugins.logs import Logger
from script import START_TEXT, HELP_TEXT, SUPPORT_TEXT, ABOUT_TEXT,MOVIE_TEXT
import random

# Get environment variables
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
log_channel = int(os.getenv('LOG_CHANNEL'))
rapidapi_key = os.getenv("RAPID_API")

if not all([api_id, api_hash, bot_token, rapidapi_key, log_channel]):
    raise ValueError("Please set the API_ID, API_HASH, BOT_TOKEN, RAPID_API, and LOG_CHANNEL environment variables")

# Initialize the bot
espada = Client("movie_caption_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
logger = Logger(espada)

RAPIDAPI_URL = "https://movie-database-alternative.p.rapidapi.com/"
RAPIDAPI_HEADERS = {
    "x-rapidapi-key": rapidapi_key,
    "x-rapidapi-host": "movie-database-alternative.p.rapidapi.com"
}

# Define keyboard layouts
start_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏠 Home", callback_data="home"),
     InlineKeyboardButton("🤖 About", callback_data="about")
     ],
    [InlineKeyboardButton("💬 Support", callback_data="support"),
     InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    [InlineKeyboardButton("🍿 Movie-Anime", callback_data="movie")]
    
])

async def search_titles(query, search_type="movie"):
    """Search for movies/series using the Movie Database Alternative API"""
    try:
        params = {
            "s": query,
            "r": "json",
            "type": search_type
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(RAPIDAPI_URL, headers=RAPIDAPI_HEADERS, params=params) as response:
                data = await response.json()
                return data.get('Search', []) if data.get('Response') == 'True' else []
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []

async def get_title_details(imdb_id):
    """Get detailed information for a specific title using its IMDb ID"""
    try:
        params = {
            "r": "json",
            "i": imdb_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(RAPIDAPI_URL, headers=RAPIDAPI_HEADERS, params=params) as response:
                return await response.json()
    except Exception as e:
        print(f"Details fetch error: {str(e)}")
        return None

def create_search_results_keyboard(results):
    """Create inline keyboard from search results"""
    buttons = []
    for item in results:
        text = f"{item['Title']} ({item['Year']})"
        callback_data = f"title_{item['imdbID']}"
        buttons.append([InlineKeyboardButton(text, callback_data=callback_data)])
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="home")])
    return InlineKeyboardMarkup(buttons)

async def download_image(url):
    """Download image from URL"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
    return None

async def download_poster(poster_url):
    """Download movie poster from URL"""
    if poster_url and poster_url != 'N/A':
        async with aiohttp.ClientSession() as session:
            async with session.get(poster_url) as response:
                if response.status == 200:
                    return await response.read()
    return None

def determine_audio(movie_details):
    """
    Determine audio language/type based on available information
    
    Args:
        movie_details (dict): Movie details from Rapid API
    Returns:
        str: Audio language/type
    """
    
    audio_options = [
        'English',
        'Hindi',
        'Multi-Audio',
        'Hindi Dubbed',
        'English Dubbed'
    ] 
    
    # Safely get values and convert to lowercase, using empty string if not found
    actors = str(movie_details.get('Actors', '')).lower()
    plot = str(movie_details.get('Plot', '')).lower()
    country = str(movie_details.get('Country', '')).lower()
    language = str(movie_details.get('Language', '')).lower()
    
    # Check for Hindi content
    if 'india' in country or 'hindi' in language:
        return 'Hindi'
    
    if 'hindi' in actors or 'hindi' in plot:
        return 'Hindi'
    
    # Check for English content
    if 'usa' in country or 'uk' in country or 'english' in language:
        return 'English'
    
    if 'english' in actors or 'english' in plot:
        return 'English'
    
    # Default behavior for other cases
    if country and country not in ['usa', 'uk', 'india']:
        if random.random() < 0.7:  
            return 'Multi-Audio'
        else:
            return 'Hindi Dubbed'
    
    # Use weighted random choice if no specific criteria met
    weights = [0.3, 0.2, 0.3, 0.1, 0.1]
    return random.choices(audio_options, weights=weights)[0]

def format_caption(movie, year, audio, language, genre, imdbRating, runTime, rated, synopsis):
    """Format the caption with Markdown"""
    
    
    audio = determine_audio({
        "Language": language,
        "Genre": genre,
        "Actors": "",
        "Plot": synopsis,
        "Country": ""
    })
    
    try:
        if rated == "Not Rated":
            CertificateRating = "U/A"
        else:
            CertificateRating = rated
    except Exception as e:
        CertificateRating = rated
        
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
» 𝗥𝗮𝘁𝗲𝗱: {CertificateRating}

» 𝗦𝘆𝗻𝗼𝗽𝘀𝗶𝘀
> {synopsis}

@Teamxpirates
>[𝗜𝗳 𝗬𝗼𝘂 𝗦𝗵𝗮𝗿𝗲 𝗢𝘂𝗿 𝗙𝗶𝗹𝗲𝘀 𝗪𝗶𝘁𝗵𝗼𝘂𝘁 𝗖𝗿𝗲𝗱𝗶𝘁, 𝗧𝗵𝗲𝗻 𝗬𝗼𝘂 𝗪𝗶𝗹𝗹 𝗯𝗲 𝗕𝗮𝗻𝗻𝗲𝗱]"""
    return caption

def format_series_caption(movie, year, audio, language, genre, imdbRating, totalSeason, type, synopsis):
    """Format the caption with Markdown"""
    
    audio = determine_audio({
        "Language": language,
        "Genre": genre,
        "Actors": "",
        "Plot": synopsis,
        "Country": ""
    })
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
 ‣ 𝗔𝘂𝗱𝗶𝗼:  {audio}
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
        if callback_query.data.startswith("title_"):
            # Handle title selection
            imdb_id = callback_query.data.split("_")[1]
            await process_title_selection(callback_query, imdb_id)
            
        elif callback_query.data == "home":
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

@espada.on_message(filters.command(["captionM", "cm"]))
async def caption_command(client, message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text(
                "Please provide a movie name.\n"
                "Example: `/cm Kalki 2898 AD`"
            )
            return

        movie_name = " ".join(parts[1:])
        status_message = await message.reply_text("Searching for movies... Please wait!")

        # Search for movies
        results = await search_titles(movie_name, "movie")
        
        if not results:
            await status_message.edit_text("No movies found with that title. Please try a different search.")
            return

        # Create and send results keyboard
        reply_markup = create_search_results_keyboard(results)
        await status_message.edit_text(
            "Found the following movies. Please select one:",
            reply_markup=reply_markup
        )

    except Exception as e:
        await message.reply_text("An error occurred while processing your request. Please try again later.")
        print(f"Movie search error: {str(e)}")
        
        
@espada.on_message(filters.command(["captionS", "cs"]))
async def series_command(client, message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text(
                "Please provide a series name.\n"
                "Example: `/cs Breaking Bad`"
            )
            return

        series_name = " ".join(parts[1:])
        status_message = await message.reply_text("Searching for series... Please wait!")

        # Search for series
        results = await search_titles(series_name, "series")
        
        if not results:
            await status_message.edit_text("No series found with that title. Please try a different search.")
            return

        # Create and send results keyboard
        reply_markup = create_search_results_keyboard(results)
        await status_message.edit_text(
            "Found the following series. Please select one:",
            reply_markup=reply_markup
        )

    except Exception as e:
        await message.reply_text("An error occurred while processing your request. Please try again later.")
        print(f"Series search error: {str(e)}")
        
        
@espada.on_message(~filters.command(["start", "captionM", "cm","captionS", "cs"]) & ~filters.channel & ~filters.group)
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
async def process_title_selection(callback_query, imdb_id):
    """Process the selected title and generate the appropriate caption"""
    try:
        # Show loading message
        loading_msg = await callback_query.message.edit_text("Fetching details... Please wait!")

        # Get detailed information
        title_data = await get_title_details(imdb_id)
        if not title_data:
            await loading_msg.edit_text("Failed to fetch title details. Please try again.")
            return

        # Create data dictionary for additional message
        if title_data.get('Type') == 'series':
            series_data = {
                'movie_p': title_data.get('Title', 'N/A'),
                'year_p': title_data.get('Year', 'N/A'),
            }
            additional_message = f"""`[PirecyKings2] [Sseason Eepisode] {series_data['movie_p']} ({series_data['year_p']}) @pirecykings2`

`S01 English - Hindi [480p]`

`S01 English - Hindi [720p]`

`S01 English - Hindi [1080p]`"""
            
            caption = format_series_caption(
                title_data.get('Title', 'N/A'),
                title_data.get('Year', 'N/A'),
                title_data.get('Language', 'N/A'),
                title_data.get('Language', 'N/A'),
                title_data.get('Genre', 'N/A'),
                title_data.get('imdbRating', 'N/A'),
                title_data.get('totalSeasons', 'N/A'),
                title_data.get('Type', 'N/A'),
                title_data.get('Plot', 'N/A')
            )
        else:
            movie_data = {
                'movie_p': title_data.get('Title', 'N/A'),
                'year_p': title_data.get('Year', 'N/A'),
                'audio_p': determine_audio(title_data)
            }
            additional_message = f"""`[PirecyKings2] {movie_data['movie_p']} ({movie_data['year_p']}) @pirecykings2`

`{movie_data['movie_p']} ({movie_data['year_p']}) 480p - 1080p [{movie_data['audio_p']}]`"""
            
            caption = format_caption(
                title_data.get('Title', 'N/A'),
                title_data.get('Year', 'N/A'),
                title_data.get('Language', 'N/A'),
                title_data.get('Language', 'N/A'),
                title_data.get('Genre', 'N/A'),
                title_data.get('imdbRating', 'N/A'),
                title_data.get('Runtime', 'N/A'),
                title_data.get('Rated', 'U/A'),
                title_data.get('Plot', 'N/A')
            )

        # Handle poster and send messages
        poster_url = title_data.get('Poster')
        if poster_url and poster_url != 'N/A':
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(poster_url) as response:
                        if response.status == 200:
                            poster_data = await response.read()
                            poster_stream = BytesIO(poster_data)
                            poster_stream.name = f"poster_{imdb_id}.jpg"
                            
                            # Delete loading message
                            await callback_query.message.delete()
                            
                            # Send main caption with photo
                            await callback_query.message.reply_photo(
                                photo=poster_stream,
                                caption=caption,
                                parse_mode=ParseMode.MARKDOWN
                            )
                            
                            # Send additional message
                            await callback_query.message.reply_text(
                                additional_message,
                                parse_mode=ParseMode.MARKDOWN
                            )
                            return
            except Exception as poster_error:
                print(f"Poster download error: {str(poster_error)}")
        
        # Fallback to text-only if no poster or poster download failed
        await callback_query.message.edit_text(
            caption,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Send additional message even in text-only case
        await callback_query.message.reply_text(
            additional_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        error_msg = f"Title selection error: {str(e)}"
        print(error_msg)
        await callback_query.message.edit_text(
            "An error occurred while processing your selection. Please try again."
        )

async def start_bot():
    try:
        await espada.start()
        await logger.log_bot_start()
        print("Bot Started Successfully!")

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
