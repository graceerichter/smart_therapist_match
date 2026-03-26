import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# 1. Setup File Paths
base_path = os.path.dirname(os.path.abspath(__file__))
matches_path = os.path.join(base_path, 'top_3_therapist_recommendations.csv')

# Load the matching results
matches = pd.read_csv(matches_path)

# 2. Create a Pivot Table (Therapist vs. State)
# This counts how many patients from each state are assigned to each therapist
pivot_data = matches.groupby(['Match_1', 'State']).size().unstack(fill_value=0)

# 3. Add a 'Total Load' column and sort so the busiest therapists are at the top
pivot_data['Total_Load'] = pivot_data.sum(axis=1)
pivot_data = pivot_data.sort_values(by='Total_Load', ascending=False)

# 4. Create the Visualization
plt.figure(figsize=(12, 14))

# We'll plot the states, but keep 'Total_Load' as a reference for sorting
# Using 'YlOrRd' (Yellow-Orange-Red) to highlight the high-volume cells
sns.heatmap(pivot_data.drop(columns='Total_Load'), 
            annot=True, 
            cmap='YlOrRd', 
            fmt='g', 
            cbar_kws={'label': 'Number of Assigned Patients'})

plt.title('Network Distribution: Patient Load per State & Provider', fontsize=16, pad=20)
plt.ylabel('Provider Name', fontsize=12)
plt.xlabel('Patient Location (State)', fontsize=12)

# 5. Save the new visual
plt.tight_layout()
plt.savefig(os.path.join(base_path, 'provider_distribution_heatmap.png'))

print("-" * 30)
print("DISTRIBUTION HEATMAP COMPLETE")
print("-" * 30)
print("File saved as: provider_distribution_heatmap.png")