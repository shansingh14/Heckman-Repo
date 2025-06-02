import pandas as pd

# Read the CSV file
df = pd.read_csv('train_clicks_see0_0.5.csv')

# Keep only the first 4000 rows
df_filtered = df.head(4000)

# Save the filtered data to a new CSV file
df_filtered.to_csv('train_clicks_see0_0.5_subsection.csv', index=False)
