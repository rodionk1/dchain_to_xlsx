"""
Flask web application for viewing activation data tables
"""

from flask import Flask, render_template, request, jsonify
import os
from extraction import extract_activation_data, extract_all_regions, extract_activation_table, get_nuclides_for_region

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'


def normalize_nuclide_name(name):
    """Normalize nuclide names for robust matching (e.g. Hg-197m vs Hg197m)."""
    return ''.join(ch.lower() for ch in name if ch.isalnum())


def load_mza_data():
    """Read MZA values (3rd column) from data/MZA.dat and return a normalized lookup map."""
    mza_path = os.path.join(os.path.dirname(__file__), 'data', 'MZA.dat')
    mza_map = {}

    with open(mza_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            if len(parts) < 3:
                continue

            nuclide = parts[0]
            try:
                # File format: nuclide, MZA/kg, MZA
                mza_value = float(parts[2])
            except ValueError:
                continue

            mza_map[normalize_nuclide_name(nuclide)] = mza_value

    return mza_map

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
        # First, get the list of nuclides for the given region
        nuclides = get_nuclides_for_region(filepath, region)
        
        # Then, extract activities for those nuclides
        result = extract_activation_table(filepath, region_number=region, nuclide_list=nuclides)
        
        # Format the response for the table display
        table_data = {
            'region': result['region'],
            'times': result['times'],
            'isotopes': result['isotopes'],
            'data': result['data']
        }
        
        return jsonify(table_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/mza', methods=['GET'])
def get_mza_data():
    """Return MZA lookup table keyed by normalized nuclide name."""
    try:
        return jsonify({'success': True, 'mza': load_mza_data()})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)
