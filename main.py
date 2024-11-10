from dotenv import load_dotenv
load_dotenv()
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
import os
import asyncio

# Get environment variables
api_id = os.environ.get("API_ID")
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")

if not all([api_id, api_hash, bot_token]):
    raise ValueError("Please set the API_ID, API_HASH and BOT_TOKEN environment variables")

# Initialize your bot
app = Client("movie_caption_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Store user data during conversation
user_data = {}

# States for conversation
MOVIE = 1
AUDIO = 2
GENRE = 3
SYNOPSIS = 4

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

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "Welcome! To create a caption for an image:\n"
        "1. Send me an image\n"
        "2. Reply to that image with /caption\n"
        "3. Follow the prompts to add movie details"
    )

@app.on_message(filters.command("caption"))
async def caption_command(client, message):
    # Check if the command is a reply to an image
    if message.reply_to_message and message.reply_to_message.photo:
        user_id = message.from_user.id
        # Store the photo information for later use
        user_data[user_id] = {
            "state": MOVIE,
            "photo_id": message.reply_to_message.photo.file_id
        }
        await message.reply_text("Please enter the movie name:")
    else:
        await message.reply_text("Please reply to an image with /caption to create a caption for it.")

@app.on_message(filters.private & filters.text & ~filters.command())
async def handle_responses(client, message):
    user_id = message.from_user.id
    
    if user_id not in user_data:
        await message.reply_text("Please send an image and reply to it with /caption to start creating a caption.")
        return
    
    state = user_data[user_id]["state"]
    
    if state == MOVIE:
        user_data[user_id]["movie_p"] = message.text
        user_data[user_id]["state"] = AUDIO
        await message.reply_text("Enter the audio language(s):")
    
    elif state == AUDIO:
        user_data[user_id]["audio_p"] = message.text
        user_data[user_id]["state"] = GENRE
        await message.reply_text("Enter the genre(s):")
    
    elif state == GENRE:
        user_data[user_id]["genre_p"] = message.text
        user_data[user_id]["state"] = SYNOPSIS
        await message.reply_text("Enter the synopsis:")
    
    elif state == SYNOPSIS:
        synopsis = message.text.strip()
        # Remove any existing quotes and format for blockquote
        synopsis = synopsis.replace('"', '').replace('"', '').replace('"', '')
        
        caption = format_caption(
            user_data[user_id]['movie_p'],
            user_data[user_id]['audio_p'],
            user_data[user_id]['genre_p'],
            synopsis
        )
        
        # Send the image with the new caption
        await client.send_photo(
            chat_id=message.chat.id,
            photo=user_data[user_id]['photo_id'],
            caption=caption,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Clean up user data
        del user_data[user_id]

@app.on_message(filters.photo)
async def handle_photo(client, message):
    # Simply acknowledge receipt of the photo
    await message.reply_text("Image received! Reply to this image with /caption to add movie details.")

print("Bot is Starting...")
app.run()