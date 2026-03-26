import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. Setup
base_path = os.path.dirname(os.path.abspath(__file__))
therapists = pd.read_csv(os.path.join(base_path, 'therapists.csv'))
patients = pd.read_csv(os.path.join(base_path, 'patients.csv'))

# 2. Extract and Count Specialties (Supply)
# Since specialties are comma-separated strings, we need to flatten them
t_specs = therapists['specialties'].str.split(', ').explode().value_counts()
t_percent = (t_specs / t_specs.sum()) * 100

# 3. Extract and Count Patient Needs (Demand)
p_needs = patients['needs'].str.split(', ').explode().value_counts()
p_percent = (p_needs / p_needs.sum()) * 100

# 4. Combine into a Comparison DataFrame
df_gap = pd.DataFrame({
    'Clinical Demand (%)': p_percent,
    'Provider Supply (%)': t_percent
}).fillna(0).reset_index()

df_gap.columns = ['Specialty', 'Demand', 'Supply']
df_gap = df_gap.sort_values(by='Demand', ascending=False)

# 5. Melt the data for Seaborn (Long format)
df_plot = df_gap.melt(id_vars='Specialty', var_name='Type', value_name='Percentage')

# 6. Create the Visualization
plt.figure(figsize=(12, 8))
sns.set_style("whitegrid")

ax = sns.barplot(data=df_plot, x='Specialty', y='Percentage', hue='Type', palette=['#E74C3C', '#2ECC71'])

plt.title('Clinical Gap Analysis: Patient Needs vs. Provider Specialties', fontsize=16, pad=20)
plt.ylabel('Percentage of Total Population (%)', fontsize=12)
plt.xlabel('Clinical Specialty', fontsize=12)
plt.xticks(rotation=45)

# Add a "Hiring Priority" label to gaps larger than 5%
for i, row in df_gap.iterrows():
    if row['Demand'] > row['Supply'] + 5:
        plt.text(i, row['Demand'] + 1, 'HIRING NEED', color='red', 
                 ha='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(base_path, 'clinical_gap_analysis.png'))

print("-" * 30)
print("GAP ANALYSIS COMPLETE")
print("-" * 30)
print("Visual saved as: clinical_gap_analysis.png")
