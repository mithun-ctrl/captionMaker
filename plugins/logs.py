# plugins/logs.py
from pyrogram import Client
from datetime import datetime
import pytz
import os
from typing import Optional

class Logger:
    def __init__(self, client: Client):
        self.client = client
        self.log_channel = os.environ.get("LOG_CHANNEL")
        if not self.log_channel:
            raise ValueError("LOG_CHANNEL environment variable is not set")
        
        # Convert log channel to integer
        try:
            self.log_channel = int(self.log_channel)
        except ValueError:
            raise ValueError("LOG_CHANNEL must be a valid integer channel ID")
    
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
        try:
            await self.client.send_message(
                chat_id=self.log_channel,
                text=log_message,
                disable_notification=False  # Enable notification for bot start
            )
        except Exception as e:
            print(f"Failed to send bot start log: {str(e)}")

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
        try:
            await self.client.send_message(
                chat_id=self.log_channel,
                text=log_message,
                disable_notification=False  # Enable notification for crashes
            )
        except Exception as e:
            print(f"Failed to send bot crash log: {str(e)}")
        
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
        # Get current time in IST
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")
        
        # Build log message
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
        
        try:
            await self.client.send_message(
                chat_id=self.log_channel,
                text=log_message,
                disable_notification=True
            )
        except Exception as e:
            print(f"Failed to send log message: {str(e)}")