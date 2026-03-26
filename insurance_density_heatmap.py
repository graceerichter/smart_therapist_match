import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# 1. Setup File Paths
base_path = os.path.dirname(os.path.abspath(__file__))
matches_path = os.path.join(base_path, 'top_3_therapist_recommendations.csv')

# Load the matching results
matches = pd.read_csv(matches_path)

# 2. Create the Pivot Table (Provider vs. Insurance)
# This counts how many patients of each insurance type are assigned to each provider
insurance_pivot = matches.groupby(['Match_1', 'Insurance']).size().unstack(fill_value=0)

# 3. Add a 'Total' column to sort by the busiest providers
insurance_pivot['Total_Patients'] = insurance_pivot.sum(axis=1)
insurance_pivot = insurance_pivot.sort_values(by='Total_Patients', ascending=False)

# 4. Create the Visualization
plt.figure(figsize=(12, 10))

# Plot the insurance types (dropping the Total column for the actual heatmap)
sns.heatmap(insurance_pivot.drop(columns='Total_Patients'), 
            annot=True, 
            cmap='PuBuGn', # Purple-Blue-Green palette
            fmt='g', 
            cbar_kws={'label': 'Patient Count'})

plt.title('Insurance Density: Patient Volume per Payer & Provider', fontsize=16, pad=20)
plt.ylabel('Provider Name', fontsize=12)
plt.xlabel('Insurance Provider (Payer)', fontsize=12)

# 5. Save the visual
plt.tight_layout()
plt.savefig(os.path.join(base_path, 'insurance_density_heatmap.png'))

print("-" * 30)
print("INSURANCE DENSITY HEATMAP COMPLETE")
print("-" * 30)
print("File saved as: insurance_density_heatmap.png")