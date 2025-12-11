import re
import time
import pandas as pd
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)
from docling.datamodel.settings import settings
from docling.document_converter import DocumentConverter, PdfFormatOption, WordFormatOption
from docling.pipeline.simple_pipeline import SimplePipeline
from core.settings import TABLE_VALIDATION, STORE_VALIDATION

def load_validation_data(field_type=None):
    """
    Loads validation data from the database with caching.
    
    Args:
        field_type (str, optional): Specific field type to load. If None, loads all.
        
    Returns:
        dict: Dictionary of validation data by field type
    """
    global validation_cache
    
    try:
        # Return cached data if available
        if validation_cache and field_type and field_type in validation_cache:
            return validation_cache[field_type]
        
        if validation_cache and not field_type:
            return validation_cache
        
        # Load data from database
        if field_type:
            data = STORE_VALIDATION.find_one({"standard_variable": field_type})
            if data:
                validation_cache[field_type] = data
                return data
            return None
        else:
            # Load all validation data
            all_data = list(STORE_VALIDATION.find())
            validation_cache = {item.get('standard_variable'): item for item in all_data if item.get('standard_variable')}
            return validation_cache
    except Exception as e:
        return {} if field_type else {}

# Function to get field aliases from validation collections
def get_field_aliases(field_type):
    """
    Get aliases for a specific field type from the validation collections.
    
    Args:
        field_type (str): The type of field to get aliases for (e.g., 'medicine_name', 'doctor_name')
        
    Returns:
        list: List of aliases for the field type
    """
    try:
        # Get validation data from cache or database
        validation_data = load_validation_data(field_type)
        
        if not validation_data:
            return []
        
        # Extract aliases from the validation data
        aliases = validation_data.get("aliases", [])
        return aliases
        
    except Exception as e:
        return []
    

def validate_pattern(value, field_type):
    """
    Validates if a value matches any pattern defined for the given field type.
    
    Args:
        value (str): The value to validate
        field_type (str): The type of field to validate against (e.g., 'doctor_name', 'patient_name')
        
    Returns:
        bool: True if the value matches any pattern, False otherwise
    """
    try:
        # Get the appropriate collection based on field type
        collection = STORE_VALIDATION
        
        # Find the mapping document for this field type
        mapping = collection.find_one({"standard_variable": field_type})
        if not mapping:
            return True  # Default to True if no mapping found
        
        # Get patterns from the mapping
        patterns = mapping.get("patterns", [])
        if not patterns:
            return True  # Default to True if no patterns defined
        
        # Check if the value matches any pattern
        for pattern_dict in patterns:
            try:
                # Extract pattern from dictionary if it's a dict, otherwise use as is
                pattern_str = pattern_dict.get('regex') if isinstance(pattern_dict, dict) else pattern_dict
                if not isinstance(pattern_str, str):
                    continue
                    
                if re.search(pattern_str, value, re.IGNORECASE):
                    return True
            except re.error:
                continue
            except TypeError:
                continue
        
        # Check exclude patterns
        exclude_patterns = mapping.get("exclude_patterns", [])
        for pattern in exclude_patterns:
            if not isinstance(pattern, str):
                continue
                
            try:
                if re.search(pattern, value, re.IGNORECASE):
                    return False  # Value matches an exclude pattern
            except re.error:
                continue
            except TypeError:
                continue
        
        # If we have patterns but none matched, return False
        return False
    except Exception as e:
        return True  # Default to True on error


