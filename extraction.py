"""
Module for extracting activation data from PHITS-DCHAIN .act files
"""

import re


def extract_activation_data(filename, region_number=None, time_value=None, time_unit=None):
    """
    Extract activation and isotope data from a PHITS .act file.
    
    If region_number, time_value, and time_unit are not provided, extracts the first dataset.
    
    Args:
        filename (str): Path to the .act file
        region_number (int or str, optional): Region number to extract
        time_value (str, optional): Time value (e.g., '10')
        time_unit (str, optional): Time unit (e.g., '[d]', '[h]', '[s]')
    
    Returns:
        dict: Dictionary containing:
            - 'isotopes': list of isotope names
            - 'activities': list of activity values (in Bq/cc)
            - 'atoms': list of atom concentrations
            - 'half_lives': list of half-lives (formatted strings)
            - 'region': region number
            - 'time': time value
            - 'time_unit': time unit
    """
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except IOError as e:
        raise IOError(f"Cannot open file {filename}: {e}")
    
    # Split into lines for processing
    lines = content.split('\n')
    
    # If specific region/time not provided, use the first one found
    region_to_find = region_number
    time_to_find = time_value
    
    isotopes = []
    activities = []
    atoms = []
    half_lives = []
    found_region = None
    found_time = None
    found_time_unit = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Find region marker
        if region_to_find is not None and str(region_to_find) in line and 'region number' in line:
            found_region = region_to_find
            i += 1
            
            # Find the output time line
            while i < len(lines):
                line = lines[i]
                if 'output time' in line or '--- output time ---' in line:
                    # Parse time from this line
                    # Format: --- output time ---         10 [d]
                    parts = line.split()
                    for j, part in enumerate(parts):
                        if part.isdigit() or ('.' in part and part.replace('.', '').replace('E', '').replace('-', '').replace('+', '').isdigit()):
                            try:
                                found_time = part
                                if j + 1 < len(parts):
                                    found_time_unit = parts[j + 1]
                                break
                            except:
                                pass
                    i += 1
                    break
                i += 1
            
            if found_region is None:
                i += 1
                continue
        elif region_to_find is None and 'region number' in line and 'no.' in line:
            # Find first region if none specified
            match = re.search(r'region number\s+(\d+)', line)
            if match:
                found_region = int(match.group(1))
                i += 1
                
                # Find the output time line
                while i < len(lines):
                    line = lines[i]
                    if 'output time' in line or '--- output time ---' in line:
                        parts = line.split()
                        for j, part in enumerate(parts):
                            if part.isdigit() or ('.' in part and part.replace('.', '').replace('E', '').replace('-', '').replace('+', '').isdigit()):
                                try:
                                    found_time = part
                                    if j + 1 < len(parts):
                                        found_time_unit = parts[j + 1]
                                    break
                                except:
                                    pass
                        i += 1
                        break
                    i += 1
        
        # Find the isotope data table header
        if 'nuclide' in line and 'atoms' in line and 'radioactivity' in line:
            # Skip header line
            i += 1
            
            # Parse isotope data lines
            while i < len(lines):
                line = lines[i].strip()
                if not line or line.startswith('gamma-ray') or line.startswith('---'):
                    break
                
                try:
                    parts = line.split()
                    if len(parts) >= 3:
                        # Parse isotope name (first 1-2 elements)
                        iso_name = None
                        atoms_val = None
                        activity_val = None
                        
                        if len(parts) >= 3:
                            # Try to determine isotope format
                            if parts[0].isalpha():
                                # Format: "H   3" or similar
                                element = parts[0]
                                mass = parts[1]
                                iso_name = f"{element}{mass}"
                                
                                # Activity is typically the 3rd numeric column after iso name
                                try:
                                    atoms_val = float(parts[2])
                                    activity_val = float(parts[3])
                                except (ValueError, IndexError):
                                    i += 1
                                    continue
                            else:
                                # Skip lines that don't start with element
                                i += 1
                                continue
                            
                            if iso_name:
                                isotopes.append(iso_name)
                                atoms.append(atoms_val)
                                activities.append(activity_val)
                                half_lives.append("")  # Will be extracted separately if needed
                
                except (ValueError, IndexError):
                    pass
                
                i += 1
        else:
            i += 1
    
    return {
        'isotopes': isotopes,
        'activities': activities,
        'atoms': atoms,
        'half_lives': half_lives,
        'region': found_region,
        'time': found_time,
        'time_unit': found_time_unit,
    }


