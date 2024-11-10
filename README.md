# Movie Caption Bot

A Telegram bot built with Pyrogram that automatically creates formatted movie captions using OMDB API integration. It fetches movie details like title, audio languages, genre, and synopsis automatically when you provide a movie name.

## Features

- Automatic movie information fetching via OMDB API
- Interactive caption creation process
- Formatted movie information
- Support for photos with captions
- Professional movie detail formatting
- Real-time movie data validation

## Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Telegram API credentials (api_id and api_hash from [my.telegram.org](https://my.telegram.org))
- OMDB API key (from [omdbapi.com](http://www.omdbapi.com/apikey.aspx))

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

4. Create a `.env` file with your credentials:
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
OMDB_API_KEY=your_omdb_api_key
LOG_CHANNEL=your_channel_id
MAIN_CHANNEL="espada_org"
SUPPORT_CHANNEL="espadaSupport"
```

## Deployment on Railway

### Step 1: Prepare Your Repository

1. Create a new repository on GitHub
2. Create these files in your repository:
   - `main.py` (the bot code)
   - `requirements.txt`
   - `Procfile`
   - `README.md`
   - `.env.example` (template for environment variables)

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
   - `OMDB_API_KEY` - Your OMDB API Key

Railway will automatically detect the Python runtime from your repository and deploy your bot.

## Usage

1. Start the bot by sending `/start`
2. Use the `/caption` command followed by the movie name
   Example: `/caption The Dark Knight`
3. The bot will automatically:
   - Fetch movie details from OMDB
   - Download the movie poster
   - Add the formatted caption
   - Send the poster with caption

Example output:
```
The Dark Knight
» 𝗔𝘂𝗱𝗶𝗼: English
» 𝗤𝘂𝗮𝗹𝗶𝘁𝘆: 480p | 720p | 1080p 
» 𝗚𝗲𝗻𝗿𝗲: Action, Crime, Drama
» 𝗦𝘆𝗻𝗼𝗽𝘀𝗶𝘀
> When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.
@Teamxpirates
[𝗜𝗳 𝗬𝗼𝘂 𝗦𝗵𝗮𝗿𝗲 𝗢𝘂𝗿 𝗙𝗶𝗹𝗲𝘀 𝗪𝗶𝘁𝗵𝗼𝘂𝘁 𝗖𝗿𝗲𝗱𝗶𝘁, 𝗧𝗵𝗲𝗻 𝗬𝗼𝘂 𝗪𝗶𝗹𝗹 𝗯𝗲 𝗕𝗮𝗻𝗻𝗲𝗱]
```

## Directory Structure
```
movie-caption-bot/
├── main.py
├── .env
├── .env.example
├── requirements.txt
├── Procfile
└── README.md
```
## Error Handling

The bot handles various scenarios:
- Movie not found in OMDB database
- Poster image not available
- Network connection issues
- Invalid movie names
- API timeout errors

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OMDB API](http://www.omdbapi.com/) for providing movie data
- [Pyrogram](https://docs.pyrogram.org/) for the Telegram bot framework
