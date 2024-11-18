from dotenv import load_dotenv
load_dotenv()
import aiohttp
import os

omdb_api_key = os.getenv("OMDB_API_KEY")

async def fetch_movie_data(movie_name):
    """Fetch movie data from OMDB API"""
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={omdb_api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if data.get('Response') == 'True':
                return {
                    'movie_p': data.get('Title', movie_name),
                    'year_p': data.get('Year', 'N/A'),
                    'genre_p': data.get('Genre', 'N/A'),
                    'imdbRating_p': data.get('imdbRating', 'N/A'),
                    'runTime_p': data.get('Runtime', 'N/A'),
                    'rated_p': data.get('Rated', 'U/A'),
                    'synopsis_p': data.get('Plot', 'N/A'),
                    'totalSeasons_p': data.get('totalSeasons', 'N/A'),
                    'type_p': data.get('Type', 'N/A'),
                    'audio_p': data.get('Language', 'N/A'),
                    'poster': data.get('Poster', None)
                }
            return None