def extract_store_details(content):
    """
    Extracts store details from the given markdown content using master validation mappings.
    
    This function parses unstructured text to extract structured information about
    patients, doctors, hospitals, and other entities using both database-defined
    patterns and fallback generic patterns.
    
    Args:
        content (str): Markdown content to parse
        
    Returns:
        dict: Dictionary of extracted fields with standardized values
        
    Process flow:
        1. Load field mappings from validation collection
        2. Try pattern matching using database-defined patterns
        3. Fall back to generic patterns for fields that weren't matched
        4. Clean and validate extracted values
        5. Standardize values using master data mappings
    """
    field_mappings = list(STORE_VALIDATION.find())

    # Define standard fields
    standard_fields = {
        'patient_name': '',
        'relationship': '',  # This will be empty by default
        'patient_age': '',
        'doctor_name': '',
        'prescription_id': '',
        'phone_number': '',
        'email': '',
        'address': '',
        'hospital_name': '',
        'pharmacy_name': '',
        'lab_name': ''
    }
    
    # Generic patterns for common fields (fallback patterns)
    generic_patterns = {
        'phone_number': r'(?:Ph(?:one)?[.: ]|(?:#|No)[.: ]|Contact[.: ]*)?(\+?(?:\d[\d\- ]{8,}|\d{10}))',
        'email': r'[\w\.-]+@[\w\.-]+\.\w+',
        'doctor_name': r'(?:dr\.?|doctor|physician)[:\s]+([A-Za-z\s\.]+)(?=[\n,]|$)',
        'patient_name': r'(?:patient|name|pt\.?)[:\s]+([A-Za-z\s]+)(?=[\n,]|$)',
        'patient_age': r'(?:age|yrs?)[:\s](\d+)(?:\s(?:years|yrs?|y)?)',
        'prescription_id': r'(?:prescription|rx|bill|invoice)\s*(?:no|number|id)[:\s]*([A-Za-z0-9-]+)',
        'address': r'(?:address|location|add)[:\s]+([^,\n]+(?:,[^,\n]+)*)',
        'hospital_name': r'(?:hospital|nursing\s+home|medical\s+center)[:\s]+([A-Za-z0-9\s]+)',
        'pharmacy_name': r'(?:pharmacy|chemist|medical|drug\s+store)[:\s]+([A-Za-z0-9\s]+)',
        'lab_name': r'(?:laboratory|lab|diagnostic)[:\s]+([A-Za-z0-9\s]+)'
    }
    
    lines = content.split('\n')
    
    # First try MongoDB patterns
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Try patterns from MongoDB mappings
        for mapping in field_mappings:
            standard_variable = mapping.get('standard_variable')
            if not standard_variable or standard_variable not in standard_fields:
                continue
                
            patterns = mapping.get('patterns', [])
            aliases = mapping.get('aliases', [])
            exclude_patterns = mapping.get('exclude_patterns', [])
            standard_values = mapping.get('standard_values', {})
            # Skip if line matches any exclude pattern
            should_exclude = False
            for exclude_pattern in exclude_patterns:
                try:
                    if re.search(exclude_pattern, line, re.IGNORECASE):
                        should_exclude = True
                        break
                except (re.error, TypeError):
                    continue
            
            if should_exclude:
                continue

            # Try custom pattern matching
            for pattern_dict in patterns:
                try:
                    # Extract pattern from dictionary if it's a dict, otherwise use as is
                    pattern_str = pattern_dict.get('regex') if isinstance(pattern_dict, dict) else pattern_dict
                    if not isinstance(pattern_str, str):
                        continue
                        
                    match = re.search(pattern_str, line, re.IGNORECASE)
                    if match:
                        value = match.group(1).strip() if match.groups() else match.group(0).strip()
                        # Additional validation for specific fields
                        if standard_variable == 'patient_age' and value:
                            try:
                                age = int(''.join(filter(str.isdigit, value)))
                                if 0 <= age <= 150:  # Reasonable age range
                                    standard_fields[standard_variable] = str(age)
                            except ValueError:
                                continue
                        elif standard_variable == 'phone_number' and value:
                            # Clean phone number and validate
                            clean_number = ''.join(filter(str.isdigit, value))
                            if len(clean_number) == 10:  # Standard phone number length
                                standard_fields[standard_variable] = clean_number
                        else:
                            if value and len(value) <= 100:  # Reasonable length check
                                standard_fields[standard_variable] = value
                        break
                except re.error as e:
                    print(f"Invalid regex pattern '{pattern_str}': {e}")
                except TypeError as e:
                    print(f"Type error with pattern for {standard_variable}: {e}")
            
            # Try alias matching if no pattern match
            if not standard_fields[standard_variable]:
                for alias in aliases:
                    if not isinstance(alias, str):
                        continue
                    if alias.lower() in line.lower():
                        if ':' in line:
                            value = line.split(':')[1].strip()
                        else:
                            value = line[line.lower().find(alias.lower()) + len(alias):].strip()
                        if value and len(value) <= 100:  # Reasonable length check
                            standard_fields[standard_variable] = value
                            break
            
            # Standardize values if available
            if standard_fields[standard_variable] and standard_values:
                value = standard_fields[standard_variable]
                standardized = standard_values.get(value.lower(), value)
                if value != standardized:
                    standard_fields[standard_variable] = standardized
    
    # Then try generic patterns for any fields that are still empty
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        for field, pattern in generic_patterns.items():
            if not standard_fields[field]:  # Only try if field is still empty
                try:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        value = match.group(1).strip() if match.groups() else match.group(0).strip()
                        # Additional validation for specific fields
                        if field == 'patient_age' and value:
                            try:
                                age = int(''.join(filter(str.isdigit, value)))
                                if 0 <= age <= 150:  # Reasonable age range
                                    standard_fields[field] = str(age)
                            except ValueError:
                                continue
                        elif field == 'phone_number' and value:
                            # Clean phone number and validate
                            clean_number = ''.join(filter(str.isdigit, value))
                            if len(clean_number) == 10:  # Standard phone number length
                                standard_fields[field] = clean_number
                        else:
                            if value and len(value) <= 100:  # Reasonable length check
                                standard_fields[field] = value
                    
                except Exception as e:
                    return e
    
    # Clean up and validate final values
    for field in standard_fields:
        value = standard_fields[field]
        if value:
            # Remove any unwanted characters or patterns
            value = re.sub(r'[^\w\s@.-]+', ' ', value)  # Keep only alphanumeric, @, ., - and spaces
            value = re.sub(r'\s+', ' ', value).strip()  # Normalize spaces
            if field == 'email' and '@' not in value:
                value = ''  # Clear invalid email
            standard_fields[field] = value
    
    return standard_fields

