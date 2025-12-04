import scrapy
from datetime import datetime


class MiningSpider(scrapy.Spider):
    name = "mining_spider"
    allowed_domains = ["mining.com"]
    start_urls = ["https://www.mining.com"]
    
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 10  # Solo 10 artículos
    }

    def parse(self, response):
        """Parse homepage and extract article links"""
        # Mining.com article links
        article_links = response.css('article h3 a::attr(href), article h2 a::attr(href)').getall()[:10]
        
        for url in article_links:
            if url.startswith('/'):
                url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.parse_article)

    def parse_article(self, response):
        """Parse individual article page"""
        
        # Extract title
        title = response.css('h1.entry-title::text').get()
        if not title:
            title = response.css('h1::text').get()
        
        # Extract author
        author = response.css('.author a::text').get()
        if not author:
            author = response.css('[rel="author"]::text').get()
        
        # Extract published date
        published_at = response.css('time::attr(datetime)').get()
        
        # Extract content
        content_paragraphs = response.css('.entry-content p::text, .entry-content p *::text').getall()
        content_text = ' '.join([p.strip() for p in content_paragraphs if p.strip()])
        
        content_html = ''.join(response.css('.entry-content p').getall())
        
        # Extract summary
        summary = content_text[:250] + '...' if len(content_text) > 250 else content_text
        
        # Extract tags
        tags = response.css('.tags a::text, .entry-meta a[rel="tag"]::text').getall()
        
        # Extract images
        images = []
        for img in response.css('.entry-content img'):
            img_url = img.css('::attr(src)').get()
            img_alt = img.css('::attr(alt)').get()
            if img_url:
                images.append({
                    'url': img_url,
                    'alt': img_alt or ''
                })
        
        yield {
            'title': title.strip() if title else 'No title',
            'author': author.strip() if author else 'Unknown',
            'publishedAt': published_at or datetime.utcnow().isoformat() + 'Z',
            'content_html': content_html,
            'content_text': content_text,
            'summary': summary,
            'tags': tags,
            'images': images,
            'source': 'mining.com',
            'source_url': response.url,
            'language': 'en',
            'scraped_at': datetime.utcnow().isoformat() + 'Z'
        }
