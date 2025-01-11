import pandas as pd

# Read the CSV files
csv1 = pd.read_csv('/home/nikhil/sitare /others/NYD_Hackathon/ancient-wisdom-rag/data/Bhagwad_Gita_Verses_English_Questions.csv')  # CSV with chapter, verse, speaker, sanskrit, translation, question
csv2 = pd.read_csv('/home/nikhil/sitare /others/NYD_Hackathon/ancient-wisdom-rag/data/s.csv')  # CSV with Chapter, verse, explanation

# Merge the dataframes based on 'chapter' and 'verse' columns
merged_df = pd.merge(csv1[['chapter', 'verse', 'sanskrit', 'translation']], 
                     csv2[['Chapter', 'verse', 'explanation']], 
                     left_on=['chapter', 'verse'], 
                     right_on=['Chapter', 'verse'], 
                     how='left')

# Drop the 'Chapter' column (from the second CSV) as it's redundant
merged_df = merged_df.drop(columns=['Chapter'])

# Save the merged data into a new CSV file
merged_df.to_csv('merged_gita.csv', index=False)

print("Merged CSV file created successfully.")
























# import pandas as pd

# # Load the two CSV files
# file1 = '/home/nikhil/sitare /others/NYD_Hackathon/ancient-wisdom-rag/data/Patanjali_Yoga_Sutras_Verses_English_Questions.csv'  # Replace with the path to your first CSV file
# file2 = '/home/nikhil/sitare /others/NYD_Hackathon/patanjali_sutra_final.csv'  # Replace with the path to your second CSV file

# # Read the CSV files into DataFrames
# df1 = pd.read_csv(file1)
# df2 = pd.read_csv(file2)

# # Merge the two DataFrames on the 'chapter' and 'verse' columns
# merged_df = pd.merge(df1, df2, how='inner', left_on=['chapter', 'verse'], right_on=['Chapter', 'Verse'])

# # Drop unnecessary columns, including 'question', 'Chapter', and 'Verse'
# merged_df.drop(columns=['question', 'Chapter', 'Verse'], inplace=True)
# # Save the merged DataFrame to a new CSV file
# output_file = 'merged_patanjali_yoga_sutra.csv'  # Replace with the desired output file path
# merged_df.to_csv(output_file, index=False)

# print(f"CSV files merged successfully and saved to {output_file}")
