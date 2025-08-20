import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import json
from datetime import datetime

class BookScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        # Using Books-A-Million instead as it's more scraping-friendly
        self.base_url = "https://www.booksamillion.com/bestsellers"
        self.categories = {
            'hardcover_fiction': 'F',
            'hardcover_nonfiction': 'N',
            'paperback_fiction': 'P',
            'young_adult': 'Y',
            'middle_grade': 'M'
        }

    def get_book_details(self, book_element, rank, category):
        """Extract book information from a single book element"""
        try:
            # Title
            title_element = book_element.find('div', class_='title')
            title = title_element.text.strip() if title_element else 'N/A'

            # Author
            author_element = book_element.find('div', class_='author')
            author = author_element.text.replace('by ', '').strip() if author_element else 'N/A'

            # Publication Info
            pub_element = book_element.find('div', class_='details')
            pub_year = 'N/A'
            if pub_element:
                pub_text = pub_element.text
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', pub_text)
            if year_match:
                    pub_year = year_match.group(0)

            # Price as a popularity indicator
            price_element = book_element.find('span', class_='price')
            price = price_element.text.strip() if price_element else 'N/A'

            # Format/Genre
            format_element = book_element.find('div', class_='format')
            format_text = format_element.text.strip() if format_element else 'N/A'

            return {
                'Title': title,
                'Author': author,
                'Category': category,
                'Format/Genre': format_text,
                'Publication_Year': pub_year,
                'Rank': rank,
                'Price': price,
                'Scrape_Date': datetime.now().strftime('%Y-%m-%d')
            }

        except Exception as e:
            print(f"Error extracting book details: {e}")
            return None

    def scrape_category(self, category_name, category_code):
        """Scrape books from a specific category"""
        books_data = []
        url = f"{self.base_url}/{category_code}"
        
        try:
            print(f"Fetching {url}")
            time.sleep(random.uniform(2, 4))  # Polite delay
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            book_elements = soup.find_all('div', class_='product-list-item')
            
            print(f"Found {len(book_elements)} books in {category_name}")
            
            for rank, book in enumerate(book_elements, 1):
                book_data = self.get_book_details(book, rank, category_name)
                if book_data:
                    books_data.append(book_data)
                time.sleep(random.uniform(0.5, 1))

        except Exception as e:
            print(f"Error scraping {category_name}: {e}")

        return books_data

    def scrape_all_categories(self):
        """Scrape books from all categories"""
        all_books = []
        
        for category_name, category_code in self.categories.items():
            print(f"\nScraping {category_name} category...")
            category_books = self.scrape_category(category_name, category_code)
            
            if category_books:
                all_books.extend(category_books)
                print(f"Successfully collected {len(category_books)} books from {category_name}")
            else:
                print(f"No books collected from {category_name}")
            
            time.sleep(random.uniform(3, 5))
        
        return all_books

def save_data(books_data):
    """Save the collected data to files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save to CSV
    df = pd.DataFrame(books_data)
    csv_filename = f'bestseller_books_{timestamp}.csv'
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    print(f"\nSaved CSV file: {csv_filename}")
    
    # Save to JSON
    json_filename = f'bestseller_books_{timestamp}.json'
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(books_data, f, ensure_ascii=False, indent=4)
    print(f"Saved JSON file: {json_filename}")
    
    # Display sample of collected data
    print("\nSample of collected data:")
    print(df[['Title', 'Author', 'Category', 'Publication_Year', 'Rank']].head())

def main():
    print("Starting bestseller book data collection...")
    
    scraper = BookScraper()
    books_data = scraper.scrape_all_categories()
    
    if books_data:
        print(f"\nTotal books collected: {len(books_data)}")
        save_data(books_data)
    else:
        print("No data was collected. Please check the website structure or connection.")

if __name__ == "__main__":
    main()
