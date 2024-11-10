from dotenv import load_dotenv
load_dotenv()
from pyrogram import Client, filters
from pyrogram.types import Message
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

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Welcome! Use /caption to start creating a movie caption.")

@app.on_message(filters.command("caption"))
async def caption_command(client, message):
    user_id = message.from_user.id
    user_data[user_id] = {"state": MOVIE}
    await message.reply_text("Please enter the movie name:")

@app.on_message(filters.private & filters.text & ~filters.command("start") & ~filters.command("caption"))
async def handle_responses(client, message):
    user_id = message.from_user.id
    
    if user_id not in user_data:
        await message.reply_text("Please use /caption to start creating a caption.")
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
        # Remove any existing quotes from the synopsis
        synopsis = synopsis.replace('"', '').replace('"', '').replace('"', '')
        user_data[user_id]["synopsis_p"] = synopsis
        
        # Format the caption with proper synopsis quotes
        caption = f"""{user_data[user_id]['movie_p']}
» 𝗔𝘂𝗱𝗶𝗼: {user_data[user_id]['audio_p']}
» 𝗤𝘂𝗮𝗹𝗶𝘁𝘆: 480p | 720p | 1080p 
» 𝗚𝗲𝗻𝗿𝗲: {user_data[user_id]['genre_p']}
» 𝗦𝘆𝗻𝗼𝗽𝘀𝗶𝘀
"{synopsis}"
@Teamxpirates
[𝗜𝗳 𝗬𝗼𝘂 𝗦𝗵𝗮𝗿𝗲 𝗢𝘂𝗿 𝗙𝗶𝗹𝗲𝘀 𝗪𝗶𝘁𝗵𝗼𝘂𝘁 𝗖𝗿𝗲𝗱𝗶𝘁, 𝗧𝗵𝗲𝗻 𝗬𝗼𝘂 𝗪𝗶𝗹𝗹 𝗯𝗲 𝗕𝗮𝗻𝗻𝗲𝗱]"""
        
        await message.reply_text("Here's your formatted caption:\n\n" + caption)
        # Clean up user data
        del user_data[user_id]

@app.on_message(filters.photo)
async def handle_photo(client, message):
    user_id = message.from_user.id
    if message.caption:
        # If photo has caption, process it
        await message.reply_photo(
            photo=message.photo.file_id,
            caption=message.caption
        )
    else:
        await message.reply_text("Please send the photo with a caption or use /caption first.")

print("Bot is Starting...")
app.run()