import pandas as pd
import os

# 1. Setup File Paths
base_path = os.path.dirname(os.path.abspath(__file__))
matches_path = os.path.join(base_path, 'top_3_therapist_recommendations.csv')
therapists_path = os.path.join(base_path, 'therapists.csv')
patients_path = os.path.join(base_path, 'patients.csv')

# Load Datasets
matches = pd.read_csv(matches_path)
therapists = pd.read_csv(therapists_path)
patients = pd.read_csv(patients_path)

# 2. Operational Parameters
MAX_CAPACITY = 25
WARNING_THRESHOLD = 80   # Trigger: Start recruitment pipeline
CRITICAL_THRESHOLD = 90  # Trigger: Halt new intakes for this provider
BURNOUT_THRESHOLD = 100  # Trigger: Immediate workload shift required

# 3. Calculate Real-Time Utilization
workload = matches['Match_1'].value_counts()
df_strat = pd.merge(therapists, workload.rename('current_load'), left_on='name', right_index=True, how='left').fillna(0)
df_strat['utilization'] = (df_strat['current_load'] / MAX_CAPACITY) * 100

# 4. Generate the Strategic Report
report_file = os.path.join(base_path, 'operational_strategy_report.txt')

with open(report_file, 'w') as f:
    f.write("====================================================\n")
    f.write("      CLINICAL OPERATIONS: STRATEGIC CAPACITY REPORT \n")
    f.write("====================================================\n\n")

    # SECTION 1: PROACTIVE RECRUITMENT & BURNOUT ALERTS
    f.write("--- [PHASE 1] PROVIDER CAPACITY ALERTS ---\n")
    
    # Sort by utilization so most urgent is at the top
    df_strat = df_strat.sort_values(by='utilization', ascending=False)

    for _, row in df_strat.iterrows():
        status_label = ""
        action_plan = ""
        
        if row['utilization'] >= BURNOUT_THRESHOLD:
            status_label = "!!! BURNOUT (EMERGENCY) !!!"
            action_plan = "IMMEDIATE ACTION: Stop all intake and redirect 5+ existing patients."
        elif row['utilization'] >= CRITICAL_THRESHOLD:
            status_label = "!!! CRITICAL (CAPACITY FULL) !!!"
            action_plan = "ACTION: Halt new matching. High priority for regional hiring."
        elif row['utilization'] >= WARNING_THRESHOLD:
            status_label = "--- WARNING (GROWTH LIMIT) ---"
            action_plan = "ACTION: Initiate 90-day recruitment cycle for this license/specialty."
        
        if status_label:
            f.write(f"{status_label}\n")
            f.write(f"Provider: {row['name']} | Utilization: {row['utilization']:.0f}%\n")
            f.write(f"Location: {row['licensed_states']}\n")
            f.write(f"{action_plan}\n")
            
            # --- SMART REDIRECT LOGIC ---
            # If they are over 90%, look for valid "Load Balancers"
            if row['utilization'] >= CRITICAL_THRESHOLD:
                # Find patients assigned to this provider
                assigned = matches[matches['Match_1'] == row['name']].head(3)
                for _, p_match in assigned.iterrows():
                    p_data = patients[patients['id'] == p_match['Patient_ID']].iloc[0]
                    p_needs = set(str(p_data['needs']).split(', '))
                    
                    # Search for Valid Alt: Correct State + Correct Specialty + Under Warning Threshold
                    alts = df_strat[
                        (df_strat['licensed_states'].str.contains(p_data['state'])) & 
                        (df_strat['specialties'].apply(lambda x: any(need in str(x) for need in p_needs))) &
                        (df_strat['utilization'] < WARNING_THRESHOLD) &
                        (df_strat['name'] != row['name'])
                    ]
                    
                    if not alts.empty:
                        best_alt = alts.iloc[0]['name']
                        f.write(f"  -> VALID REDIRECT: Move {p_data['name']} to {best_alt}\n")
                    else:
                        f.write(f"  -> GAP IDENTIFIED: No valid alternatives for {p_data['name']} ({p_data['state']}).\n")
            f.write("-" * 20 + "\n")

    # SECTION 2: CLINICAL DESERT ANALYSIS (RECRUITMENT PRIORITIES)
    f.write("\n--- [PHASE 2] CLINICAL DESERT & NETWORK GAPS ---\n")
    unmatched_ids = matches[matches['Match_1_Score'] == 0]['Patient_ID']
    unmatched_data = patients[patients['id'].isin(unmatched_ids)]
    
    if not unmatched_data.empty:
        # Group by state and needs to find the biggest "Clinical Deserts"
        gaps = unmatched_data.groupby(['state', 'needs']).size().sort_values(ascending=False).head(5)
        f.write("The following specific markets require immediate Provider Recruitment:\n")
        for (state, need), count in gaps.items():
            f.write(f"  * PRIORITY 1: {state} | Specialty: {need} ({count} patients on waitlist)\n")
    else:
        f.write("No patient waitlists identified. Network is currently balanced.\n")

    # SECTION 3: SYSTEM HEALTH METRICS
    f.write("\n--- [PHASE 3] EXECUTIVE SUMMARY ---\n")
    f.write(f"Average Network Utilization: {df_strat['utilization'].mean():.1f}%\n")
    f.write(f"Total Patients Unmatched: {len(unmatched_data)}\n")
    f.write(f"Providers Flagged for Recruitment (80%+): {len(df_strat[df_strat['utilization'] >= 80])}\n")

print(f"Strategic Report generated: {report_file}")