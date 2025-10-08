"""
SMS CSV File Parser
Parses SMS CSV files with columns: Type, Date, Name / Number, Sender, Content
"""
import pandas as pd
from datetime import datetime
import re

class SMSParser:
    """Parser for SMS CSV exports"""
    
    def __init__(self):
        self.messages = []
        self.contact_name = None
        self.contact_phone = None
        
    def parse_file(self, file_path):
        """
        Parse SMS CSV file and extract messages
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            dict: Parsed data with messages, metadata, and statistics
        """
        # Read CSV
        df = pd.read_csv(file_path)
        
        # Validate columns
        required_cols = ['Type', 'Date', 'Name / Number', 'Sender', 'Content']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"CSV must contain columns: {required_cols}")
        
        # Extract contact information (assuming single conversation)
        # Parse contact name and phone from first entry
        first_contact = df['Name / Number'].iloc[0]
        self.contact_name, self.contact_phone = self._parse_contact_info(first_contact)
        
        # Process each message
        messages = []
        for idx, row in df.iterrows():
            try:
                parsed_msg = self._parse_message(row)
                if parsed_msg:
                    messages.append(parsed_msg)
            except Exception as e:
                print(f"Warning: Could not parse row {idx}: {e}")
                continue
        
        # Sort by timestamp
        messages.sort(key=lambda x: x['timestamp'])
        
        # Generate statistics
        stats = self._generate_statistics(messages)
        
        return {
            'messages': messages,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'statistics': stats
        }
    
    def _parse_contact_info(self, contact_string):
        """
        Extract contact name and phone number
        
        Example: "Alex (A-Money) 🏀 (+17185551234)" -> ("Alex (A-Money) 🏀", "+17185551234")
        """
        # Match phone number in parentheses at the end
        phone_pattern = r'\((\+\d+)\)$'
        phone_match = re.search(phone_pattern, contact_string)
        
        if phone_match:
            phone = phone_match.group(1)
            # Remove phone number part to get name
            name = contact_string[:phone_match.start()].strip()
            return name, phone
        
        # If no phone found, return full string as name
        return contact_string, "Unknown"
    
    def _parse_message(self, row):
        """
        Parse a single message row
        
        Returns:
            dict: Message data with timestamp, sender, content, type
        """
        # Parse date
        try:
            timestamp = pd.to_datetime(row['Date'], format='%m/%d/%Y %H:%M')
        except:
            # Try alternative formats
            timestamp = pd.to_datetime(row['Date'])
        
        # Determine sender
        if row['Type'] == 'Sent':
            sender = 'You'
        else:
            # Use Sender column if available, otherwise use contact name
            sender = row['Sender'] if row['Sender'] else self.contact_name
        
        # Clean content
        content = str(row['Content']).strip()
        
        # Skip empty messages
        if not content or content == 'nan':
            return None
        
        return {
            'timestamp': timestamp,
            'sender': sender,
            'content': content,
            'type': row['Type'].lower(),
            'date': timestamp.date(),
            'time': timestamp.time()
        }
    
    def _generate_statistics(self, messages):
        """Generate conversation statistics"""
        if not messages:
            return {}
        
        total = len(messages)
        sent = sum(1 for m in messages if m['type'] == 'sent')
        received = total - sent
        
        # Date range
        start_date = messages[0]['timestamp']
        end_date = messages[-1]['timestamp']
        duration_days = (end_date - start_date).days
        
        # Average message length
        avg_length = sum(len(m['content']) for m in messages) / total
        
        # Messages per day
        messages_per_day = total / max(duration_days, 1)
        
        return {
            'total_messages': total,
            'sent_count': sent,
            'received_count': received,
            'start_date': start_date,
            'end_date': end_date,
            'duration_days': duration_days,
            'avg_message_length': round(avg_length, 1),
            'messages_per_day': round(messages_per_day, 1)
        }
    
    def get_conversation_context(self, messages, window_size=5):
        """
        Get conversation context by grouping messages
        
        Args:
            messages: List of message dicts
            window_size: Number of messages to group together
            
        Returns:
            list: Grouped message contexts
        """
        contexts = []
        for i in range(0, len(messages), window_size):
            window = messages[i:i+window_size]
            combined_text = ' '.join([m['content'] for m in window])
            contexts.append({
                'text': combined_text,
                'start_time': window[0]['timestamp'],
                'end_time': window[-1]['timestamp'],
                'message_count': len(window)
            })
        return contexts