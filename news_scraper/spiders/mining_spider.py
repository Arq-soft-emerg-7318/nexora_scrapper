import scrapy
from datetime import datetime


class MiningSpider(scrapy.Spider):
    name = "mining_spider"
    allowed_domains = ["mining.com"]
    start_urls = ["https://www.mining.com"]

    def parse(self, response):
        """Parse home page and follow article links"""
        # Extract article links
        article_links = response.css('article a::attr(href), h2 a::attr(href), h3 a::attr(href), .post-title a::attr(href)').getall()
        
        # Follow each article link (limit to 20)
        seen = set()
        for link in article_links:
            if link and link not in seen and '/news/' in link or '/articles/' in link or len(seen) < 20:
                seen.add(link)
                yield response.follow(link, callback=self.parse_article)
                if len(seen) >= 20:
                    break

    def parse_article(self, response):
        """Extract article data"""
        # Extract title
        title = response.css('h1::text, h1.entry-title::text, h1.article-title::text').get()
        if not title:
            title = response.css('title::text').get()
        title = title.strip() if title else ""

        # Extract author
        author = response.css('.author::text, [rel="author"]::text, .byline::text, .entry-author::text').get()
        if not author:
            author = response.css('meta[name="author"]::attr(content)').get()
        author = author.strip() if author else ""

        # Extract published date
        published_at = response.css('time::attr(datetime), meta[property="article:published_time"]::attr(content)').get()
        if not published_at:
            published_at = response.css('.published::text, .date::text').get()
        published_at = published_at if published_at else ""

        # Extract content HTML
        content_html = response.css('article .entry-content, article .post-content, article .article-content, .main-content article').get()
        if not content_html:
            content_html = response.css('article').get()
        content_html = content_html if content_html else ""

        # Extract content text
        content_text = response.css('article .entry-content ::text, article .post-content ::text, article .article-content ::text').getall()
        if not content_text:
            content_text = response.css('article ::text').getall()
        content_text = ' '.join([text.strip() for text in content_text if text.strip()])

        # Generate summary (first 250 chars)
        summary = content_text[:250] + "..." if len(content_text) > 250 else content_text

        # Extract tags
        tags = response.css('.tags a::text, .post-tags a::text, [rel="tag"]::text, .entry-tags a::text').getall()
        tags = [tag.strip() for tag in tags if tag.strip()]

        # Extract images
        images = []
        for img in response.css('article img, .entry-content img, .post-content img'):
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
            "source": "mining.com",
            "source_url": response.url,
            "language": "en",
            "scraped_at": datetime.utcnow().isoformat() + "Z"
        }

        yield article
