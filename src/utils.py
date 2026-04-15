import re
import logging

# 1. Setup a standard logger so we don't just use print() everywhere
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - WebMind AI - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def is_valid_url(url: str) -> bool:
    """
    Validates if a string is a properly formatted web URL.
    Useful for checking user input in Streamlit before scraping.
    """
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return re.match(regex, url) is not None

def estimate_tokens(text: str) -> int:
    """
    A rough heuristic to estimate tokens (1 token ≈ 4 chars in English).
    Helpful to warn the user if a website is too massive to process.
    """
    if not text:
        return 0
    return len(text) // 4