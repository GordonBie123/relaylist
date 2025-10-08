"""
Music Preference Capture - Multiple methods for understanding user taste
"""
import streamlit as st

class MusicPreferenceCapture:
    """Handles capturing and storing user music preferences"""
    
    # Comprehensive genre list from Spotify
    GENRES = [
        # Popular/Mainstream
        "pop", "rock", "hip-hop", "r&b", "country", "electronic", "dance",
        
        # Electronic subgenres
        "edm", "house", "techno", "dubstep", "drum-and-bass", "trance",
        
        # Rock subgenres
        "indie-rock", "alternative", "punk", "metal", "hard-rock", "classic-rock",
        
        # Hip-Hop subgenres
        "rap", "trap", "lo-fi", "boom-bap",
        
        # Jazz & Blues
        "jazz", "blues", "soul", "funk",
        
        # Latin
        "reggaeton", "latin", "salsa", "bachata",
        
        # Other
        "folk", "acoustic", "indie", "classical", "k-pop", "j-pop",
        "reggae", "ska", "gospel", "ambient", "chill", "study"
    ]
    
    MOOD_GENRES = {
        # Map moods to genre recommendations
        "happy": ["pop", "dance", "funk", "disco", "reggae"],
        "sad": ["indie", "acoustic", "blues", "r&b", "soul"],
        "energetic": ["edm", "rock", "hip-hop", "metal", "drum-and-bass"],
        "chill": ["lo-fi", "ambient", "jazz", "acoustic", "indie"],
        "romantic": ["r&b", "soul", "indie", "pop", "acoustic"],
        "angry": ["metal", "punk", "hard-rock", "rap", "dubstep"],
        "focused": ["classical", "ambient", "lo-fi", "study", "jazz"]
    }
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state for preferences"""
        if 'user_genres' not in st.session_state:
            st.session_state.user_genres = []
        if 'seed_artists' not in st.session_state:
            st.session_state.seed_artists = []
        if 'seed_tracks' not in st.session_state:
            st.session_state.seed_tracks = []
        if 'preference_method' not in st.session_state:
            st.session_state.preference_method = "genre_selection"
    
    def render_preference_ui(self):
        """
        Render the complete preference capture UI
        Returns: dict with user preferences
        """
        st.subheader("Music Preferences")
        
        # Method selection
        method = st.radio(
            "How would you like to set your music preferences?",
            [
                "Select Genres I Like",
                "Connect My Spotify Account",
                "Provide Favorite Artists/Songs"
            ],
            index=0
        )
        
        preferences = {}
        
        if "Select Genres" in method:
            preferences = self._genre_selection_ui()
            
        elif "Connect My Spotify" in method:
            preferences = self._spotify_profile_ui()
            
        elif "Provide Favorite" in method:
            preferences = self._seed_input_ui()
        
        return preferences
    
    def _genre_selection_ui(self):
        """Method 1: Direct genre selection"""
        st.markdown("""
        Select your preferred music genres. We'll use these to filter recommendations
        that match both your chat's mood and your musical taste.
        """)
        
        # Primary genres (select 1-5)
        st.write("**Primary Genres** (Select 1-5)")
        
        cols = st.columns(3)
        selected_genres = []
        
        sorted_genres = sorted(self.GENRES)
        
        for idx, genre in enumerate(sorted_genres):
            col_idx = idx % 3
            with cols[col_idx]:
                if st.checkbox(genre.title(), key=f"genre_{genre}"):
                    selected_genres.append(genre)
        
        # Validation
        if len(selected_genres) > 5:
            st.warning("Please select a maximum of 5 genres for best results")
            selected_genres = selected_genres[:5]
        
        st.session_state.user_genres = selected_genres
        
        # Additional preferences
        st.divider()
        st.write("**Additional Preferences** (Optional)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            explicit_content = st.checkbox(
                "Include explicit content",
                value=True,
                help="Allow songs with explicit lyrics"
            )
        
        with col2:
            popularity_range = st.slider(
                "Song popularity",
                0, 100, (20, 100),
                help="0 = obscure tracks, 100 = mainstream hits"
            )
        
        # Energy preference
        energy_pref = st.select_slider(
            "Energy preference",
            options=["Very Calm", "Calm", "Moderate", "Energetic", "Very Energetic"],
            value="Moderate",
            help="Adjusts the intensity of recommended tracks"
        )
        
        return {
            'method': 'genre_selection',
            'genres': selected_genres,
            'explicit_allowed': explicit_content,
            'popularity_range': popularity_range,
            'energy_preference': energy_pref
        }
    
    def _spotify_profile_ui(self):
        """Method 2: Use actual Spotify listening history"""
        st.markdown("""
        Connect your Spotify account to automatically use your actual listening habits.
        This provides the most accurate recommendations based on what you already enjoy!
        """)
        
        if not st.session_state.get('spotify_authenticated', False):
            st.info("You'll need to authenticate with Spotify first")
            
            if st.button("Connect to Spotify", type="primary"):
                st.info("Spotify authentication will be implemented in the Recommendations page")
                # This will trigger OAuth flow in the Recommendations page
        else:
            st.success("Spotify Connected!")
            
            # Show what will be analyzed
            st.markdown("""
            We'll analyze:
            - Your top artists (last 6 months)
            - Your top tracks (last 6 months)  
            - Your saved songs
            - Genres you listen to most
            """)
            
            time_range = st.select_slider(
                "Time range to analyze",
                options=["Last 4 weeks", "Last 6 months", "All time"],
                value="Last 6 months"
            )
        
        return {
            'method': 'spotify_profile',
            'authenticated': st.session_state.get('spotify_authenticated', False),
            'time_range': time_range if st.session_state.get('spotify_authenticated') else None
        }
    
    def _seed_input_ui(self):
        """Method 3: Manual artist/track seeds"""
        st.markdown("""
        Tell us your favorite artists or songs, and we'll find similar music
        that matches your chat's vibe.
        """)
        
        # Artist input
        st.write("**Favorite Artists** (Enter 1-3)")
        artist_inputs = []
        for i in range(3):
            artist = st.text_input(
                f"Artist {i+1}",
                key=f"artist_{i}",
                placeholder="e.g., Taylor Swift, Kendrick Lamar, The Weeknd"
            )
            if artist:
                artist_inputs.append(artist.strip())
        
        st.divider()
        
        # Track input
        st.write("**Favorite Songs** (Enter 1-3)")
        track_inputs = []
        for i in range(3):
            track = st.text_input(
                f"Song {i+1}",
                key=f"track_{i}",
                placeholder="e.g., Song Name - Artist Name"
            )
            if track:
                track_inputs.append(track.strip())
        
        st.session_state.seed_artists = artist_inputs
        st.session_state.seed_tracks = track_inputs
        
        if not artist_inputs and not track_inputs:
            st.warning("Please provide at least one artist or song")
        
        return {
            'method': 'seed_input',
            'artists': artist_inputs,
            'tracks': track_inputs
        }
    
    def get_genre_suggestions_from_emotion(self, dominant_emotion):
        """
        Suggest genres based on chat emotion analysis
        This bridges the gap between NLP results and music preferences
        """
        emotion_to_mood = {
            'joy': 'happy',
            'sadness': 'sad',
            'anger': 'angry',
            'fear': 'focused',
            'surprise': 'energetic',
            'neutral': 'chill'
        }
        
        mood = emotion_to_mood.get(dominant_emotion, 'chill')
        return self.MOOD_GENRES.get(mood, ['pop', 'indie'])
    
    def combine_preferences_with_analysis(self, user_prefs, chat_analysis):
        """
        Intelligently combine user genre preferences with chat emotional analysis
        
        Args:
            user_prefs: User's genre preferences
            chat_analysis: NLP analysis results from chat
            
        Returns:
            dict: Combined parameters for music recommendation
        """
        # Get emotion from chat
        dominant_emotion = chat_analysis.get('emotions', {}).get('dominant', 'neutral')
        sentiment = chat_analysis.get('sentiment', {}).get('average_polarity', 0)
        
        # Get suggested genres from emotion
        emotion_genres = self.get_genre_suggestions_from_emotion(dominant_emotion)
        
        # Combine with user preferences
        if user_prefs['method'] == 'genre_selection':
            user_genres = user_prefs['genres']
            
            # Find intersection between user preferences and emotion-matched genres
            combined_genres = list(set(user_genres + emotion_genres))
            
            # Prioritize user's selected genres
            final_genres = user_genres if user_genres else emotion_genres
            
        elif user_prefs['method'] == 'spotify_profile':
            # Will use Spotify's recommendation engine with user's profile
            final_genres = None  # Handled by Spotify API
            
        else:  # seed_input
            # Use emotion genres as backup
            final_genres = emotion_genres
        
        # Map sentiment to audio features
        # Sentiment ranges from -1 (negative) to 1 (positive)
        valence_target = (sentiment + 1) / 2  # Convert to 0-1 range
        
        # Adjust energy based on emotion
        energy_map = {
            'joy': 0.7,
            'sadness': 0.3,
            'anger': 0.85,
            'fear': 0.5,
            'surprise': 0.75,
            'neutral': 0.5
        }
        energy_target = energy_map.get(dominant_emotion, 0.5)
        
        return {
            'genres': final_genres,
            'target_valence': valence_target,  # Happiness of the track
            'target_energy': energy_target,     # Intensity of the track
            'dominant_emotion': dominant_emotion,
            'sentiment_score': sentiment,
            'user_method': user_prefs['method'],
            'user_preferences': user_prefs
        }


def render_preference_summary(preferences):
    """Display a summary of user preferences"""
    st.subheader("Preference Summary")
    
    if preferences['method'] == 'genre_selection':
        if preferences['genres']:
            st.write("**Selected Genres:**")
            st.write(", ".join([g.title() for g in preferences['genres']]))
        else:
            st.warning("No genres selected yet")
            
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Explicit Content", "Allowed" if preferences['explicit_allowed'] else "Filtered")
        with col2:
            pop_range = preferences['popularity_range']
            st.metric("Popularity Range", f"{pop_range[0]}-{pop_range[1]}")
            
    elif preferences['method'] == 'spotify_profile':
        if preferences['authenticated']:
            st.success("Will use your Spotify listening history")
        else:
            st.info("Spotify authentication pending")
            
    elif preferences['method'] == 'seed_input':
        if preferences['artists']:
            st.write("**Artists:**", ", ".join(preferences['artists']))
        if preferences['tracks']:
            st.write("**Songs:**", ", ".join(preferences['tracks']))