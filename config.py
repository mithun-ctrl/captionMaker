import os
from dotenv import load_dotenv
load_dotenv()
from pyrogram import Client
from typing import Dict

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
log_channel = int(os.getenv('LOG_CHANNEL'))
tmdb_api_token = os.getenv("API_TOKEN_TMDB")
omdb_api = os.getenv("OMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
espada = Client("movie_caption_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

#dump channel
#not working currently
DUMP_CHANNELS: Dict[int, int] = {}

#tmdb header

TMDB_HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {tmdb_api_token}"
}
