# Scrapy settings for news_scraper project

BOT_NAME = "news_scraper"

SPIDER_MODULES = ["news_scraper.spiders"]
NEWSPIDER_MODULE = "news_scraper.spiders"

# Crawl responsibly by identifying yourself
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16

# Configure a delay for requests
DOWNLOAD_DELAY = 1

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
}

# Enable or disable item pipelines
ITEM_PIPELINES = {
    "news_scraper.pipelines.ApiPipeline": 300,
}

# Set settings whose default value is deprecated
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Playwright settings (if needed)
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
}
