from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.enums import ParseMode
import asyncio
from io import BytesIO
import random
from plugins.logs import Logger
from script import START_TEXT, HELP_TEXT, SUPPORT_TEXT, ABOUT_TEXT, MOVIE_TEXT
from buttons.startButton import start_keyboard
from config import (
    espada,
    api_hash,
    api_id,
    bot_token,
    log_channel,
    tmdb_api_token,
    omdb_api,
    DUMP_CHANNELS,
)
from handlers.tmdb import tmdbFunctions
from handlers.download import downloadHandler

if not all([api_id, api_hash, bot_token, log_channel, tmdb_api_token, omdb_api]):
    raise ValueError("Please set environment variables correctly")

logger = Logger(espada)
OMDB_API_KEY = omdb_api
TMDB_API_KEY = tmdb_api_token

tmdb = tmdbFunctions()
download = downloadHandler()


def create_content_list_keyboard(results, page, total_pages, command_type):
    buttons = []
    for item in results:
        title = item.get("title") or item.get("name")
        release_date = item.get("release_date") or item.get("first_air_date", "")
        year = release_date[:4] if release_date else "N/A"
        if "first_air_date" in item:
            media_type = "tv"
        elif "release_date" in item:
            media_type = "movie"
        else:
            media_type = item.get("media_type", "movie")
        text = f"{title} ({year})"
        callback_data = f"title_{item['id']}_{media_type}"
        buttons.append([InlineKeyboardButton(text, callback_data=callback_data)])
    nav_buttons = []
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                "⬅️ Previous", callback_data=f"{command_type}_page_{page-1}"
            )
        )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton("Next ➡️", callback_data=f"{command_type}_page_{page+1}")
        )
    if nav_buttons:
        buttons.append(nav_buttons)
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_search")])
    return InlineKeyboardMarkup(buttons)


def determine_audio(movie_details):
    audio_options = [
        "Hindi-English",
        "Hindi",
        "Hindi-English",
        "Hindi-English",
        "English-Hindi",
    ]
    actors = str(movie_details.get("Actors", "")).lower()
    plot = str(movie_details.get("Plot", "")).lower()
    country = str(movie_details.get("Country", "")).lower()
    language = str(movie_details.get("Language", "")).lower()
    
    if "india" in country or "hindi" in language:
        return "Hindi"
    if "hindi" in actors or "hindi" in plot:
        return "Hindi"
    if "usa" in country or "uk" in country or "english" in language:
        return "Hindi-English"
    if "english" in actors or "english" in plot:
        return "Hindi-English"
    if country and country not in ["usa", "uk", "india"]:
        if random.random() < 0.7:
            return "Hindi-English"
        else:
            return "Hindi-English"
    weights = [0.3, 0.2, 0.3, 0.1, 0.1]
    return random.choices(audio_options, weights=weights)[0]


def format_caption(movie, year, audio, language, genre, imdb_rating, runTime, rated, synopsis):
    audio = determine_audio(
        {
            "Language": language,
            "Genre": genre,
            "Actors": "",
            "Plot": synopsis,
            "Country": "",
        }
    )
    try:
        if rated == "Not Rated":
            CertificateRating = "U/A"
        else:
            CertificateRating = rated
    except Exception as e:
        CertificateRating = rated
    try:
        minutes = int(runTime.split()[0])
        if minutes > 60:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            formatted_runtime = f"{hours}h {remaining_minutes}min"
        elif minutes == 60:
            hours = minutes // 60
            formatted_runtime = f"{hours}h"
        else:
            formatted_runtime = runTime
    except (ValueError, IndexError):
        formatted_runtime = runTime
    caption = f""" {movie} ({year})
    
» 𝗔𝘂𝗱𝗶𝗼: {audio} (Esub)
» 𝗤𝘂𝗮𝗹𝗶𝘁𝘆: 480p | 720p | 1080p |
» 𝗚𝗲𝗻𝗿𝗲: {genre}
» 𝗜𝗺𝗱𝗯 𝗥𝗮𝘁𝗶𝗻𝗴: {imdb_rating}/10
» 𝗥𝘂𝗻𝘁𝗶𝗺𝗲: {formatted_runtime}
» 𝗥𝗮𝘁𝗲𝗱: {CertificateRating}

» 𝗦𝘆𝗻𝗼𝗽𝘀𝗶𝘀
> {synopsis}

@Teamxpirates
>[𝗜𝗳 𝗬𝗼𝘂 𝗦𝗵𝗮𝗿𝗲 𝗢𝘂𝗿 𝗙𝗶𝗹𝗲𝘀 𝗪𝗶𝘁𝗵𝗼𝘂𝘁 𝗖𝗿𝗲𝗱𝗶𝘁, 𝗧𝗵𝗲𝗻 𝗬𝗼𝘂 𝗪𝗶𝗹𝗹 𝗯𝗲 𝗕𝗮𝗻𝗻𝗲𝗱]"""
    return caption

