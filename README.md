# Movie Caption Bot

A Telegram bot built with Pyrogram that helps create formatted movie captions with details like movie name, audio languages, genre, and synopsis.

## Features

- Interactive caption creation process
- Formatted movie information
- Support for photos with captions
- Automated synopsis quotation
- Professional movie detail formatting

## Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Telegram API credentials (api_id and api_hash from [my.telegram.org](https://my.telegram.org))

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/movie-caption-bot.git
cd movie-caption-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `config.py` file with your credentials:
```python
API_ID = "your_api_id"
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
```

## Deployment on Railway

### Step 1: Prepare Your Repository

1. Create a new repository on GitHub
2. Create these files in your repository:
   - `main.py` (the bot code)
   - `requirements.txt`
   - `Procfile`
   - `README.md`

The `requirements.txt` should contain:
```
pyrogram
tgcrypto
```

The `Procfile` should contain:
```
worker: python main.py
```

### Step 2: Deploy to Railway

1. Go to [Railway.app](https://railway.app/)
2. Login with your GitHub account
3. Click on "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Add the following environment variables in Railway:
   - `API_ID` - Your Telegram API ID
   - `API_HASH` - Your Telegram API Hash
   - `BOT_TOKEN` - Your Telegram Bot Token

Railway will automatically detect the Python runtime from your repository and deploy your bot.

## Usage

1. Start the bot by sending `/start`
2. Use `/caption` to begin creating a new movie caption
3. Follow the bot's prompts to enter:
   - Movie name
   - Audio language(s)
   - Genre(s)
   - Synopsis
4. The bot will generate a formatted caption with your input

Example output:
```
Movie Name
» 𝗔𝘂𝗱𝗶𝗼: English, Hindi
» 𝗤𝘂𝗮𝗹𝗶𝘁𝘆: 480p | 720p | 1080p 
» 𝗚𝗲𝗻𝗿𝗲: Action, Adventure
» 𝗦𝘆𝗻𝗼𝗽𝘀𝗶𝘀
"An exciting adventure that follows our hero through incredible challenges."
@Teamxpirates
[𝗜𝗳 𝗬𝗼𝘂 𝗦𝗵𝗮𝗿𝗲 𝗢𝘂𝗿 𝗙𝗶𝗹𝗲𝘀 𝗪𝗶𝘁𝗵𝗼𝘂𝘁 𝗖𝗿𝗲𝗱𝗶𝘁, 𝗧𝗵𝗲𝗻 𝗬𝗼𝘂 𝗪𝗶𝗹𝗹 𝗯𝗲 𝗕𝗮𝗻𝗻𝗲𝗱]
```

## Directory Structure
```
movie-caption-bot/
├── main.py
├── config.py
├── requirements.txt
├── Procfile
└── README.md
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.