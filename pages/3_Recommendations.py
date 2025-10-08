"""
Music Recommendations Page - Spotify Dark Theme
"""
import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load custom CSS
def load_css():
    css_file = "styles/custom.css"
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

from utils.music_preferences import MusicPreferenceCapture, render_preference_summary
from models.music_recommender import MusicRecommender
from services.spotify_client import SpotifyClient
from utils.database import save_recommendations

st.set_page_config(page_title="Music Recommendations", page_icon="♪", layout="wide")

st.title("Your Personalized Music Recommendations")

# Check if analysis is complete
if not st.session_state.get('analysis_complete', False):
    st.warning("Please upload and analyze a chat file first!")
    st.info("Use the sidebar to navigate to the Upload page")
    st.stop()

# Initialize preference capture
pref_capture = MusicPreferenceCapture()

# Create tabs for the recommendation process
tab1, tab2, tab3 = st.tabs(["Set Preferences", "Get Recommendations", "Your Playlist"])

# TAB 1: Set Preferences
with tab1:
    st.header("Tell Us What You Like")
    
    st.markdown("""
    To give you the best recommendations, we need to know your music taste!
    Your chat analysis tells us the mood - you tell us the genre.
    """)
    
    # Show chat emotion summary
    with st.expander("Your Chat's Emotional Profile"):
        if 'analysis_results' in st.session_state:
            analysis = st.session_state.analysis_results
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Dominant Emotion", analysis['emotions']['dominant'].title())
            with col2:
                st.metric("Sentiment", analysis['sentiment']['sentiment_label'])
            with col3:
                st.metric("Polarity", f"{analysis['sentiment']['average_polarity']:.2f}")
            
            st.info(f"We'll recommend music that matches this {analysis['emotions']['dominant']} mood in your preferred genres!")
    
    st.divider()
    
    # Render preference UI
    user_preferences = pref_capture.render_preference_ui()
    
    # Store in session state
    st.session_state.user_music_preferences = user_preferences
    
    # Show summary
    if user_preferences.get('genres') or user_preferences.get('artists') or user_preferences.get('authenticated'):
        st.divider()
        render_preference_summary(user_preferences)
        
        st.success("Preferences saved! Go to the 'Get Recommendations' tab.")

# TAB 2: Generate Recommendations
with tab2:
    st.header("Generate Your Playlist")
    
    # Check if preferences are set
    if 'user_music_preferences' not in st.session_state:
        st.warning("Please set your music preferences in the first tab!")
        st.stop()
    
    user_prefs = st.session_state.user_music_preferences
    
    # Validate preferences based on method
    prefs_valid = False
    
    if user_prefs['method'] == 'genre_selection':
        prefs_valid = len(user_prefs.get('genres', [])) > 0
        if not prefs_valid:
            st.warning("Please select at least one genre in the preferences tab")
    elif user_prefs['method'] == 'spotify_profile':
        prefs_valid = user_prefs.get('authenticated', False)
        if not prefs_valid:
            st.warning("Please authenticate with Spotify in the preferences tab")
    elif user_prefs['method'] == 'seed_input':
        prefs_valid = len(user_prefs.get('artists', [])) > 0 or len(user_prefs.get('tracks', [])) > 0
        if not prefs_valid:
            st.warning("Please provide at least one artist or song in the preferences tab")
    
    if not prefs_valid:
        st.stop()
    
    # Show what we'll use
    st.subheader("Recommendation Strategy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**From Your Chat:**")
        if 'analysis_results' in st.session_state:
            analysis = st.session_state.analysis_results
            st.write(f"- Emotion: {analysis['emotions']['dominant'].title()}")
            st.write(f"- Sentiment: {analysis['sentiment']['sentiment_label']}")
            st.write(f"- Vibe: {analysis['sentiment']['trend']}")
    
    with col2:
        st.markdown("**From Your Preferences:**")
        if user_prefs['method'] == 'genre_selection':
            st.write(f"- Genres: {', '.join(user_prefs['genres'])}")
        elif user_prefs['method'] == 'spotify_profile':
            st.write("- Using your Spotify profile")
        else:
            st.write(f"- Artists/Songs: {len(user_prefs.get('artists', []) + user_prefs.get('tracks', []))}")
    
    st.divider()
    
    # Number of recommendations
    num_tracks = st.slider(
        "How many songs do you want?",
        min_value=10,
        max_value=50,
        value=20,
        step=5
    )
    
    # Generate button
    if st.button("Generate Recommendations", type="primary", use_container_width=True):
        
        with st.spinner("Finding perfect tracks for you..."):
            try:
                # Initialize Spotify client
                spotify = SpotifyClient(use_oauth=True)
                
                # Initialize recommender
                recommender = MusicRecommender(spotify.sp)
                
                # Get analysis results
                analysis = st.session_state.analysis_results
                
                # Generate recommendations
                recommendations = recommender.generate_recommendations(
                    chat_analysis=analysis,
                    user_preferences=user_prefs,
                    limit=num_tracks
                )
                
                if recommendations:
                    # Save to database
                    save_recommendations(
                        st.session_state.current_session_id,
                        recommendations
                    )
                    
                    st.session_state.recommendations = recommendations
                    st.session_state.recommendations_ready = True
                    
                    st.success(f"Generated {len(recommendations)} recommendations!")
                    st.balloons()
                else:
                    st.error("No recommendations found. Try different preferences!")
                
            except Exception as e:
                st.error(f"Error generating recommendations: {e}")
                import traceback
                with st.expander("Error details"):
                    st.code(traceback.format_exc())

