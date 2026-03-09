"""
Flask web application for viewing activation data tables
"""

from flask import Flask, render_template, request, jsonify
import os
from extraction import extract_activation_data, extract_all_regions

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and return available regions"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.act'):
        return jsonify({'error': 'File must be .act format'}), 400
    
    # Save uploaded file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    try:
        # Extract regions available in the file
        regions = extract_all_regions(filepath)
        return jsonify({
            'success': True,
            'filename': file.filename,
            'filepath': filepath,
            'regions': regions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/extract', methods=['POST'])
def extract_data():
    """Extract activation data for specified region and time"""
    data = request.json
    filepath = data.get('filepath')
    region = data.get('region')
    
    if not filepath or not region:
        return jsonify({'error': 'Missing filepath or region'}), 400
    
    try:
        result = extract_activation_data(filepath, region_number=region)
        
        # Format the response
        table_data = {
            'region': result['region'],
            'time': result['time'],
            'time_unit': result['time_unit'],
            'data': []
        }
        
        for i, iso in enumerate(result['isotopes']):
            table_data['data'].append({
                'isotope': iso,
                'atoms': f"{result['atoms'][i]:.4E}" if result['atoms'][i] else "0",
                'activity': f"{result['activities'][i]:.4E}" if result['activities'][i] else "0"
            })
        
        return jsonify(table_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)
