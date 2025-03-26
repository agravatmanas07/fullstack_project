import os
import pandas as pd

# Get the absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "data", "Womens Clothing E-Commerce Reviews.csv")

def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)
    df = df[['Clothing ID', 'Age', 'Title', 'Review Text', 'Rating', 
             'Recommended IND', 'Positive Feedback Count', 'Division Name', 
             'Department Name', 'Class Name']]
    
    df['Review Text'] = df['Review Text'].fillna('')
    df['Title'] = df['Title'].fillna('')
    
    df['user_id'] = pd.factorize(df['Age'].astype(str) + df['Review Text'])[0]
    
    df = df.dropna(subset=['Clothing ID', 'user_id', 'Rating'])
    
    return df

if __name__ == "__main__":
    if not os.path.exists(data_path):
        print(f"Error: File not found at {data_path}")
    else:
        processed_data = load_and_preprocess_data(data_path)
        processed_data.to_csv(os.path.join(BASE_DIR, "data", "processed_data.csv"), index=False)
        print("✅ Data preprocessing completed successfully.")
