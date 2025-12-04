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
        self.api_base = os.getenv('API_BASE', 'https://nexora-gyhmeqctccb0b9g9.francecentral-01.azurewebsites.net')
        self.api_token = os.getenv('API_TOKEN', '')  # JWT token (opcional si endpoint es público)
        self.author_id = int(os.getenv('AUTHOR_ID', '1'))  # ID del autor por defecto
        self.category_id = int(os.getenv('CATEGORY_ID', '1'))  # ID categoría tecnología/minería
        self.community_id = int(os.getenv('COMMUNITY_ID', '1'))  # ID comunidad
        self.api_endpoint = f"{self.api_base}/api/v1/posts"
        
    def process_item(self, item, spider):
        """Send each article as a Post to the API"""
        
        # VALIDACIÓN FINAL: Verificar título y body antes de enviar
        title = item.get('title', '').strip()
        content_text = item.get('content_text', '').strip()
        
        # Rechazar si no hay título válido
        if not title or len(title) == 0:
            spider.logger.warning(f"⚠️  Pipeline - Post rechazado sin título: {item.get('source_url', 'unknown')}")
            return item
        
        # Rechazar si no hay contenido suficiente
        if not content_text or len(content_text) < 100:
            spider.logger.warning(f"⚠️  Pipeline - Post rechazado sin contenido suficiente: {title[:50]}")
            return item
        
        try:
            # Prepare headers
            headers = {
                'accept': 'application/json'
            }
            
            # Agregar token solo si existe
            if self.api_token:
                headers['Authorization'] = f'Bearer {self.api_token}'
            
            # Preparar el body del post (content_text limitado)
            body_content = content_text
            if not body_content:
                body_content = item.get('summary', '')
            
            # Limitar body a primeros 800 caracteres (2-3 párrafos aprox)
            if len(body_content) > 800:
                body_content = body_content[:800] + "..."
            
            # Preparar el JSON para CreatePostResource
            post_data = {
                "title": item.get('title', 'Sin título')[:255],  # Limitar título
                "authorId": self.author_id,
                "body": body_content,
                "reactions": 0,
                "categoryId": self.category_id,
                "fileId": 0,  # 0 en lugar de null
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
                timeout=30
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
