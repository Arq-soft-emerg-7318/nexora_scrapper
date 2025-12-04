import scrapy
from datetime import datetime


class XatakaSpider(scrapy.Spider):
    name = "xataka_spider"
    allowed_domains = ["xataka.com"]
    start_urls = ["https://www.xataka.com"]

    def parse(self, response):
        """Parse home page and follow article links"""
        # Extract article links from home page
        article_links = response.css('article a.article-link::attr(href)').getall()
        
        # Also try other common selectors
        if not article_links:
            article_links = response.css('h2 a::attr(href), h3 a::attr(href)').getall()
        
        # Follow each article link
        for link in article_links[:20]:  # Limit to 20 articles
            if link:
                yield response.follow(link, callback=self.parse_article)

    def parse_article(self, response):
        """Extract article data"""
        # Extract title
        title = response.css('h1::text, h1.article-title::text').get()
        if not title:
            title = response.css('title::text').get()
        title = title.strip() if title else ""

        # Extract author
        author = response.css('.author::text, [rel="author"]::text, .article-author::text').get()
        author = author.strip() if author else ""

        # Extract published date
        published_at = response.css('time::attr(datetime), meta[property="article:published_time"]::attr(content)').get()
        if not published_at:
            published_at = ""

        # Extract content HTML
        content_html = response.css('article .article-content, article .entry-content, .post-content').get()
        if not content_html:
            content_html = response.css('article').get()
        content_html = content_html if content_html else ""

        # Extract content text
        content_text = response.css('article .article-content ::text, article .entry-content ::text, .post-content ::text').getall()
        if not content_text:
            content_text = response.css('article ::text').getall()
        content_text = ' '.join([text.strip() for text in content_text if text.strip()])

        # Generate summary (first 250 chars)
        summary = content_text[:250] + "..." if len(content_text) > 250 else content_text

        # Extract tags
        tags = response.css('.tags a::text, .article-tags a::text, [rel="tag"]::text').getall()
        tags = [tag.strip() for tag in tags if tag.strip()]

        # Extract images
        images = []
        for img in response.css('article img, .article-content img'):
            img_url = img.css('::attr(src)').get()
            img_alt = img.css('::attr(alt)').get()
            if img_url:
                images.append({
                    "url": response.urljoin(img_url),
                    "alt": img_alt if img_alt else ""
                })

        # Create article item
        article = {
            "title": title,
            "author": author,
            "publishedAt": published_at,
            "content_html": content_html,
            "content_text": content_text,
            "summary": summary,
            "tags": tags,
            "images": images,
            "source": "xataka.com",
            "source_url": response.url,
            "language": "es",
            "scraped_at": datetime.utcnow().isoformat() + "Z"
        }

        yield article
