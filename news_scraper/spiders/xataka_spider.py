import scrapy
from datetime import datetime


class XatakaSpider(scrapy.Spider):
    name = "xataka_spider"
    allowed_domains = ["xataka.com"]
    start_urls = ["https://www.xataka.com"]
    
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 10  # Solo 10 artículos
    }

    def parse(self, response):
        """Parse homepage and extract article links"""
        # Xataka uses article tags with specific classes
        article_links = response.css('article h2 a::attr(href)').getall()[:10]
        
        for url in article_links:
            yield response.follow(url, callback=self.parse_article)

    def parse_article(self, response):
        """Parse individual article page"""
        
        # Extract title
        title = response.css('h1.article-header__title::text').get()
        if not title:
            title = response.css('h1::text').get()
        
        # Extract author
        author = response.css('.article-header__author a::text').get()
        if not author:
            author = response.css('[rel="author"]::text').get()
        
        # Extract published date
        published_at = response.css('time::attr(datetime)').get()
        
        # Extract content
        content_paragraphs = response.css('article p::text, article p *::text').getall()
        content_text = ' '.join([p.strip() for p in content_paragraphs if p.strip()])
        
        content_html = ''.join(response.css('article p').getall())
        
        # Extract summary (first 250 chars)
        summary = content_text[:250] + '...' if len(content_text) > 250 else content_text
        
        # Extract tags
        tags = response.css('.article-tags a::text').getall()
        
        # Extract images
        images = []
        for img in response.css('article img'):
            img_url = img.css('::attr(src)').get()
            img_alt = img.css('::attr(alt)').get()
            if img_url:
                images.append({
                    'url': img_url,
                    'alt': img_alt or ''
                })
        
        # VALIDACIÓN: Rechazar artículos sin título válido
        if not title or len(title.strip()) == 0:
            self.logger.warning(f"⚠️  Artículo rechazado - Sin título: {response.url}")
            return
        
        # VALIDACIÓN: Rechazar artículos sin contenido suficiente (mínimo 100 caracteres)
        if not content_text or len(content_text.strip()) < 100:
            self.logger.warning(f"⚠️  Artículo rechazado - Contenido insuficiente: {title[:50]}")
            return
        
        # Si pasa validación, crear el item
        article = {
            'title': title.strip(),
            'author': author.strip() if author else 'Desconocido',
            'publishedAt': published_at or datetime.utcnow().isoformat() + 'Z',
            'content_html': content_html,
            'content_text': content_text,
            'summary': summary,
            'tags': tags,
            'images': images,
            'source': 'xataka.com',
            'source_url': response.url,
            'language': 'es',
            'scraped_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        self.logger.info(f"✅ Artículo válido extraído: {title[:50]}...")
        yield article
