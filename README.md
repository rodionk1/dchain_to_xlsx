# Activation Data Viewer

A web application for extracting and visualizing activation tables from PHITS-DCHAIN .act files.

## Features

- **File Upload**: Upload .act files directly from the browser
- **Region Selection**: Choose specific regions from the data file
- **Activation Table**: View isotope data with atoms/cc and activity in Bq/cc
- **CSV Export**: Export the extracted data as a CSV file
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
Extract activation data for a specific region.

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
  "time": "10",
  "time_unit": "[d]",
  "data": [
    {"isotope": "H3", "atoms": "3.2214E+16", "activity": "5.7431E+07"},
    ...
  ]
}
```

## Extraction Module

The `extraction.py` module provides two main functions:

### extract_activation_data(filename, region_number=None, time_value=None, time_unit=None)
Extracts activation data for a specific region and time from a .act file.

```python
from extraction import extract_activation_data

data = extract_activation_data('data/C_activation_80-35-10d.act', region_number=11)
print(data['isotopes'])    # List of isotope names
print(data['activities'])  # List of activity values
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
