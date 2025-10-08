"""
Home_Page.py - Relaylist
Transform your conversations into personalized music experiences
"""
import streamlit as st
from utils.database import init_database, get_all_sessions
import os

# Page configuration
st.set_page_config(
    page_title="Relaylist - Conversation to Music",
    page_icon="♫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_file = "styles/custom.css"
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Additional inline CSS fix for Material Icons - Pure CSS only
# st.markdown("""
# <style>
#     /* Hide Material Icons text */
#     [data-testid="collapsedControl"],
#     button[kind="header"] {
#         font-size: 0 !important;
#         color: transparent !important;
#         width: 40px !important;
#         height: 40px !important;
#     }
    
#     [data-testid="collapsedControl"]::before,
#     button[kind="header"]::before {
#         content: "☰" !important;
#         font-size: 1.5rem !important;
#         color: #FFFFFF !important;
#         font-family: 'Inter', sans-serif !important;
#         display: block !important;
#     }
    
#     .streamlit-expanderHeader svg,
#     .streamlit-expanderHeader i,
#     .streamlit-expanderHeader .material-icons {
#         display: none !important;
#     }
    
#     .streamlit-expanderHeader::after {
#         content: "▼" !important;
#         color: #1DB954 !important;
#         font-size: 1rem !important;
#         float: right !important;
#         font-family: 'Inter', sans-serif !important;
#     }
    
#     [aria-expanded="true"] .streamlit-expanderHeader::after {
#         content: "▲" !important;
#     }
    
#     span.material-icons,
#     i.material-icons {
#         font-size: 0 !important;
#         display: none !important;
#     }
# </style>
# """, unsafe_allow_html=True)

# Initialize database
init_database()

# Initialize session state variables
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'recommendations_ready' not in st.session_state:
    st.session_state.recommendations_ready = False
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None
if 'spotify_authenticated' not in st.session_state:
    st.session_state.spotify_authenticated = False

# Main header - Spotify gradient style
st.markdown("""
<div style='text-align: center; padding: 3rem 0 2rem 0;'>
    <h1 style='font-size: 4rem; margin-bottom: 0.5rem; background: linear-gradient(90deg, #1DB954 0%, #1ed760 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 700;'>Relaylist</h1>
    <p style='font-size: 1.25rem; color: #B3B3B3; font-weight: 500;'>Transform conversations into music</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Introduction section
st.markdown("""
<div style='background-color: #181818; padding: 32px; border-radius: 8px; border: 1px solid #282828; margin-bottom: 32px;'>
    <p style='color: #FFFFFF; font-size: 1.1rem; line-height: 1.6; margin: 0;'>
        Relaylist analyzes the emotional landscape of your SMS conversations and creates Spotify playlists that match the mood and energy of your chats. Using advanced natural language processing, we understand the feelings behind your words and translate them into music you'll love.
    </p>
</div>
""", unsafe_allow_html=True)

# How it works section
st.markdown("<h3 style='color: #FFFFFF; margin-top: 2rem; margin-bottom: 1.5rem;'>How It Works</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background-color: #181818; border: 1px solid #282828; border-radius: 8px; padding: 32px 24px; text-align: center; min-height: 320px; display: flex; flex-direction: column; justify-content: center;'>
        <div style='font-size: 3.5rem; color: #1DB954; margin-bottom: 20px; font-weight: 200;'>↑</div>
        <h4 style='color: #FFFFFF; margin-bottom: 16px; font-weight: 700; font-size: 1.25rem;'>Upload</h4>
        <p style='color: #B3B3B3; font-size: 0.938rem; line-height: 1.6;'>Export your SMS conversations as a CSV file and upload it to Relaylist. We support standard SMS export formats.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background-color: #181818; border: 1px solid #282828; border-radius: 8px; padding: 32px 24px; text-align: center; min-height: 320px; display: flex; flex-direction: column; justify-content: center;'>
        <div style='font-size: 3.5rem; color: #1DB954; margin-bottom: 20px; font-weight: 200;'>○</div>
        <h4 style='color: #FFFFFF; margin-bottom: 16px; font-weight: 700; font-size: 1.25rem;'>Analyze</h4>
        <p style='color: #B3B3B3; font-size: 0.938rem; line-height: 1.6;'>Our NLP engine analyzes emotions, sentiment patterns, key topics, and conversation dynamics.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background-color: #181818; border: 1px solid #282828; border-radius: 8px; padding: 32px 24px; text-align: center; min-height: 320px; display: flex; flex-direction: column; justify-content: center;'>
        <div style='font-size: 3.5rem; color: #1DB954; margin-bottom: 20px; font-weight: 200;'>♪</div>
        <h4 style='color: #FFFFFF; margin-bottom: 16px; font-weight: 700; font-size: 1.25rem;'>Discover</h4>
        <p style='color: #B3B3B3; font-size: 0.938rem; line-height: 1.6;'>Get personalized Spotify recommendations that match your conversation's emotional tone and your music preferences.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# What we analyze section
st.markdown("<h3 style='color: #FFFFFF; margin-top: 2rem; margin-bottom: 1.5rem;'>What We Analyze</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style='background-color: #181818; border: 1px solid #282828; border-radius: 8px; padding: 24px;'>
        <h4 style='color: #FFFFFF; margin-bottom: 20px; font-weight: 700; font-size: 1.125rem;'>Emotional Analysis</h4>
        <ul style='color: #B3B3B3; line-height: 2; margin: 0; padding-left: 20px;'>
            <li style='padding: 6px 0;'>Primary emotions: joy, sadness, anger, surprise, fear</li>
            <li style='padding: 6px 0;'>Emotional distribution throughout conversation</li>
            <li style='padding: 6px 0;'>Sentiment polarity and subjectivity</li>
            <li style='padding: 6px 0;'>Mood trends over time</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background-color: #181818; border: 1px solid #282828; border-radius: 8px; padding: 24px;'>
        <h4 style='color: #FFFFFF; margin-bottom: 20px; font-weight: 700; font-size: 1.125rem;'>Conversation Insights</h4>
        <ul style='color: #B3B3B3; line-height: 2; margin: 0; padding-left: 20px;'>
            <li style='padding: 6px 0;'>Key topics and themes discussed</li>
            <li style='padding: 6px 0;'>Temporal messaging patterns</li>
            <li style='padding: 6px 0;'>Vocabulary richness and communication style</li>
            <li style='padding: 6px 0;'>Response dynamics and engagement levels</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Current status
if st.session_state.analysis_complete:
    st.success("Analysis Complete - Your conversation has been analyzed and is ready for review.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("View Analysis Results", use_container_width=True):
            st.switch_page("pages/2_Analysis.py")
    with col2:
        if st.button("Get Music Recommendations", use_container_width=True):
            st.switch_page("pages/3_Recommendations.py")
    with col3:
        if st.button("Start New Analysis", use_container_width=True):
            st.session_state.analysis_complete = False
            st.session_state.recommendations_ready = False
            st.rerun()
else:
    st.info("Ready to begin? Navigate to the Upload Chat page using the sidebar to start your analysis.")

st.markdown("<br><br>", unsafe_allow_html=True)

# Show previous sessions
st.markdown("<h3 style='color: #FFFFFF; margin-top: 2rem; margin-bottom: 1.5rem;'>Recent Sessions</h3>", unsafe_allow_html=True)

sessions = get_all_sessions()
if sessions:
    for session in sessions[:5]:
        with st.expander(f"{session['contact_name']} | {session['filename']} | {session['message_count']} messages"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Uploaded:** {session['upload_date']}")
                st.write(f"**Contact:** {session['contact_name']}")
            with col2:
                if st.button("Load Session", key=f"load_{session['id']}"):
                    st.session_state.current_session_id = session['id']
                    st.session_state.analysis_complete = True
                    st.switch_page("pages/2_Analysis.py")
else:
    st.markdown("<p style='color: #B3B3B3;'>No previous sessions found. Upload your first conversation to create your first Relaylist.</p>", unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #B3B3B3; padding: 2rem 0; border-top: 1px solid #282828;'>
    <p style='margin-bottom: 0.5rem;'><strong style='color: #FFFFFF;'>Relaylist</strong> | Built with Streamlit, Natural Language Processing, and Spotify API</p>
    <p style='font-size: 0.85rem; color: #535353;'>Your data is processed locally and never shared with third parties</p>
</div>
""", unsafe_allow_html=True)

# Sidebar info
with st.sidebar:
    st.markdown("### Navigation")
    st.markdown("""
    - **Home** - Overview and instructions
    - **Upload Chat** - Import your conversation
    - **Analysis** - View emotional insights
    - **Recommendations** - Get music suggestions
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### Tips for Best Results")
    st.markdown("""
    - Longer conversations provide more accurate analysis
    - Include both sent and received messages
    - Try conversations with varied emotional tones
    - Ensure your CSV file has all required columns
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.analysis_complete:
        st.success("Analysis Ready")
    
    if st.session_state.spotify_authenticated:
        st.success("Spotify Connected")