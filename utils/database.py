"""
Database utilities for storing and retrieving chat analysis data
using basic SQLite database to test app prototype, could use a
different relational database of your choosing
"""
import sqlite3
import json
from datetime import datetime
import os

DB_PATH = "data/relaylist.db"

def get_connection():
    """Get database connection"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Chat sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            filename TEXT NOT NULL,
            contact_name TEXT,
            contact_phone TEXT,
            message_count INTEGER,
            sent_count INTEGER,
            received_count INTEGER,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            duration_days INTEGER
        )
    """)
    
    # Analysis results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            emotions TEXT,
            sentiment TEXT,
            topics TEXT,
            temporal_patterns TEXT,
            summary TEXT,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
        )
    """)
    
    # Recommendations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            track_id TEXT,
            track_name TEXT,
            artist TEXT,
            spotify_url TEXT,
            relevance_score REAL,
            audio_features TEXT,
            recommendation_reason TEXT,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
        )
    """)
    
    # Spotify auth table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_auth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            access_token TEXT,
            refresh_token TEXT,
            token_expiry TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def save_chat_session(filename, contact_name, contact_phone, stats, analysis):
    """
    Save chat session and analysis to database
    
    Args:
        filename: Name of uploaded file
        contact_name: Contact's name
        contact_phone: Contact's phone number
        stats: Statistics from parser
        analysis: Analysis results from analyzer
        
    Returns:
        int: Session ID
    """
    import pandas as pd
    from datetime import datetime
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Convert pandas Timestamps to strings for SQLite
    start_date = str(stats['start_date']) if stats['start_date'] else None
    end_date = str(stats['end_date']) if stats['end_date'] else None
    
    # Helper function to convert timestamps in nested structures
    def convert_timestamps(obj):
        """Recursively convert pandas Timestamps to strings"""
        if isinstance(obj, pd.Timestamp):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: convert_timestamps(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_timestamps(item) for item in obj]
        else:
            return obj
    
    # Convert all timestamps in analysis data
    analysis_clean = convert_timestamps(analysis)
    
    # Insert chat session
    cursor.execute("""
        INSERT INTO chat_sessions 
        (filename, contact_name, contact_phone, message_count, sent_count, 
         received_count, start_date, end_date, duration_days)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        filename,
        contact_name,
        contact_phone,
        stats['total_messages'],
        stats['sent_count'],
        stats['received_count'],
        start_date,
        end_date,
        stats['duration_days']
    ))
    
    session_id = cursor.lastrowid
    
    # Insert analysis results with cleaned data
    cursor.execute("""
        INSERT INTO analysis_results
        (session_id, emotions, sentiment, topics, temporal_patterns, summary)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        json.dumps(analysis_clean['emotions']),
        json.dumps(analysis_clean['sentiment']),
        json.dumps(analysis_clean['topics']),
        json.dumps(analysis_clean['temporal_patterns']),
        analysis_clean['summary']
    ))
    
    conn.commit()
    conn.close()
    
    return session_id

def get_session(session_id):
    """Get chat session and analysis by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT cs.*, ar.emotions, ar.sentiment, ar.topics, 
               ar.temporal_patterns, ar.summary
        FROM chat_sessions cs
        LEFT JOIN analysis_results ar ON cs.id = ar.session_id
        WHERE cs.id = ?
    """, (session_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row['id'],
            'filename': row['filename'],
            'contact_name': row['contact_name'],
            'contact_phone': row['contact_phone'],
            'message_count': row['message_count'],
            'sent_count': row['sent_count'],
            'received_count': row['received_count'],
            'start_date': row['start_date'],
            'end_date': row['end_date'],
            'duration_days': row['duration_days'],
            'emotions': json.loads(row['emotions']) if row['emotions'] else {},
            'sentiment': json.loads(row['sentiment']) if row['sentiment'] else {},
            'topics': json.loads(row['topics']) if row['topics'] else {},
            'temporal_patterns': json.loads(row['temporal_patterns']) if row['temporal_patterns'] else {},
            'summary': row['summary']
        }
    return None

def save_recommendations(session_id, recommendations):
    """Save music recommendations to database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    for rec in recommendations:
        cursor.execute("""
            INSERT INTO recommendations
            (session_id, track_id, track_name, artist, spotify_url, 
             relevance_score, audio_features, recommendation_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            rec['id'],
            rec['name'],
            rec['artist'],
            rec['spotify_url'],
            rec.get('relevance_score', 0),
            json.dumps(rec.get('audio_features', {})),
            rec.get('reason', '')
        ))
    
    conn.commit()
    conn.close()

def get_recommendations(session_id):
    """Get recommendations for a session"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM recommendations
        WHERE session_id = ?
        ORDER BY relevance_score DESC
    """, (session_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row['track_id'],
            'name': row['track_name'],
            'artist': row['artist'],
            'spotify_url': row['spotify_url'],
            'relevance_score': row['relevance_score'],
            'audio_features': json.loads(row['audio_features']) if row['audio_features'] else {},
            'reason': row['recommendation_reason']
        }
        for row in rows
    ]

def get_all_sessions():
    """Get all chat sessions"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, filename, contact_name, upload_date, message_count
        FROM chat_sessions
        ORDER BY upload_date DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]