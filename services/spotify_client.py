"""
Spotify Client - Handles authentication and API interactions
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SpotifyClient:
    """Wrapper for Spotify API using spotipy"""
    
    def __init__(self, use_oauth=True):
        """
        Initialize Spotify client
        
        Args:
            use_oauth: If True, use OAuth (requires user login)
                      If False, use client credentials (no user data)
        """
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8501/callback')
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Spotify credentials not found! "
                "Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env file"
            )
        
        self.use_oauth = use_oauth
        self.sp = None
        
        if use_oauth:
            self._init_oauth()
        else:
            self._init_client_credentials()
    
    def _init_oauth(self):
        """Initialize with OAuth (full user access)"""
        scope = " ".join([
            "user-read-private",
            "user-read-email",
            "user-read-playback-state",
            "user-modify-playback-state",
            "user-read-currently-playing",
            "user-top-read",
            "user-read-recently-played",
            "user-library-read",
            "user-library-modify",
            "playlist-read-private",
            "playlist-read-collaborative",
            "playlist-modify-public",
            "playlist-modify-private",
            "user-follow-read",
            "user-follow-modify"
        ])
        
        auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=scope,
            cache_path=".spotify_cache"
        )
        
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
    
    def _init_client_credentials(self):
        """Initialize with client credentials (no user data access)"""
        auth_manager = SpotifyClientCredentials(
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
    
    def get_auth_url(self):
        """Get OAuth authorization URL"""
        if not self.use_oauth:
            raise ValueError("OAuth not enabled for this client")
        
        return self.sp.auth_manager.get_authorize_url()
    
    def search_track(self, query, limit=10):
        """
        Search for tracks
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            list: Track results
        """
        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            return results['tracks']['items']
        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []
    
    def search_artist(self, query, limit=5):
        """Search for artists"""
        try:
            results = self.sp.search(q=query, type='artist', limit=limit)
            return results['artists']['items']
        except Exception as e:
            print(f"Error searching artists: {e}")
            return []
    
    def get_recommendations(self, seed_tracks=None, seed_artists=None, 
                          seed_genres=None, limit=20, **kwargs):
        """
        Get track recommendations
        
        Args:
            seed_tracks: List of track IDs
            seed_artists: List of artist IDs
            seed_genres: List of genre strings
            limit: Number of recommendations
            **kwargs: Additional parameters (target_valence, target_energy, etc.)
            
        Returns:
            dict: Recommendations response
        """
        try:
            return self.sp.recommendations(
                seed_tracks=seed_tracks,
                seed_artists=seed_artists,
                seed_genres=seed_genres,
                limit=limit,
                **kwargs
            )
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return {'tracks': []}
    
    def get_audio_features(self, track_ids):
        """
        Get audio features for tracks
        
        Args:
            track_ids: List of track IDs
            
        Returns:
            list: Audio features for each track
        """
        try:
            return self.sp.audio_features(track_ids)
        except Exception as e:
            print(f"Error getting audio features: {e}")
            return [None] * len(track_ids)
    
    def create_playlist(self, name, track_ids, description="", public=True):
        """
        Create a playlist with tracks
        
        Args:
            name: Playlist name
            track_ids: List of track IDs to add
            description: Playlist description
            public: Whether playlist is public
            
        Returns:
            str: Playlist URL
        """
        try:
            # Get current user
            user = self.sp.current_user()
            user_id = user['id']
            
            # Create playlist
            playlist = self.sp.user_playlist_create(
                user=user_id,
                name=name,
                public=public,
                description=description
            )
            
            # Add tracks (max 100 at a time)
            if track_ids:
                for i in range(0, len(track_ids), 100):
                    batch = track_ids[i:i+100]
                    self.sp.playlist_add_items(playlist['id'], batch)
            
            return playlist['external_urls']['spotify']
            
        except Exception as e:
            print(f"Error creating playlist: {e}")
            raise
    
    def get_user_top_tracks(self, limit=20, time_range='medium_term'):
        """
        Get user's top tracks
        
        Args:
            limit: Number of tracks
            time_range: 'short_term' (4 weeks), 'medium_term' (6 months), 
                       'long_term' (all time)
        
        Returns:
            dict: Top tracks response
        """
        try:
            return self.sp.current_user_top_tracks(
                limit=limit,
                time_range=time_range
            )
        except Exception as e:
            print(f"Error getting top tracks: {e}")
            return {'items': []}
    
    def get_user_top_artists(self, limit=20, time_range='medium_term'):
        """Get user's top artists"""
        try:
            return self.sp.current_user_top_artists(
                limit=limit,
                time_range=time_range
            )
        except Exception as e:
            print(f"Error getting top artists: {e}")
            return {'items': []}
    
    def get_available_genre_seeds(self):
        """Get list of available genre seeds"""
        try:
            return self.sp.recommendation_genre_seeds()['genres']
        except Exception as e:
            print(f"Error getting genres: {e}")
            return []


# Simple test function
def test_spotify_connection():
    """Test Spotify API connection"""
    try:
        client = SpotifyClient(use_oauth=False)
        
        # Test search
        results = client.search_track("Hello", limit=1)
        
        if results:
            print("✅ Spotify connection successful!")
            print(f"Test search found: {results[0]['name']} by {results[0]['artists'][0]['name']}")
            return True
        else:
            print("⚠️ Connection works but no results found")
            return False
            
    except Exception as e:
        print(f"❌ Spotify connection failed: {e}")
        return False


if __name__ == "__main__":
    # Run test when executed directly
    test_spotify_connection()