from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏠 Home", callback_data="home"),
     InlineKeyboardButton("🤖 About", callback_data="about")],
    [InlineKeyboardButton("💬 Support", callback_data="support"),
     InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    [InlineKeyboardButton("🎬 MoAni Hub", callback_data="movie_anime_hub"),
     InlineKeyboardButton("🙅‍♂️ Close", callback_data="close")
     ]
])