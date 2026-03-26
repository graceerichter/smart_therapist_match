import pandas as pd
import os

# 1. Setup
base_path = os.path.dirname(os.path.abspath(__file__))
matches = pd.read_csv(os.path.join(base_path, 'top_3_therapist_recommendations.csv'))
therapists = pd.read_csv(os.path.join(base_path, 'therapists.csv'))
patients = pd.read_csv(os.path.join(base_path, 'patients.csv'))
MAX_CAPACITY = 25

# 2. Identify Overloaded Providers (>80% utilization)
workload = matches['Match_1'].value_counts()
df_strat = pd.merge(therapists, workload.rename('current_load'), left_on='name', right_index=True, how='left').fillna(0)
df_strat['utilization'] = (df_strat['current_load'] / MAX_CAPACITY) * 100
at_risk = df_strat[df_strat['utilization'] >= 80]

# 3. Clinical & Financial Risk Audit
with open(os.path.join(base_path, 'clinical_network_audit.txt'), 'w') as f:
    f.write("=== CLINICAL NETWORK ADEQUACY & RISK AUDIT ===\n")
    f.write("Analyzing Clinical Specialties, Payer Access, and Regulatory Compliance\n\n")

    for _, provider in at_risk.iterrows():
        f.write(f"AT-RISK PROVIDER: {provider['name']} ({provider['utilization']:.0f}% capacity)\n")
        f.write(f"Licenses: {provider['licensed_states']} | Specialties: {provider['specialties']}\n")
        
        # Get patients currently assigned to this provider
        p_list = matches[matches['Match_1'] == provider['name']]
        
        # We'll check the 'Uniqueness' of this provider for each patient they carry
        f.write(f"  Analyzing redundancy for {len(p_list)} active patients...\n")
        
        # Group by State + Insurance + Specialty to find common gaps
        for _, p_match in p_list.iterrows():
            p_data = patients[patients['id'] == p_match['Patient_ID']].iloc[0]
            p_needs = set(str(p_data['needs']).split(', '))
            
            # Find ANY other provider who could legally and clinically see this patient
            # Must match: State AND Insurance AND at least one Specialty
            redundancy = df_strat[
                (df_strat['licensed_states'].str.contains(p_data['state'])) & 
                (df_strat['insurance_accepted'].str.contains(p_data['insurance'])) &
                (df_strat['specialties'].apply(lambda x: any(need in str(x) for need in p_needs))) &
                (df_strat['name'] != provider['name'])
            ]
            
            if redundancy.empty:
                f.write(f"    [!!!] CRITICAL GAP: {p_data['name']} has NO BACKUP options.\n")
                f.write(f"          Reason: {provider['name']} is the ONLY provider for [{p_data['state']} + {p_data['insurance']} + {p_data['needs']}]\n")
            elif len(redundancy) == 1:
                f.write(f"    [!] FRAGILE MATCH: Only one backup exists for {p_data['name']} ({redundancy.iloc[0]['name']}).\n")
        
        f.write("-" * 30 + "\n")

print("Clinical Network Audit generated: clinical_network_audit.txt")