def parse_markdown_table(content: str):
    """
    Parses a markdown table using master validation mappings.

    Args:
        content (str): Markdown content containing tables

    Returns:
        DataFrame: Pandas DataFrame with standardized column names and validated data
    """

    # Define standard columns at the top so they’re always available
    standard_columns = ['sr_no', 'medicine_name', "dosage", 'manufacturer_name', 'batch_number', 'quantity']

    try:
        #  Fetch column mappings
        column_mappings = list(TABLE_VALIDATION.find({}))
        if not column_mappings:
            raise ValueError("Column validation mappings not found in database")

        # Find table content in markdown
        table_matches = re.findall(r'\|(.*?)\|\n', content, re.MULTILINE)
        if not table_matches:
            return pd.DataFrame(columns=standard_columns)

        # Clean up table matches and remove separator lines
        table_matches = [line.strip() for line in table_matches if line.strip()]
        table_matches = [line for line in table_matches if not re.match(r'^[-:|]+$', line.strip())]

        if not table_matches:
            return pd.DataFrame(columns=standard_columns)

        # Get headers from first row
        headers = [col.strip().lower() for col in table_matches[0].split('|') if col.strip()]

        # Create header mapping using database mappings
        header_mapping = {}
        for mapping in column_mappings:
            standard_column = mapping.get('standard_column')
            if not standard_column or standard_column not in standard_columns:
                continue

            aliases = mapping.get('aliases', [])
            patterns = mapping.get('patterns', [])

            for idx, header in enumerate(headers):
                clean_header = re.sub(r'[^a-zA-Z0-9\s]', '', header).lower().strip()

                # Match alias
                if any(str(alias).lower().strip() == clean_header for alias in aliases):
                    header_mapping[idx] = standard_column
                    break

                # Match regex pattern
                for pattern in patterns:
                    try:
                        pattern_str = pattern.get('regex') if isinstance(pattern, dict) else pattern
                        if re.search(pattern_str, clean_header, re.IGNORECASE):
                            header_mapping[idx] = standard_column
                            break
                    except (re.error, AttributeError) as e:
                        print(f"Invalid pattern in database: {e}")


        # Process data rows
        data_rows = []
        expected_col_count = len(headers)
        for row in table_matches[1:]:  # Skip header row
            cells = [cell.strip() for cell in row.split('|')]
            if len(cells) < expected_col_count:
                cells += [''] * (expected_col_count - len(cells))
            elif len(cells) > expected_col_count:
                cells = cells[:expected_col_count]

            # Remove empty leading/trailing cells
            while cells and cells[0] == '':
                cells.pop(0)
            while cells and cells[-1] == '':
                cells.pop()

            if len(cells) < expected_col_count:
                cells += [''] * (expected_col_count - len(cells))

            if not cells:
                continue

            # Create standardized row
            new_row = {col: '' for col in standard_columns}

            for idx, cell in enumerate(cells):
                if idx in header_mapping:
                    std_col = header_mapping[idx]
                    new_row[std_col] = cell

            # Apply validation rules
            for mapping in column_mappings:
                std_col = mapping.get('standard_column')
                if not std_col or std_col not in new_row:
                    continue

                value = new_row[std_col]
                if not value:
                    continue

                # Validation patterns
                validation_patterns = mapping.get('validation_patterns', [])
                for pattern in validation_patterns:
                    try:
                        pattern_str = pattern.get('regex') if isinstance(pattern, dict) else pattern
                        if pattern_str:
                            match = re.match(pattern_str, value, re.IGNORECASE)
                            if match and match.groups():
                                new_row[std_col] = match.group(1)
                    except (re.error, AttributeError) as e:
                        print(f"Invalid validation pattern in database: {e}")

                # Standardization
                standard_values = mapping.get('standard_values', {})
                if standard_values and isinstance(standard_values, dict):
                    value_lower = value.lower()
                    if value_lower in standard_values:
                        new_row[std_col] = standard_values[value_lower]

            # Special handling for manufacturer/date
            if 'manufacturer_name' in new_row and 'manufactured_date' in new_row:
                mfg_value = new_row.get('manufactured_date', '')
                if mfg_value:
                    is_date = bool(re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', mfg_value))
                    if not is_date and not new_row.get('manufacturer_name'):
                        new_row['manufacturer_name'] = mfg_value
                        new_row['manufactured_date'] = ''
                    elif is_date and new_row.get('manufacturer_name') and not re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', new_row['manufacturer_name']):
                        new_row['manufactured_date'], new_row['manufacturer_name'] = new_row['manufacturer_name'], new_row['manufactured_date']

            data_rows.append(new_row)

        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=standard_columns)
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x).fillna('')

        # Add serial numbers if missing
        if df['sr_no'].isnull().all() or df['sr_no'].eq('').all():
            df['sr_no'] = range(1, len(df) + 1)

        return df

    except Exception as e:
        return pd.DataFrame(columns=standard_columns)

