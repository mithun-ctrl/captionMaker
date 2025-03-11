from config import omdb_api, TMDB_BASE_URL, tmdb_api_token, TMDB_HEADERS
import aiohttp


class tmdbFunctions:
    async def get_imdb_rating(self, imdb_id):
        """ Fetch IMDb rating using OMDB API """
        try:
            if not imdb_id:
                return 'N/A'
                
            url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={omdb_api}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        rating = data.get('imdbRating')
                        return rating if rating and rating != 'N/A' else '0'
                    return '0'
        except Exception as e:
            print(f"Error fetching IMDb rating: {str(e)}")
            return '0'
        
    async def get_tmdb_data(self, endpoint, params=None):
        """Generic function to fetch data from TMDB API"""
        try:
            url = f"{TMDB_BASE_URL}/{endpoint}"
            params = params or {}
            params['api_key'] = tmdb_api_token
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=TMDB_HEADERS, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"TMDB API error: {response.status}")
                        return None
        except Exception as e:
            print(f"TMDB API error: {str(e)}")
            return None

    async def search_titles(self, query, media_type="movie", page=1):
        """Search for movies/TV shows using TMDB API"""
        params = {
            "query": query,
            "include_adult": "false",
            "language": "en-US",
            "page": page
        }
        
        if media_type == "movie":
            endpoint = "search/movie"
        else:
            endpoint = "search/tv"
            
        data = await self.get_tmdb_data(endpoint, params)
        return data.get('results', []) if data else []

    async def get_title_details(self, tmdb_id, media_type="movie"):
        """Get detailed information for a specific title"""
        try:
            endpoint = f"{media_type}/{tmdb_id}"
            params = {
                "language": "en-US",
                "append_to_response": "credits,videos,images,external_ids"
            }
            
            data = await self.get_tmdb_data(endpoint, params)
            
            if data:
                # Get IMDb ID from external_ids
                imdb_id = data.get('external_ids', {}).get('imdb_id')
                if imdb_id:
                    # Fetch and add IMDb rating
                    imdb_rating = await self.get_imdb_rating(imdb_id)
                    data['imdb_rating'] = imdb_rating
                else:
                    data['imdb_rating'] = '0'
                    
            return data
        except Exception as e:
            print(f"Error getting title details: {str(e)}")
            return None
    
    async def get_similar_titles(self, tmdb_id, media_type="movie"):
        """Get similar movies/TV shows"""
        endpoint = f"{media_type}/{tmdb_id}/similar"
        params = {"page": 1}
        return await self.get_tmdb_data(endpoint, params)

    async def get_images(self, tmdb_id, media_type="movie"):
        """Get additional images for a title"""
        endpoint = f"{media_type}/{tmdb_id}/images"
        return await self.get_tmdb_data(endpoint)

    async def get_trending_content(self, media_type="all", time_window="week", page=1):
        """Get trending movies/TV shows"""
        endpoint = f"trending/{media_type}/{time_window}"
        params = {"page": page}
        return await self.get_tmdb_data(endpoint, params)

    async def get_popular_content(self, media_type="movie", page=1):
        """Get popular movies/TV shows"""
        endpoint = f"{media_type}/popular"
        params = {"page": page}
        return await self.get_tmdb_data(endpoint, params)

    async def get_upcoming_content(self, page=1):
        """Get upcoming movies"""
        endpoint = "movie/upcoming"
        params = {"page": page}
        return await self.get_tmdb_data(endpoint, params)
    
    
    async def full_search_titles(self, query, media_type="movie", page=1):
        """Search for movies/TV shows and return full response including pagination info"""
        params = {
            "query": query,
            "include_adult": "false",
            "language": "en-US",
            "page": page
        }
    
        if media_type == "movie":
            endpoint = "search/movie"
        else:
            endpoint = "search/tv"
        
        data = await self.get_tmdb_data(endpoint, params)
        return data if data else {"results": [], "page": 1, "total_pages": 1}
