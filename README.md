# Relaylist 🎵💬

Transform your SMS conversations into personalized Spotify playlists using Natural Language Processing and emotion analysis.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28%2B-FF4B4B)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Overview

Relaylist analyzes the emotional landscape of your text conversations and generates music recommendations that match the mood and energy of your chats. Using advanced NLP techniques and the Spotify API, it bridges the gap between conversational sentiment and musical expression.

### Key Features

- **Emotion Detection**: Identifies joy, sadness, anger, fear, surprise, and neutral emotions
- **Sentiment Analysis**: Tracks emotional polarity and trends over time
- **Topic Modeling**: Extracts key themes and conversation patterns
- **Temporal Analysis**: Discovers messaging patterns by hour and day
- **Spotify Integration**: Generates personalized playlists based on conversation mood
- **Multiple Preference Methods**: Genre selection, Spotify profile sync, or artist/track seeds

## 🎬 Demo
https://relaylist.streamlit.app

*Screenshots available in `/docs/screenshots/`*

## 🏗️ Architecture

```
User SMS Export → File Parser → NLP Analyzer → Emotion Mapper → Spotify API → Playlist
                                      ↓
                              Music Preferences ← User Input
```

### Tech Stack

- **Frontend**: Streamlit with custom Spotify-inspired UI
- **NLP**: NLTK, TextBlob for sentiment analysis
- **Music API**: Spotify Web API via Spotipy
- **Database**: SQLite for session storage
- **Visualization**: Plotly for interactive charts

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Spotify Developer Account
- SMS conversation export in CSV format

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/relaylist.git
cd relaylist
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up Spotify API credentials**

Create a `.env` file in the root directory:
```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8501/callback
```

See [API Setup Guide](docs/API_SETUP.md) for detailed instructions.

5. **Run the application**
```bash
streamlit run Home_Page.py
```

## 📊 CSV Format

Your SMS export should contain these columns:
(You can get the exports via a SMS Backup & Restore mobile app)
(Pseudo data provided for testing purposes)

| Column | Description | Example |
|--------|-------------|---------|
| Type | Message direction | "Sent" or "Received" |
| Date | Timestamp | "9/1/2024 10:54" |
| Name / Number | Contact info | "John Doe (+15551234567)" |
| Sender | Sender name | "John Doe" or empty for sent |
| Content | Message text | "Hey, how are you?" |

## 🎯 Usage

1. **Upload**: Export your SMS conversation and upload the CSV file
2. **Analyze**: View emotional insights, sentiment trends, and conversation patterns
3. **Preferences**: Set your music taste via genres, Spotify profile, or seed tracks
4. **Discover**: Get personalized playlist recommendations

## 🧪 Core Project Structure

```
relaylist/
├── models/           # Core NLP and recommendation algorithms
├── services/         # External API integrations (Spotify)
├── utils/            # Helper functions and utilities
├── pages/            # Streamlit page components
└── styles/           # Custom CSS styling
```

## 🔧 Configuration

### Audio Feature Mapping

Emotions are mapped to Spotify audio features:

- **Joy**: High valence (0.6-1.0), moderate-high energy
- **Sadness**: Low valence (0.0-0.4), low energy, acoustic
- **Anger**: Low valence, high energy (0.7-1.0), loud
- **Surprise**: Moderate-high valence and energy
- **Neutral**: Balanced features

### NLP Pipeline

1. Tokenization (NLTK)
2. Emotion keyword matching
3. Sentiment polarity analysis (TextBlob)
4. Topic extraction via frequency analysis
5. Temporal pattern recognition

## 📈 Future Enhancements

- [ ] Support for WhatsApp exports
- [ ] Real-time conversation analysis
- [ ] Collaborative playlist generation
- [ ] Export to Apple Music
- [ ] Advanced topic modeling with LDA
- [ ] Emotion tracking dashboard
- [ ] Multi-language support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Spotify Web API for music data
- NLTK and TextBlob for NLP capabilities
- Streamlit for the web framework
- The open-source community

## 📧 Contact

Gordon - gordonbie2@gmail.com

Project Link: [https://github.com/yourusername/relaylist](https://github.com/GordonBie123/relaylist)

## ⚠️ Privacy & Security

- All conversation data is processed locally
- No messages are stored on external servers
- Spotify authentication uses OAuth 2.0
- Session data stored in local SQLite database
- See [Privacy Policy](docs/PRIVACY.md) for details

---

**Built with 💚 using Python, NLP, and Spotify API**