def extract_all_regions(filename):
    """
    Extract all regions from an .act file.
    
    Returns:
        list: List of dictionaries with region data
    """
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except IOError as e:
        raise IOError(f"Cannot open file {filename}: {e}")
    
    regions = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if 'region number' in line and '.....' in line:
            # Extract region number from line like: "region number .....          11  (in nmtc yield file)"
            match = re.search(r'region number\s+\.+\s+(\d+)', line)
            if match:
                region_num = int(match.group(1))
                
                # Find output time
                time_info = {'value': None, 'unit': None}
                for j in range(i, min(i + 20, len(lines))):
                    if 'output time' in lines[j] or '--- output time ---' in lines[j]:
                        parts = lines[j].split()
                        for k, part in enumerate(parts):
                            try:
                                val = float(part)
                                time_info['value'] = part
                                if k + 1 < len(parts) and '[' in parts[k + 1]:
                                    time_info['unit'] = parts[k + 1]
                                break
                            except ValueError:
                                pass
                        break
                
                regions.append({
                    'region': region_num,
                    'time': time_info['value'],
                    'time_unit': time_info['unit']
                })
    
    return regions


def extract_activation_table(filename, region_number=None):
    """
    Extract activation data for all time points in a .act file.
    
    Returns a table where:
    - Rows are isotopes
    - Columns are time points
    - Values are activity in Bq/cc
    
    Args:
        filename (str): Path to the .act file
        region_number (int or str, optional): Region number to extract
    
    Returns:
        dict: Dictionary containing:
            - 'times': list of time strings (e.g., ['10 [d]', '11 [d]', ...])
            - 'isotopes': list of unique isotope names
            - 'data': dict where key is isotope, value is dict of time->activity
            - 'region': region number
    """
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except IOError as e:
        raise IOError(f"Cannot open file {filename}: {e}")
    
    lines = content.split('\n')
    time_sections = []
    found_region = None
    
    # Find all output time sections
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Find region marker (if specified)
        if region_number is not None and 'region number' in line and '.....' in line:
            match = re.search(r'region number\s+\.+\s+(\d+)', line)
            if match and int(match.group(1)) == int(region_number):
                found_region = int(match.group(1))
                i += 1
                continue
            elif found_region is not None and int(match.group(1)) != int(region_number):
                # Found a different region, stop if we already found our target
                break
        
        # Find output time header
        if '--- output time ---' in line:
            # Parse time from this line
            parts = line.split()
            time_str = None
            for j, part in enumerate(parts):
                if part.replace('.', '').replace('E', '').replace('-', '').replace('+', '').isdigit():
                    try:
                        time_str = part
                        if j + 1 < len(parts) and '[' in parts[j + 1]:
                            time_str += ' ' + parts[j + 1]
                        break
                    except:
                        pass
            
            if time_str:
                # Find the isotope table for this time section
                isotopes_data = []
                isotopes_found = False
                
                # Skip to the table header
                while i < len(lines) and not ('nuclide' in lines[i] and 'atoms' in lines[i] and 'radioactivity' in lines[i]):
                    i += 1
                
                if i < len(lines):
                    i += 1  # Skip header line
                    
                    # Parse isotope data lines
                    while i < len(lines):
                        line = lines[i].strip()
                        if not line or line.startswith('gamma-ray') or line.startswith('---') or line.startswith('total') or line.startswith('activated'):
                            break
                        
                        try:
                            parts = line.split()
                            if len(parts) >= 4:
                                # Parse isotope name
                                if parts[0].isalpha() and len(parts) >= 4:
                                    element = parts[0]
                                    mass = parts[1]
                                    isotope_name = f"{element}{mass}"
                                    
                                    # Activity is typically the 3rd numeric column
                                    try:
                                        activity_val = float(parts[3])
                                        isotopes_data.append({
                                            'isotope': isotope_name,
                                            'activity': activity_val
                                        })
                                    except (ValueError, IndexError):
                                        pass
                        except:
                            pass
                        
                        i += 1
                
                if isotopes_data:
                    time_sections.append({
                        'time': time_str,
                        'isotopes': isotopes_data
                    })
        
        i += 1
    
    if not time_sections:
        return {
            'times': [],
            'isotopes': [],
            'data': {},
            'region': found_region or region_number
        }
    
    # Create the table structure
    # Collect all unique isotopes
    all_isotopes = set()
    for section in time_sections:
        for iso_data in section['isotopes']:
            all_isotopes.add(iso_data['isotope'])
    
    isotopes_list = sorted(list(all_isotopes))
    times_list = [section['time'] for section in time_sections]
    
    # Create data dictionary: isotope -> {time: activity}
    data_dict = {}
    for isotope in isotopes_list:
        data_dict[isotope] = {}
        for section in time_sections:
            # Find this isotope in this time section
            activity = 0.0
            for iso_data in section['isotopes']:
                if iso_data['isotope'] == isotope:
                    activity = iso_data['activity']
                    break
            data_dict[isotope][section['time']] = activity
    
    return {
        'times': times_list,
        'isotopes': isotopes_list,
        'data': data_dict,
        'region': found_region or region_number
    }
