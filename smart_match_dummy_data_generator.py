import pandas as pd
import random

# 1. Setup Enterprise Constants
SPECIALTIES = [
    'CBT', 'DBT', 'Trauma', 'LGBTQ+', 'Anxiety', 
    'Depression', 'Family Therapy', 'Eating Disorders'
]
INSURANCE = ['Aetna', 'Blue Shield', 'Kaiser', 'UnitedHealthcare', 'Cigna']
TIMES = ['Morning', 'Afternoon', 'Evening']
STATES = ['CA', 'OR', 'WA', 'AZ', 'NV']  # West Coast focus

# 2. Generate 25 Therapists
therapist_data = []
for i in range(25):
    t_id = f"T-{100+i}"
    name = f"Provider {i+1}"
    
    # Randomly assign 2-4 specialties
    specs = ", ".join(random.sample(SPECIALTIES, random.randint(2, 4)))
    
    # Randomly assign 2-4 insurance providers
    ins = random.sample(INSURANCE, random.randint(2, 4))
    
    # Randomly assign 1-3 availability slots
    avail = ", ".join(random.sample(TIMES, random.randint(1, 3)))
    
    # COMPLIANCE: Randomly assign 1-3 state licenses
    licensed = random.sample(STATES, random.randint(1, 3))
    
    # The "Superstar" Provider (QA Lead)
    if i == 0:
        name = "Dr. Belle Richter, PsyD"
        specs = "Anxiety, Stress Management, Specialized Cuddling"
        licensed = STATES  # Licensed in all 5 states
    
    therapist_data.append([
        t_id, name, specs, ", ".join(ins), avail, ", ".join(licensed)
    ])

therapists_df = pd.DataFrame(therapist_data, columns=[
    'id', 'name', 'specialties', 'insurance_accepted', 'available_slots', 'licensed_states'
])
therapists_df.to_csv('therapists.csv', index=False)

# 3. Generate 500 Patients (The 20:1 Caseload Ratio)
patient_data = []
for i in range(500):
    p_id = f"P-{1000+i}"
    name = f"Client {i+1}"
    
    # Patient usually has 1-2 specific clinical needs
    needs = ", ".join(random.sample(SPECIALTIES, random.randint(1, 2)))
    
    # Patient has 1 insurance provider
    ins = random.choice(INSURANCE)
    
    # Patient has 1 preferred time
    pref = random.choice(TIMES)
    
    # COMPLIANCE: Patient is located in exactly 1 state
    loc = random.choice(STATES)
    
    patient_data.append([p_id, name, needs, ins, pref, loc])

patients_df = pd.DataFrame(patient_data, columns=[
    'id', 'name', 'needs', 'insurance', 'pref_time', 'state'
])
patients_df.to_csv('patients.csv', index=False)

print("-" * 30)
print("ENTERPRISE DATA GENERATION COMPLETE")
print("-" * 30)
print(f"Therapists: {len(therapists_df)} (Licensed across {', '.join(STATES)})")
print(f"Patients:   {len(patients_df)}")
print(f"Ratio:      {len(patients_df)/len(therapists_df):.0f}:1 (Target Caseload)")
print("-" * 30)
print("Files saved: therapists.csv, patients.csv")