"""
Music Recommender - Combines NLP chat analysis with user preferences
"""
import random

class MusicRecommender:
    """
    Generates music recommendations by combining:
    1. Chat emotional analysis (from NLP)
    2. User music preferences (genres, artists, etc.)
    3. Spotify's recommendation algorithm
    """
    
    def __init__(self, spotify_client):
        """
        Args:
            spotify_client: Authenticated Spotify client (spotipy)
        """
        self.sp = spotify_client
        
        # Emotion to Spotify audio feature mapping
        self.emotion_features = {
            'joy': {
                'valence': (0.6, 1.0),      # Happy
                'energy': (0.5, 0.9),        # Moderate to high energy
                'danceability': (0.5, 1.0),  # Danceable
                'acousticness': (0.0, 0.5)   # Not too acoustic
            },
            'sadness': {
                'valence': (0.0, 0.4),       # Sad
                'energy': (0.2, 0.5),        # Low energy
                'acousticness': (0.3, 1.0),  # More acoustic
                'instrumentalness': (0.0, 0.7)
            },
            'anger': {
                'valence': (0.0, 0.5),       # Negative
                'energy': (0.7, 1.0),        # High energy
                'loudness': (-5, 0),         # Loud
                'tempo': (120, 180)          # Fast
            },
            'surprise': {
                'valence': (0.4, 0.8),
                'energy': (0.6, 0.9),
                'danceability': (0.4, 0.8)
            },
            'neutral': {
                'valence': (0.4, 0.6),       # Balanced
                'energy': (0.4, 0.6)         # Medium
            },
            'chill': {
                'valence': (0.4, 0.7),
                'energy': (0.2, 0.5),
                'acousticness': (0.3, 0.8),
                'tempo': (60, 120)
            }
        }
    
    def generate_recommendations(self, chat_analysis, user_preferences, limit=20):
        """
        Generate music recommendations combining chat analysis and user preferences
        
        Args:
            chat_analysis: Results from ChatAnalyzer
            user_preferences: Results from MusicPreferenceCapture
            limit: Number of tracks to recommend
            
        Returns:
            list: Recommended tracks with relevance scores
        """
        method = user_preferences['method']
        
        if method == 'genre_selection':
            return self._recommend_by_genre(chat_analysis, user_preferences, limit)
        
        elif method == 'spotify_profile':
            return self._recommend_by_profile(chat_analysis, user_preferences, limit)
        
        elif method == 'seed_input':
            return self._recommend_by_seeds(chat_analysis, user_preferences, limit)
        
        else:
            # Fallback to genre-based
            return self._recommend_by_genre(chat_analysis, user_preferences, limit)
    
    def _recommend_by_genre(self, chat_analysis, user_prefs, limit):
        """
        Recommendation using search instead of recommendations API
        (Workaround for API restrictions)
        """
        emotion = chat_analysis['emotions']['dominant']
        sentiment = chat_analysis['sentiment']['average_polarity']
        
        # Get user's selected genres
        user_genres = user_prefs.get('genres', [])
        
        if not user_genres:
            from utils.music_preferences import MusicPreferenceCapture
            pref_capture = MusicPreferenceCapture()
            user_genres = pref_capture.get_genre_suggestions_from_emotion(emotion)
        
        recommendations = []
        
        # Use search instead of recommendations API
        # Create search queries based on emotion and genre
        search_terms = {
            'joy': ['happy', 'upbeat', 'cheerful', 'positive'],
            'sadness': ['sad', 'melancholy', 'emotional', 'heartbreak'],
            'anger': ['intense', 'aggressive', 'powerful', 'energy'],
            'surprise': ['exciting', 'dynamic', 'unexpected'],
            'neutral': ['chill', 'relaxed', 'calm', 'smooth']
        }
        
        emotion_terms = search_terms.get(emotion, search_terms['neutral'])
        
        # Search for tracks
        try:
            for genre in user_genres[:3]:
                for term in emotion_terms[:2]:  # Use 2 terms per genre
                    query = f"{term} {genre}"
                    results = self.sp.search(q=query, type='track', limit=5)
                    
                    if results and 'tracks' in results and 'items' in results['tracks']:
                        for track in results['tracks']['items']:
                            # Avoid duplicates
                            if not any(r['id'] == track['id'] for r in recommendations):
                                recommendations.append(self._format_track(track, genre, emotion))
                    
                    if len(recommendations) >= limit:
                        break
                
                if len(recommendations) >= limit:
                    break
            
            # Get audio features for scoring (if available)
            scored_recs = []
            for track in recommendations[:limit]:
                # Try to get audio features, but don't fail if not available
                try:
                    features = self.sp.audio_features([track['id']])
                    if features and features[0]:
                        track['audio_features'] = features[0]
                        # Simple scoring based on popularity
                        track['relevance_score'] = track['popularity'] / 100
                    else:
                        track['audio_features'] = {}
                        track['relevance_score'] = 0.7  # Default score
                except:
                    track['audio_features'] = {}
                    track['relevance_score'] = 0.7
                
                track['reason'] = f"Matches {emotion} mood and {track['genre_source']} genre"
                scored_recs.append(track)
            
            return sorted(scored_recs, key=lambda x: x.get('relevance_score', 0.5), reverse=True)[:limit]
            
        except Exception as e:
            print(f"Error in search-based recommendations: {e}")
            return []
    
    def _recommend_by_profile(self, chat_analysis, user_prefs, limit):
        """
        Recommendation using user's actual Spotify listening history
        Most personalized method!
        """
        emotion = chat_analysis['emotions']['dominant']
        sentiment = chat_analysis['sentiment']['average_polarity']
        
        try:
            # Get user's top artists
            top_artists = self.sp.current_user_top_artists(
                limit=5,
                time_range='medium_term'  # Last 6 months
            )
            
            # Get user's top tracks
            top_tracks = self.sp.current_user_top_tracks(
                limit=5,
                time_range='medium_term'
            )
            
            # Extract artist and track IDs as seeds
            seed_artists = [artist['id'] for artist in top_artists['items'][:2]]
            seed_tracks = [track['id'] for track in top_tracks['items'][:2]]
            
            # Get audio feature targets
            feature_targets = self.emotion_features.get(emotion, self.emotion_features['neutral'])
            
            # Get recommendations based on user's actual taste + emotion
            results = self.sp.recommendations(
                seed_artists=seed_artists,
                seed_tracks=seed_tracks,
                limit=limit,
                target_valence=(sentiment + 1) / 2,
                target_energy=sum(feature_targets.get('energy', (0.5, 0.5))) / 2
            )
            
            recommendations = []
            for track in results['tracks']:
                recommendations.append(self._format_track(track, 'profile-based', emotion))
            
            # Score recommendations
            scored_recs = self._score_recommendations(
                recommendations,
                chat_analysis,
                user_prefs
            )
            
            return sorted(scored_recs, key=lambda x: x['relevance_score'], reverse=True)[:limit]
            
        except Exception as e:
            print(f"Error with profile-based recommendations: {e}")
            # Fallback to genre-based
            return self._recommend_by_genre(chat_analysis, user_prefs, limit)
    
    def _recommend_by_seeds(self, chat_analysis, user_prefs, limit):
        """
        Recommendation using user-provided artists/tracks as seeds
        """
        emotion = chat_analysis['emotions']['dominant']
        sentiment = chat_analysis['sentiment']['average_polarity']
        
        seed_artists = []
        seed_tracks = []
        
        # Search for artist IDs
        for artist_name in user_prefs.get('artists', []):
            try:
                results = self.sp.search(q=f'artist:{artist_name}', type='artist', limit=1)
                if results['artists']['items']:
                    seed_artists.append(results['artists']['items'][0]['id'])
            except:
                continue
        
        # Search for track IDs
        for track_name in user_prefs.get('tracks', []):
            try:
                results = self.sp.search(q=track_name, type='track', limit=1)
                if results['tracks']['items']:
                    seed_tracks.append(results['tracks']['items'][0]['id'])
            except:
                continue
        
        if not seed_artists and not seed_tracks:
            # No valid seeds found, fallback
            return self._recommend_by_genre(chat_analysis, user_prefs, limit)
        
        # Get recommendations
        feature_targets = self.emotion_features.get(emotion, self.emotion_features['neutral'])
        
        try:
            results = self.sp.recommendations(
                seed_artists=seed_artists[:2],  # Max 2 artists
                seed_tracks=seed_tracks[:3],    # Max 3 tracks (Spotify allows 5 total seeds)
                limit=limit,
                target_valence=(sentiment + 1) / 2,
                target_energy=sum(feature_targets.get('energy', (0.5, 0.5))) / 2
            )
            
            recommendations = []
            for track in results['tracks']:
                recommendations.append(self._format_track(track, 'seed-based', emotion))
            
            scored_recs = self._score_recommendations(
                recommendations,
                chat_analysis,
                user_prefs
            )
            
            return sorted(scored_recs, key=lambda x: x['relevance_score'], reverse=True)[:limit]
            
        except Exception as e:
            print(f"Error with seed-based recommendations: {e}")
            return []
    
    def _format_track(self, track, genre, emotion):
        """Format Spotify track object into our structure"""
        return {
            'id': track['id'],
            'name': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'spotify_url': track['external_urls']['spotify'],
            'preview_url': track.get('preview_url'),
            'duration_ms': track['duration_ms'],
            'popularity': track['popularity'],
            'genre_source': genre,
            'emotion_match': emotion,
            'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None
        }
    
    def _score_recommendations(self, tracks, chat_analysis, user_prefs):
        """
        Score each track based on:
        1. How well audio features match emotion
        2. User preference alignment
        3. Spotify popularity (balanced)
        """
        emotion = chat_analysis['emotions']['dominant']
        sentiment = chat_analysis['sentiment']['average_polarity']
        
        # Get audio features for all tracks
        track_ids = [t['id'] for t in tracks]
        
        try:
            audio_features = self.sp.audio_features(track_ids)
        except:
            audio_features = [None] * len(track_ids)
        
        scored_tracks = []
        
        for track, features in zip(tracks, audio_features):
            if not features:
                track['relevance_score'] = 0.5
                track['audio_features'] = {}
                scored_tracks.append(track)
                continue
            
            # Calculate emotion match score
            target_features = self.emotion_features.get(emotion, self.emotion_features['neutral'])
            
            emotion_score = 0
            feature_count = 0
            
            for feature_name, target_range in target_features.items():
                if feature_name in features and features[feature_name] is not None:
                    value = features[feature_name]
                    min_val, max_val = target_range
                    
                    # Calculate how well the value fits in the target range
                    if min_val <= value <= max_val:
                        emotion_score += 1.0
                    else:
                        # Penalize based on distance from range
                        if value < min_val:
                            distance = (min_val - value) / min_val if min_val != 0 else 1
                        else:
                            distance = (value - max_val) / (1 - max_val) if max_val != 1 else 1
                        emotion_score += max(0, 1 - distance)
                    
                    feature_count += 1
            
            emotion_score = emotion_score / feature_count if feature_count > 0 else 0.5
            
            # Popularity score (prefer somewhat popular but not too mainstream)
            popularity = track['popularity']
            if user_prefs.get('popularity_range'):
                min_pop, max_pop = user_prefs['popularity_range']
                if min_pop <= popularity <= max_pop:
                    popularity_score = 1.0
                else:
                    popularity_score = 0.5
            else:
                # Default: prefer moderate popularity
                popularity_score = 1 - abs(popularity - 60) / 60
            
            # Final score: weighted combination
            relevance_score = (
                emotion_score * 0.6 +      # 60% emotion match
                popularity_score * 0.4     # 40% popularity
            )
            
            track['relevance_score'] = relevance_score
            track['audio_features'] = features
            track['emotion_match_score'] = emotion_score
            
            # Add explanation
            track['reason'] = self._generate_recommendation_reason(
                emotion, features, emotion_score
            )
            
            scored_tracks.append(track)
        
        return scored_tracks
    
    def _generate_recommendation_reason(self, emotion, features, score):
        """Generate human-readable explanation for recommendation"""
        reasons = []
        
        valence = features.get('valence', 0.5)
        energy = features.get('energy', 0.5)
        
        if emotion == 'joy' and valence > 0.6:
            reasons.append("upbeat and positive vibe")
        elif emotion == 'sadness' and valence < 0.4:
            reasons.append("melancholic tone")
        elif emotion == 'anger' and energy > 0.7:
            reasons.append("high energy and intensity")
        
        if score > 0.8:
            return f"Perfect match - {', '.join(reasons)}" if reasons else "Perfect emotional match"
        elif score > 0.6:
            return f"Great match - {', '.join(reasons)}" if reasons else "Strong emotional match"
        else:
            return "Matches your conversation's mood"