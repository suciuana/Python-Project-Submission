#DC code generates 1 file: scraped_books.csv

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import sleep

def scrape_books():
    print("Starting book scraping...")
    books = []
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    books_scraped = 0
    page = 1
    
    while books_scraped < 10:
        try:
            url = base_url.format(page)
            print(f"Accessing page {page}...")
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            soup = BeautifulSoup(response.content, 'html.parser')
            
            book_elements = soup.find_all('article', class_='product_pod')
            if not book_elements:
                print(f"No books found on page {page}")
                break
                
            for book in book_elements:
                if books_scraped >= 10:
                    break
                    
                try:
                    title = book.find('h3').find('a')['title']
                    print(f"Scraping book: {title}")
                    
                    price = book.find('p', class_='price_color').text.strip()
                    rating = book.find('p', class_='star-rating')['class'][1]
                    availability = book.find('p', class_='instock availability').text.strip()
                    
                    # Get book page URL
                    book_url = book.find('h3').find('a')['href']
                    if not book_url.startswith('http'):
                        book_url = "http://books.toscrape.com/catalogue/" + book_url.lstrip('/')
                    
                    book_response = requests.get(book_url)
                    book_response.raise_for_status()
                    book_soup = BeautifulSoup(book_response.content, 'html.parser')
                    
                    # Get genre
                    breadcrumbs = book_soup.find('ul', class_='breadcrumb')
                    genre = breadcrumbs.find_all('li')[2].text.strip() if breadcrumbs else 'Unknown'
                    
                    # Get product info
                    product_info = book_soup.find('table', class_='table table-striped')
                    info_dict = {}
                    if product_info:
                        rows = product_info.find_all('tr')
                        for row in rows:
                            header = row.find('th').text.strip()
                            value = row.find('td').text.strip()
                            info_dict[header] = value
                    
                    # Extract specific information
                    upc = info_dict.get('UPC', 'N/A')
                    author = info_dict.get('Author', 'Unknown')
                    publication_year = info_dict.get('Published', 'N/A')
                    
                    if publication_year != 'N/A':
                        try:
                            publication_year = publication_year.split('/')[-1]
                        except:
                            publication_year = 'N/A'
                    
                    # Calculate ranking and popularity
                    ranking = (page - 1) * 20 + list(book_elements).index(book) + 1
                    
                    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
                    rating_numeric = rating_map.get(rating, 0)
                    
                    try:
                        match = re.search(r'\d+', availability)
                        availability_number = int(match.group()) if match else 0
                    except:
                        availability_number = 0
                    
                    popularity = (rating_numeric * 10) + (20 - min(availability_number, 20))
                    
                    books.append({
                        'title': title,
                        'author': author,
                        'genre': genre,
                        'price': price,
                        'rating': rating,
                        'availability': availability,
                        'upc': upc,
                        'publication_year': publication_year,
                        'ranking': ranking,
                        'popularity': popularity
                    })
                    
                    books_scraped += 1
                    print(f"Successfully scraped book {books_scraped}/10")
                    sleep(1)
                    
                except Exception as e:
                    print(f"Error scraping individual book: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error on page {page}: {str(e)}")
            break
            
        page += 1
    
    if books:
        print("Creating DataFrame and saving to CSV...")
        df = pd.DataFrame(books)
        df.to_csv('scraped_books.csv', index=False)
        print(f"Successfully scraped {len(books)} books and saved to scraped_books.csv")
        print("\nFirst few rows of the data:")
        print(df.head())
        return df
    else:
        print("No books were scraped.")
        return None

if __name__ == "__main__":
    scrape_books()
