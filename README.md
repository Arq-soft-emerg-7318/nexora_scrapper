# News Scraper - Web Scraping Simple

Proyecto Scrapy para extraer artículos de noticias de tecnología y minería, enviándolos automáticamente a una API Java Spring Boot.

## Sitios Web

- **Tecnología**: [Xataka](https://www.xataka.com)
- **Minería**: [Mining.com](https://www.mining.com)

## Requisitos

- Python 3.8+
- API Java Spring Boot funcionando

## Instalación

### 1. Crear entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 3. Instalar navegadores Playwright (opcional, solo si necesitas JavaScript)

```powershell
playwright install
```

### 4. Configurar variables de entorno

Copia el archivo de ejemplo y edita con tus valores:

```powershell
copy .env.example .env
```

Edita `.env`:
```
API_BASE=http://localhost:8080
API_KEY=tu_api_key_aqui
```

## Uso

### Ejecutar spider de Xataka

```powershell
scrapy crawl xataka_spider
```

### Ejecutar spider de Mining.com

```powershell
scrapy crawl mining_spider
```

### Ejecutar ambos spiders

```powershell
scrapy crawl xataka_spider
scrapy crawl mining_spider
```

## Estructura del Proyecto

```
WebScrapping/
├── news_scraper/
│   ├── spiders/
│   │   ├── __init__.py
│   │   ├── xataka_spider.py      # Spider para Xataka
│   │   └── mining_spider.py      # Spider para Mining.com
│   ├── __init__.py
│   ├── pipelines.py              # Pipeline para enviar a API
│   └── settings.py               # Configuración Scrapy
├── scrapy.cfg
├── requirements.txt
├── .env.example
└── README.md
```

## Esquema de Datos

Cada artículo se envía con el siguiente formato JSON:

```json
{
  "title": "Título del artículo",
  "author": "Autor",
  "publishedAt": "2025-11-30T10:00:00Z",
  "content_html": "<p>Contenido HTML...</p>",
  "content_text": "Contenido en texto plano...",
  "summary": "Resumen de 200-300 caracteres...",
  "tags": ["tag1", "tag2"],
  "images": [
    {"url": "https://...", "alt": "Descripción"}
  ],
  "source": "xataka.com",
  "source_url": "https://www.xataka.com/articulo",
  "language": "es",
  "scraped_at": "2025-11-30T12:00:00Z"
}
```

## API Backend

El scraper envía cada artículo vía POST a:

```
${API_BASE}/api/articles
```

Headers:
```
Content-Type: application/json
Authorization: Bearer ${API_KEY}
```

## Configuración

Puedes ajustar la configuración en `news_scraper/settings.py`:

- `CONCURRENT_REQUESTS`: Número de peticiones simultáneas
- `DOWNLOAD_DELAY`: Delay entre peticiones (segundos)
- `USER_AGENT`: User agent usado en las peticiones

## Notas

- El scraper extrae máximo 20 artículos por ejecución (configurable en cada spider)
- Los errores se registran en la consola
- Si la API no está disponible, el scraper continuará pero registrará los errores

## Solución de Problemas

### Error: Import "scrapy" could not be resolved

Asegúrate de haber activado el entorno virtual e instalado las dependencias:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Error al conectar con la API

Verifica que:
1. Tu API Spring Boot esté ejecutándose
2. Las variables `API_BASE` y `API_KEY` en `.env` sean correctas
3. El endpoint `/api/articles` acepte POST requests

### No se extraen artículos

Algunos sitios pueden cambiar su estructura HTML. Revisa los selectores CSS en los archivos de spider si no se extraen datos.
