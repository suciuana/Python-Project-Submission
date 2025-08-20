import pandas as pd
import numpy as np
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import logging
import traceback
import random

# Set up logging configuration
logging.basicConfig(filename='book_filter_app.log', 
                   level=logging.ERROR,
                   format='%(asctime)s:%(levelname)s:%(message)s')

class BookFilterApp:
    def __init__(self, root):
        """Initialize the application"""
        try:
            self.root = root
            self.root.title("Book Filter Application")
            self.root.geometry("1000x800")
            
            # Load the data
            self.df = self.load_and_clean_data()
            
            if self.df is not None:
                self.create_widgets()
            else:
                self.display_error("Failed to load data. Please check the data file.")
        except Exception as e:
            self.log_error("Initialization error", e)
            self.display_error("Application failed to start properly.")

    def load_and_clean_data(self):
        """Load and clean the book data"""
        try:
            # Attempt to read the CSV file
            df = pd.read_csv('scraped_books.csv')
            
            # Clean price data
            df['price'] = pd.to_numeric(df['price'].str.replace('£', ''), errors='coerce')
            
            # Map ratings to numeric values
            rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
            df['rating_numeric'] = df['rating'].map(rating_map)
            
            # Clean genre data
            df['genre'] = df['genre'].fillna('Unknown').astype('category')
            
            # Create popularity metric if not exists
            if 'popularity' not in df.columns:
                df['popularity'] = df['rating_numeric'] * 2
            
            # Remove any rows with NaN values
            df = df.dropna(subset=['price', 'rating_numeric', 'genre'])
            
            return df
            
        except FileNotFoundError:
            self.log_error("Data file not found", "scraped_books.csv is missing")
            return None
        except Exception as e:
            self.log_error("Data loading error", e)
            return None

    def create_widgets(self):
        """Create and setup GUI widgets"""
        try:
            # Create main frames
            self.filter_frame = ttk.LabelFrame(self.root, text="Filters", padding="10")
            self.filter_frame.pack(fill="x", padx=10, pady=5)
            
            self.results_frame = ttk.LabelFrame(self.root, text="Results", padding="10")
            self.results_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Setup Genre Filter
            self.setup_genre_filter()
            
            # Setup Price Filter
            self.setup_price_filter()
            
            # Setup Rating Filter
            self.setup_rating_filter()
            
            # Setup Sort Options
            self.setup_sort_options()
            
            # Setup Buttons
            self.setup_buttons()
            
            # Setup Results Area
            self.setup_results_area()
            
            # Display initial results
            self.display_all_books()
            
        except Exception as e:
            self.log_error("Widget creation error", e)
            self.display_error("Error creating application interface.")

    def setup_genre_filter(self):
        """Setup the genre filter dropdown"""
        ttk.Label(self.filter_frame, text="Genre:").grid(row=0, column=0, padx=5, pady=5)
        self.genre_var = tk.StringVar()
        genres = ['All'] + sorted(list(self.df['genre'].unique()))
        self.genre_combo = ttk.Combobox(self.filter_frame, textvariable=self.genre_var, values=genres)
        self.genre_combo.set('All')
        self.genre_combo.grid(row=0, column=1, padx=5, pady=5)

    def setup_price_filter(self):
        """Setup the price range filter"""
        ttk.Label(self.filter_frame, text="Price Range (£):").grid(row=0, column=2, padx=5, pady=5)
        self.price_min_var = tk.StringVar()
        self.price_max_var = tk.StringVar()
        self.price_min_entry = ttk.Entry(self.filter_frame, textvariable=self.price_min_var, width=10)
        self.price_max_entry = ttk.Entry(self.filter_frame, textvariable=self.price_max_var, width=10)
        self.price_min_entry.grid(row=0, column=3, padx=5, pady=5)
        self.price_max_entry.grid(row=0, column=4, padx=5, pady=5)

    def setup_rating_filter(self):
        """Setup the rating filter"""
        ttk.Label(self.filter_frame, text="Minimum Rating:").grid(row=1, column=0, padx=5, pady=5)
        self.rating_var = tk.StringVar()
        self.rating_combo = ttk.Combobox(self.filter_frame, textvariable=self.rating_var, 
                                        values=[1, 2, 3, 4, 5], width=5)
        self.rating_combo.grid(row=1, column=1, padx=5, pady=5)

    def setup_sort_options(self):
        """Setup the sort options"""
        ttk.Label(self.filter_frame, text="Sort by:").grid(row=1, column=2, padx=5, pady=5)
        self.sort_var = tk.StringVar()
        self.sort_combo = ttk.Combobox(self.filter_frame, textvariable=self.sort_var, 
                                      values=['popularity', 'price', 'rating_numeric'])
        self.sort_combo.grid(row=1, column=3, padx=5, pady=5)

    def setup_buttons(self):
        """Setup the control buttons"""
        self.apply_button = ttk.Button(self.filter_frame, text="Apply Filters", 
                                     command=self.apply_filters)
        self.apply_button.grid(row=1, column=4, padx=5, pady=5)
        
        self.reset_button = ttk.Button(self.filter_frame, text="Reset", 
                                     command=self.reset_filters)
        self.reset_button.grid(row=2, column=4, padx=5, pady=5)
        
        self.suggest_button = ttk.Button(self.filter_frame, text="Suggest Random Book", 
                                        command=self.suggest_random_book)
        self.suggest_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def setup_results_area(self):
        """Setup the results display area"""
        self.results_text = ScrolledText(self.results_frame, height=20)
        self.results_text.pack(fill="both", expand=True)

    def apply_filters(self):
        """Apply selected filters to the data"""
        try:
            filtered_df = self.df.copy()
            
            # Apply genre filter
            if self.genre_var.get() != 'All':
                filtered_df = filtered_df[filtered_df['genre'] == self.genre_var.get()]
            
            # Apply price filter
            if self.price_min_var.get():
                try:
                    min_price = float(self.price_min_var.get())
                    if min_price < 0:
                        raise ValueError("Minimum price cannot be negative")
                    filtered_df = filtered_df[filtered_df['price'] >= min_price]
                except ValueError as ve:
                    self.display_error("Invalid minimum price. Please enter a positive number.")
                    return
                    
            if self.price_max_var.get():
                try:
                    max_price = float(self.price_max_var.get())
                    if max_price < 0:
                        raise ValueError("Maximum price cannot be negative")
                    filtered_df = filtered_df[filtered_df['price'] <= max_price]
                except ValueError as ve:
                    self.display_error("Invalid maximum price. Please enter a positive number.")
                    return
            
            # Apply rating filter
            if self.rating_var.get():
                try:
                    rating = int(self.rating_var.get())
                    if rating not in [1, 2, 3, 4, 5]:
                        raise ValueError("Invalid rating value")
                    filtered_df = filtered_df[filtered_df['rating_numeric'] >= rating]
                except ValueError:
                    self.display_error("Please select a valid rating (1-5).")
                    return
            
            # Apply sorting
            if self.sort_var.get():
                filtered_df = filtered_df.sort_values(by=self.sort_var.get(), ascending=False)
            
            self.display_results(filtered_df)
            
        except Exception as e:
            self.log_error("Filter application error", e)
            self.display_error("Error applying filters.")

    def reset_filters(self):
        """Reset all filters to default values"""
        try:
            self.genre_var.set('All')
            self.price_min_var.set('')
            self.price_max_var.set('')
            self.rating_var.set('')
            self.sort_var.set('')
            self.display_all_books()
        except Exception as e:
            self.log_error("Reset error", e)
            self.display_error("Error resetting filters.")

    def display_results(self, df):
        """Display filtered results"""
        try:
            self.results_text.delete(1.0, tk.END)
            
            if df.empty:
                self.results_text.insert(tk.END, "No books found matching the filters.")
                return
            
            self.results_text.insert(tk.END, f"Found {len(df)} books matching the criteria:\n\n")
            
            for _, book in df.iterrows():
                self.results_text.insert(tk.END,
                    f"Title: {book['title']}\n"
                    f"Author: {book['author']}\n"
                    f"Genre: {book['genre']}\n"
                    f"Price: £{book['price']:.2f}\n"
                    f"Rating: {book['rating']}\n"
                    f"Popularity: {book['popularity']:.1f}\n"
                    f"{'-'*50}\n\n"
                )
        except Exception as e:
            self.log_error("Display error", e)
            self.display_error("Error displaying results.")

    def display_all_books(self):
        """Display all books without filters"""
        self.display_results(self.df)

    def suggest_random_book(self):
        """Suggest a random book from the selected genre"""
        try:
            genre = self.genre_var.get()
            if genre == 'All':
                book = self.df.sample(n=1).iloc[0]
            else:
                genre_df = self.df[self.df['genre'] == genre]
                if genre_df.empty:
                    self.display_error(f"No books found in the {genre} genre.")
                    return
                book = genre_df.sample(n=1).iloc[0]
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Random Book Suggestion:\n\n")
            self.results_text.insert(tk.END,
                f"Title: {book['title']}\n"
                f"Author: {book['author']}\n"
                f"Genre: {book['genre']}\n"
                f"Price: £{book['price']:.2f}\n"
                f"Rating: {book['rating']}\n"
                f"Popularity: {book['popularity']:.1f}\n"
                f"{'-'*50}\n"
            )
        except Exception as e:
            self.log_error("Random suggestion error", e)
            self.display_error("Error suggesting a random book.")

    def display_error(self, message):
        """Display error message to user"""
        messagebox.showerror("Error", message)

    def log_error(self, error_type, error_message):
        """Log error to file"""
        logging.error(f"{error_type}: {str(error_message)}\n{traceback.format_exc()}")

def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        app = BookFilterApp(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Application crash: {str(e)}\n{traceback.format_exc()}")
        messagebox.showerror("Fatal Error", "Application failed to start.")

if __name__ == "__main__":
    main()
