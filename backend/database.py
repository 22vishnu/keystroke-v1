import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_name='keystroke_study.db'):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # Create participants table
        c.execute('''CREATE TABLE IF NOT EXISTS participants
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Create events table
        c.execute('''CREATE TABLE IF NOT EXISTS events
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      participant_id INTEGER,
                      task_type TEXT,
                      event_type TEXT,
                      key TEXT,
                      code TEXT,
                      timestamp REAL,
                      FOREIGN KEY(participant_id) REFERENCES participants(id))''')
        
        # Create features table
        c.execute('''CREATE TABLE IF NOT EXISTS features
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      participant_id INTEGER,
                      condition TEXT,
                      total_keys_pressed INTEGER,
                      total_backspaces INTEGER,
                      error_rate REAL,
                      typing_accuracy REAL,
                      hold_time_mean REAL,
                      hold_time_std REAL,
                      hold_time_median REAL,
                      latency_mean REAL,
                      latency_std REAL,
                      latency_median REAL,
                      typing_speed_wpm REAL,
                      session_duration_ms REAL,
                      FOREIGN KEY(participant_id) REFERENCES participants(id))''')
        
        conn.commit()
        conn.close()
    
    def create_participant(self):
        """Create a new participant and return their ID"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('INSERT INTO participants DEFAULT VALUES')
        participant_id = c.lastrowid
        
        conn.commit()
        conn.close()
        
        return participant_id
    
    def save_events(self, participant_id, task_type, events):
        """Save events to the database"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        for event in events:
            c.execute('''INSERT INTO events (participant_id, task_type, event_type, key, code, timestamp)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                     (participant_id, task_type, event['type'], event['key'], event['code'], event['timestamp']))
        
        conn.commit()
        conn.close()
        
        return True
    
    def save_features(self, participant_id, condition, features):
        """Save features to the database"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('''INSERT INTO features 
                    (participant_id, condition, total_keys_pressed, total_backspaces, error_rate, 
                     typing_accuracy, hold_time_mean, hold_time_std, hold_time_median, 
                     latency_mean, latency_std, latency_median, typing_speed_wpm, session_duration_ms)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (participant_id, condition, 
                  features['total_keys_pressed'], features['total_backspaces'], features['error_rate'],
                  features['typing_accuracy'], features['hold_time_mean'], features['hold_time_std'],
                  features['hold_time_median'], features['latency_mean'], features['latency_std'],
                  features['latency_median'], features['typing_speed_wpm'], features['session_duration_ms']))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_all_data(self):
        """Retrieve all data from the database"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        c = conn.cursor()
        
        # Get participants
        c.execute('SELECT * FROM participants')
        participants = [dict(row) for row in c.fetchall()]
        
        # Get features for each participant
        for participant in participants:
            c.execute('SELECT * FROM features WHERE participant_id = ?', (participant['id'],))
            participant['features'] = [dict(row) for row in c.fetchall()]
            
            # Get events for each participant
            c.execute('SELECT * FROM events WHERE participant_id = ?', (participant['id'],))
            participant['events'] = [dict(row) for row in c.fetchall()]
        
        conn.close()
        
        return participants
    
    def export_to_csv(self):
        """Export all data to CSV format"""
        participants = self.get_all_data()
        
        # Create CSV content
        csv_content = "participant_id,condition,total_keys_pressed,total_backspaces,error_rate,typing_accuracy,hold_time_mean,hold_time_std,hold_time_median,latency_mean,latency_std,latency_median,typing_speed_wpm,session_duration_ms\n"
        
        for participant in participants:
            for feature in participant['features']:
                csv_content += f"{participant['id']},{feature['condition']},{feature['total_keys_pressed']},{feature['total_backspaces']},{feature['error_rate']},{feature['typing_accuracy']},{feature['hold_time_mean']},{feature['hold_time_std']},{feature['hold_time_median']},{feature['latency_mean']},{feature['latency_std']},{feature['latency_median']},{feature['typing_speed_wpm']},{feature['session_duration_ms']}\n"
        
        return csv_content

# Example usage
if __name__ == '__main__':
    db = Database()
    print("Database initialized successfully!")