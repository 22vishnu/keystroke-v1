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