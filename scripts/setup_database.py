"""
Setup SQLite database and load patient records
"""
import sqlite3
import json
import os

def create_database():
    """Create SQLite database with patients table"""
    conn = sqlite3.connect('data/patients.db')
    cursor = conn.cursor()
    
    # Drop existing table
    cursor.execute('DROP TABLE IF EXISTS patients')
    
    # Create patients table
    cursor.execute('''
        CREATE TABLE patients (
            patient_id INTEGER PRIMARY KEY,
            patient_name TEXT NOT NULL,
            date_of_birth TEXT,
            discharge_date TEXT,
            admission_date TEXT,
            primary_diagnosis TEXT,
            secondary_diagnoses TEXT,
            medications TEXT,
            dietary_restrictions TEXT,
            follow_up TEXT,
            warning_signs TEXT,
            discharge_instructions TEXT,
            lab_results TEXT,
            contact_number TEXT,
            emergency_contact TEXT
        )
    ''')
    
    conn.commit()
    print("✅ Database table created successfully")
    return conn

def load_patients(conn):
    """Load patient records from JSON into database"""
    cursor = conn.cursor()
    
    # Load JSON data
    with open('data/patients.json', 'r') as f:
        patients = json.load(f)
    
    # Insert each patient
    for patient in patients:
        cursor.execute('''
            INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            patient['patient_id'],
            patient['patient_name'],
            patient['date_of_birth'],
            patient['discharge_date'],
            patient['admission_date'],
            patient['primary_diagnosis'],
            json.dumps(patient['secondary_diagnoses']),
            json.dumps(patient['medications']),
            patient['dietary_restrictions'],
            patient['follow_up'],
            patient['warning_signs'],
            patient['discharge_instructions'],
            json.dumps(patient['lab_results']),
            patient['contact_number'],
            json.dumps(patient['emergency_contact'])
        ))
    
    conn.commit()
    print(f"✅ Loaded {len(patients)} patient records into database")
    
    # Verify
    cursor.execute('SELECT COUNT(*) FROM patients')
    count = cursor.fetchone()[0]
    print(f"📊 Total patients in database: {count}")
    
    return patients

def test_query(conn):
    """Test database query"""
    cursor = conn.cursor()
    
    # Get a random patient
    cursor.execute('SELECT patient_name, primary_diagnosis FROM patients LIMIT 1')
    result = cursor.fetchone()
    
    print(f"\n🧪 Test Query:")
    print(f"   Patient: {result[0]}")
    print(f"   Diagnosis: {result[1]}")

def main():
    """Main setup function"""
    print("Setting up patient database...\n")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Create and populate database
    conn = create_database()
    load_patients(conn)
    test_query(conn)
    
    conn.close()
    print("\n✅ Database setup complete!")

if __name__ == "__main__":
    main()