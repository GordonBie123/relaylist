"""
Chat Analyzer - Performs NLP analysis on SMS conversations
"""
import nltk
from textblob import TextBlob
from collections import Counter
import numpy as np
from datetime import datetime

# Download required NLTK data (run once)
# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class ChatAnalyzer:
    """Analyzes chat conversations for emotions, sentiment, and topics"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        
        # Emotion keyword mappings
        self.emotion_keywords = {
            'joy': ['happy', 'excited', 'great', 'awesome', 'love', 'lol', 'haha', 
                    'wonderful', 'amazing', 'fantastic', 'glad', 'yay', '😂', '😊', '❤️'],
            'sadness': ['sad', 'sorry', 'miss', 'cry', 'depressed', 'down', 
                       'unhappy', 'disappointed', 'hurt', '😢', '😭'],
            'anger': ['angry', 'mad', 'hate', 'annoyed', 'frustrated', 'furious', 
                     'irritated', 'pissed', '😠', '😡'],
            'fear': ['worried', 'scared', 'afraid', 'anxious', 'nervous', 'fear', 
                    'concern', 'stress', 'panic'],
            'surprise': ['wow', 'omg', 'really', 'shocked', 'surprised', 'unbelievable', 
                        'amazing', '😱', '😲'],
            'neutral': ['okay', 'ok', 'fine', 'alright', 'sure', 'maybe']
        }
    
    def analyze(self, messages):
        """
        Perform comprehensive analysis on messages
        
        Args:
            messages: List of message dicts from SMSParser
            
        Returns:
            dict: Complete analysis results
        """
        # Extract text content
        all_text = ' '.join([m['content'] for m in messages])
        
        # Perform analyses
        emotions = self.extract_emotions(messages)
        sentiment = self.analyze_sentiment(messages)
        topics = self.identify_topics(messages)
        temporal_patterns = self.analyze_temporal_patterns(messages)
        
        # Generate summary
        summary = self.generate_summary({
            'emotions': emotions,
            'sentiment': sentiment,
            'topics': topics,
            'temporal': temporal_patterns,
            'message_count': len(messages)
        })
        
        return {
            'emotions': emotions,
            'sentiment': sentiment,
            'topics': topics,
            'temporal_patterns': temporal_patterns,
            'summary': summary
        }
    
    def extract_emotions(self, messages):
        """
        Extract emotional content from messages
        
        Returns:
            dict: Emotion scores and distribution
        """
        emotion_counts = Counter()
        message_emotions = []
        
        for message in messages:
            text = message['content'].lower()
            msg_emotions = []
            
            # Check for emotion keywords
            for emotion, keywords in self.emotion_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        emotion_counts[emotion] += 1
                        msg_emotions.append(emotion)
            
            # If no emotion found, mark as neutral
            if not msg_emotions:
                emotion_counts['neutral'] += 1
                msg_emotions.append('neutral')
            
            message_emotions.append(msg_emotions[0])  # Primary emotion
        
        # Calculate percentages
        total = sum(emotion_counts.values())
        emotion_percentages = {
            emotion: (count / total) * 100 
            for emotion, count in emotion_counts.items()
        }
        
        # Find dominant emotion
        dominant = max(emotion_counts.items(), key=lambda x: x[1])[0]
        
        return {
            'counts': dict(emotion_counts),
            'percentages': emotion_percentages,
            'dominant': dominant,
            'message_emotions': message_emotions,
            'total_analyzed': len(messages)
        }
    
    def analyze_sentiment(self, messages):
        """
        Analyze sentiment polarity and subjectivity over time
        
        Returns:
            dict: Sentiment scores and trends
        """
        sentiments = []
        
        for message in messages:
            blob = TextBlob(message['content'])
            sentiments.append({
                'timestamp': message['timestamp'],
                'polarity': blob.sentiment.polarity,  # -1 to 1
                'subjectivity': blob.sentiment.subjectivity,  # 0 to 1
                'sender': message['sender']
            })
        
        # Calculate averages
        polarities = [s['polarity'] for s in sentiments]
        subjectivities = [s['subjectivity'] for s in sentiments]
        
        avg_polarity = np.mean(polarities)
        avg_subjectivity = np.mean(subjectivities)
        
        # Determine sentiment label
        if avg_polarity > 0.1:
            sentiment_label = 'Positive'
        elif avg_polarity < -0.1:
            sentiment_label = 'Negative'
        else:
            sentiment_label = 'Neutral'
        
        # Calculate trend (simple linear regression slope)
        if len(sentiments) > 1:
            x = np.arange(len(polarities))
            trend = np.polyfit(x, polarities, 1)[0]
            trend_direction = 'Improving' if trend > 0.01 else 'Declining' if trend < -0.01 else 'Stable'
        else:
            trend_direction = 'Stable'
        
        return {
            'average_polarity': round(avg_polarity, 3),
            'average_subjectivity': round(avg_subjectivity, 3),
            'sentiment_label': sentiment_label,
            'trend': trend_direction,
            'timeline': sentiments,
            'count': len(messages)
        }
    
    def identify_topics(self, messages, top_n=10):
        """
        Identify key topics using word frequency analysis
        
        Returns:
            dict: Top topics and keywords
        """
        # Combine all message content
        all_text = ' '.join([m['content'].lower() for m in messages])
        
        # Tokenize and remove stopwords
        tokens = word_tokenize(all_text)
        
        # Filter tokens (remove stopwords, short words, and punctuation)
        filtered_tokens = [
            word for word in tokens 
            if word.isalpha() 
            and len(word) > 3 
            and word not in self.stop_words
        ]
        
        # Count word frequencies
        word_freq = Counter(filtered_tokens)
        top_words = word_freq.most_common(top_n)
        
        # Identify potential topics (bigrams)
        from nltk import bigrams
        bigram_list = list(bigrams(filtered_tokens))
        bigram_freq = Counter(bigram_list)
        top_bigrams = bigram_freq.most_common(5)
        
        # Format bigrams
        formatted_bigrams = [
            (' '.join(bigram), count) 
            for bigram, count in top_bigrams
        ]
        
        return {
            'top_words': top_words,
            'top_phrases': formatted_bigrams,
            'total_unique_words': len(word_freq),
            'total_words': len(filtered_tokens)
        }
    
    def analyze_temporal_patterns(self, messages):
        """
        Analyze messaging patterns over time
        
        Returns:
            dict: Temporal patterns and statistics
        """
        # Group by hour of day
        hour_counts = Counter()
        for message in messages:
            hour = message['timestamp'].hour
            hour_counts[hour] += 1
        
        # Find peak hours
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
        
        # Group by day of week
        day_counts = Counter()
        for message in messages:
            day = message['timestamp'].strftime('%A')
            day_counts[day] += 1
        
        most_active_day = max(day_counts.items(), key=lambda x: x[1])[0]
        
        return {
            'hourly_distribution': dict(hour_counts),
            'peak_hour': peak_hour,
            'daily_distribution': dict(day_counts),
            'most_active_day': most_active_day
        }
    
    def generate_summary(self, analysis_data):
        """
        Generate a human-readable summary of the analysis
        
        Returns:
            str: Formatted summary text
        """
        emotions = analysis_data['emotions']
        sentiment = analysis_data['sentiment']
        topics = analysis_data['topics']
        
        summary = f"""
**Conversation Overview:**
This conversation contains {analysis_data['message_count']} messages with a {sentiment['sentiment_label'].lower()} overall tone (sentiment score: {sentiment['average_polarity']}).

**Emotional Analysis:**
The conversation is predominantly {emotions['dominant']}, with {emotions['percentages'].get(emotions['dominant'], 0):.1f}% of messages expressing this emotion.

**Key Topics:**
The main topics discussed include: {', '.join([word for word, _ in topics['top_words'][:5]])}.

**Sentiment Trend:**
The emotional tone appears to be {sentiment['trend'].lower()} throughout the conversation.
"""
        return summary.strip()