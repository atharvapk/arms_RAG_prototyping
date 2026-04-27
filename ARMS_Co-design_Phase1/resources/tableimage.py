import pdfplumber
import re
import sqlite3

def extract_and_transform_to_sql_ready(pdf_path, standard_val="ANSI", fit_type_val="Clearance"):
    # Our blueprint maps to the 5 data columns (indices 1 through 5)
    blueprint = [
        {"category": "Loose Running", "hole_class": "C11", "shaft_class": "h11", "col_index": 1},
        {"category": "Free Running", "hole_class": "D9", "shaft_class": "h9", "col_index": 2},
        {"category": "Close Running", "hole_class": "F8", "shaft_class": "h7", "col_index": 3},
        {"category": "Sliding", "hole_class": "G7", "shaft_class": "h6", "col_index": 4},
        {"category": "Locational Clearance", "hole_class": "H7", "shaft_class": "h6", "col_index": 5}
    ]
    
    sql_ready_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0] 
        tables = page.extract_tables()
        
        if not tables:
            return []
            
        raw_table = tables[0]
        
        for row in raw_table:
            if not row or not row[0]:
                continue
            
            col_0_str = str(row[0])
            
            if 'Max' in col_0_str and 'Min' in col_0_str:
                
                basic_size_raw = re.split(r'\s+', col_0_str)[0]
                
                try:
                    basic_size = float(basic_size_raw.replace(',', '.'))
                except ValueError:
                    continue 
                
                for fit in blueprint:
                    col_idx = fit["col_index"]
                    cell_content = row[col_idx]
                    
                    if not cell_content:
                        continue
                        
                    lines = str(cell_content).strip().split('\n')
                    if len(lines) != 2:
                        continue 
                        
                    max_vals = lines[0].split()
                    min_vals = lines[1].split()
                    
                    if len(max_vals) >= 3 and len(min_vals) >= 3:
                        try:
                            record = {
                                "standard": standard_val,
                                "fit_type": fit_type_val,
                                "basic_size": basic_size,
                                "fit_category": fit["category"],
                                "hole_class": fit["hole_class"],
                                "shaft_class": fit["shaft_class"],
                                "hole_max": float(max_vals[0].replace(',', '.')),
                                "shaft_max": float(max_vals[1].replace(',', '.')),
                                "fit_max": float(max_vals[2].replace(',', '.')),
                                "hole_min": float(min_vals[0].replace(',', '.')),
                                "shaft_min": float(min_vals[1].replace(',', '.')),
                                "fit_min": float(min_vals[2].replace(',', '.'))
                            }
                            sql_ready_data.append(record)
                        except ValueError:
                            pass
                            
    return sql_ready_data

def load_data_to_sqlite(data, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS engineering_fits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            standard TEXT,
            fit_type TEXT,
            basic_size REAL,
            fit_category TEXT,
            hole_class TEXT,
            shaft_class TEXT,
            hole_max REAL,
            shaft_max REAL,
            fit_max REAL,
            hole_min REAL,
            shaft_min REAL,
            fit_min REAL
        )
    ''')
    
    insert_query = '''
        INSERT INTO engineering_fits (
            standard, fit_type, basic_size, fit_category, hole_class, shaft_class, 
            hole_max, shaft_max, fit_max, hole_min, shaft_min, fit_min
        ) VALUES (
            :standard, :fit_type, :basic_size, :fit_category, :hole_class, :shaft_class, 
            :hole_max, :shaft_max, :fit_max, :hole_min, :shaft_min, :fit_min
        )
    '''
    
    cursor.executemany(insert_query, data)
    
    conn.commit()
    conn.close()
    
    print(f"Successfully loaded {len(data)} records into '{db_name}'.")

if __name__ == "__main__":
    pdf_file = "1.pdf" 
    
    # CHANGE THESE VARIABLES for each run:
    db_file_name = "engineering_standards.db" 
    manual_standard = "ANSI"
    manual_fit_type = "Clearance"
    
    clean_data = extract_and_transform_to_sql_ready(
        pdf_path=pdf_file, 
        standard_val=manual_standard, 
        fit_type_val=manual_fit_type
    )
    
    if clean_data:
        load_data_to_sqlite(clean_data, db_file_name)
    else:
        print("No data was extracted from the PDF.")