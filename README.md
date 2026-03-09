# Activation Data Viewer

A web application for extracting and visualizing activation tables from PHITS-DCHAIN .act files.

## Features

- **File Upload**: Upload .act files directly from the browser
- **Region Selection**: Choose specific regions from the data file
- **Activation Table**: View isotope data across multiple time points (columns = time points, rows = isotopes)
- **CSV Export**: Export the complete activation table as a CSV file
- **Modern UI**: Clean, responsive web interface

## Project Structure

```
.
├── extraction.py          # Core extraction functions
├── app.py                 # Flask web application
├── templates/
│   └── index.html        # Web interface (HTML/CSS/JS)
├── data/                  # Sample .act data files
├── oldscripts/           # Original extraction scripts
└── requirements.txt      # Python dependencies
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Click "📂 Choose .act File" to upload a PHITS .act data file
2. Select a region from the dropdown (automatically populated from the file)
3. Click "Extract Data" to parse the activation data
4. View the activation table showing isotopes and their activity values
5. Click "📥 Export as CSV" to download the data as a CSV file

## API Endpoints

### POST /api/upload
Upload a .act file and get available regions.

**Response:**
```json
{
  "success": true,
  "filename": "C_activation_80-35-10d.act",
  "filepath": "uploads/C_activation_80-35-10d.act",
  "regions": [
    {"region": 11, "time": "10", "time_unit": "[d]"}
  ]
}
```

### POST /api/extract
Extract activation data for a specific region across all time points.

**Request:**
```json
{
  "filepath": "uploads/C_activation_80-35-10d.act",
  "region": 11
}
```

**Response:**
```json
{
  "region": 11,
  "times": ["10 [d]", "11 [d]", "12 [d]", "20 [d]"],
  "isotopes": ["H3", "Be7", "C11", ...],
  "data": {
    "H3": {
      "10 [d]": 57431000.0,
      "11 [d]": 57422000.0,
      "12 [d]": 57414000.0,
      "20 [d]": 57343000.0
    },
    "Be7": {
      "10 [d]": 13648000000.0,
      ...
    }
  }
}
```

## Extraction Module

The `extraction.py` module provides functions for extracting activation data from PHITS .act files:

### extract_activation_table(filename, region_number=None)
Extracts activation data for all time points in a .act file and returns a table format.

**Returns:** Dictionary with:
- `times`: List of time strings (e.g., ['10 [d]', '11 [d]', ...])
- `isotopes`: List of unique isotope names
- `data`: Dictionary where key is isotope, value is dict of time->activity
- `region`: Region number

```python
from extraction import extract_activation_table

data = extract_activation_table('data/C_activation_80-35-10d.act', region_number=11)
print("Time points:", data['times'])
print("Isotopes:", data['isotopes'])
print("H3 activity at 10 [d]:", data['data']['H3']['10 [d]'])
```

### extract_all_regions(filename)
Lists all available regions in a .act file.

```python
from extraction import extract_all_regions

regions = extract_all_regions('data/C_activation_80-35-10d.act')
for region in regions:
    print(f"Region {region['region']}: {region['time']} {region['time_unit']}")
```

## File Format

The application reads PHITS-DCHAIN output files (.act format) which contain:
- Region definitions with activation data
- Output time stamps
- Isotope tables with activation information (atoms/cc, radioactivity in Bq/cc)
- Half-life and decay heat data

## Notes

- Maximum file size: 16 MB
- Supported format: .act (PHITS output)
- The application expects standard PHITS formatting in the .act files
- Uploaded files are stored in the `uploads/` directory
