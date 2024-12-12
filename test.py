import os
import pandas as pd

# Path to the folder containing the Excel files
folder_path = '/home/jp/Desktop/Swat Datasets/D1/'

# Iterate over each file in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.xlsx'):
        file_path = os.path.join(folder_path, file_name)
        try:
            # Read the Excel file
            data = pd.read_excel(file_path)

            # Step 1: Replace 1 with 0
            data = data.replace(1, 0)

            # Step 2: Replace 2 with 1
            data = data.replace(2, 1)

            # Save the updated data back to the same file
            data.to_excel(file_path, index=False)
            print(f"Processed: {file_name}")
        except Exception as e:
            print(f"Error processing {file_name}: {e}")

print("Done processing all files.")
