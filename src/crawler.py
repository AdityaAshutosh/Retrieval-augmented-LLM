import os
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
from config import BASE_URL, MAX_DEPTH, RAW_DATA_DIR

visited_links = set()

def save_data(url, content, depth):
    path = os.path.join(RAW_DATA_DIR, f"depth_{depth}")
    os.makedirs(path, exist_ok=True)
    filename = os.path.join(path, f"{hash(url)}.txt")
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def fetch_links(url, depth):
    if depth > MAX_DEPTH or url in visited_links:
        return
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        visited_links.add(url)
        content = soup.get_text()
        save_data(url, content, depth)
        print(f"Fetched {url} at depth {depth}")
        
        links = [a['href'] for a in soup.find_all('a', href=True)]
        for link in links:
            full_link = urljoin(BASE_URL, link)
            fetch_links(full_link, depth + 1)
            time.sleep(1)  # To avoid overloading the server
    except Exception as e:
        print(f"Error fetching {url}: {e}")

def main():
    fetch_links(BASE_URL, 1)

if __name__ == "__main__":
    main()
