from dotenv import load_dotenv
load_dotenv()
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
import os
import asyncio
import aiohttp
from io import BytesIO

# Get environment variables
api_id = os.environ.get("API_ID")
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")
omdb_api_key = os.environ.get("OMDB_API_KEY")

if not all([api_id, api_hash, bot_token, omdb_api_key]):
    raise ValueError("Please set the API_ID, API_HASH, BOT_TOKEN, and OMDB_API_KEY environment variables")

# Initialize your bot
app = Client("movie_caption_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

async def fetch_movie_data(movie_name):
    """Fetch movie data from OMDB API"""
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={omdb_api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if data.get('Response') == 'True':
                return {
                    'movie_p': data.get('Title', movie_name),
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

def format_caption(movie, audio, genre, synopsis):
    # Format the caption with Markdown
    caption = f"""{movie}
» `𝗔𝘂𝗱𝗶𝗼:` {audio}
» `𝗤𝘂𝗮𝗹𝗶𝘁𝘆:` 480p | 720p | 1080p 
» `𝗚𝗲𝗻𝗿𝗲:` {genre}
» `𝗦𝘆𝗻𝗼𝗽𝘀𝗶𝘀`
> {synopsis}
@Teamxpirates
[𝗜𝗳 𝗬𝗼𝘂 𝗦𝗵𝗮𝗿𝗲 𝗢𝘂𝗿 𝗙𝗶𝗹𝗲𝘀 𝗪𝗶𝘁𝗵𝗼𝘂𝘁 𝗖𝗿𝗲𝗱𝗶𝘁, 𝗧𝗵𝗲𝗻 𝗬𝗼𝘂 𝗪𝗶𝗹𝗹 𝗯𝗲 𝗕𝗮𝗻𝗻𝗲𝗱]"""
    return caption

@app.on_message(filters.command(["start"]))
async def start_command(client, message):
    await message.reply_text(
        "Welcome! To get movie information and poster:\n"
        "Use /caption followed by the movie name\n"
        "Example: `/caption The Dark Knight`"
    )

@app.on_message(filters.command(["caption"]))
async def caption_command(client, message):
    try:
        # Extract movie name from command
        movie_name = " ".join(message.text.split()[1:])
        
        if not movie_name:
            await message.reply_text(
                "Please provide a movie name.\n"
                "Example: `/caption The Dark Knight`"
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
            await status_message.edit_text("Sorry, couldn't fetch the movie poster. Please try another movie.")
            return

        # Format caption
        caption = format_caption(
            movie_data['movie_p'],
            movie_data['audio_p'],
            movie_data['genre_p'],
            movie_data['synopsis_p']
        )

        # Send poster with caption
        await client.send_photo(
            chat_id=message.chat.id,
            photo=poster_data,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN
        )

        # Delete the status message
        await status_message.delete()

    except Exception as e:
        await message.reply_text(f"An error occurred while processing your request. Please try again later.")
        print(f"Error: {str(e)}")

print("Bot is Starting...")
app.run()