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

You can run the scraper directly from the command line by passing the target URL as an argument. By default, the scraper will **crawl the entire domain** associated with the URL, discovering and extracting text from all internal links it finds.

The extracted text from all discovered pages will be aggregated and saved into a single, unified `.txt` file inside a domain-specific folder under `scraped_content`.

```bash
python scraper.py <URL>
```

### Options

- `--max-pages`: Set a limit on the maximum number of pages to crawl. Defaults to `0` (unlimited crawling).
- `-o`, `--output`: Specify a custom output file name for the aggregated text. If not provided, it generates one automatically from the domain and timestamp.
- `-d`, `--dir`: Specify a custom base output directory. Defaults to `scraped_content`.

### Examples

**Full Domain Crawl (Default Behavior):**
Scrape the entire domain starting from a specific URL. It will automatically follow all internal links and generate a single aggregated file like `scraped_content/pcvcare.com/index_2026-03-17_14-30-00.txt`:
```bash
python scraper.py https://pcvcare.com
```

**Limit Crawl Depth:**
Crawl the domain but stop after extracting 10 pages:
```bash
python scraper.py https://pcvcare.com --max-pages 10
```

**Custom Output Name:**
Save the single aggregated text output to a specific file name inside the domain folder:
```bash
python scraper.py https://pcvcare.com -o pcvcare_full_scrape.txt
```

**Custom Output Directory:**
Save the output to a different root directory instead of the default `scraped_content`:
```bash
python scraper.py https://pcvcare.com -d my_datasets
```
