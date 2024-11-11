import os
import pandas as pd

# Folder containing CSV files
levelName = 'G3'
csv_folder = f'csv/{levelName}'

# List to store DataFrames
dataframes = []

# Read each CSV file in the folder
for filename in os.listdir(csv_folder):
    if filename.endswith('.csv'):
        file_path = os.path.join(csv_folder, filename)
        df = pd.read_csv(file_path)
        dataframes.append(df)

# Concatenate all DataFrames into a single DataFrame
combined_df = pd.concat(dataframes, ignore_index=True)

# Save the combined DataFrame to a new CSV file
combined_df.to_csv('combined_output.csv', index=False)

print("CSV files combined successfully into 'combined_output.csv'")
