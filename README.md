# AI Web Scraper

A Python-based web scraper designed to extract clean text content from web pages, heavily optimized for consumption by AI models like LLMs. It uses `requests` and `BeautifulSoup4` to fetch and parse html, discarding visual noise, navigation, and unnecessary components to deliver a pure text payload.

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

## Usage

You can run the scraper directly from the command line by passing the target URL as an argument.

```bash
python scraper.py <URL>
```

### Example

```bash
python scraper.py https://en.wikipedia.org/wiki/Web_scraping
```

The script will fetch the web page, extract the core text content, and print it to the standard output. If you want to save the output to a file, you can pipe it:

```bash
python scraper.py https://en.wikipedia.org/wiki/Web_scraping > output.txt
```
