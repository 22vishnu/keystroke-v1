
from flask import Flask, request, jsonify, send_from_directory
import os
import sqlite3
from flask_cors import CORS

# Initialize Flask app at the very top
app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))

# Serve index.html at root
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

# Serve static files (JS, CSS, etc.)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)

# Ensure the database table exists
def create_table():
    conn = sqlite3.connect('keystroke_study.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keystroke_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            session_duration_ms REAL
        )
    ''')
    conn.commit()
    conn.close()

create_table()

# Insert features into the database
def insert_features(data):
    conn = sqlite3.connect('keystroke_study.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO keystroke_features (
            condition, total_keys_pressed, total_backspaces, error_rate, typing_accuracy,
            hold_time_mean, hold_time_std, hold_time_median,
            latency_mean, latency_std, latency_median,
            typing_speed_wpm, session_duration_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('condition'),
        data.get('total_keys_pressed'),
        data.get('total_backspaces'),
        data.get('error_rate'),
        data.get('typing_accuracy'),
        data.get('hold_time_mean'),
        data.get('hold_time_std'),
        data.get('hold_time_median'),
        data.get('latency_mean'),
        data.get('latency_std'),
        data.get('latency_median'),
        data.get('typing_speed_wpm'),
        data.get('session_duration_ms')
    ))
    conn.commit()
    conn.close()

@app.route('/save_features', methods=['POST'])
def save_features():
    data = request.json
    insert_features(data)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import Database
import os

app = Flask(__name__)
CORS(app)  # This allows frontend to communicate with backend

# Initialize database
db = Database()

# API route to save events
@app.route('/api/save_events', methods=['POST'])
def save_events():
    try:
        data = request.json
        participant_id = data.get('participant_id')
        task_type = data.get('task_type')
        events = data.get('events')
        
        db.save_events(participant_id, task_type, events)
        
        return jsonify({'success': True, 'message': 'Events saved successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# API route to save features
@app.route('/api/save_features', methods=['POST'])
def save_features():
    try:
        data = request.json
        participant_id = data.get('participant_id')
        condition = data.get('condition')
        features = data.get('features')
        
        db.save_features(participant_id, condition, features)
        
        return jsonify({'success': True, 'message': 'Features saved successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# API route to create a new participant
@app.route('/api/create_participant', methods=['POST'])
def create_participant():
    try:
        participant_id = db.create_participant()
        return jsonify({'success': True, 'participant_id': participant_id})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# API route to get all data
@app.route('/api/get_data', methods=['GET'])
def get_data():
    try:
        data = db.get_all_data()
        return jsonify({'success': True, 'data': data})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# API route to export data as CSV
@app.route('/api/export_csv', methods=['GET'])
def export_csv():
    try:
        csv_content = db.export_to_csv()
        return csv_content, 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=keystroke_data.csv'}
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Serve frontend files
@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory('../frontend', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)