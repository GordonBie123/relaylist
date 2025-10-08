"""
Upload Page - SMS CSV File Upload and Initial Analysis
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load custom CSS
def load_css():
    css_file = "styles/custom.css"
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

from utils.file_parser import SMSParser
from models.chat_analyzer import ChatAnalyzer
from utils.database import save_chat_session

st.set_page_config(page_title="Upload Chat", page_icon="↑", layout="wide")

st.title("Upload Your SMS Chat History")

st.markdown("""
<div style='background-color: #181818; padding: 24px; border-radius: 8px; border: 1px solid #282828; margin-bottom: 24px;'>
<p style='color: #FFFFFF; font-size: 1rem; line-height: 1.6; margin-bottom: 12px;'>Upload your SMS conversation export in CSV format. Your file should contain these columns:</p>
<ul style='color: #B3B3B3; line-height: 1.8;'>
    <li><strong style='color: #FFFFFF;'>Type</strong> - Message direction (Sent or Received)</li>
    <li><strong style='color: #FFFFFF;'>Date</strong> - Message timestamp</li>
    <li><strong style='color: #FFFFFF;'>Name / Number</strong> - Contact information</li>
    <li><strong style='color: #FFFFFF;'>Sender</strong> - Sender name (empty for sent messages)</li>
    <li><strong style='color: #FFFFFF;'>Content</strong> - Message text content</li>
</ul>
</div>
""", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader(
    "Choose your SMS CSV file",
    type=['csv'],
    help="Upload the exported SMS conversation CSV file"
)

if uploaded_file is not None:
    # Display file info
    st.success(f"File uploaded: {uploaded_file.name} ({uploaded_file.size:,} bytes)")
    
    # Preview option
    with st.expander("Preview File Content"):
        try:
            preview_df = pd.read_csv(uploaded_file)
            st.dataframe(preview_df.head(10), use_container_width=True)
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Messages", len(preview_df))
            with col2:
                sent_count = len(preview_df[preview_df['Type'] == 'Sent'])
                st.metric("Sent Messages", sent_count)
            with col3:
                received_count = len(preview_df[preview_df['Type'] == 'Received'])
                st.metric("Received Messages", received_count)
            
            # Reset file pointer for analysis
            uploaded_file.seek(0)
        except Exception as e:
            st.error(f"Error previewing file: {e}")
    
    st.divider()
    
    # Analysis options
    st.markdown("### Analysis Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        include_sent = st.checkbox("Include sent messages", value=True)
    with col2:
        include_received = st.checkbox("Include received messages", value=True)
    
    # Analyze button
    if st.button("Analyze Conversation", type="primary", use_container_width=True):
        if not include_sent and not include_received:
            st.error("Please select at least one message type to analyze!")
        else:
            with st.spinner("Analyzing your conversation... This may take a minute."):
                try:
                    # Save file temporarily
                    temp_path = f"data/temp_{uploaded_file.name}"
                    os.makedirs("data", exist_ok=True)
                    
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Parse SMS file
                    parser = SMSParser()
                    parsed_data = parser.parse_file(temp_path)
                    
                    messages = parsed_data['messages']
                    
                    # Filter messages based on user selection
                    if not include_sent:
                        messages = [m for m in messages if m['type'] != 'sent']
                    if not include_received:
                        messages = [m for m in messages if m['type'] != 'received']
                    
                    if len(messages) == 0:
                        st.error("No messages to analyze after filtering!")
                        st.stop()
                    
                    # Initialize analyzer
                    analyzer = ChatAnalyzer()
                    
                    # Perform analysis
                    analysis_results = analyzer.analyze(messages)
                    
                    # Save to database
                    session_id = save_chat_session(
                        filename=uploaded_file.name,
                        contact_name=parsed_data['contact_name'],
                        contact_phone=parsed_data['contact_phone'],
                        stats=parsed_data['statistics'],
                        analysis=analysis_results
                    )
                    
                    # Update session state
                    st.session_state.current_session_id = session_id
                    st.session_state.analysis_complete = True
                    st.session_state.messages = messages
                    st.session_state.parsed_data = parsed_data
                    st.session_state.analysis_results = analysis_results
                    
                    # Clean up temp file
                    os.remove(temp_path)
                    
                    # Success message
                    st.success("Analysis complete!")
                    st.balloons()
                    
                    # Show quick stats
                    st.markdown("### Quick Statistics")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Messages Analyzed", len(messages))
                    with col2:
                        st.metric("Dominant Emotion", analysis_results['emotions']['dominant'].title())
                    with col3:
                        sentiment_label = analysis_results['sentiment']['sentiment_label']
                        st.metric("Overall Sentiment", sentiment_label)
                    with col4:
                        st.metric("Conversation Days", parsed_data['statistics']['duration_days'])
                    
                    st.info("Navigate to the Analysis page to see detailed results.")
                    
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    import traceback
                    with st.expander("Show error details"):
                        st.code(traceback.format_exc())

else:
    st.info("Please upload your SMS CSV file to begin analysis.")
    
    # Show example format
    with st.expander("View Example CSV Format"):
        example_data = {
            'Type': ['Received', 'Sent', 'Received'],
            'Date': ['9/1/2024 10:54', '9/1/2024 11:05', '9/1/2024 11:30'],
            'Name / Number': ['John Doe (+15551234567)', 'John Doe (+15551234567)', 'John Doe (+15551234567)'],
            'Sender': ['John Doe', '', 'John Doe'],
            'Content': ['Hey, how are you?', 'I\'m doing great!', 'That\'s awesome!']
        }
        example_df = pd.DataFrame(example_data)
        st.dataframe(example_df, use_container_width=True)