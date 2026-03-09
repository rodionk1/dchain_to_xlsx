import re


def convert_to_seconds(value, unit):
    """
    Convert time value to seconds based on unit.
    
    Args:
        value (float): Time value
        unit (str): Time unit ('s', 'm', 'h', 'd', 'y')
    
    Returns:
        float: Time in seconds
    """
    unit = unit.lower()
    if unit == 's':
        return value
    elif unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400
    elif unit == 'y':
        return value * 31536000  # 365 days
    else:
        return value  # Default to seconds if unknown unit


def format_half_life(half_life_seconds):
    """
    Format half-life in seconds to appropriate units.
    
    Args:
        half_life_seconds (float): Half-life in seconds
    
    Returns:
        tuple: (formatted_value, unit)
    """
    if half_life_seconds <= 0:
        return "0.000", "s"
    
    if half_life_seconds < 60:
        return f"{half_life_seconds:.3f}", "s"
    elif half_life_seconds < 3600:  # < 1 hour
        return f"{half_life_seconds/60:.3f}", "m"
    elif half_life_seconds < 86400:  # < 1 day
        return f"{half_life_seconds/3600:.3f}", "h"
    elif half_life_seconds < 31536000:  # < 1 year
        return f"{half_life_seconds/86400:.3f}", "d"
    else:
        return f"{half_life_seconds/31536000:.3f}", "y"


