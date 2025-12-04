import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ApiPipeline:
    """Pipeline to send scraped articles to Java Spring Boot API as Posts"""
    
    def __init__(self):
        self.api_base = os.getenv('API_BASE', 'http://localhost:8080')
        self.api_token = os.getenv('API_TOKEN', '')  # JWT token
        self.author_id = int(os.getenv('AUTHOR_ID', '1'))  # ID del autor por defecto
        self.category_id = int(os.getenv('CATEGORY_ID', '1'))  # ID categoría tecnología/minería
        self.community_id = int(os.getenv('COMMUNITY_ID', '1'))  # ID comunidad
        self.api_endpoint = f"{self.api_base}/api/v1/posts"  # Ajusta según tu ruta
        
    def process_item(self, item, spider):
        """Send each article as a Post to the API"""
        try:
            # Prepare headers with JWT token
            headers = {
                'Authorization': f'Bearer {self.api_token}'
            }
            
            # Preparar el body del post (content_text o content_html)
            body_content = item.get('content_text', '')
            if not body_content:
                body_content = item.get('content_html', '')
            
            # Limitar body a primeros 5000 caracteres si es muy largo
            if len(body_content) > 5000:
                body_content = body_content[:5000] + "..."
            
            # Preparar el JSON para CreatePostResource
            post_data = {
                "title": item.get('title', 'Sin título')[:255],  # Limitar título
                "authorId": self.author_id,
                "body": body_content,
                "reactions": 0,
                "categoryId": self.category_id,
                "fileId": None,
                "communityId": self.community_id
            }
            
            # Crear multipart/form-data
            files = {
                'post': (None, json.dumps(post_data), 'application/json')
            }
            
            # Send POST request
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                files=files,
                timeout=15
            )
            
            # Check response
            if response.status_code in [200, 201]:
                spider.logger.info(f"✓ Post creado: {item.get('title', 'Unknown')[:50]}")
            else:
                spider.logger.error(f"✗ Error al crear post: {response.status_code} - {response.text[:300]}")
                
        except requests.exceptions.RequestException as e:
            spider.logger.error(f"✗ Error de conexión con API: {str(e)}")
        except Exception as e:
            spider.logger.error(f"✗ Error inesperado: {str(e)}")
            
        return item
