import requests
from bs4 import BeautifulSoup
import re

class WebMindScraper:
    def __init__(self):
        # Universal browser headers for 2026
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/"
        }

    def fetch_page(self, url):
        """Fetches the raw HTML content of any provided URL."""
        try:
            # allow_redirects=True is vital for modern short-links and marketing URLs
            response = requests.get(url, headers=self.headers, timeout=20, allow_redirects=True)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"❌ WebMind Error: Could not reach {url}. Details: {e}")
            return None

    def clean_content(self, html):
        """Universal text extraction and noise reduction."""
        soup = BeautifulSoup(html, 'html.parser')

        # 1. Strip away non-visible/non-content elements
        for element in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "button", "aside"]):
            element.decompose()

        # 2. Target standard semantic tags used across the web
        content_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'td', 'article'])
        
        extracted_lines = []
        for tag in content_tags:
            text = tag.get_text(separator=' ').strip()
            
            # 3. Intelligent Noise Filter
            # We keep lines that look like actual information (usually > 2 words)
            # This avoids capturing "Log In", "Search", or "Click Here"
            if len(text.split()) > 2:
                extracted_lines.append(text)

        # 4. Global De-duplication
        # Modern sites often repeat headers or taglines; we only need one copy.
        seen = set()
        unique_lines = []
        for line in extracted_lines:
            if line not in seen:
                unique_lines.append(line)
                seen.add(line)

        # Join into a coherent block of text
        full_text = " ".join(unique_lines)
        
        # Final regex to fix spacing and hidden characters
        clean_text = re.sub(r'\s+', ' ', full_text).strip()
        
        return clean_text

# --- Universal Test Execution ---
if __name__ == "__main__":
    scraper = WebMindScraper()
    
    # You can now test this with ANY website (e.g., Wikipedia, a blog, or tech docs)
    test_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    
    html = scraper.fetch_page(test_url)
    
    if html:
        content = scraper.clean_content(html)
        print(f"✅ WebMind Scraping Complete!")
        print(f"📊 Content Length: {len(content)} characters")
        print("-" * 30)
        print(f"📝 Data Preview:\n{content[:500]}...") 
    else:
        print("❌ WebMind was unable to read the site. Check the URL or your connection.")