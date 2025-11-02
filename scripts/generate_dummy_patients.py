"""
Generate 25+ dummy patient discharge reports for nephrology patients
"""
import json
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# Nephrology-specific data
DIAGNOSES = [
    "Chronic Kidney Disease Stage 3",
    "Chronic Kidney Disease Stage 4",
    "Acute Kidney Injury",
    "End-Stage Renal Disease",
    "Glomerulonephritis",
    "Diabetic Nephropathy",
    "Hypertensive Nephropathy",
    "Polycystic Kidney Disease",
    "Nephrotic Syndrome",
    "IgA Nephropathy"
]

MEDICATIONS = [
    ["Lisinopril 10mg daily", "Furosemide 20mg twice daily"],
    ["Amlodipine 5mg daily", "Sodium bicarbonate 650mg three times daily"],
    ["Losartan 50mg daily", "Calcitriol 0.25mcg daily"],
    ["Carvedilol 12.5mg twice daily", "Sevelamer 800mg with meals"],
    ["Enalapril 10mg daily", "Erythropoietin 4000 units weekly"],
    ["Spironolactone 25mg daily", "Iron supplement 325mg daily"],
    ["Ramipril 5mg daily", "Vitamin D3 2000 units daily"],
]

DIETARY_RESTRICTIONS = [
    "Low sodium (2g/day), fluid restriction (1.5L/day)",
    "Low potassium diet, limit phosphorus intake",
    "Protein restriction (0.8g/kg/day), low sodium",
    "Diabetic diet, low sodium (2g/day)",
    "Fluid restriction (1L/day), avoid high-potassium foods",
    "Low protein diet, restrict phosphorus-rich foods"
]

WARNING_SIGNS = [
    "Swelling, shortness of breath, decreased urine output",
    "Chest pain, severe headache, confusion",
    "Nausea, vomiting, extreme fatigue",
    "Blood in urine, severe back pain, fever",
    "Rapid weight gain, difficulty breathing, irregular heartbeat",
    "Severe itching, muscle cramps, loss of appetite"
]

DISCHARGE_INSTRUCTIONS = [
    "Monitor blood pressure daily, weigh yourself daily",
    "Check blood glucose twice daily, track fluid intake",
    "Record daily weight, limit salt intake strictly",
    "Take medications as prescribed, avoid NSAIDs",
    "Follow dialysis schedule, maintain vascular access site",
    "Monitor for signs of infection, keep follow-up appointments"
]

def generate_patient():
    """Generate a single patient record"""
    discharge_date = fake.date_between(start_date='-90d', end_date='today')
    
    patient = {
        "patient_id": fake.unique.random_int(min=1000, max=9999),
        "patient_name": fake.name(),
        "date_of_birth": fake.date_of_birth(minimum_age=30, maximum_age=85).strftime("%Y-%m-%d"),
        "discharge_date": discharge_date.strftime("%Y-%m-%d"),
        "admission_date": (discharge_date - timedelta(days=random.randint(3, 14))).strftime("%Y-%m-%d"),
        "primary_diagnosis": random.choice(DIAGNOSES),
        "secondary_diagnoses": random.sample([
            "Type 2 Diabetes", 
            "Hypertension", 
            "Anemia", 
            "Hyperkalemia",
            "Metabolic acidosis",
            "Secondary hyperparathyroidism"
        ], k=random.randint(1, 3)),
        "medications": random.choice(MEDICATIONS),
        "dietary_restrictions": random.choice(DIETARY_RESTRICTIONS),
        "follow_up": f"Nephrology clinic in {random.choice([1, 2, 3, 4])} weeks",
        "warning_signs": random.choice(WARNING_SIGNS),
        "discharge_instructions": random.choice(DISCHARGE_INSTRUCTIONS),
        "lab_results": {
            "creatinine_mg_dl": round(random.uniform(1.5, 6.5), 2),
            "egfr_ml_min": random.randint(15, 55),
            "potassium_meq_l": round(random.uniform(3.5, 5.8), 1),
            "hemoglobin_g_dl": round(random.uniform(8.5, 12.5), 1)
        },
        "contact_number": fake.phone_number(),
        "emergency_contact": {
            "name": fake.name(),
            "relationship": random.choice(["Spouse", "Son", "Daughter", "Sibling"]),
            "phone": fake.phone_number()
        }
    }
    return patient

def main():
    """Generate 30 patient records and save to JSON"""
    print("Generating 30 dummy patient records...")
    
    patients = []
    for i in range(30):
        patient = generate_patient()
        patients.append(patient)
        print(f"Generated patient {i+1}: {patient['patient_name']}")
    
    # Save to JSON
    output_file = "data/patients.json"
    with open(output_file, "w") as f:
        json.dump(patients, f, indent=2)
    
    print(f"\n✅ Successfully generated {len(patients)} patient records")
    print(f"📁 Saved to: {output_file}")
    
    # Print sample
    print("\n📋 Sample Patient Record:")
    print(json.dumps(patients[0], indent=2))

if __name__ == "__main__":
    main()