import httpx
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any, Set
from urllib.parse import urljoin, urlparse
import asyncio

logger = logging.getLogger(__name__)

class WebsiteCrawler:
    def __init__(self, max_depth: int = 2, max_pages: int = 50, rate_limit_delay: float = 0.5):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.rate_limit_delay = rate_limit_delay
        
    async def crawl(self, start_url: str) -> List[Dict[str, Any]]:
        visited: Set[str] = set()
        to_visit = [(start_url, 0)]
        results = []
        
        base_domain = urlparse(start_url).netloc

        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            while to_visit and len(visited) < self.max_pages:
                current_url, depth = to_visit.pop(0)
                
                # Normalize URL (remove fragments)
                current_url = current_url.split('#')[0]
                
                if current_url in visited:
                    continue
                    
                visited.add(current_url)
                
                try:
                    logger.info(f"Crawling {current_url} at depth {depth}")
                    response = await client.get(current_url)
                    response.raise_for_status()
                    
                    content_type = response.headers.get("Content-Type", "")
                    if "text/html" not in content_type:
                        continue
                        
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    # Extract Data
                    title = soup.title.string.strip() if soup.title and soup.title.string else current_url
                    
                    # Clean up
                    for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                        element.decompose()
                        
                    text_content = soup.get_text(separator="\n\n", strip=True)
                    
                    results.append({
                        "url": current_url,
                        "title": title,
                        "content": text_content,
                        "depth": depth
                    })
                    
                    # Enqueue Links
                    if depth < self.max_depth:
                        links = soup.find_all("a", href=True)
                        for link in links:
                            next_url = urljoin(current_url, link["href"]).split('#')[0]
                            # Only crawl within same domain
                            if urlparse(next_url).netloc == base_domain and next_url not in visited:
                                to_visit.append((next_url, depth + 1))
                                
                    await asyncio.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"Failed to crawl {current_url}: {str(e)}")
                    continue
                    
        return results

website_crawler = WebsiteCrawler()
