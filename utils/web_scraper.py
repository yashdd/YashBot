import logging
import trafilatura
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse, urljoin
import re

# Try to import Document from different possible locations
try:
    from langchain_core.documents import Document
except ImportError:
    try:
        from langchain.schema import Document
    except ImportError:
        # Define a simple Document class as fallback
        class Document:
            def __init__(self, page_content, metadata=None):
                self.page_content = page_content
                self.metadata = metadata or {}

logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> str:
    """
    Extract main text content from a website.
    
    Args:
        url: The URL of the website to scrape
        
    Returns:
        Extracted text content from the website
    """
    try:
        logger.debug(f"Fetching content from URL: {url}")
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            logger.error(f"Failed to download content from {url}")
            return ""
            
        text = trafilatura.extract(downloaded)
        if not text:
            logger.warning(f"No text content extracted from {url}")
            return ""
            
        logger.debug(f"Successfully extracted {len(text)} characters from {url}")
        return text
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return ""

def crawl_website(base_url: str, max_pages: int = 10, max_depth: int = 2) -> List[Dict[str, str]]:
    """
    Crawl a website to extract content from multiple pages.
    
    Args:
        base_url: The starting URL for crawling
        max_pages: Maximum number of pages to crawl
        max_depth: Maximum depth of crawling from the base URL
        
    Returns:
        List of dictionaries with 'url' and 'content' keys
    """
    try:
        # Parse the base URL to get domain information
        parsed_base_url = urlparse(base_url)
        base_domain = parsed_base_url.netloc
        
        # Initialize variables
        visited_urls = set()
        to_visit = [[base_url, 0]]  # [url, depth] as list instead of tuple
        results = []
        
        logger.info(f"Starting website crawl from {base_url}")
        
        # Crawl until we reach max_pages or run out of URLs to visit
        while to_visit and len(results) < max_pages:
            # Get next URL to visit
            current_url, current_depth = to_visit.pop(0)
            
            # Skip if already visited or exceeds max depth
            if current_url in visited_urls or current_depth > max_depth:
                continue
                
            logger.debug(f"Crawling URL: {current_url} (depth: {current_depth})")
            visited_urls.add(current_url)
            
            # Get content from the current URL
            downloaded = trafilatura.fetch_url(current_url)
            if not downloaded:
                logger.warning(f"Could not download content from {current_url}")
                continue
                
            # Extract text content
            text = trafilatura.extract(downloaded)
            if text:
                results.append({
                    "url": current_url,
                    "content": text
                })
                logger.debug(f"Added content from {current_url} ({len(text)} chars)")
                
            # If we've reached max depth, don't look for more links
            if current_depth >= max_depth:
                continue
                
            # Extract links from the current page
            if current_depth < max_depth:
                try:
                    # Find all links on the page using regex
                    links = re.findall(r'href=[\'"]?([^\'" >]+)', downloaded.decode('utf-8', errors='ignore'))
                    
                    # Process each link
                    for link in links:
                        # Convert relative URLs to absolute
                        if link.startswith('/'):
                            next_url = urljoin(current_url, link)
                        else:
                            next_url = link
                            
                        # Make sure URL is well-formed
                        try:
                            parsed_url = urlparse(next_url)
                            # Only process URLs from the same domain
                            if parsed_url.netloc == base_domain and next_url not in visited_urls:
                                # Add as a list instead of tuple to avoid LSP type error
                                to_visit.append([next_url, current_depth + 1])
                        except:
                            continue
                except Exception as e:
                    logger.error(f"Error extracting links from {current_url}: {str(e)}")
                    
        logger.info(f"Crawl completed. Processed {len(results)} pages out of {len(visited_urls)} visited.")
        return results
    except Exception as e:
        logger.error(f"Error crawling website {base_url}: {str(e)}")
        return []

def website_to_documents(url: str, max_pages: int = 10, max_depth: int = 2) -> List[Document]:
    """
    Convert website content to LangChain documents for the RAG pipeline.
    
    Args:
        url: The starting URL for crawling
        max_pages: Maximum number of pages to crawl
        max_depth: Maximum depth of crawling from the base URL
        
    Returns:
        List of LangChain Document objects
    """
    try:
        logger.info(f"Converting website {url} to documents")
        
        # For a single page
        if max_pages == 1 or max_depth == 0:
            content = get_website_text_content(url)
            if not content:
                logger.warning(f"No content extracted from {url}")
                return []
                
            # Create a document for single page
            return [Document(
                page_content=content,
                metadata={
                    "source": url,
                    "type": "website"
                }
            )]
            
        # For multiple pages (crawling)
        else:
            # Crawl the website
            crawl_results = crawl_website(url, max_pages=max_pages, max_depth=max_depth)
            if not crawl_results:
                logger.warning(f"No content extracted from crawling {url}")
                return []
                
            # Convert results to documents
            documents = []
            for result in crawl_results:
                doc = Document(
                    page_content=result["content"],
                    metadata={
                        "source": result["url"],
                        "type": "website"
                    }
                )
                documents.append(doc)
                
            logger.info(f"Created {len(documents)} documents from website {url}")
            return documents
    except Exception as e:
        logger.error(f"Error converting website to documents: {str(e)}")
        return []