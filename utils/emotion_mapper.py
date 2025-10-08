"""
Emotion Mapper - Maps chat emotions to Spotify audio features and genres
"""

class EmotionMapper:
    """Maps emotional analysis to music parameters"""
    
    # Emotion to Spotify audio feature ranges
    EMOTION_AUDIO_FEATURES = {
        'joy': {
            'valence': (0.6, 1.0),        # Happy/positive
            'energy': (0.5, 0.9),          # Moderate to high energy
            'danceability': (0.5, 1.0),    # Danceable
            'tempo': (100, 150),           # Upbeat tempo
            'acousticness': (0.0, 0.5),    # More electronic
            'mode': 1                       # Major key
        },
        'sadness': {
            'valence': (0.0, 0.4),         # Sad/negative
            'energy': (0.2, 0.5),          # Low energy
            'danceability': (0.0, 0.4),    # Not danceable
            'tempo': (60, 100),            # Slow tempo
            'acousticness': (0.3, 1.0),    # More acoustic
            'mode': 0                       # Minor key
        },
        'anger': {
            'valence': (0.0, 0.5),         # Negative
            'energy': (0.7, 1.0),          # High energy
            'danceability': (0.3, 0.7),    # Moderate
            'tempo': (120, 180),           # Fast tempo
            'loudness': (-5, 0),           # Loud
            'instrumentalness': (0.0, 0.5)
        },
        'fear': {
            'valence': (0.2, 0.5),         # Slightly negative
            'energy': (0.4, 0.7),          # Medium energy
            'danceability': (0.2, 0.5),    # Low dance
            'tempo': (80, 120),            # Moderate tempo
            'acousticness': (0.2, 0.7),
            'instrumentalness': (0.0, 0.6)
        },
        'surprise': {
            'valence': (0.5, 0.8),         # Positive to neutral
            'energy': (0.6, 0.9),          # High energy
            'danceability': (0.5, 0.8),    # Danceable
            'tempo': (110, 160),           # Upbeat
            'acousticness': (0.0, 0.5)
        },
        'neutral': {
            'valence': (0.4, 0.6),         # Balanced
            'energy': (0.4, 0.6),          # Medium energy
            'danceability': (0.4, 0.6),    # Medium dance
            'tempo': (90, 130),            # Moderate tempo
            'acousticness': (0.2, 0.6)
        }
    }
    
    # Emotion to genre recommendations
    EMOTION_GENRES = {
        'joy': [
            'pop', 'dance', 'funk', 'disco', 'reggae', 
            'edm', 'house', 'indie-pop', 'summer'
        ],
        'sadness': [
            'indie', 'acoustic', 'blues', 'r&b', 'soul',
            'singer-songwriter', 'folk', 'ambient', 'sad'
        ],
        'anger': [
            'metal', 'punk', 'hard-rock', 'rap', 'hardcore',
            'dubstep', 'drum-and-bass', 'grunge', 'rock'
        ],
        'fear': [
            'ambient', 'electronic', 'instrumental', 'classical',
            'downtempo', 'trip-hop', 'dark-ambient'
        ],
        'surprise': [
            'electronic', 'edm', 'indie', 'alternative',
            'experimental', 'progressive', 'indie-rock'
        ],
        'neutral': [
            'indie', 'alternative', 'rock', 'pop', 'jazz',
            'chill', 'lo-fi', 'study'
        ]
    }
    
    @staticmethod
    def emotion_to_audio_params(emotion, sentiment_score=0.0):
        """
        Convert emotion and sentiment to Spotify audio feature parameters
        
        Args:
            emotion: Primary emotion (joy, sadness, anger, etc.)
            sentiment_score: Sentiment polarity from -1 to 1
            
        Returns:
            dict: Target audio features for Spotify API
        """
        emotion = emotion.lower()
        
        # Get base features for emotion
        base_features = EmotionMapper.EMOTION_AUDIO_FEATURES.get(
            emotion,
            EmotionMapper.EMOTION_AUDIO_FEATURES['neutral']
        )
        
        # Adjust valence based on sentiment
        sentiment_valence = (sentiment_score + 1) / 2
        
        # Blend emotion valence with sentiment valence
        if 'valence' in base_features:
            emotion_valence = sum(base_features['valence']) / 2
            adjusted_valence = emotion_valence * 0.7 + sentiment_valence * 0.3
        else:
            adjusted_valence = sentiment_valence
        
        # Build parameter dict
        params = {}
        
        for feature, value in base_features.items():
            if isinstance(value, tuple):
                params[f'target_{feature}'] = sum(value) / 2
                params[f'min_{feature}'] = value[0]
                params[f'max_{feature}'] = value[1]
            else:
                params[f'target_{feature}'] = value
        
        # Override valence with adjusted value
        params['target_valence'] = adjusted_valence
        
        return params
    
    @staticmethod
    def emotion_to_genres(emotion, limit=5):
        """
        Get genre suggestions based on emotion
        
        Args:
            emotion: Primary emotion
            limit: Number of genres to return
            
        Returns:
            list: Recommended genres
        """
        emotion = emotion.lower()
        genres = EmotionMapper.EMOTION_GENRES.get(
            emotion,
            EmotionMapper.EMOTION_GENRES['neutral']
        )
        return genres[:limit]
    
    @staticmethod
    def get_mood_description(emotion, sentiment_score):
        """
        Generate human-readable mood description
        
        Args:
            emotion: Primary emotion
            sentiment_score: Sentiment polarity
            
        Returns:
            str: Mood description
        """
        emotion = emotion.lower()
        
        descriptions = {
            'joy': {
                'high': 'ecstatic and euphoric',
                'medium': 'happy and upbeat',
                'low': 'contentedly cheerful'
            },
            'sadness': {
                'high': 'deeply melancholic',
                'medium': 'bittersweet and reflective',
                'low': 'wistfully contemplative'
            },
            'anger': {
                'high': 'intensely aggressive',
                'medium': 'frustrated and energetic',
                'low': 'mildly irritated'
            },
            'fear': {
                'high': 'anxiously tense',
                'medium': 'nervously uncertain',
                'low': 'cautiously aware'
            },
            'surprise': {
                'high': 'excitedly astonished',
                'medium': 'pleasantly unexpected',
                'low': 'mildly curious'
            },
            'neutral': {
                'high': 'balanced and steady',
                'medium': 'casually relaxed',
                'low': 'calmly centered'
            }
        }
        
        # Determine intensity level
        abs_sentiment = abs(sentiment_score)
        if abs_sentiment > 0.6:
            level = 'high'
        elif abs_sentiment > 0.3:
            level = 'medium'
        else:
            level = 'low'
        
        return descriptions.get(emotion, descriptions['neutral']).get(level, 'balanced')