def process_document(file_path: str):
    """
    Perform OCR on a given file, extract markdown text,
    and parse structured tables into a DataFrame.

    Args:
        file_path (str): Path to the document (PDF, image, or DOCX).

    Returns:
        dict: {
            "content": str,        # Extracted OCR text in markdown format
            "table_data": list,    # Structured table rows as list of dicts
            "rows": int,           # Count of extracted rows
            "error": str | None    # Error message if OCR fails
        }
    """
    start_time = time.time()
    result = {"content": "", "table_data": [], "rows": 0, "store_details": {}, "error": None}

    try:
        # Accelerator settings
        accelerator_options = AcceleratorOptions(
            num_threads=8,
            device=AcceleratorDevice.CUDA
        )

        # Pipeline settings
        pipeline_options = PdfPipelineOptions()
        pipeline_options.accelerator_options = accelerator_options
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.do_cell_matching = True

        # Converter
        converter = DocumentConverter(
            allowed_formats=[InputFormat.PDF, InputFormat.IMAGE, InputFormat.DOCX],
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
                InputFormat.DOCX: WordFormatOption(pipeline_cls=SimplePipeline)
            }
        )

        # Run OCR
        conversion_result = converter.convert(file_path)
        extracted_content = conversion_result.document.export_to_markdown()

        # Extract structured data
        df = parse_markdown_table(extracted_content)

        table_data = []
        for row in df.to_dict(orient="records"):
            table_data.append({
                "sr_no": row.get("sr_no"),
                "medicine_name": row.get("medicine_name"),
                "dosage": row.get("dosage"),  # map OCR "quantity" → dosage field
                "frequency": "",  # can’t OCR, keep blank
                "duration": "",
                "method": "",
                "instructions": "",
            })

        # Extract store/patient details
        store_details = extract_store_details(extracted_content)

        elapsed = time.time() - start_time

        result.update({
            "content": extracted_content,
            "table_data": table_data,
            "rows": len(table_data),
            "store_details": store_details
        })

    except Exception as e:
        elapsed = time.time() - start_time
        result["error"] = str(e)

    return result