def format_series_caption(movie, year, audio, language, genre, imdb_rating, runTime, totalSeason, type, synopsis):
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
            season_count += f"\n│S{season}) [𝟺𝟾𝟶ᴘ]  [𝟽𝟸𝟶ᴘ]  [𝟷𝟶𝟾𝟶ᴘ]"
    except ValueError:
        season_count = "N/A"
    
    # calcate runtime    
        
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
        
    
    caption = f""" {movie} ({year})
╭──────────────────────
 ‣ 𝗧𝘆𝗽𝗲: {type.capitalize()}
 ‣ 𝗦𝗲𝗮𝘀𝗼𝗻: {totalSeason}
 ‣ 𝗘𝗽𝗶𝘀𝗼𝗱𝗲𝘀: 01-08
 ‣ 𝗜𝗠𝗗𝗯 𝗥𝗮𝘁𝗶𝗻𝗴𝘀: {imdb_rating}/10
 ‣ 𝗣𝗶𝘅𝗲𝗹𝘀: 480p, 720p, 1080p
 ‣ 𝗔𝘂𝗱𝗶𝗼: {audio}
 ‣ 𝗥𝘂𝗻𝘁𝗶𝗺𝗲: {formatted_runtime}
├──────────────────────
 ‣ 𝗚𝗲𝗻𝗿𝗲𝘀: {genre}
╰──────────────────────
┌────────────────────────
│{season_count}
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
        start_image = await download.download_image("https://jpcdn.it/img/small/682f656e6957597eebce76a1b99ea9e4.jpg")
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

@espada.on_message(filters.command(["trending", "tr"]))
async def trending_command(client, message):
    try:

        await message.delete()

        parts = message.text.split()
        page = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1

        # Show loading message
        status_message = await message.reply_text("Fetching trending content... Please wait!")

        # Get trending content
        trending_data = await tmdb.get_trending_content(page=page)

        if not trending_data or not trending_data.get('results'):
            await status_message.edit_text("No trending content found.")
            return

        # Create keyboard with results
        keyboard = create_content_list_keyboard(
            trending_data['results'],
            page,
            trending_data['total_pages'],
            'trending'
        )

        # Update message with results
        await status_message.edit_text(
            f"📈 Trending Movies & TV Shows (Page {page}/{trending_data['total_pages']})",
            reply_markup=keyboard
        )
        await logger.log_message(
            action="Trending Command",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id
        )

    except Exception as e:
        await message.reply_text("An error occurred while fetching trending content.")
        print(f"Trending command error: {str(e)}")

@espada.on_message(filters.command(["popular", "pp"]))
async def popular_command(client, message):
    try:
        
        await message.delete()
        
        parts = message.text.split()
        page = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
        
        # Show loading message
        status_message = await message.reply_text("Fetching popular content... Please wait!")
        
        # Get popular content
        popular_data = await tmdb.get_popular_content(page=page)
        
        if not popular_data or not popular_data.get('results'):
            await status_message.edit_text("No popular content found.")
            return
        
        # Create keyboard with results
        keyboard = create_content_list_keyboard(
            popular_data['results'],
            page,
            popular_data['total_pages'],
            'popular'
        )
        
        # Update message with results
        await status_message.edit_text(
            f"🔥 Popular Movies (Page {page}/{popular_data['total_pages']})",
            reply_markup=keyboard
        )
        
        await logger.log_message(
            action="Popular Command",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id
        )
        
    except Exception as e:
        await message.reply_text("An error occurred while fetching popular content.")
        print(f"Popular command error: {str(e)}")

@espada.on_message(filters.command(["upcoming", "up"]))
async def upcoming_command(client, message):
    try:
        
        await message.delete()
        
        parts = message.text.split()
        page = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
        
        # Show loading message
        status_message = await message.reply_text("Fetching upcoming content... Please wait!")
        
        # Get upcoming content
        upcoming_data = await tmdb.get_upcoming_content(page=page)
        
        if not upcoming_data or not upcoming_data.get('results'):
            await status_message.edit_text("No upcoming content found.")
            return
        
        # Create keyboard with results
        keyboard = create_content_list_keyboard(
            upcoming_data['results'],
            page,
            upcoming_data['total_pages'],
            'upcoming'
        )
        
        # Update message with results
        await status_message.edit_text(
            f"🆕 Upcoming Movies (Page {page}/{upcoming_data['total_pages']})",
            reply_markup=keyboard
        )
        
        await logger.log_message(
            action="Upcoming Command",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id
        )
        
    except Exception as e:
        await message.reply_text("An error occurred while fetching upcoming content.")
        print(f"Upcoming command error: {str(e)}")

@espada.on_callback_query()
async def callback_query(client, callback_query: CallbackQuery):
    try:
        data = callback_query.data
        
        if "_page_" in data:
            parts = data.split("_page_")
            category = parts[0]
            page = int(parts[1])
            
            # Show loading message
            await callback_query.message.edit_text("Loading next page... Please wait!")
            
            if category == "trending":
                content = await tmdb.get_trending_content(page=page)
                title = "📈 Trending Movies & TV Shows"
            elif category == "popular":
                content = await tmdb.get_popular_content(page=page)
                title = "🔥 Popular Movies"
            elif category == "upcoming":
                content = await tmdb.get_upcoming_content(page=page)
                title = "🆕 Upcoming Movies"
            elif category == "movie_search":
                # Get the original search query from the message text
                message_text = callback_query.message.text
                # Extract the search query from the message
                search_query = message_text.split("'")[1] if "'" in message_text else ""
                content = await tmdb.full_search_titles(search_query, "movie", page=page)
                title = f"🎬 Found movies matching '{search_query}'"
            elif category == "series_search":
                # Get the original search query from the message text
                message_text = callback_query.message.text
                # Extract the search query from the message
                search_query = message_text.split("'")[1] if "'" in message_text else ""
                content = await tmdb.full_search_titles(search_query, "tv", page=page)
                # Mark each result as TV
                for result in content.get('results', []):
                    result['media_type'] = 'tv'
                title = f"📺 Found series matching '{search_query}'"
            
            if content and content.get('results'):
                keyboard = create_content_list_keyboard(
                    content['results'],
                    page,
                    content['total_pages'],
                    category
                )
                await callback_query.message.edit_text(
                    f"{title} (Page {page}/{content['total_pages']})",
                    reply_markup=keyboard
                )
            else:
                await callback_query.message.edit_text("No content found for this page.")
        
        elif data.startswith("title_"):
            # Parse the callback data correctly
            parts = data.split("_")
            if len(parts) >= 3:
                tmdb_id = parts[1]
                media_type = parts[2]
                # Process the title selection without deleting the search results
                await process_title_selection(callback_query, tmdb_id, media_type)
            else:
                await callback_query.answer("Invalid selection data")
        
        elif callback_query.data == "cancel_search":
            await callback_query.message.delete()
            
        elif callback_query.data == "home":
            # Check if the current caption is different from START_TEXT
            current_caption = callback_query.message.caption or callback_query.message.text
            if current_caption != START_TEXT:
                await callback_query.message.edit_caption(
                    caption=START_TEXT,
                    reply_markup=start_keyboard,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                # If already on home, just acknowledge the callback query
                await callback_query.answer("Already on Home screen")
        
        elif callback_query.data == "about":
            # Similar approach for other buttons
            current_caption = callback_query.message.caption or callback_query.message.text
            if current_caption != ABOUT_TEXT:
                await callback_query.message.edit_caption(
                    caption=ABOUT_TEXT,
                    reply_markup=start_keyboard,
                    parse_mode=ParseMode.HTML
                )
            else:
                await callback_query.answer("Already on About screen")
        
        elif callback_query.data == "help":
            current_caption = callback_query.message.caption or callback_query.message.text
            if current_caption != HELP_TEXT:
                await callback_query.message.edit_caption(
                    caption=HELP_TEXT,
                    reply_markup=start_keyboard,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await callback_query.answer("Already on Help screen")
        
        elif callback_query.data == "support":
            current_caption = callback_query.message.caption or callback_query.message.text
            if current_caption != SUPPORT_TEXT:
                await callback_query.message.edit_caption(
                    caption=SUPPORT_TEXT,
                    reply_markup=start_keyboard,
                    parse_mode=ParseMode.HTML
                )
            else:
                await callback_query.answer("Already on Support screen")
        
        elif callback_query.data == "movie_anime_hub":
            current_caption = callback_query.message.caption or callback_query.message.text
            if current_caption != MOVIE_TEXT:
                await callback_query.message.edit_caption(
                    caption=MOVIE_TEXT,
                    reply_markup=start_keyboard,
                    parse_mode=ParseMode.HTML
                )
            else:
                await callback_query.answer("Already on Movie screen")
        elif callback_query.data == "close":
            await callback_query.message.delete()
        
        await callback_query.answer()
    
    except Exception as e:
        print(f"Callback query error: {str(e)}")
        try:
            await callback_query.answer("An error occurred. Please try again.")
        except:
            pass

@espada.on_message(filters.command(["captionM", "cm"]))
async def caption_command(client, message):
    try:
        await message.delete()
        
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text(
                "Please provide a movie name.\n"
                "Example: `/cm Kalki 2898 AD`"
            )
            return

        # Check if page number is provided
        page = 1
        if parts[-1].isdigit() and len(parts) > 2:
            page = int(parts[-1])
            movie_name = " ".join(parts[1:-1])
        else:
            movie_name = " ".join(parts[1:])
            
        status_message = await message.reply_text("Searching for movies... Please wait!")

        # Search for movies with pagination
        search_results = await tmdb.search_titles(movie_name, "movie", page=page)
        
        if not search_results:
            await status_message.edit_text("No movies found with that title. Please try a different search.")
            return

        # Get total_pages from search results
        # Create a new endpoint in tmdb.py that returns the full response including total_pages
        full_search_data = await tmdb.full_search_titles(movie_name, "movie", page=page)
        total_pages = full_search_data.get('total_pages', 1)
        
        # Create keyboard with results and pagination
        keyboard = create_content_list_keyboard(
            search_results[:10],  # Limit to top 10 results per page
            page,
            total_pages,
            'movie_search'
        )
        
        await status_message.edit_text(
            f"🎬 Found movies matching '{movie_name}' (Page {page}/{total_pages}):",
            reply_markup=keyboard
        )
        
        await logger.log_message(
            action="Movie Caption Command",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id
        )

    except Exception as e:
        await message.reply_text("An error occurred while processing your request. Please try again later.")
        print(f"Movie search error: {str(e)}")  
        
        
@espada.on_message(filters.command(["captionS", "cs"]))
async def series_command(client, message):
    try:
        await message.delete()
        
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text(
                "Please provide a series name.\n"
                "Example: `/cs Breaking Bad`"
            )
            return

        # Check if page number is provided
        page = 1
        if parts[-1].isdigit() and len(parts) > 2:
            page = int(parts[-1])
            series_name = " ".join(parts[1:-1])
        else:
            series_name = " ".join(parts[1:])
            
        status_message = await message.reply_text("Searching for series... Please wait!")

        # Search specifically for TV series with pagination
        full_search_data = await tmdb.full_search_titles(series_name, "tv", page=page)
        results = full_search_data.get('results', [])
        total_pages = full_search_data.get('total_pages', 1)
        
        if not results:
            await status_message.edit_text("No series found with that title. Please try a different search.")
            return

        # Ensure each result is marked as a TV series
        for result in results:
            result['media_type'] = 'tv'

        # Create keyboard with properly tagged results and pagination
        keyboard = create_content_list_keyboard(
            results[:10],  # Limit to top 10 results per page
            page,
            total_pages,
            'series_search'
        )
        
        await status_message.edit_text(
            f"📺 Found series matching '{series_name}' (Page {page}/{total_pages}):",
            reply_markup=keyboard
        )
        
        await logger.log_message(
            action="Series Caption Command",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id
        )

    except Exception as e:
        await message.reply_text("An error occurred while processing your request. Please try again later.")
        print(f"Series search error: {str(e)}")
        
@espada.on_message(filters.command(["dump"]))
async def set_dump_channel(client, message):
    try:
        
        await message.delete()
        
        if len(message.command) != 2:
            await message.reply_text(
                "Please provide the channel ID.\n"
                "Usage: `/dump -100xxxxxxxxxxxx`"
            )
            return
        
        channel_id = int(message.command[1])
        user_id = message.from_user.id
        
        try:
            # Try to send a test message to verify bot has access
            test_msg = await client.send_message(channel_id, "Testing channel access...")
            await test_msg.delete()
            
            DUMP_CHANNELS[user_id] = channel_id
            await message.reply_text("✅ Dump channel set successfully!")
            
        except Exception as e:
            await message.reply_text(
                "❌ Failed to set dump channel. Please make sure:\n"
                "1. The channel ID is correct\n"
                "2. The bot is added to the channel\n"
                "3. The bot has permission to post in the channel"
            )
            
    except Exception as e:
        await message.reply_text("An error occurred while setting dump channel.")
        print(f"Set dump channel error: {str(e)}") 
        
@espada.on_message(~filters.command(["start", "captionM", "cm","captionS", "cs"]) & ~filters.channel & ~filters.group)
async def default_response(client, message):
    try:
        
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

async def process_backdrops(client, user_id: int, title_data: dict, images_data: dict) -> None:
    """Process and send backdrop images to appropriate channels"""
    try:
        if not images_data or not images_data.get('backdrops'):
            return

        title = title_data.get('title') or title_data.get('name', 'N/A')
        year = (title_data.get('release_date') or title_data.get('first_air_date', 'N/A'))[:4]
        
        # Get first 3 backdrop images
        backdrops = images_data['backdrops'][:3]
        if not backdrops:
            return
            
        backdrop_media = []
        
        # First backdrop with English text
        if len(backdrops) > 0:
            backdrop_path = backdrops[0].get('file_path')
            if backdrop_path:
                backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop_path}"
                caption = f"🎬 {title} ({year}) #English"
                backdrop_media.append(InputMediaPhoto(media=backdrop_url, caption=caption))
        
        # Other backdrops without text
        for backdrop in backdrops[1:]:
            backdrop_path = backdrop.get('file_path')
            if backdrop_path:
                backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop_path}"
                caption = f"🎬 {title} ({year})"
                backdrop_media.append(InputMediaPhoto(media=backdrop_url, caption=caption))
        
        # Send to dump channel if configured
        dump_channel = DUMP_CHANNELS.get(user_id)
        if dump_channel and backdrop_media:
            await client.send_media_group(dump_channel, backdrop_media)
            
    except Exception as e:
        print(f"Error processing backdrops: {str(e)}")

async def process_title_selection(callback_query: CallbackQuery, tmdb_id: str, media_type: str = "movie") -> None:
    """Process the selected title and generate the appropriate caption with related content"""
    try:
        # Create a separate loading message instead of editing the original
        loading_msg = await callback_query.message.reply_text("Fetching details... Please wait!")

        # Get detailed information
        title_data = await tmdb.get_title_details(tmdb_id, media_type)
        similar_data = await tmdb.get_similar_titles(tmdb_id, media_type)
        images_data = await tmdb.get_images(tmdb_id, media_type)

        if not title_data:
            await loading_msg.edit_text("Failed to fetch title details. Please try again.")
            return

        imdb_rating = title_data.get('imdb_rating', 'N/A')
        
        # Create data dictionary for additional message
        if media_type == "tv":
            series_data = {
                'movie_p': title_data.get('name', 'N/A'),
                'year_p': title_data.get('first_air_date', 'N/A')[:4] if title_data.get('first_air_date') else 'N/A',
            }
            additional_message = f"""`[PirecyKings3] S{{season}} E{{episode}} {series_data['movie_p']} ({series_data['year_p']}) @pirecykings3`

