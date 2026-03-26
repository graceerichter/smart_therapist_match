import pandas as pd
import os

# 1. Setup
base_path = os.path.dirname(os.path.abspath(__file__))
matches = pd.read_csv(os.path.join(base_path, 'top_3_therapist_recommendations.csv'))
patients = pd.read_csv(os.path.join(base_path, 'patients.csv'))

# 2. Identify Every "Single Point of Failure" (SPF)
# Logic: If Match_2 is "No Eligible Match", the network has ZERO redundancy for this patient.
spf_matches = matches[matches['Match_2'] == "No Eligible Match"].copy()

# 3. Categorize the Gaps
# We split them into "Critical" (No Match at all) and "Fragile" (Only 1 Match)
spf_matches['Risk_Level'] = spf_matches['Match_1'].apply(
    lambda x: 'CRITICAL: Zero Matches' if x == "No Eligible Match" else 'FRAGILE: Single Match Only'
)

# 4. Merge with Patient Needs to get the "Hiring Profile"
# This tells us exactly what specialty/insurance/state we are missing backups for
gap_analysis = pd.merge(
    spf_matches[['Patient_ID', 'Risk_Level', 'Match_1']], 
    patients[['id', 'state', 'insurance', 'needs']], 
    left_on='Patient_ID', 
    right_on='id'
)

# 5. Aggregate into a Strategic Recruitment Plan
# We group by the specific requirements so we can say "We need 5 therapists for this specific profile"
recruitment_plan = gap_analysis.groupby(['Risk_Level', 'state', 'insurance', 'needs']).size().reset_index(name='Patient_Volume')

# Sort: Critical first, then by the volume of patients affected
recruitment_plan = recruitment_plan.sort_values(by=['Risk_Level', 'Patient_Volume'], ascending=[True, False])

# 6. Export the Strategic Roadmap
recruitment_plan.to_csv(os.path.join(base_path, 'strategic_recruitment_roadmap.csv'), index=False)

print("-" * 30)
print("NETWORK RESILIENCY AUDIT COMPLETE")
print("-" * 30)
print(f"Total 'Single Point of Failure' Patients: {len(gap_analysis)}")
print(f"Strategic Hires Identified: {len(recruitment_plan)}")
print("File saved: strategic_recruitment_roadmap.csv")