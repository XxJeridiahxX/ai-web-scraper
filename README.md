# AI Web Scraper

A Python-based web scraper designed to extract clean text content from web pages, heavily optimized for consumption by AI models like LLMs. It uses `Playwright` to execute JavaScript and fetch web pages, and `BeautifulSoup4` to parse html, discarding visual noise, navigation, and unnecessary components to deliver a pure text payload.

## Features

- Strips out irrelevant HTML like `<script>`, `<style>`, `<nav>`, `<footer>`, `<header>`, and sidebars.
- Targets and extracts the main content block.
- Converts HTML headings (`<h1>`-`<h6>`) and list items (`<li>`) to clean Markdown formats.
- Retains linear text sequence and structure.

## Installation

1. Make sure you have Python 3 installed.
2. (Optional but recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install the Playwright browser binaries (this is required to execute JavaScript on scraped pages):
   ```bash
   python -m playwright install chromium
   ```

## Usage

You can run the scraper directly from the command line by passing the target URL as an argument. The scraper will automatically generate an appropriate filename based on the URL (and current time) and save the extracted text into a domain-specific folder inside `scraped_content`.

```bash
python scraper.py <URL>
```

### Options

- `-o`, `--output`: Specify a custom output file name. If not provided, one is generated from the URL.
- `-d`, `--dir`: Specify a custom base output directory. Defaults to `scraped_content`.

### Examples

**Basic Usage:**
Scrape an article and let the script auto-generate the filename in a domain folder (e.g., `scraped_content/en.wikipedia.org/wiki_Web_scraping_2023-10-27_14-30-00.txt`):
```bash
python scraper.py https://en.wikipedia.org/wiki/Web_scraping
```

**Custom File Name:**
Save the output to a specific file in the base directory (this bypasses the domain folder logic):
```bash
python scraper.py https://en.wikipedia.org/wiki/Web_scraping -o wiki_scraping.txt
```

**Custom Directory:**
Save the auto-generated domain folder and file to a different directory (e.g., `my_data/en.wikipedia.org/wiki_Web_scraping_2023-10-27_14-30-00.txt`):
```bash
python scraper.py https://en.wikipedia.org/wiki/Web_scraping -d my_data
```

**Custom File Name and Directory:**
Specify both the exact file name and location (this bypasses the domain folder logic):
```bash
python scraper.py https://en.wikipedia.org/wiki/Web_scraping -d output_files -o wiki.txt
```
