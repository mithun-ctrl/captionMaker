from dotenv import load_dotenv
load_dotenv()
from dotenv import load_dotenv
load_dotenv()
from dotenv import load_dotenv
load_dotenv()
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
import os
import asyncio
import aiohttp
import json

# Get environment variables
api_id = os.environ.get("API_ID")
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")
omdb_api_key = os.environ.get("OMDB_API_KEY")  # Add OMDB API key

if not all([api_id, api_hash, bot_token, omdb_api_key]):
    raise ValueError("Please set the API_ID, API_HASH, BOT_TOKEN, and OMDB_API_KEY environment variables")

# Initialize your bot
app = Client("movie_caption_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Store user data during conversation
user_data = {}

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
                    'audio_p': data.get('Language', 'N/A')
                }
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
        "Welcome! To create a caption for an image:\n"
        "1. Send me an image\n"
        "2. Reply to that image with /caption\n"
        "3. Enter the movie name when prompted"
    )

@app.on_message(filters.command(["caption"]))
async def caption_command(client, message):
    # Check if the command is a reply to an image
    if message.reply_to_message and message.reply_to_message.photo:
        user_id = message.from_user.id
        # Store the photo information for later use
        user_data[user_id] = {
            "photo_id": message.reply_to_message.photo.file_id
        }
        await message.reply_text("Please enter the movie name:")
    else:
        await message.reply_text("Please reply to an image with /caption to create a caption for it.")

@app.on_message(filters.private & filters.text & ~filters.command(["start", "caption"]))
async def handle_responses(client, message):
    user_id = message.from_user.id
    
    if user_id not in user_data:
        await message.reply_text("Please send an image and reply to it with /caption to start creating a caption.")
        return

    # Show "Creating Caption..." message
    status_message = await message.reply_text("Creating Caption... Please wait!")
    
    # Fetch movie data from OMDB
    movie_data = await fetch_movie_data(message.text)
    
    if movie_data:
        caption = format_caption(
            movie_data['movie_p'],
            movie_data['audio_p'],
            movie_data['genre_p'],
            movie_data['synopsis_p']
        )
        
        # Send the image with the new caption
        await client.send_photo(
            chat_id=message.chat.id,
            photo=user_data[user_id]['photo_id'],
            caption=caption,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Delete the status message
        await status_message.delete()
        
        # Clean up user data
        del user_data[user_id]
    else:
        await status_message.edit_text("Sorry, I couldn't find information for that movie. Please check the movie name and try again.")

@app.on_message(filters.photo)
async def handle_photo(client, message):
    # Simply acknowledge receipt of the photo
    await message.reply_text("Image received! Reply to this image with /caption to add movie details.")

print("Bot is Starting...")
app.run()