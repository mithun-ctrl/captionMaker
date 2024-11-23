# Movie & TV Series Info Bot 🎬

A Telegram bot that provides detailed information about movies and TV series using TMDB and OMDB APIs. The bot offers features like searching, trending content updates, and formatted media information with custom captions.

## Features 🌟

- **Search Movies & TV Shows**: Search for any movie or TV series with detailed information
- **Trending Content**: Get updates on trending movies and TV shows
- **Popular Content**: Discover popular movies and TV series
- **Upcoming Releases**: Stay informed about upcoming movie releases
- **Rich Media Support**: View movie/series posters and backdrops
- **Detailed Information**: Get comprehensive details including:
  - IMDb ratings
  - Runtime
  - Genre
  - Audio languages
  - Synopsis
  - Release year
  - Content rating

## Commands 📝

- `/start` - Start the bot and see the main menu
- `/cm` or `/captionM` - Search for a movie (e.g., `/cm Kalki 2898 AD`)
- `/cs` or `/captionS` - Search for a TV series (e.g., `/cs Breaking Bad`)
- `/tr` or `/trending` - View trending content
- `/pp` or `/popular` - View popular movies
- `/up` or `/upcoming` - View upcoming movies

## Prerequisites 🛠️

- Python 3.7+
- Pyrogram library
- aiohttp library
- TMDB API key
- OMDB API key
- Telegram Bot Token

## Environment Variables 🔐

The following environment variables need to be set:

```
api_id=YOUR_TELEGRAM_API_ID
api_hash=YOUR_TELEGRAM_API_HASH
bot_token=YOUR_BOT_TOKEN
log_channel=YOUR_LOG_CHANNEL_ID
api_token=YOUR_TMDB_API_TOKEN
omdb_api=YOUR_OMDB_API_KEY
```

## Installation 📥

1. Clone the repository:
```bash
git clone https://github.com/mithun-ctrl/captionMaker.git
cd movie-tv-bot
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables

4. Run the bot:
```bash
python main.py
```

## Features in Detail 📋

### Movie Information
- Title and release year
- Audio language information
- Quality options (480p, 720p, 1080p)
- Genre classification
- IMDb rating
- Runtime
- Content rating
- Plot synopsis

### TV Series Information
- Series title and year
- Season information
- Episode count
- IMDb ratings
- Available quality options
- Audio language options
- Runtime per episode
- Genre details

### Additional Features
- Automatic audio language detection
- Custom formatting for movie/series captions
- Image carousel for posters and backdrops
- Pagination support for search results
- Interactive buttons for navigation

## Error Handling 🔧

The bot includes comprehensive error handling:
- Connection error recovery
- API failure handling
- Invalid command responses
- Search result validation
- Media processing error handling

## Logging 📊

The bot maintains detailed logs including:
- Bot start/stop events
- User interactions
- Command usage
- Error occurrences
- API responses

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer ⚠️

This bot is for educational purposes only. Please ensure you comply with TMDB and OMDB API terms of service and Telegram's bot policies when using this code.

## Support 💬

For support, please open an issue in the GitHub repository or contact through the support channels mentioned in the bot's help section.

---
Made with ❤️ for movie and TV show enthusiasts