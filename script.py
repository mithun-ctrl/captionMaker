from dotenv import load_dotenv
import os
load_dotenv()

main_channel = os.getenv("MAIN_CHANNEL")
support_channel = os.getenv("SUPPORT_CHANNEL")

START_TEXT = """ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴍᴏᴠɪᴇ ᴄᴀᴘᴛɪᴏɴ ʙᴏᴛ! 🎬

ɪ ᴄᴀɴ ʜᴇʟᴘ ʏᴏᴜ ᴄʀᴇᴀᴛᴇ ʙᴇᴀᴜᴛɪғᴜʟ ᴄᴀᴘᴛɪᴏɴs ғᴏʀ ᴍᴏᴠɪᴇs ᴡɪᴛʜ ᴀᴜᴛᴏᴍᴀᴛɪᴄ ᴘᴏsᴛᴇʀ ғᴇᴛᴄʜɪɴɢ."""

ABOUT_TEXT = """
    🤖 ᴄᴀᴘᴛɪᴏɴ ᴍᴀᴋᴇʀ
    📝 ℑ𝔫𝔣𝔬𝔯𝔪𝔞𝔱𝔦𝔬𝔫:
    ├ ɴᴀᴍᴇ:  ᴛɪᴇʀ ʜᴀʀʀɪʙᴇʟ‌
    ├ ʀᴀɴᴋ: ᴇsᴘᴀᴅᴀ ɴᴏ.𝟹
    ├ ʟᴀɴɢᴜᴀɢᴇ: <a href=https://www.python.org>ᴘʏᴛʜᴏɴ</a>
    ├ ʟɪʙʀᴀʀʏ: <a href=https://pytba.readthedocs.io/en/latest>ᴘʏʀᴏɢʀᴀᴍ</a>
    └ ᴄʀᴇᴀᴛᴏʀ: <a href=https://t.me/mithun_naam_toh_suna_hoga>ᴍɪᴛʜᴜɴ</a>"""

HELP_TEXT = f"""🔍 **Available Commands:**

• /start - sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ
• /caption [movie name] - ɢᴇᴛ ᴍᴏᴠɪᴇ ᴘᴏsᴛᴇʀ ᴡɪᴛʜ ᴄᴀᴘᴛɪᴏɴ

**ʜᴏᴡ ᴛᴏ ᴜsᴇ:**
𝟷. ᴊᴜsᴛ sᴇɴᴅ `/caption` ғᴏʟʟᴏᴡᴇᴅ ʙʏ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ 
𝟸. ᴡᴀɪᴛ ғᴏʀ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ғᴇᴛᴄʜ ᴅᴇᴛᴀɪʟs 
𝟹. ɢᴇᴛ ʏᴏᴜʀ ᴘᴏsᴛᴇʀ ᴡɪᴛʜ ғᴏʀᴍᴀᴛᴛᴇᴅ ᴄᴀᴘᴛɪᴏɴ!"""

SUPPORT_TEXT = f"""**ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs:**

├ ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ:  <a href=https://t.me/{main_channel}>ᴇsᴘᴀᴅᴀ.ᴏʀɢ</a>
├ sᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ: <a href https://t.me/{support_channel}>ᴇsᴘᴀᴅᴀ.ᴏʀɢ sᴜᴘᴘᴏʀᴛ</a>

𝔍𝔬𝔦𝔫 𝔲𝔰 𝔣𝔬𝔯 𝔲𝔭𝔡𝔞𝔱𝔢𝔰 𝔞𝔫𝔡 𝔰𝔲𝔭𝔭𝔬𝔯𝔱!"""