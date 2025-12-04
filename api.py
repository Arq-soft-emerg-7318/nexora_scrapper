from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import threading
import subprocess
import os

app = FastAPI(title="News Scraper API", version="1.0.0")

# Variable global para controlar si hay un scraping en proceso
scraping_in_progress = False
scraping_results = {"status": "idle", "message": "No scraping in progress"}


def run_spider(spider_name: str):
    """Ejecuta un spider en un proceso separado"""
    global scraping_in_progress, scraping_results
    
    try:
        scraping_results = {
            "status": "running",
            "message": f"Scraping {spider_name}...",
            "spider": spider_name
        }
        
        # Ejecutar scrapy crawl en un subproceso
        result = subprocess.run(
            ["scrapy", "crawl", spider_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )
        
        if result.returncode == 0:
            scraping_results = {
                "status": "completed",
                "message": f"Scraping {spider_name} completed successfully",
                "spider": spider_name
            }
        else:
            scraping_results = {
                "status": "error",
                "message": f"Error scraping {spider_name}: {result.stderr}",
                "spider": spider_name
            }
    except Exception as e:
        scraping_results = {
            "status": "error",
            "message": f"Exception: {str(e)}",
            "spider": spider_name
        }
    finally:
        scraping_in_progress = False


@app.get("/")
def read_root():
    """Endpoint raíz"""
    return {
        "message": "News Scraper API",
        "endpoints": {
            "GET /scrape/xataka": "Scrape articles from Xataka",
            "GET /scrape/mining": "Scrape articles from Mining.com",
            "GET /scrape/all": "Scrape from both sources",
            "GET /status": "Get current scraping status"
        }
    }


@app.get("/scrape/xataka")
async def scrape_xataka(background_tasks: BackgroundTasks):
    """Endpoint para scrapear Xataka"""
    global scraping_in_progress
    
    if scraping_in_progress:
        return JSONResponse(
            status_code=409,
            content={"status": "error", "message": "Scraping already in progress"}
        )
    
    scraping_in_progress = True
    background_tasks.add_task(run_spider, "xataka_spider")
    
    return {
        "status": "started",
        "message": "Xataka scraping started",
        "spider": "xataka_spider"
    }


@app.get("/scrape/mining")
async def scrape_mining(background_tasks: BackgroundTasks):
    """Endpoint para scrapear Mining.com"""
    global scraping_in_progress
    
    if scraping_in_progress:
        return JSONResponse(
            status_code=409,
            content={"status": "error", "message": "Scraping already in progress"}
        )
    
    scraping_in_progress = True
    background_tasks.add_task(run_spider, "mining_spider")
    
    return {
        "status": "started",
        "message": "Mining.com scraping started",
        "spider": "mining_spider"
    }


@app.get("/scrape/all")
async def scrape_all(background_tasks: BackgroundTasks):
    """Endpoint para scrapear ambas fuentes"""
    global scraping_in_progress
    
    if scraping_in_progress:
        return JSONResponse(
            status_code=409,
            content={"status": "error", "message": "Scraping already in progress"}
        )
    
    scraping_in_progress = True
    
    # Ejecutar ambos spiders secuencialmente
    def run_both():
        global scraping_in_progress, scraping_results
        try:
            scraping_results = {"status": "running", "message": "Scraping both sources..."}
            
            # Xataka
            subprocess.run(
                ["scrapy", "crawl", "xataka_spider"],
                timeout=300
            )
            
            # Mining
            subprocess.run(
                ["scrapy", "crawl", "mining_spider"],
                timeout=300
            )
            
            scraping_results = {
                "status": "completed",
                "message": "Both sources scraped successfully"
            }
        except Exception as e:
            scraping_results = {
                "status": "error",
                "message": f"Error: {str(e)}"
            }
        finally:
            scraping_in_progress = False
    
    background_tasks.add_task(run_both)
    
    return {
        "status": "started",
        "message": "Scraping both sources started"
    }


@app.get("/status")
def get_status():
    """Obtener el estado actual del scraping"""
    return scraping_results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
