"""
A web scraper module that uses Playwright and BeautifulSoup to extract clean text.
"""
import argparse
import datetime
import os
import re
import sys
from urllib.parse import urlparse, urljoin

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
        # Use word boundaries or strict matching to avoid fetching things like 'navLinksContentId'
        content_regex = re.compile(r'\b(main|content)\b', re.I)
        
        potential_mains = [
            soup.find('main'),
            soup.find('article'),
        ]
        
        # Add elements that have main/content in id but avoid nav/menu/sidebar
        for tag in ['div', 'section']:
            for el in soup.find_all(tag, id=content_regex):
                if not re.search(r'nav|menu|sidebar|header|footer', el.get('id', ''), re.I):
                    potential_mains.append(el)
            for el in soup.find_all(tag, class_=content_regex):
                class_str = ' '.join(el.get('class', []))
                if not re.search(r'nav|menu|sidebar|header|footer', class_str, re.I):
                    potential_mains.append(el)
        
        main_content = None
        body_text_len = len(soup.body.get_text(strip=True)) if soup.body else 0
        
        # Sort candidates by length of text to find the largest meaningful container
        valid_candidates = [c for c in potential_mains if c]
        valid_candidates.sort(key=lambda x: len(x.get_text(strip=True)), reverse=True)
        
        for candidate in valid_candidates:
            text_len = len(candidate.get_text(strip=True))
            # Require the candidate to contain at least 40% of the visible body text
            if text_len > 50 and (body_text_len == 0 or (text_len / body_text_len) > 0.4):
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

    def extract_internal_links(self, html_content, base_url):
        """Finds all internal links in the HTML and returns a list of unique absolute URLs."""
        if not html_content:
            return []
            
        soup = BeautifulSoup(html_content, 'html.parser')
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc.replace('www.', '')
        
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            if not href or href.startswith(('javascript:', 'mailto:', 'tel:')):
                continue
                
            if href.startswith('#'):
                continue
                
            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)
            full_url = full_url.split('#')[0]
            
            url_domain = parsed_url.netloc.replace('www.', '')
            if url_domain == base_domain:
                links.add(full_url)
                
        return list(links)
        
    def crawl(self, start_url, output_dir, max_pages=50, output_name=None):
        """Crawls the domain starting from start_url, up to max_pages, and saves to a single file."""
        domain, auto_file = get_domain_and_filename(start_url)
        out_dir = os.path.join(output_dir, domain)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
            
        out_file_name = output_name if output_name else auto_file
        out_path = os.path.join(out_dir, out_file_name)
            
        visited = set()
        queue = [start_url]
        pages_crawled = 0
        aggregated_text = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=self.user_agent)
                page = context.new_page()
                
                while queue and pages_crawled < max_pages:
                    url = queue.pop(0)
                    if url in visited:
                        continue
                        
                    visited.add(url)
                    print(f"Crawling ({pages_crawled+1}/{max_pages}): {url}", file=sys.stderr)
                    
                    try:
                        response = page.goto(url, wait_until="networkidle", timeout=30000)
                        if response and not response.ok:
                            print(f"Warning: HTTP status {response.status} for {url}", file=sys.stderr)
                    except Exception as e:
                        print(f"Error fetching {url}: {e}", file=sys.stderr)
                        continue
                        
                    html = page.content()
                    text = self.extract_text(html)
                    
                    if text:
                        page_divider = f"\n\n========================================\nURL: {url}\n========================================\n\n"
                        aggregated_text.append(page_divider + text)
                            
                    # Add new internal links to queue
                    new_links = self.extract_internal_links(html, url)
                    for link in new_links:
                        # normalize
                        if link not in visited and link not in queue:
                            queue.append(link)
                            
                    pages_crawled += 1
                    
                browser.close()
                print(f"Crawl completed. Crawled {pages_crawled} pages.", file=sys.stderr)
                
                # Write aggregated text to the single output file
                if aggregated_text:
                    try:
                        with open(out_path, 'w', encoding='utf-8') as f:
                            f.write("".join(aggregated_text))
                        print(f"All content successfully saved to {out_path}", file=sys.stderr)
                    except IOError as e:
                        print(f"Error saving to file: {e}", file=sys.stderr)
                else:
                    print("No main content extracted from any pages.", file=sys.stderr)
                    
        except Exception as e:
            print(f"Browser error during crawl: {e}", file=sys.stderr)

def main():
    """Main entry point for the web scraper CLI."""
    parser = argparse.ArgumentParser(description="Extract clean text from entire websites for AI processing.")
    parser.add_argument("url", help="The URL to start crawling from.")
    parser.add_argument("-o", "--output", help="Optional output file name. If not provided, one is generated from the URL.")
    parser.add_argument("-d", "--dir", default="scraped_content", help="Optional base output directory. Defaults to 'scraped_content'.")
    parser.add_argument("--max-pages", type=int, default=50, help="Maximum number of pages to crawl (default: 50).")
    args = parser.parse_args()

    scraper = WebScraper()
    
    print(f"Starting crawl at: {args.url} (max {args.max_pages} pages)", file=sys.stderr)
    scraper.crawl(args.url, args.dir, args.max_pages, args.output)

if __name__ == "__main__":
    main()