def format_cooldown_time(time_str):
    """
    Format cooldown time string to appropriate units.
    
    Args:
        time_str (str): Time string like "10 [d]" or "1.0007E+01 [d]"
    
    Returns:
        str: Formatted cooldown time
    """
    # Parse the time string
    match = re.match(r'([0-9.E+-]+)\s*\[([a-zA-Z]+)\]', time_str)
    if not match:
        return time_str
    
    value = float(match.group(1))
    unit = match.group(2)
    
    # Convert to appropriate units
    if unit == 's':
        if value < 60:
            return f"{value:.1f} s"
        elif value < 3600:
            return f"{value/60:.1f} m"
        elif value < 86400:
            return f"{value/3600:.1f} h"
        else:
            return f"{value/86400:.1f} d"
    elif unit == 'm':
        if value < 60:
            return f"{value:.1f} m"
        else:
            return f"{value/60:.1f} h"
    elif unit == 'h':
        if value < 24:
            return f"{value:.1f} h"
        else:
            return f"{value/24:.1f} d"
    elif unit == 'd':
        if value < 365:
            return f"{value:.1f} d"
        else:
            return f"{value/365:.1f} y"
    else:
        return time_str


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
            - 'activities': list of activity values (in Bq)
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
                        activitycc_val = None
                        activity_val = None
                        
                        if len(parts) >= 3:
                            # Try to determine isotope format
                            if parts[0].isalpha():
                                # Format: "H   3" or similar
                                element = parts[0]
                                mass = parts[1]
                                iso_name = f"{element}{mass}"
                                
                                # Activity pr cc is typically the 3rd numeric column after iso name
                                # Activity is often in the 4th column (index 3)
                                try:
                                    atoms_val = float(parts[2])
                                    activitycc_val = float(parts[3])
                                    activity_val = float(parts[4])
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
    - Columns are cooldown time points (time after last shutdown)
    - Values are activity in Bq
    
    Time points are extracted from "(after the last shutdown: XX [unit])" markers.
    If no such marker is present, the time point is treated as immediately after irradiation (0 cooldown).
    
    Args:
        filename (str): Path to the .act file
        region_number (int or str, optional): Region number to extract
    
    Returns:
        dict: Dictionary containing:
            - 'times': list of cooldown time strings (e.g., ['0.0 s', '10.0 m', '1.0 h', ...])
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
    
    # Extract irradiation time from header
    irradiation_time_seconds = None
    for line in lines[:20]:  # Check first 20 lines for header
        if 'irradiation time' in line:
            match = re.search(r'irradiation time\s*\.\.+\s*([0-9.E+-]+)\s*\[([a-zA-Z]+)\]', line)
            if match:
                irrad_val = float(match.group(1))
                irrad_unit = match.group(2)
                irradiation_time_seconds = convert_to_seconds(irrad_val, irrad_unit)
                break
    
    # Find all output time sections
    i = 0
    in_target_region = region_number is None  # If no region specified, process all
    while i < len(lines):
        line = lines[i]
        time_label = "0.0 s"  # Default initialization
        
        # Find region marker
        if 'region number' in line and '.....' in line:
            match = re.search(r'region number\s+\.+\s+(\d+)', line)
            if match:
                current_region = int(match.group(1))
                if region_number is not None:
                    if current_region == int(region_number):
                        in_target_region = True
                        found_region = current_region
                    else:
                        in_target_region = False
                        if found_region is not None:
                            # Already processed target region, stop
                            break
                i += 1
                continue
        
        # Process time sections only if in target region
        if in_target_region and '--- output time ---' in line:
            # Extract output time value
            output_time_seconds = None
            parts = line.split()
            for j, part in enumerate(parts):
                if part.replace('.', '').replace('E', '').replace('-', '').replace('+', '').isdigit():
                    # Look for the time value followed by unit in brackets
                    if j + 1 < len(parts) and '[' in parts[j + 1]:
                        time_val = float(part)
                        unit_match = re.search(r'\[([a-zA-Z]+)\]', parts[j + 1])
                        if unit_match:
                            unit = unit_match.group(1)
                            output_time_seconds = convert_to_seconds(time_val, unit)
                        break
            
            # Determine time label based on comparison with irradiation time
            time_label = "0.0 s"  # Default
            
            if output_time_seconds is not None and irradiation_time_seconds is not None:
                if output_time_seconds < irradiation_time_seconds:
                    # During irradiation
                    formatted_time = format_cooldown_time(f"{output_time_seconds} [s]")
                    time_label = f"irradiation time: {formatted_time}"
                else:
                    # After irradiation - check for shutdown marker
                    shutdown_match = re.search(r'\(after the last shutdown:\s*([0-9.E+-]+)\s*\[([a-zA-Z]+)\]', line)
                    if shutdown_match:
                        cooldown_val = float(shutdown_match.group(1))
                        cooldown_unit = shutdown_match.group(2)
                        formatted_cooldown = format_cooldown_time(f"{cooldown_val} [{cooldown_unit}]")
                        time_label = f"cooldown time: {formatted_cooldown}"
                    else:
                        # Immediately after irradiation
                        time_label = "cooldown time: 0.0 s"
            else:
                # Fallback: look for shutdown marker anyway
                shutdown_match = re.search(r'\(after the last shutdown:\s*([0-9.E+-]+)\s*\[([a-zA-Z]+)\]', line)
                if shutdown_match:
                    cooldown_val = float(shutdown_match.group(1))
                    cooldown_unit = shutdown_match.group(2)
                    formatted_cooldown = format_cooldown_time(f"{cooldown_val} [{cooldown_unit}]")
                    time_label = f"cooldown time: {formatted_cooldown}"
            
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
                            # Parse isotope name - handle "Element Mass" and "ElementMass" formats
                            isotope_name = None
                            activity_idx = 3  # Default position for activity

                            # Format: separate element and mass columns
                            if parts[0].isalpha() and len(parts) >= 4:
                                element = parts[0]
                                mass = parts[1]
                                isotope_name = f"{element}{mass}"
                                activity_idx = 3
                            # Format: combined element+mass (e.g. Sm155, Tl201)
                            elif len(parts[0]) > 2 and parts[0][:2].isalpha() and parts[0][2:].isdigit():
                                element = parts[0][:2]
                                mass = parts[0][2:]
                                isotope_name = f"{element}{mass}"
                                activity_idx = 2
                            elif len(parts[0]) > 1 and parts[0][0].isalpha() and parts[0][1:].isdigit():
                                element = parts[0][0]
                                mass = parts[0][1:]
                                isotope_name = f"{element}{mass}"
                                activity_idx = 2

                            if isotope_name:
                                try:
                                    activity_val = float(parts[activity_idx])
                                    # Extract half-life from the last column before dose-rate
                                    half_life_val = float(parts[-2]) if len(parts) >= 6 else 0.0
                                    isotopes_data.append({
                                        'isotope': isotope_name,
                                        'activity': activity_val,
                                        'half_life': half_life_val
                                    })
                                except (ValueError, IndexError):
                                    pass
                    except:
                        pass
                    
                    i += 1
            
            if isotopes_data:
                time_sections.append({
                    'time': time_label,
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
    
    # periodic order mapping (symbol -> atomic number)
    periodic_order = {
        'H':1,'He':2,'Li':3,'Be':4,'B':5,'C':6,'N':7,'O':8,'F':9,'Ne':10,
        'Na':11,'Mg':12,'Al':13,'Si':14,'P':15,'S':16,'Cl':17,'Ar':18,'K':19,'Ca':20,
        'Sc':21,'Ti':22,'V':23,'Cr':24,'Mn':25,'Fe':26,'Co':27,'Ni':28,'Cu':29,'Zn':30,
        'Ga':31,'Ge':32,'As':33,'Se':34,'Br':35,'Kr':36,'Rb':37,'Sr':38,'Y':39,'Zr':40,
        'Nb':41,'Mo':42,'Tc':43,'Ru':44,'Rh':45,'Pd':46,'Ag':47,'Cd':48,'In':49,'Sn':50,
        'Sb':51,'Te':52,'I':53,'Xe':54,'Cs':55,'Ba':56,'La':57,'Ce':58,'Pr':59,'Nd':60,
        'Pm':61,'Sm':62,'Eu':63,'Gd':64,'Tb':65,'Dy':66,'Ho':67,'Er':68,'Tm':69,'Yb':70,
        'Lu':71,'Hf':72,'Ta':73,'W':74,'Re':75,'Os':76,'Ir':77,'Pt':78,'Au':79,'Hg':80,
        'Tl':81,'Pb':82,'Bi':83,'Po':84,'At':85,'Rn':86,'Fr':87,'Ra':88,'Ac':89,'Th':90,
        'Pa':91,'U':92,'Np':93,'Pu':94,'Am':95,'Cm':96,'Bk':97,'Cf':98,'Es':99,'Fm':100,
        # extend as needed
    }
    
    def isotope_key(iso):
        # iso like 'C11' or 'H3'
        m = re.match(r'([A-Za-z]+)(\d+)', iso)
        if not m:
            return (999, 999)
        elem = m.group(1)
        mass = int(m.group(2))
        atomnum = periodic_order.get(elem, 999)
        return (atomnum, mass)
    
    isotopes_list = sorted(list(all_isotopes), key=isotope_key)
    times_list = [section['time'] for section in time_sections]
    
    # Create data dictionary: isotope -> {time: activity, half_life: value, half_life_unit: unit}
    data_dict = {}
    for isotope in isotopes_list:
        data_dict[isotope] = {'half_life': 0.0, 'half_life_unit': 's'}
        for section in time_sections:
            # Find this isotope in this time section
            activity = 0.0
            half_life = 0.0
            for iso_data in section['isotopes']:
                if iso_data['isotope'] == isotope:
                    activity = iso_data['activity']
                    half_life = iso_data.get('half_life', 0.0)
                    break
            data_dict[isotope][section['time']] = activity
            if half_life > 0:
                formatted_val, unit = format_half_life(half_life)
                data_dict[isotope]['half_life'] = formatted_val
                data_dict[isotope]['half_life_unit'] = unit
    
    return {
        'times': times_list,
        'isotopes': isotopes_list,
        'data': data_dict,
        'region': found_region or region_number
    }
