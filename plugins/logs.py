# plugins/logs.py
from pyrogram import Client, utils
from datetime import datetime
import pytz
import os
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

log_channel_id = int(os.getenv('LOG_CHANNEL'))

class Logger:
    def __init__(self, client: Client):
        self.client = client
        self.log_channel = log_channel_id
        if not self.log_channel:
            raise ValueError("LOG_CHANNEL environment variable is not set")
        
        # Convert log channel to integer and ensure it has the correct format
        try:
            # Remove any existing prefixes and convert to integer
            clean_id = str(self.log_channel).replace("-100", "").replace("-", "")
            self.log_channel = int(f"-100{clean_id}")
            
            # Check if the clean ID is numeric
            if not clean_id.isdigit():
                raise ValueError("Channel ID must contain only numbers")
                
            # For Pyrogram, supergroup/channel IDs should be passed as negative integers
            # with -100 prefix
            self.log_channel = int(f"-100{clean_id}")
        except ValueError as e:
            raise ValueError(f"Invalid channel ID format: {str(e)}")

    async def send_log(self, message: str, notify: bool = False):
        """
        Helper method to send logs with error handling
        """
        try:
            await self.client.send_message(
                chat_id=self.log_channel,
                text=message,
                disable_notification=not notify
            )
        except Exception as e:
            print(f"Logging Error: {str(e)}")
            print(f"Attempted to send to channel: {self.log_channel}")
            print(f"Message content: {message}")
    
    async def log_bot_start(self):
        """
        Log bot startup with distinctive formatting
        """
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")
        
        log_message = f"""
╔══════════════════════╗
║     BOT STARTED      ║
╚══════════════════════╝

🤖 **Bot:** @TierHarribelBot
📡 **Status:** `Online`
⏰ **Start Time:** `{current_time}`
🟢 **State:** `Operational`

╭─────────────────────
├ **System:** `Active`
├ **Services:** `Running`
╰─────────────────────

**Bot is Ready to Use!**
"""
        await self.send_log(log_message, notify=True)

    async def log_bot_crash(self, error: Exception):
        """
        Log bot crash with distinctive formatting
        """
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")
        
        log_message = f"""
╔══════════════════════╗
║     BOT CRASHED      ║
╚══════════════════════╝

🤖 **Bot:** @TierHarribelBot
📡 **Status:** `Offline`
⏰ **Crash Time:** `{current_time}`
🔴 **State:** `Crashed`

╭─────────────────────
├ **System:** `Error`
├ **Services:** `Stopped`
├ **Error Details:**
│ `{str(error)}`
╰─────────────────────

**Immediate Attention Required!**
"""
        await self.send_log(log_message, notify=True)
        
    async def log_message(
        self,
        action: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        chat_id: Optional[int] = None,
        chat_title: Optional[str] = None,
        error: Optional[Exception] = None
    ):
        """
        Log a message to the specified logging channel
        """
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")
        
        log_parts = [
            f"🤖 **Bot:** @TierHarribelBot",
            f"📋 **New {action}**",
            f"⏰ **Time:** `{current_time}`"
        ]
        
        if user_id:
            log_parts.append(f"👤 **User ID:** `{user_id}`")
        if username:
            log_parts.append(f"📛 **Username:** @{username}")
        if chat_id:
            log_parts.append(f"💭 **Chat ID:** `{chat_id}`")
        if chat_title:
            log_parts.append(f"📢 **Chat Title:** {chat_title}")
        if error:
            log_parts.append(f"❌ **Error:** `{str(error)}`")
            
        log_message = "\n".join(log_parts)
        await self.send_log(log_message)