# TAB 3: Display Playlist - SPOTIFY STYLE
with tab3:
    st.header("Your Personalized Playlist")
    
    if 'recommendations' not in st.session_state or not st.session_state.recommendations:
        st.info("Generate recommendations first in the previous tab!")
        st.stop()
    
    recommendations = st.session_state.recommendations
    
    # Playlist summary
    st.subheader("Playlist Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tracks", len(recommendations))
    with col2:
        avg_score = sum(r.get('relevance_score', 0.5) for r in recommendations) / len(recommendations)
        st.metric("Avg Match Score", f"{avg_score:.0%}")
    with col3:
        avg_popularity = sum(r['popularity'] for r in recommendations) / len(recommendations)
        st.metric("Avg Popularity", f"{avg_popularity:.0f}")
    with col4:
        total_duration = sum(r['duration_ms'] for r in recommendations) / 1000 / 60
        st.metric("Total Duration", f"{total_duration:.0f} min")
    
    st.divider()
    
    # Display each track - SPOTIFY CARD STYLE
    st.subheader("Your Tracks")
    
    for idx, track in enumerate(recommendations, 1):
        # Spotify-style track card
        st.markdown(f"""
        <div class='spotify-card' style='margin-bottom: 16px;'>
            <div style='display: flex; align-items: center; gap: 16px;'>
                <span class='track-number' style='color: #B3B3B3; font-size: 1rem; font-weight: 400; min-width: 24px;'>{idx}</span>
                <div style='width: 48px; height: 48px; background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%); border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);'></div>
                <div style='flex: 1;'>
                    <div style='color: #FFFFFF; font-size: 1rem; font-weight: 600; margin-bottom: 4px;'>{track['name']}</div>
                    <div style='color: #B3B3B3; font-size: 0.875rem;'>{track['artist']}</div>
                </div>
                <div style='text-align: right; min-width: 100px;'>
                    <div style='color: #1DB954; font-weight: 700; font-size: 1.125rem;'>{track.get('relevance_score', 0.5):.0%}</div>
                    <div style='color: #B3B3B3; font-size: 0.75rem;'>Match</div>
                </div>
            </div>
            <div style='margin-top: 12px; padding-top: 12px; border-top: 1px solid #282828;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div style='color: #B3B3B3; font-size: 0.813rem;'>◉ {track.get('reason', 'Matches your preferences')}</div>
                    <div style='color: #535353; font-size: 0.75rem;'>{track['album']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Spotify button
        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            if track['spotify_url']:
                st.link_button("▶ Play on Spotify", track['spotify_url'])
        
        # Show audio features if available
        if 'audio_features' in track and track['audio_features']:
            with st.expander("Audio Features"):
                features = track['audio_features']
                
                feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4)
                with feat_col1:
                    st.metric("Energy", f"{features.get('energy', 0):.2f}")
                with feat_col2:
                    st.metric("Valence", f"{features.get('valence', 0):.2f}")
                with feat_col3:
                    st.metric("Danceability", f"{features.get('danceability', 0):.2f}")
                with feat_col4:
                    st.metric("Tempo", f"{features.get('tempo', 0):.0f} BPM")
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.divider()
    
    # Export note with Spotify styling
    st.markdown("""
    <div class='spotify-card'>
        <h3 style='color: #FFFFFF; margin-bottom: 12px;'>📝 Save Your Playlist</h3>
        <p style='color: #B3B3B3; margin-bottom: 16px;'>
            Click the "Play on Spotify" buttons above to listen to each track directly in Spotify!
        </p>
        <p style='color: #B3B3B3; font-size: 0.875rem;'>
            Note: Direct playlist creation requires additional OAuth permissions. 
            For now, you can save tracks individually by clicking each link.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick stats summary
    st.subheader("Playlist Breakdown")
    
    # Genre distribution (if available)
    if recommendations:
        genres_count = {}
        for track in recommendations:
            genre = track.get('genre_source', 'Unknown')
            genres_count[genre] = genres_count.get(genre, 0) + 1
        
        st.markdown("**Genres in Your Playlist:**")
        genre_cols = st.columns(min(len(genres_count), 4))
        for idx, (genre, count) in enumerate(genres_count.items()):
            with genre_cols[idx % len(genre_cols)]:
                st.metric(genre.title(), count)

st.markdown("<br><br>", unsafe_allow_html=True)