import os
from pyrogram import Client, filters
from dotenv import load_dotenv

load_dotenv()

# Get the bot token and owner ID from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
SUDO_ADMIN_IDS = [int(id) for id in os.getenv("SUDO_ADMIN_IDS", "").split(",")]

# Initialize the Pyrogram client
espada = Client("bot", api_id=os.getenv("API_ID"), api_hash=os.getenv("API_HASH"), bot_token=BOT_TOKEN)

@espada.on_message(filters.command("restart") & (filters.user(OWNER_ID) | filters.user(SUDO_ADMIN_IDS)))
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
    except Exception as e:
        await message.reply(f"Error restarting the bot: {str(e)}")

if __name__ == "__main__":
    espada.run()