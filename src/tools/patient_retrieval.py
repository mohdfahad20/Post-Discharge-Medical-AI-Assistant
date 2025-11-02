"""
Patient Data Retrieval Tool for Database Interaction
"""
import sqlite3
import json
from typing import Optional, Dict, List
from datetime import datetime

class PatientRetrievalTool:
    def __init__(self, db_path: str = "data/patients.db"):
        self.db_path = db_path
        self.log_entries = []
    
    def _log(self, action: str, input_data: str, output: any, success: bool):
        """Internal logging method"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": "patient_retrieval",
            "action": action,
            "input": input_data,
            "output": str(output)[:200],  # Truncate for logging
            "success": success
        }
        self.log_entries.append(log_entry)
    
    def get_patient_by_name(self, patient_name: str) -> Optional[Dict]:
        """
        Retrieve patient discharge report by name
        
        Args:
            patient_name: Full or partial patient name
            
        Returns:
            Patient data dict or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            # Case-insensitive search
            cursor.execute('''
                SELECT * FROM patients 
                WHERE LOWER(patient_name) LIKE LOWER(?)
            ''', (f'%{patient_name}%',))
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                self._log("get_patient_by_name", patient_name, "No patient found", False)
                return None
            
            if len(results) > 1:
                # Multiple patients with similar names
                patient_list = [dict(row)['patient_name'] for row in results]
                self._log("get_patient_by_name", patient_name, 
                         f"Multiple patients found: {patient_list}", False)
                return {
                    "error": "multiple_patients",
                    "message": f"Found {len(results)} patients with similar names. Please be more specific.",
                    "patients": patient_list
                }
            
            # Single patient found - convert to dict
            patient = dict(results[0])
            
            # Parse JSON fields
            patient['secondary_diagnoses'] = json.loads(patient['secondary_diagnoses'])
            patient['medications'] = json.loads(patient['medications'])
            patient['lab_results'] = json.loads(patient['lab_results'])
            patient['emergency_contact'] = json.loads(patient['emergency_contact'])
            
            self._log("get_patient_by_name", patient_name, f"Found: {patient['patient_name']}", True)
            return patient
            
        except Exception as e:
            self._log("get_patient_by_name", patient_name, f"Error: {str(e)}", False)
            return {
                "error": "database_error",
                "message": f"Failed to retrieve patient data: {str(e)}"
            }
    
    def get_all_patient_names(self) -> List[str]:
        """Get list of all patient names for reference"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT patient_name FROM patients ORDER BY patient_name')
            names = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            self._log("get_all_patient_names", "", f"Retrieved {len(names)} names", True)
            return names
            
        except Exception as e:
            self._log("get_all_patient_names", "", f"Error: {str(e)}", False)
            return []
    
    def format_patient_summary(self, patient: Dict) -> str:
        """
        Format patient data into readable summary for agent
        """
        if "error" in patient:
            return patient["message"]
        
        summary = f"""
Patient: {patient['patient_name']}
DOB: {patient['date_of_birth']}
Discharge Date: {patient['discharge_date']}

PRIMARY DIAGNOSIS: {patient['primary_diagnosis']}
Secondary Conditions: {', '.join(patient['secondary_diagnoses'])}

MEDICATIONS:
{chr(10).join(f"  • {med}" for med in patient['medications'])}

DIETARY RESTRICTIONS: {patient['dietary_restrictions']}

FOLLOW-UP: {patient['follow_up']}

WARNING SIGNS TO WATCH FOR:
{patient['warning_signs']}

DISCHARGE INSTRUCTIONS:
{patient['discharge_instructions']}

LAB RESULTS:
  • Creatinine: {patient['lab_results']['creatinine_mg_dl']} mg/dL
  • eGFR: {patient['lab_results']['egfr_ml_min']} mL/min
  • Potassium: {patient['lab_results']['potassium_meq_l']} mEq/L
  • Hemoglobin: {patient['lab_results']['hemoglobin_g_dl']} g/dL
"""
        return summary.strip()
    
    def get_logs(self) -> List[Dict]:
        """Return all logged interactions"""
        return self.log_entries


# LangChain Tool Wrapper
def create_langchain_tool():
    """
    Create LangChain-compatible tool for patient retrieval
    """
    from langchain.tools import Tool
    
    retrieval_tool = PatientRetrievalTool()
    
    def fetch_patient(patient_name: str) -> str:
        """Fetch patient discharge report by name"""
        patient = retrieval_tool.get_patient_by_name(patient_name)
        if patient:
            return retrieval_tool.format_patient_summary(patient)
        return f"No patient found with name: {patient_name}"
    
    tool = Tool(
        name="fetch_patient_data",
        description=(
            "Retrieves a patient's discharge report from the database by their name. "
            "Use this when the patient tells you their name. "
            "Input should be the patient's full or partial name. "
            "Returns complete discharge information including diagnosis, medications, "
            "dietary restrictions, and follow-up instructions."
        ),
        func=fetch_patient
    )
    
    return tool, retrieval_tool


# Test the tool
if __name__ == "__main__":
    tool = PatientRetrievalTool()
    
    # Get all patient names for testing
    names = tool.get_all_patient_names()
    print(f"Total patients in database: {len(names)}")
    print(f"\nFirst 5 patients:")
    for name in names[:5]:
        print(f"  - {name}")
    
    # Test retrieval with first patient
    if names:
        print(f"\n{'='*60}")
        print(f"Testing retrieval for: {names[0]}")
        print('='*60)
        patient = tool.get_patient_by_name(names[0])
        if patient:
            print(tool.format_patient_summary(patient))
        
        print(f"\n{'='*60}")
        print("Logs:")
        print('='*60)
        for log in tool.get_logs():
            print(f"{log['timestamp']} - {log['action']}: {log['success']}")