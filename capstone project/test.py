import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import logging
import traceback
import random
import requests
import json

# Set up logging configuration
logging.basicConfig(filename='book_filter_app.log', 
                   level=logging.ERROR,
                   format='%(asctime)s:%(levelname)s:%(message)s')

API_KEY = "392d51b948msh719002aa232c03ap1cb410jsnc2b241bcbb2b"

def fetch_books():
    """Function to fetch books from the Goodreads API"""
    url = "https://goodreads12.p.rapidapi.com/searchBooks?page=1"
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "goodreads12.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        books = data.get('books', [])
        
        books_data = []
        for book in books[:10]:  # Limit to 10 books
            books_data.append({
                'title': book.get('title', 'Unknown'),
                   'author': book.get('author', 'Unknown'),
                'rating': float(book.get('rating', 0)),
                'genre': book.get('genre', 'Unknown'),
                'price': round(random.uniform(5, 30), 2)  # Random price as API doesn't provide price
            })
            print(f"Fetched book: {books_data[-1]['title']}")
        
        return pd.DataFrame(books_data)
    
    except requests.exceptions.RequestException as e:
        logging.error(f"API request error: {str(e)}")
        return None

class BookFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Filter Application")
        self.root.geometry("1000x800")
        
        self.loading_label = ttk.Label(self.root, text="Loading books...", font=('Helvetica', 12))
        self.loading_label.pack(pady=20)
        
        self.root.after(100, self.load_initial_data)

    def load_initial_data(self):
        try:
            self.df = fetch_books()
            
            if self.df is not None and not self.df.empty:
                self.prepare_data()
                self.loading_label.destroy()
                self.create_widgets()
            else:
                messagebox.showerror("Error", "Failed to load book data.")
                self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start application: {str(e)}")
            logging.error(f"Initialization error: {str(e)}\n{traceback.format_exc()}")
            self.root.destroy()

    def prepare_data(self):
        self.df['popularity'] = self.df['rating'] * 20  # Scale rating to 0-100 for popularity

    def create_widgets(self):
        self.filter_frame = ttk.LabelFrame(self.root, text="Filters", padding="10")
        self.filter_frame.pack(fill="x", padx=10, pady=5)
        
        self.results_frame = ttk.LabelFrame(self.root, text="Results", padding="10")
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ttk.Label(self.filter_frame, text="Genre:").grid(row=0, column=0, padx=5, pady=5)
        self.genre_var = tk.StringVar()
        genres = ['All'] + sorted(list(self.df['genre'].unique()))
        self.genre_combo = ttk.Combobox(self.filter_frame, textvariable=self.genre_var, values=genres)
        self.genre_combo.set('All')
        self.genre_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.filter_frame, text="Price Range ($):").grid(row=0, column=2, padx=5, pady=5)
        self.price_min_var = tk.StringVar()
        self.price_max_var = tk.StringVar()
        self.price_min_entry = ttk.Entry(self.filter_frame, textvariable=self.price_min_var, width=10)
        self.price_max_entry = ttk.Entry(self.filter_frame, textvariable=self.price_max_var, width=10)
        self.price_min_entry.grid(row=0, column=3, padx=5, pady=5)
        self.price_max_entry.grid(row=0, column=4, padx=5, pady=5)
        
        ttk.Label(self.filter_frame, text="Minimum Rating:").grid(row=1, column=0, padx=5, pady=5)
        self.rating_var = tk.StringVar()
        self.rating_combo = ttk.Combobox(self.filter_frame, textvariable=self.rating_var, 
                                        values=[1, 2, 3, 4, 5], width=5)
        self.rating_combo.grid(row=1, column=1, padx=5, pady=5)
        
        self.apply_button = ttk.Button(self.filter_frame, text="Apply Filters", 
                                     command=self.apply_filters)
        self.apply_button.grid(row=1, column=3, padx=5, pady=5)
        
        self.reset_button = ttk.Button(self.filter_frame, text="Reset", 
                                     command=self.reset_filters)
        self.reset_button.grid(row=1, column=4, padx=5, pady=5)
        
        self.random_button = ttk.Button(self.filter_frame, text="Random Book", 
                                      command=self.suggest_random_book)
        self.random_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        self.refresh_button = ttk.Button(self.filter_frame, text="Refresh Data", 
                                       command=self.refresh_data)
        self.refresh_button.grid(row=2, column=3, columnspan=2, padx=5, pady=5)
        
        self.results_text = ScrolledText(self.results_frame, height=20)
        self.results_text.pack(fill="both", expand=True)
        
        self.display_all_books()

    def apply_filters(self):
        try:
            filtered_df = self.df.copy()
            
            if self.genre_var.get() != 'All':
                filtered_df = filtered_df[filtered_df['genre'] == self.genre_var.get()]
            
            if self.price_min_var.get():
                try:
                    min_price = float(self.price_min_var.get())
                    filtered_df = filtered_df[filtered_df['price'] >= min_price]
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid minimum price")
                    return
                    
            if self.price_max_var.get():
                try:
                    max_price = float(self.price_max_var.get())
                    filtered_df = filtered_df[filtered_df['price'] <= max_price]
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid maximum price")
                    return
            
            if self.rating_var.get():
                filtered_df = filtered_df[filtered_df['rating'] >= float(self.rating_var.get())]
            
            self.display_results(filtered_df)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error applying filters: {str(e)}")

    def reset_filters(self):
        self.genre_var.set('All')
        self.price_min_var.set('')
        self.price_max_var.set('')
        self.rating_var.set('')
        self.display_all_books()

    def display_results(self, df):
        self.results_text.delete(1.0, tk.END)
        
        if df.empty:
            self.results_text.insert(tk.END, "No books found matching the filters.")
            return
        
        self.results_text.insert(tk.END, f"Found {len(df)} books:\n\n")
        
        for _, book in df.iterrows():
            self.results_text.insert(tk.END,
                f"Title: {book['title']}\n"
                f"Author: {book['author']}\n"
                f"Genre: {book['genre']}\n"
                f"Price: ${book['price']:.2f}\n"
                f"Rating: {book['rating']:.1f}\n"
                f"Popularity: {book['popularity']:.1f}\n"
                f"{'-'*50}\n\n"
            )

    def display_all_books(self):
        self.display_results(self.df)

    def suggest_random_book(self):
        try:
            genre = self.genre_var.get()
            if genre == 'All':
                book = self.df.sample(n=1).iloc[0]
            else:
                genre_df = self.df[self.df['genre'] == genre]
                if genre_df.empty:
                    messagebox.showinfo("Info", f"No books found in {genre} genre")
                    return
                book = genre_df.sample(n=1).iloc[0]
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Random Book Suggestion:\n\n")
            self.results_text.insert(tk.END,
                f"Title: {book['title']}\n"
                f"Author: {book['author']}\n"
                f"Genre: {book['genre']}\n"
                f"Price: ${book['price']:.2f}\n"
                f"Rating: {book['rating']:.1f}\n"
                f"Popularity: {book['popularity']:.1f}\n"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error suggesting random book: {str(e)}")

    def refresh_data(self):
        try:
            self.loading_label = ttk.Label(self.root, text="Refreshing data...", font=('Helvetica', 12))
            self.loading_label.pack(pady=20)
            self.df = fetch_books()
            if self.df is not None:
                self.prepare_data()
                self.display_all_books()
                messagebox.showinfo("Success", "Data refreshed successfully!")
            else:
                messagebox.showerror("Error", "Failed to refresh data.")
            self.loading_label.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh data: {str(e)}")

def main():
    try:
        root = tk.Tk()
        app = BookFilterApp(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Application crash: {str(e)}\n{traceback.format_exc()}")
        messagebox.showerror("Fatal Error", "Application failed to start.")

if __name__ == "__main__":
    main()
