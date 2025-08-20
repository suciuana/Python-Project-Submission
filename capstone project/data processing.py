#DP code generates 2 files: 
#1.book_analysis.xslx
#2.cleaned_books.csv

import pandas as pd
import numpy as np
from datetime import datetime

def clean_book_data(csv_file='scraped_books.csv'):
    try:
        # Read the CSV file
        print("Reading the CSV file...")
        df = pd.read_csv(csv_file)
        
        # Display initial information about the dataset
        print("\nInitial dataset information:")
        print(df.info())
        
        # Clean and transform the data
        print("\nCleaning and transforming data...")
        
        # Clean price column - remove £ symbol and convert to float
        df['price'] = df['price'].str.replace('£', '').astype(float)
        
        # Convert rating to numeric scale (1-5)
        rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
        df['rating_numeric'] = df['rating'].map(rating_map)
        
        # Convert publication_year to numeric
        df['publication_year'] = pd.to_numeric(df['publication_year'], errors='coerce')
        
        # Create a categorical type for genre
        df['genre'] = df['genre'].astype('category')
        
        # Calculate additional metrics
        df['price_category'] = pd.qcut(df['price'], q=3, labels=['Low', 'Medium', 'High'])
        df['is_recent'] = df['publication_year'] >= 2020
        
        # Remove any duplicate entries
        df = df.drop_duplicates(subset=['title', 'author'], keep='first')
        
        # Handle missing values
        df['author'] = df['author'].fillna('Unknown Author')
        df['publication_year'] = df['publication_year'].fillna(df['publication_year'].median())
        
        # Create summary statistics
        print("\nSummary Statistics:")
        print("\nPrice Statistics:")
        print(df['price'].describe())
        
        print("\nBooks per Genre:")
        print(df['genre'].value_counts())
        
        print("\nAverage Rating by Genre:")
        print(df.groupby('genre')['rating_numeric'].mean().round(2))
        
        # Create some useful analysis
        print("\nTop 5 Most Popular Books:")
        print(df.nlargest(5, 'popularity')[['title', 'author', 'popularity', 'rating']])
        
        print("\nPrice Range by Genre:")
        genre_price = df.groupby('genre').agg({
            'price': ['mean', 'min', 'max']
        }).round(2)
        print(genre_price)
        
        # Save the cleaned data
        output_file = 'cleaned_books.csv'
        df.to_csv(output_file, index=False)
        print(f"\nCleaned data saved to {output_file}")
        
        # Create Excel file with multiple sheets for different analyses
        print("\nCreating Excel report...")
        with pd.ExcelWriter('book_analysis.xlsx') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='Clean_Data', index=False)
            
            # Genre Analysis
            genre_analysis = df.groupby('genre').agg({
                'title': 'count',
                'price': 'mean',
                'rating_numeric': 'mean',
                'popularity': 'mean'
            }).round(2)
            genre_analysis.to_excel(writer, sheet_name='Genre_Analysis')
            
            # Price Analysis
            price_analysis = df.groupby('price_category').agg({
                'title': 'count',
                'rating_numeric': 'mean',
                'popularity': 'mean'
            }).round(2)
            price_analysis.to_excel(writer, sheet_name='Price_Analysis')
            
            # Top Books
            df.nlargest(10, 'popularity')[['title', 'author', 'genre', 'price', 'rating', 'popularity']].to_excel(
                writer, sheet_name='Top_Books')
        
        print("Excel report created: book_analysis.xlsx")
        
        return df
        
    except FileNotFoundError:
        print(f"Error: The file {csv_file} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def generate_insights(df):
    "Generate additional insights from the cleaned data"
    if df is not None:
        print("\nGenerating Additional Insights...")
        
        # Price correlations
        print("\nCorrelations with Price:")
        correlations = df[['price', 'rating_numeric', 'popularity']].corr()['price'].round(3)
        print(correlations)
        
        # Average price by publication year (for recent books)
        recent_prices = df[df['is_recent']].groupby('publication_year')['price'].mean().round(2)
        print("\nAverage Prices by Recent Publication Years:")
        print(recent_prices)
        
        # Genre diversity
        print("\nGenre Diversity:")
        genre_diversity = df.groupby('genre').agg({
            'title': 'count',
            'author': 'unique',
            'price': ['mean', 'std']
        }).round(2)
        print(genre_diversity)
        
        # Rating distribution
        print("\nRating Distribution:")
        print(df['rating'].value_counts())
        
        # Price analysis by rating
        print("\nAverage Price by Rating:")
        rating_price = df.groupby('rating')['price'].agg(['mean', 'count']).round(2)
        print(rating_price)

if __name__ == "__main__":
    # Clean and analyze the data
    cleaned_df = clean_book_data()
    
    # Generate additional insights if data cleaning was successful
    if cleaned_df is not None:
        generate_insights(cleaned_df)
