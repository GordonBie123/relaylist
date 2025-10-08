"""
Analysis Results Page - Spotify Dark Theme
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
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

from utils.database import get_session

st.set_page_config(page_title="Analysis Results", page_icon="○", layout="wide")

st.title("Chat Analysis Results")

# Check if analysis is complete
if not st.session_state.get('analysis_complete', False):
    st.warning("Please upload and analyze a chat file first!")
    st.info("Use the sidebar to navigate to the Upload page")
    st.stop()

# Get analysis data
if 'analysis_results' in st.session_state:
    analysis = st.session_state.analysis_results
    parsed_data = st.session_state.get('parsed_data', {})
else:
    st.error("Analysis data not found in session. Please re-upload your chat.")
    st.stop()

# Summary section
st.header("Conversation Summary")

with st.container():
    st.markdown(analysis['summary'])

st.divider()

# Key Metrics
st.header("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    sentiment_label = analysis['sentiment']['sentiment_label']
    st.metric(
        "Overall Sentiment",
        sentiment_label,
        f"{analysis['sentiment']['average_polarity']:.2f}"
    )

with col2:
    dominant_emotion = analysis['emotions']['dominant'].title()
    st.metric(
        "Dominant Emotion",
        dominant_emotion,
        f"{analysis['emotions']['percentages'].get(analysis['emotions']['dominant'], 0):.1f}%"
    )

with col3:
    st.metric(
        "Sentiment Trend",
        analysis['sentiment']['trend']
    )

with col4:
    total_msgs = analysis['emotions']['total_analyzed']
    st.metric(
        "Messages Analyzed",
        total_msgs
    )

st.divider()

# Emotion Analysis
st.header("Emotional Breakdown")

col1, col2 = st.columns([2, 1])

with col1:
    # Emotion distribution pie chart - UPDATED FOR SPOTIFY THEME
    emotions_data = analysis['emotions']['percentages']
    
    fig_emotions = go.Figure(data=[go.Pie(
        labels=[e.title() for e in emotions_data.keys()],
        values=list(emotions_data.values()),
        hole=0.4,
        marker=dict(
            colors=['#1DB954', '#1ed760', '#2ebd59', '#3fce5e', '#50df63', '#61f068']
        ),
        textinfo='label+percent',
        textfont=dict(size=14, color='white')
    )])
    
    fig_emotions.update_layout(
        title="Emotion Distribution",
        height=400,
        showlegend=True,
        template="plotly_dark",
        paper_bgcolor='#181818',
        plot_bgcolor='#181818',
        font=dict(color='white')
    )
    
    st.plotly_chart(fig_emotions, use_container_width=True)

with col2:
    st.subheader("Emotion Breakdown")
    
    # Create a more detailed breakdown
    emotions_df = pd.DataFrame([
        {
            'Emotion': emotion.title(),
            'Percentage': f"{percentage:.1f}%",
            'Count': analysis['emotions']['counts'].get(emotion, 0)
        }
        for emotion, percentage in sorted(
            emotions_data.items(),
            key=lambda x: x[1],
            reverse=True
        )
    ])
    
    st.dataframe(
        emotions_df,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# Sentiment Timeline
st.header("Sentiment Over Time")

if 'messages' in st.session_state:
    messages = st.session_state.messages
    
    # Create sentiment timeline
    sentiment_timeline = []
    window_size = max(len(messages) // 50, 1)
    
    for i in range(0, len(messages), window_size):
        window = messages[i:i+window_size]
        if window:
            from textblob import TextBlob
            avg_sentiment = sum(
                TextBlob(msg['content']).sentiment.polarity
                for msg in window
            ) / len(window)
            
            sentiment_timeline.append({
                'timestamp': window[0]['timestamp'],
                'sentiment': avg_sentiment,
                'message_count': len(window)
            })
    
    # Create dataframe
    timeline_df = pd.DataFrame(sentiment_timeline)
    
    # Plot sentiment over time - UPDATED FOR SPOTIFY THEME
    fig_timeline = go.Figure()
    
    fig_timeline.add_trace(go.Scatter(
        x=timeline_df['timestamp'],
        y=timeline_df['sentiment'],
        mode='lines+markers',
        name='Sentiment',
        line=dict(color='#1DB954', width=3),
        marker=dict(size=6, color='#1ed760'),
        fill='tozeroy',
        fillcolor='rgba(29, 185, 84, 0.2)'
    ))
    
    # Add zero line
    fig_timeline.add_hline(
        y=0,
        line_dash="dash",
        line_color="#535353",
        annotation_text="Neutral",
        annotation_font_color="#B3B3B3"
    )
    
    fig_timeline.update_layout(
        title="Sentiment Trend Throughout Conversation",
        xaxis_title="Time",
        yaxis_title="Sentiment Score",
        yaxis_range=[-1, 1],
        height=400,
        hovermode='x unified',
        template="plotly_dark",
        paper_bgcolor='#181818',
        plot_bgcolor='#181818',
        font=dict(color='white')
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Sentiment statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        positive_msgs = sum(1 for s in timeline_df['sentiment'] if s > 0.1)
        st.metric("Positive Periods", f"{positive_msgs}/{len(timeline_df)}")
    
    with col2:
        negative_msgs = sum(1 for s in timeline_df['sentiment'] if s < -0.1)
        st.metric("Negative Periods", f"{negative_msgs}/{len(timeline_df)}")
    
    with col3:
        neutral_msgs = len(timeline_df) - positive_msgs - negative_msgs
        st.metric("Neutral Periods", f"{neutral_msgs}/{len(timeline_df)}")

st.divider()

# Topic Analysis
st.header("Key Topics Discussed")

topics = analysis['topics']

col1, col2 = st.columns([2, 1])

with col1:
    # Top words bar chart - UPDATED FOR SPOTIFY THEME
    top_words_df = pd.DataFrame(
        topics['top_words'],
        columns=['Word', 'Frequency']
    )
    
    fig_words = px.bar(
        top_words_df,
        x='Frequency',
        y='Word',
        orientation='h',
        title='Most Frequent Words',
        color='Frequency',
        color_continuous_scale=['#121212', '#1DB954', '#1ed760']
    )
    
    fig_words.update_layout(
        height=400,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'},
        template="plotly_dark",
        paper_bgcolor='#181818',
        plot_bgcolor='#181818',
        font=dict(color='white')
    )
    
    st.plotly_chart(fig_words, use_container_width=True)

with col2:
    st.subheader("Top Phrases")
    
    if topics['top_phrases']:
        phrases_df = pd.DataFrame(
            topics['top_phrases'],
            columns=['Phrase', 'Count']
        )
        st.dataframe(
            phrases_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No significant phrases detected")
    
    st.divider()
    
    # Vocabulary stats
    st.metric("Unique Words", topics['total_unique_words'])
    st.metric("Total Words", topics['total_words'])

st.divider()

# Temporal Patterns
st.header("Messaging Patterns")

temporal = analysis.get('temporal_patterns', {})

if temporal:
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly distribution - UPDATED FOR SPOTIFY THEME
        hourly = temporal.get('hourly_distribution', {})
        
        if hourly:
            hours = list(range(24))
            counts = [hourly.get(h, 0) for h in hours]
            
            fig_hourly = go.Figure()
            
            fig_hourly.add_trace(go.Bar(
                x=hours,
                y=counts,
                marker_color='#1DB954',
                marker_line_color='#1ed760',
                marker_line_width=1,
                name='Messages'
            ))
            
            fig_hourly.update_layout(
                title='Messages by Hour of Day',
                xaxis_title='Hour',
                yaxis_title='Message Count',
                height=350,
                xaxis=dict(tickmode='linear', tick0=0, dtick=2),
                template="plotly_dark",
                paper_bgcolor='#181818',
                plot_bgcolor='#181818',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig_hourly, use_container_width=True)
            
            st.info(f"Peak messaging hour: {temporal.get('peak_hour', 'N/A')}:00")
    
    with col2:
        # Daily distribution - UPDATED FOR SPOTIFY THEME
        daily = temporal.get('daily_distribution', {})
        
        if daily:
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                         'Friday', 'Saturday', 'Sunday']
            days = [d for d in days_order if d in daily]
            counts = [daily[d] for d in days]
            
            fig_daily = go.Figure()
            
            fig_daily.add_trace(go.Bar(
                x=days,
                y=counts,
                marker_color='#1DB954',
                marker_line_color='#1ed760',
                marker_line_width=1,
                name='Messages'
            ))
            
            fig_daily.update_layout(
                title='Messages by Day of Week',
                xaxis_title='Day',
                yaxis_title='Message Count',
                height=350,
                template="plotly_dark",
                paper_bgcolor='#181818',
                plot_bgcolor='#181818',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig_daily, use_container_width=True)
            
            st.info(f"Most active day: {temporal.get('most_active_day', 'N/A')}")

st.divider()

# Conversation Stats
st.header("Conversation Statistics")

if parsed_data and 'statistics' in parsed_data:
    stats = parsed_data['statistics']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Messages", stats['total_messages'])
    
    with col2:
        st.metric("Messages Sent", stats['sent_count'])
    
    with col3:
        st.metric("Messages Received", stats['received_count'])
    
    with col4:
        st.metric("Duration (days)", stats['duration_days'])
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Avg Message Length", f"{stats['avg_message_length']:.0f} chars")
    
    with col2:
        st.metric("Messages Per Day", f"{stats['messages_per_day']:.1f}")
    
    with col3:
        response_rate = (stats['sent_count'] / stats['received_count'] * 100) if stats['received_count'] > 0 else 0
        st.metric("Response Rate", f"{response_rate:.0f}%")

st.divider()

# Next steps
st.header("Ready for Recommendations?")

st.markdown("""
Your chat analysis is complete! Now you can:
- Get music recommendations that match this conversation's mood
- Set your genre preferences
- Create a personalized Spotify playlist
""")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("Get Recommendations", type="primary", use_container_width=True):
        st.switch_page("pages/3_Recommendations.py")

with col2:
    if st.button("Start New Analysis", use_container_width=True):
        st.session_state.analysis_complete = False
        st.session_state.recommendations_ready = False
        st.switch_page("pages/1_Upload_Chat.py")