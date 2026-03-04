"""
A web scraper module that uses Playwright and BeautifulSoup to extract clean text.
"""
import argparse
import datetime
import os
import re
import sys
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def get_domain_and_filename(url):
    """Generates an appropriate domain folder and filename based on the URL."""
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    path = parsed.path.strip('/').replace('/', '_')
    if not path:
        path = "index"
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Clean invalid characters
    domain = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', domain)
    filename = f"{path}_{timestamp}.txt"
    filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
    return domain, filename
class WebScraper:
    """A scraper that fetches and cleans HTML content from web pages."""
    def __init__(self, user_agent="AI Web Scraper Bot 1.0"):
        self.user_agent = user_agent

    def fetch(self, url):
        """Fetches HTML content from the given URL using a headless browser to render JavaScript."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=self.user_agent)
                page = context.new_page()
                
                # Navigate and wait for network activity to cease
                response = page.goto(url, wait_until="networkidle", timeout=30000)
                
                if response and not response.ok:
                    print(f"Warning: HTTP status {response.status} for {url}", file=sys.stderr)
                    
                html = page.content()
                browser.close()
                return html
        except Exception as e:  # pylint: disable=broad-exception-caught
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
        potential_mains = [
            soup.find('main'),
            soup.find('article'),
            soup.find(['div', 'section'], id=re.compile(r'content|main', re.I)),
            soup.find(['div', 'section'], class_=re.compile(r'content|main', re.I))
        ]
        
        main_content = None
        for candidate in potential_mains:
            if candidate and len(candidate.get_text(strip=True)) > 50:
                main_content = candidate
                break
        
        # If no main container found with substantial text, use the body
        root_element = main_content if main_content else soup.body if soup.body else soup

        # Convert headers and list items to preserve markdown formatting
        for i in range(1, 7):
            for h in root_element.find_all(f'h{i}'):
                text = h.get_text(strip=True)
                if text:
                    h.clear()
                    h.append(f"MARKDOWN_H{i} {text}")
                    
        for li in root_element.find_all('li'):
            text = li.get_text(strip=True)
            if text:
                li.clear()
                li.append(f"MARKDOWN_LI {text}")

        # Extract all textual content, flattening divs/spans
        full_text = root_element.get_text(separator='\n', strip=True)

        # Restore markdown formatting
        for i in range(1, 7):
            full_text = full_text.replace(f"MARKDOWN_H{i} ", f"\n\n{'#' * i} ")
        full_text = full_text.replace("MARKDOWN_LI ", "\n- ")
        
        # Clean up excessive empty lines
        full_text = re.sub(r'\n{3,}', '\n\n', full_text)
        
        return full_text.strip()

def main():
    """Main entry point for the web scraper CLI."""
    parser = argparse.ArgumentParser(description="Extract clean text from web pages for AI processing.")
    parser.add_argument("url", help="The URL to scrape.")
    parser.add_argument("-o", "--output", help="Optional output file name. If not provided, one is generated from the URL.")
    parser.add_argument("-d", "--dir", default="scraped_content", help="Optional base output directory. Defaults to 'scraped_content'.")
    args = parser.parse_args()

    scraper = WebScraper()
    print(f"Fetching: {args.url}...", file=sys.stderr)
    
    html = scraper.fetch(args.url)
    if html:
        text = scraper.extract_text(html)
        if text:
            domain, auto_file = get_domain_and_filename(args.url)
            
            # If no output file is specified, organize into a domain folder
            if not args.output:
                out_dir = os.path.join(args.dir, domain)
                out_file = auto_file
            else:
                out_dir = args.dir
                out_file = args.output

            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

            out_path = os.path.join(out_dir, out_file)
            
            try:
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"Content successfully saved to {out_path}", file=sys.stderr)
            except IOError as e:
                print(f"Error saving to file: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("No main content extracted.", file=sys.stderr)
            sys.exit(1)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
