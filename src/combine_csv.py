import os
import pandas as pd

# Folder containing CSV files
grade = 7
levelName = f'G{grade}'

csv_folder = f'csv/{levelName}'

# List to store DataFrames
dataframes = []

fileNumberRange = {
   3: [2, 63],
   4: [2, 105],
   5: [3, 107],
   6: [3, 97],
   7: [3, 101]
}

range_start, range_end = fileNumberRange.get(grade, [0, 0])

# Read each CSV file in the folder
for i in range(range_start, range_end + 1):
    file_path = f'{csv_folder}/G{grade}_{i}.csv'
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        dataframes.append(df)

# Concatenate all DataFrames into a single DataFrame
combined_df = pd.concat(dataframes, ignore_index=True)

# Save the combined DataFrame to a new CSV file
out_path = f'csv/{levelName}/{levelName}_total_output.csv'
combined_df.to_csv(out_path, index=False)

print(f"CSV files combined successfully into {out_path}")
