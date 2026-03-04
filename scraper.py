import argparse
import sys
import requests
from bs4 import BeautifulSoup
import re

class WebScraper:
    def __init__(self, user_agent="AI Web Scraper Bot 1.0"):
        self.headers = {
            'User-Agent': user_agent
        }

    def fetch(self, url):
        """Fetches HTML content from the given URL."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}", file=sys.stderr)
            return None

    def clean_html(self, soup):
        """Removes unwanted elements from the BeautifulSoup object."""
        # Remove script, style, navigation, footer, header, and other boilerplate elements
        for element in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe", "aside"]):
            element.decompose()

    def extract_text(self, html_content):
        """Extracts clean, structured text from HTML suitable for AI ingestion."""
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, 'html.parser')
        self.clean_html(soup)

        # Try to find the main content block to avoid sidebars and menus
        main_content = (soup.find('main') or 
                        soup.find('article') or 
                        soup.find(id=re.compile(r'content|main', re.I)) or 
                        soup.find(class_=re.compile(r'content|main', re.I)))
        
        # If no main container found, use the body
        root_element = main_content if main_content else soup.body if soup.body else soup

        extracted_text = []

        # Extract textual elements in order
        for el in root_element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li']):
            text = el.get_text(strip=True)
            if not text:
                continue

            # Format headers with markdown
            if el.name.startswith('h'):
                level = int(el.name[1])
                extracted_text.append(f"\n{'#' * level} {text}\n")
            elif el.name == 'li':
                # Convert list items to markdown lists
                extracted_text.append(f"- {text}")
            else:
                extracted_text.append(text)

        # Join the elements dynamically
        full_text = "\n".join(extracted_text)
        
        # Remove any excessive empty lines
        full_text = re.sub(r'\n{3,}', '\n\n', full_text)
        
        return full_text.strip()

def main():
    parser = argparse.ArgumentParser(description="Extract clean text from web pages for AI processing.")
    parser.add_argument("url", help="The URL to scrape.")
    args = parser.parse_args()

    scraper = WebScraper()
    print(f"Fetching: {args.url}...", file=sys.stderr)
    
    html = scraper.fetch(args.url)
    if html:
        text = scraper.extract_text(html)
        if text:
            print(text)
        else:
            print("No main content extracted.", file=sys.stderr)
            sys.exit(1)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
