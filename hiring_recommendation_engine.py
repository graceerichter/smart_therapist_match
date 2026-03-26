import pandas as pd
import os

# 1. Setup
base_path = os.path.dirname(os.path.abspath(__file__))
matches = pd.read_csv(os.path.join(base_path, 'top_3_therapist_recommendations.csv'))
therapists = pd.read_csv(os.path.join(base_path, 'therapists.csv'))
patients = pd.read_csv(os.path.join(base_path, 'patients.csv'))
MAX_CAPACITY = 25

# 2. Identify High-Risk Gaps
# Find patients with 0 matches (The "Clinical Deserts")
unmatched_ids = matches[matches['Match_1_Score'] == 0]['Patient_ID']
unmatched_data = patients[patients['id'].isin(unmatched_ids)]

# Find "Siloed" Capacity (Providers >90% who are the ONLY option for their patients)
workload = matches['Match_1'].value_counts()
df_util = pd.merge(therapists, workload.rename('load'), left_on='name', right_index=True, how='left').fillna(0)
df_util['utilization'] = (df_util['load'] / MAX_CAPACITY) * 100
critical_providers = df_util[df_util['utilization'] >= 90]['name'].tolist()

# 3. Generate the Recruitment Roadmap
hiring_needs = []

# GAP A: The "Revenue Loss" (Unmatched Patients)
for _, p in unmatched_data.iterrows():
    hiring_needs.append({
        'Priority': '1 - CRITICAL (Unmatched)',
        'State': p['state'],
        'Insurance': p['insurance'],
        'Specialty_Needed': p['needs'],
        'Reason': 'Patient currently has zero clinical/legal match options.'
    })

# GAP B: The "Burnout Protection" (Siloed Overload)
for p_name in critical_providers:
    # Find patients who HAVE a match, but their therapist is full and has no backup
    siloed_matches = matches[(matches['Match_1'] == p_name) & (matches['Match_2_Score'] == 0)]
    
    if not siloed_matches.empty:
        # Get the attributes of the first siloed patient as a sample for the role profile
        sample_p = patients[patients['id'] == siloed_matches.iloc[0]['Patient_ID']].iloc[0]
        hiring_needs.append({
            'Priority': '2 - HIGH (Siloed)',
            'State': sample_p['state'],
            'Insurance': sample_p['insurance'],
            'Specialty_Needed': sample_p['needs'],
            'Reason': f'Backfill needed for {p_name} to prevent burnout/attrition.'
        })

# 4. Export the Actionable Report
recommendations_df = pd.DataFrame(hiring_needs)

# Aggregate and count so we have "Headcount" recommendations
final_report = recommendations_df.groupby(['Priority', 'State', 'Insurance', 'Specialty_Needed', 'Reason']).size().reset_index(name='Patient_Volume')
final_report = final_report.sort_values(by=['Priority', 'Patient_Volume'], ascending=[True, False])

final_report.to_csv(os.path.join(base_path, 'recruitment_hiring_roadmap.csv'), index=False)

print("-" * 30)
print("RECRUITMENT ROADMAP GENERATED")
print("-" * 30)
print(f"Total Priority Hires Identified: {len(final_report)}")
print("File saved: recruitment_hiring_roadmap.csv")