`S01 English - Hindi [480p]`

`S01 English - Hindi [720p]`

`S01 English - Hindi [1080p]`"""
            
            caption = format_series_caption(
                movie=title_data.get('name', 'N/A'),
                year=title_data.get('first_air_date', 'N/A')[:4] if title_data.get('first_air_date') else 'N/A',
                audio='Multi',
                language=title_data.get('original_language', 'N/A'),
                genre=', '.join([genre['name'] for genre in title_data.get('genres', [])]),
                imdb_rating=imdb_rating,
                runTime=str(title_data.get('episode_run_time', [0])[0] if title_data.get('episode_run_time') else 'N/A') + ' min',
                totalSeason=str(title_data.get('number_of_seasons', 'N/A')),
                type='TV Series',
                synopsis=title_data.get('overview', 'N/A')
            )
        else:
            movie_data = {
                'movie_p': title_data.get('title', 'N/A'),
                'year_p': title_data.get('release_date', 'N/A')[:4] if title_data.get('release_date') else 'N/A',
                'audio_p': determine_audio(title_data)
            }
            additional_message = f"""`[PirecyKings3] {movie_data['movie_p']} ({movie_data['year_p']}) @pirecykings3`

`{movie_data['movie_p']} ({movie_data['year_p']}) 480p - 1080p [{movie_data['audio_p']}]`"""
            
            caption = format_caption(
                movie=title_data.get('title', 'N/A'),
                year=title_data.get('release_date', 'N/A')[:4] if title_data.get('release_date') else 'N/A',
                audio='Multi',
                language=title_data.get('original_language', 'N/A'),
                genre=', '.join([genre['name'] for genre in title_data.get('genres', [])]),
                imdb_rating=imdb_rating,
                runTime=str(title_data.get('runtime', 'N/A')) + ' min',
                rated=title_data.get('adult', False) and 'A' or 'U/A',
                synopsis=title_data.get('overview', 'N/A')
            )

        # Delete loading message
        await loading_msg.delete()

        if media_type == "tv":
            # Use backdrop for 16:9 ratio for TV series
            image_path = title_data.get('backdrop_path')
            image_size = 'w1280'  # 16:9 aspect ratio
        else:
            image_path = title_data.get('poster_path')
            image_size = 'w500'  # Default poster size
        
        if image_path:
            image_url = f"https://image.tmdb.org/t/p/{image_size}{image_path}"
            await callback_query.message.reply_photo(
                photo=image_url,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN
            )

        await process_backdrops(
            client=callback_query.message._client,
            user_id=callback_query.from_user.id,
            title_data=title_data,
            images_data=images_data
        )

        await callback_query.message.reply_text(additional_message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        error_msg = f"Title selection error: {str(e)}"
        print(error_msg)
        try:
            # Try to delete the loading message if it exists
            await loading_msg.delete()
        except:
            pass
        await callback_query.message.reply_text(
            "An error occurred while processing your selection. Please try again."
        )

# Update the command handlers to use the new functionality
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
        results = await tmdb.search_titles(movie_name, "movie")
        
        if not results:
            await status_message.edit_text("No movies found with that title. Please try a different search.")
            return

        # Create and send results keyboard
        keyboard = create_content_list_keyboard(results[:10], 1, 1, "movie")  # Limit to top 10 results
        await status_message.edit_text(
            "🎬 Found the following movies. Please select one:",
            reply_markup=keyboard
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
        results = await tmdb.search_titles(series_name, "tv")
        
        if not results:
            await status_message.edit_text("No series found with that title. Please try a different search.")
            return

        # Create and send results keyboard
        keyboard = create_content_list_keyboard(results[:10], 1, 1, "tv")  # Limit to top 10 results
        await status_message.edit_text(
            "📺 Found the following series. Please select one:",
            reply_markup=keyboard
        )

    except Exception as e:
        await message.reply_text("An error occurred while processing your request. Please try again later.")
        print(f"Series search error: {str(e)}")

async def start_bot():
    try:
        await espada.start()
        await logger.log_bot_start()
        print("Bot Started Successfully!")

        while True:
            if not espada.is_connected:
                await espada.reconnect()
            await asyncio.sleep(10)

    except Exception as e:
        print(f"Bot Crashed: {str(e)}")
        await logger.log_bot_crash(e)
    finally:
        if espada.is_connected:  
            await espada.stop()
            
if __name__ == "__main__":
    print("Bot is Starting...")
    espada.run(start_bot())
