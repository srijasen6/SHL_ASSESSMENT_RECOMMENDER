import re
import requests
import trafilatura
from typing import Optional

def extract_text_from_url(url: str) -> Optional[str]:
    """Extract text content from a URL."""
    try:
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        return text
    except Exception as e:
        print(f"Error extracting text from URL: {str(e)}")
        return None

def validate_url(url: str) -> bool:
    """Validate if the string is a valid URL."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(url))

def parse_time_constraint(query: str) -> Optional[int]:
    """Parse time constraint from the query in minutes."""
    time_patterns = [
        r'(\d+)\s*min',
        r'(\d+)\s*minute',
        r'under\s*(\d+)',
        r'less\s*than\s*(\d+)',
        r'maximum\s*(\d+)'
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, query.lower())
        if match:
            return int(match.group(1))
    return None

def format_duration(duration: str) -> str:
    """Format duration string for display."""
    if not duration:
        return "Unknown"
    return duration.strip()