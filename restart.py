import os
from pyrogram import Client, filters
from dotenv import load_dotenv
from plugins.logs import Logger

load_dotenv()

# Get the bot token and owner ID from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
SUDO_ADMIN_IDS = [int(id) for id in os.getenv("SUDO_ADMIN_IDS", "").split(",")]

# Initialize the Pyrogram client
app = Client("bot", api_id=os.getenv("API_ID"), api_hash=os.getenv("API_HASH"), bot_token=BOT_TOKEN)
logger = Logger(app)

@app.on_message(filters.command("restart") & (filters.user(OWNER_ID) | filters.user(SUDO_ADMIN_IDS)))
async def restart_bot(client, message):
    """
    Command handler to restart the bot.
    This command can only be executed by the bot owner or sudo admins.
    """
    try:
        await message.reply("Restarting the bot... Please wait!")
        await client.stop()
        await client.start()
        await message.reply("Bot restarted successfully!")
        
        await logger.log_message(
            action="Restart Command",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id
        )
    except Exception as e:
        await message.reply(f"Error restarting the bot: {str(e)}")
        print(f"Restart command error: {str(e)}")
        await logger.log_message(
            action="Restart Command Error",
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id,
            error=e
        )
        
        
if __name__ == "__main__":
    app.run()