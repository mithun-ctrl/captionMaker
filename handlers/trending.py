from pyrogram import filters
from plugins.utils.keyboard_utils import create_content_list_keyboard
from handlers.tmdb import tmdbFunctions
from plugins.logs import Logger

tmdb = tmdbFunctions()

async def trending_command_handler(client, message):
    try:
        await message.delete()
        
        parts = message.text.split()
        page = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
        
        status_message = await message.reply_text("Fetching trending content... Please wait!")
        
        trending_data = await tmdb.get_trending_content(page=page)
        
        if not trending_data or not trending_data.get('results'):
            await status_message.edit_text("No trending content found.")
            return
            
        keyboard = create_content_list_keyboard(
            trending_data['results'],
            page,
            trending_data['total_pages'],
            'trending'
        )
        
        await status_message.edit_text(
            f"📈 Trending Movies & TV Shows (Page {page}/{trending_data['total_pages']})",
            reply_markup=keyboard
        )
        
        await Logger.log_message(
            action="Trending Command",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id
        )
        
    except Exception as e:
        await message.reply_text("An error occurred while fetching trending content.")
        print(f"Trending command error: {str(e)}")
