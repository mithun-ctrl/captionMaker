from dotenv import load_dotenv
import os
load_dotenv()

main_channel = os.getenv("MAIN_CHANNEL")
support_channel = os.getenv("SUPPORT_CHANNEL")

START_TEXT = """Welcome to Movie Caption Bot! 🎬

I can help you create beautiful captions for movies with automatic poster fetching."""

ABOUT_TEXT = f"""
    🤖 ᴄᴀᴘᴛɪᴏɴ ᴍᴀᴋᴇʀ
    📝 ℑ𝔫𝔣𝔬𝔯𝔪𝔞𝔱𝔦𝔬𝔫:
    ├ ɴᴀᴍᴇ:  ᴛɪᴇʀ ʜᴀʀʀɪʙᴇʟ‌
    ├ ʀᴀɴᴋ: ᴇsᴘᴀᴅᴀ ɴᴏ.𝟹
    ├ ʟᴀɴɢᴜᴀɢᴇ: [ᴘʏᴛʜᴏɴ](https://www.python.org)
    ├ ʟɪʙʀᴀʀʏ: [ᴘʏʀᴏɢʀᴀᴍ](https://pytba.readthedocs.io/en/latest/)
    └ ᴄʀᴇᴀᴛᴏʀ: [ᴍɪᴛʜᴜɴ](https://t.me/mithun_naam_toh_suna_hoga)"""

HELP_TEXT = """🔍 **Available Commands:**

• /start - Start the bot
• /caption [movie name] - Get movie poster with caption

**How to use:**
1. Just send /caption followed by movie name
2. Wait for the bot to fetch details
3. Get your poster with formatted caption!"""

SUPPORT_TEXT = f"""**Join Our Channels:**

• @{main_channel} - Main Channel
• @{support_channel} - Support Channel

Join us for updates and support!"""