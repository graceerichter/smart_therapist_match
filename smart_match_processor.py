import pandas as pd
import os

# 1. Setup File Paths (Ensures it runs correctly on your Mac)
base_path = os.path.dirname(os.path.abspath(__file__))
therapists_path = os.path.join(base_path, 'therapists.csv')
patients_path = os.path.join(base_path, 'patients.csv')

# Load the Enterprise Datasets
therapists = pd.read_csv(therapists_path)
patients = pd.read_csv(patients_path)

def calculate_match_score(patient, therapist):
    """
    Logic: Hard constraints (State/Insurance) must be met first.
    Soft constraints (Specialties/Time) determine the ranking score.
    """
    # REGULATORY COMPLIANCE: State Licensing (Hard Requirement)
    if patient['state'] not in str(therapist['licensed_states']):
        return 0 
        
    # FINANCIAL ACCESS: Insurance (Hard Requirement)
    if patient['insurance'] not in str(therapist['insurance_accepted']):
        return 0 
    
    score = 0
    
    # CLINICAL FIT: Specialty Matching (+5 points per match)
    p_needs = set(str(patient['needs']).split(', '))
    t_specs = set(str(therapist['specialties']).split(', '))
    match_count = len(p_needs.intersection(t_specs))
    score += (match_count * 5)
    
    # CONVENIENCE: Time Preference (+3 points)
    if patient['pref_time'] in str(therapist['available_slots']):
        score += 3
        
    return score

# 2. Process all 500 Patients
print("Running Smart-Match Optimization Engine...")
final_results = []

for _, patient in patients.iterrows():
    scored_therapists = []
    
    for _, therapist in therapists.iterrows():
        match_score = calculate_match_score(patient, therapist)
        
        if match_score > 0:
            scored_therapists.append({
                'Provider': therapist['name'],
                'Score': match_score
            })
    
    # Sort therapists by highest score
    sorted_matches = sorted(scored_therapists, key=lambda x: x['Score'], reverse=True)
    
    # Format the output row
    entry = {
        'Patient_ID': patient['id'],
        'Patient_Name': patient['name'],
        'State': patient['state'],
        'Insurance': patient['insurance']
    }
    
    # Assign Top 3 Recommendations
    for i in range(3):
        if i < len(sorted_matches):
            entry[f'Match_{i+1}'] = sorted_matches[i]['Provider']
            entry[f'Match_{i+1}_Score'] = sorted_matches[i]['Score']
        else:
            entry[f'Match_{i+1}'] = "No Eligible Match"
            entry[f'Match_{i+1}_Score'] = 0
            
    final_results.append(entry)

# 3. Export to CSV
output_df = pd.DataFrame(final_results)
output_df.to_csv(os.path.join(base_path, 'top_3_therapist_recommendations.csv'), index=False)

# 4. Operational Dashboard Summary
unmatched = output_df[output_df['Match_1_Score'] == 0]
match_rate = ((len(patients) - len(unmatched)) / len(patients)) * 100

print("-" * 30)
print("SUCCESS: MATCHING COMPLETE")
print("-" * 30)
print(f"Total Patients Processed: {len(patients)}")
print(f"Successful Match Rate:    {match_rate:.1f}%")
print(f"Unmatched Patients:       {len(unmatched)} (Requires Network Expansion)")
print("-" * 30)
print("File exported: top_3_therapist_recommendations.csv")