#EH code generates a log file ('book_filter_app.log') to track any errors that occur during operation.

import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import traceback
import logging

# Set up logging
logging.basicConfig(filename='book_filter_app.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class BookFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Filter Application")
        self.root.geometry("1000x800")
        
        try:
            # Load the data
            self.df = self.load_and_clean_data()
            
            if self.df is not None:
                self.create_widgets()
            else:
                self.display_error("Failed to load data. Please check the data file and try again.")
        except Exception as e:
            self.display_error(f"An unexpected error occurred during initialization: {str(e)}")
            logging.error(f"Initialization error: {str(e)}\n{traceback.format_exc()}")
    
    def load_and_clean_data(self):
        try:
            df = pd.read_csv('scraped_books.csv')
            
            # Clean and transform data
            df['price'] = pd.to_numeric(df['price'].str.replace('£', ''), errors='coerce')
            
            rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
            df['rating_numeric'] = df['rating'].map(rating_map)
            
            df['genre'] = df['genre'].fillna('Unknown').astype('category')
            
            if 'popularity' not in df.columns:
                df['popularity'] = df['rating_numeric'] * 2
            
            # Remove rows with NaN values
            df = df.dropna()
            
            return df
            
        except FileNotFoundError:
            self.display_error("Data file 'scraped_books.csv' not found. Please ensure the file exists in the same directory.")
            logging.error("Data file not found")
            return None
        except pd.errors.EmptyDataError:
            self.display_error("The data file is empty. Please check the content of 'scraped_books.csv'.")
            logging.error("Empty data file")
            return None
        except Exception as e:
            self.display_error(f"Error loading data: {str(e)}")
            logging.error(f"Data loading error: {str(e)}\n{traceback.format_exc()}")
            return None

    def create_widgets(self):
        # Create frames
        self.filter_frame = ttk.LabelFrame(self.root, text="Filters", padding="10")
        self.filter_frame.pack(fill="x", padx=10, pady=5)
        
        self.results_frame = ttk.LabelFrame(self.root, text="Results", padding="10")
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Genre Filter
        ttk.Label(self.filter_frame, text="Genre:").grid(row=0, column=0, padx=5, pady=5)
        self.genre_var = tk.StringVar()
        genres = ['All'] + sorted(list(self.df['genre'].unique()))
        self.genre_combo = ttk.Combobox(self.filter_frame, textvariable=self.genre_var, values=genres)
        self.genre_combo.set('All')
        self.genre_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Price Range Filter
        ttk.Label(self.filter_frame, text="Price Range (£):").grid(row=0, column=2, padx=5, pady=5)
        self.price_min_var = tk.StringVar()
        self.price_max_var = tk.StringVar()
        self.price_min_entry = ttk.Entry(self.filter_frame, textvariable=self.price_min_var, width=10)
        self.price_max_entry = ttk.Entry(self.filter_frame, textvariable=self.price_max_var, width=10)
        self.price_min_entry.grid(row=0, column=3, padx=5, pady=5)
        self.price_max_entry.grid(row=0, column=4, padx=5, pady=5)
        
        # Rating Filter
        ttk.Label(self.filter_frame, text="Minimum Rating:").grid(row=1, column=0, padx=5, pady=5)
        self.rating_var = tk.StringVar()
        self.rating_combo = ttk.Combobox(self.filter_frame, textvariable=self.rating_var, 
                                        values=[1, 2, 3, 4, 5], width=5)
        self.rating_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Sort Options
        ttk.Label(self.filter_frame, text="Sort by:").grid(row=1, column=2, padx=5, pady=5)
        self.sort_var = tk.StringVar()
        sort_options = ['popularity', 'price', 'rating_numeric']
        self.sort_combo = ttk.Combobox(self.filter_frame, textvariable=self.sort_var, 
                                      values=sort_options)
        self.sort_combo.grid(row=1, column=3, padx=5, pady=5)
        
        # Buttons
        self.apply_button = ttk.Button(self.filter_frame, text="Apply Filters", 
                                     command=self.apply_filters)
        self.apply_button.grid(row=1, column=4, padx=5, pady=5)
        
        self.reset_button = ttk.Button(self.filter_frame, text="Reset", 
                                     command=self.reset_filters)
        self.reset_button.grid(row=2, column=4, padx=5, pady=5)
        
        # Results Area
        self.results_text = ScrolledText(self.results_frame, height=20)
        self.results_text.pack(fill="both", expand=True)
        
        # Initial display
        self.display_all_books()

    def apply_filters(self):
        try:
            filtered_df = self.df.copy()
            
            # Apply genre filter
            if self.genre_var.get() != 'All':
                filtered_df = filtered_df[filtered_df['genre'] == self.genre_var.get()]
            
            # Apply price filter
            if self.price_min_var.get():
                try:
                    min_price = float(self.price_min_var.get())
                    filtered_df = filtered_df[filtered_df['price'] >= min_price]
                except ValueError:
                    self.display_error("Invalid minimum price. Please enter a valid number.")
                    return
            if self.price_max_var.get():
                try:
                    max_price = float(self.price_max_var.get())
                    filtered_df = filtered_df[filtered_df['price'] <= max_price]
                except ValueError:
                    self.display_error("Invalid maximum price. Please enter a valid number.")
                    return
            
            # Apply rating filter
            if self.rating_var.get():
                try:
                    min_rating = int(self.rating_var.get())
                    filtered_df = filtered_df[filtered_df['rating_numeric'] >= min_rating]
                except ValueError:
                    self.display_error("Invalid rating. Please select a valid rating.")
                    return
            
            # Apply sorting
            if self.sort_var.get():
                filtered_df = filtered_df.sort_values(by=self.sort_var.get(), ascending=False)
            
            self.display_results(filtered_df)
        
        except Exception as e:
            self.display_error(f"An error occurred while applying filters: {str(e)}")
            logging.error(f"Filter application error: {str(e)}\n{traceback.format_exc()}")

    def reset_filters(self):
        try:
            self.genre_var.set('All')
            self.price_min_var.set('')
            self.price_max_var.set('')
            self.rating_var.set('')
            self.sort_var.set('')
            self.display_all_books()
        except Exception as e:
            self.display_error(f"An error occurred while resetting filters: {str(e)}")
            logging.error(f"Filter reset error: {str(e)}\n{traceback.format_exc()}")

    def display_results(self, df):
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
            self.display_error(f"An error occurred while displaying results: {str(e)}")
            logging.error(f"Results display error: {str(e)}\n{traceback.format_exc()}")

    def display_all_books(self):
        try:
            self.display_results(self.df)
        except Exception as e:
            self.display_error(f"An error occurred while displaying all books: {str(e)}")
            logging.error(f"All books display error: {str(e)}\n{traceback.format_exc()}")

    def display_error(self, message):
        messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = BookFilterApp(root)
    root.mainloop()
