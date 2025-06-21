#!/usr/bin/env python3
"""
Web Crawler for Search Engine MVP
Crawls websites and indexes content in Meilisearch
"""

import os
import time
import uuid
import hashlib
import logging
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse, urlunparse
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
import meilisearch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CrawlConfig:
    """Configuration for the crawler"""
    meilisearch_url: str = os.getenv('MEILISEARCH_URL', 'http://meilisearch:7700')
    meilisearch_key: str = os.getenv('MEILISEARCH_KEY', 'masterKey123')
    index_name: str = os.getenv('INDEX_NAME', 'documents')
    max_pages: int = int(os.getenv('MAX_PAGES', '50'))
    delay_seconds: float = float(os.getenv('CRAWL_DELAY', '1.0'))
    timeout_seconds: int = int(os.getenv('REQUEST_TIMEOUT', '10'))
    user_agent: str = os.getenv('USER_AGENT', 'SearchEngine-Crawler/1.0')

@dataclass
class Document:
    """Represents a crawled document"""
    id: str
    title: str
    content: str
    url: str
    timestamp: str
    word_count: int
    content_hash: str

class WebCrawler:
    """Web crawler that indexes content in Meilisearch"""
    
    def __init__(self, config: CrawlConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })
        
        # Initialize Meilisearch client
        self.client = meilisearch.Client(
            config.meilisearch_url,
            config.meilisearch_key
        )
        
        # Track crawled URLs to avoid duplicates
        self.crawled_urls: Set[str] = set()
        self.documents: List[Document] = []
        
    def setup_index(self) -> None:
        """Setup the Meilisearch index with proper configuration"""
        try:
            # Get or create index
            index = self.client.index(self.config.index_name)
            
            # Configure searchable attributes
            index.update_searchable_attributes([
                'title',
                'content',
                'url'
            ])
            
            # Configure filterable attributes
            index.update_filterable_attributes([
                'url',
                'timestamp',
                'word_count'
            ])
            
            # Configure sortable attributes
            index.update_sortable_attributes([
                'timestamp',
                'word_count'
            ])
            
            logger.info(f"Index '{self.config.index_name}' configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup index: {e}")
            raise
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and should be crawled"""
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in ('http', 'https') and
                parsed.netloc and
                not any(ext in url.lower() for ext in [
                    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
                    '.ppt', '.pptx', '.zip', '.tar', '.gz',
                    '.jpg', '.jpeg', '.png', '.gif', '.bmp',
                    '.mp4', '.avi', '.mov', '.mp3', '.wav'
                ])
            )
        except:
            return False
    
    def extract_content(self, html: str, url: str) -> Optional[Dict[str, str]]:
        """Extract title and content from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else urlparse(url).netloc
            
            # Extract main content
            # Try to find main content areas
            content_selectors = [
                'main', 'article', '[role="main"]',
                '.main-content', '.content', '.post-content',
                '#main', '#content', '#post'
            ]
            
            content_text = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content_text = content_elem.get_text()
                    break
            
            # Fallback to body if no main content found
            if not content_text:
                body = soup.find('body')
                content_text = body.get_text() if body else soup.get_text()
            
            # Clean up content
            content_text = ' '.join(content_text.split())
            
            # Skip if content is too short
            if len(content_text) < 100:
                return None
            
            return {
                'title': title[:200],  # Limit title length
                'content': content_text[:5000]  # Limit content length
            }
            
        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {e}")
            return None
    
    def crawl_url(self, url: str) -> Optional[Document]:
        """Crawl a single URL and extract content"""
        if url in self.crawled_urls or not self.is_valid_url(url):
            return None
        
        self.crawled_urls.add(url)
        
        try:
            logger.info(f"Crawling: {url}")
            
            response = self.session.get(
                url,
                timeout=self.config.timeout_seconds,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logger.warning(f"Skipping non-HTML content: {url}")
                return None
            
            # Extract content
            extracted = self.extract_content(response.text, url)
            if not extracted:
                return None
            
            # Create document
            content_hash = hashlib.md5(extracted['content'].encode()).hexdigest()
            doc_id = str(uuid.uuid4())
            
            document = Document(
                id=doc_id,
                title=extracted['title'],
                content=extracted['content'],
                url=url,
                timestamp=str(int(time.time())),
                word_count=len(extracted['content'].split()),
                content_hash=content_hash
            )
            
            logger.info(f"Extracted content from {url}: {len(extracted['content'])} chars")
            return document
            
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error crawling {url}: {e}")
            return None
    
    def index_documents(self, documents: List[Document]) -> None:
        """Index documents in Meilisearch"""
        if not documents:
            return
        
        try:
            index = self.client.index(self.config.index_name)
            
            # Convert documents to dictionaries
            docs = []
            for doc in documents:
                docs.append({
                    'id': doc.id,
                    'title': doc.title,
                    'content': doc.content,
                    'url': doc.url,
                    'timestamp': doc.timestamp,
                    'word_count': doc.word_count,
                    'content_hash': doc.content_hash
                })
            
            # Add documents to index
            task = index.add_documents(docs)
            logger.info(f"Indexing {len(docs)} documents, task ID: {task.task_uid}")
            
            # Wait for indexing to complete
            while True:
                task_status = index.get_task(task.task_uid)
                if task_status.status in ['succeeded', 'failed']:
                    break
                time.sleep(1)
            
            if task_status.status == 'succeeded':
                logger.info(f"Successfully indexed {len(docs)} documents")
            else:
                logger.error(f"Indexing failed: {task_status.error}")
                
        except Exception as e:
            logger.error(f"Failed to index documents: {e}")
    
    def crawl_seed_urls(self, seed_urls: List[str]) -> None:
        """Crawl a list of seed URLs"""
        logger.info(f"Starting crawl with {len(seed_urls)} seed URLs")
        
        crawled_count = 0
        batch_size = 10
        
        for url in seed_urls:
            if crawled_count >= self.config.max_pages:
                break
            
            document = self.crawl_url(url)
            if document:
                self.documents.append(document)
                crawled_count += 1
                
                # Index in batches
                if len(self.documents) >= batch_size:
                    self.index_documents(self.documents)
                    self.documents = []
            
            # Rate limiting
            time.sleep(self.config.delay_seconds)
        
        # Index remaining documents
        if self.documents:
            self.index_documents(self.documents)
        
        logger.info(f"Crawl completed. Processed {crawled_count} pages")

def get_default_seed_urls() -> List[str]:
    """Get default list of URLs to crawl"""
    return [
        # News and Information
        'https://en.wikipedia.org/wiki/Artificial_intelligence',
        'https://en.wikipedia.org/wiki/Machine_learning',
        'https://en.wikipedia.org/wiki/Web_search_engine',
        'https://en.wikipedia.org/wiki/Information_retrieval',
        
        # Technology
        'https://stackoverflow.com/questions/tagged/python',
        'https://stackoverflow.com/questions/tagged/javascript',
        'https://stackoverflow.com/questions/tagged/react',
        'https://stackoverflow.com/questions/tagged/golang',
        
        # Documentation (if accessible)
        'https://docs.python.org/3/tutorial/',
        'https://reactjs.org/docs/getting-started.html',
        
        # Blogs and Articles (add your preferred sources)
        'https://dev.to/t/python',
        'https://dev.to/t/webdev',
    ]

def main():
    """Main crawler function"""
    config = CrawlConfig()
    crawler = WebCrawler(config)
    
    try:
        # Setup index
        crawler.setup_index()
        
        # Get seed URLs
        seed_urls = get_default_seed_urls()
        
        # Add custom URLs from environment
        custom_urls = os.getenv('SEED_URLS', '')
        if custom_urls:
            seed_urls.extend(url.strip() for url in custom_urls.split(','))
        
        logger.info(f"Starting crawler with configuration:")
        logger.info(f"  Meilisearch URL: {config.meilisearch_url}")
        logger.info(f"  Index name: {config.index_name}")
        logger.info(f"  Max pages: {config.max_pages}")
        logger.info(f"  Delay: {config.delay_seconds}s")
        
        # Start crawling
        crawler.crawl_seed_urls(seed_urls)
        
        logger.info("Crawler finished successfully")
        
    except KeyboardInterrupt:
        logger.info("Crawler interrupted by user")
    except Exception as e:
        logger.error(f"Crawler failed: {e}")
        raise

if __name__ == '__main__':
    main() 