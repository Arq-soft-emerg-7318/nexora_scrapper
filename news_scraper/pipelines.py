import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ApiPipeline:
    """Pipeline to send scraped articles to Java Spring Boot API"""
    
    def __init__(self):
        self.api_base = os.getenv('API_BASE', 'http://localhost:8080')
        self.api_key = os.getenv('API_KEY', '')
        self.api_endpoint = f"{self.api_base}/api/articles"
        
    def process_item(self, item, spider):
        """Send each article to the API"""
        try:
            # Prepare headers
            headers = {
                'Content-Type': 'application/json'
            }
            
            # Add Authorization header if API_KEY exists
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Prepare article data
            article_data = {
                "title": item.get('title', ''),
                "author": item.get('author', ''),
                "publishedAt": item.get('publishedAt', ''),
                "content_html": item.get('content_html', ''),
                "content_text": item.get('content_text', ''),
                "summary": item.get('summary', ''),
                "tags": item.get('tags', []),
                "images": item.get('images', []),
                "source": item.get('source', ''),
                "source_url": item.get('source_url', ''),
                "language": item.get('language', ''),
                "scraped_at": item.get('scraped_at', datetime.utcnow().isoformat() + 'Z')
            }
            
            # Send POST request
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=article_data,
                timeout=10
            )
            
            # Check response
            if response.status_code in [200, 201]:
                spider.logger.info(f"✓ Article sent successfully: {item.get('title', 'Unknown')[:50]}")
            else:
                spider.logger.error(f"✗ Failed to send article: {response.status_code} - {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            spider.logger.error(f"✗ Error sending article to API: {str(e)}")
        except Exception as e:
            spider.logger.error(f"✗ Unexpected error: {str(e)}")
            
        return item
