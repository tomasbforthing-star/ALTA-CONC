import sys
import os
from urllib.parse import parse_qs

# Add the root directory to the python path so it can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app

class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        query = environ.get('QUERY_STRING', '')
        qs = parse_qs(query)
        if '__endpoint' in qs and qs['__endpoint']:
            endpoint = qs['__endpoint'][0].lstrip('/')
            environ['PATH_INFO'] = f"/api/{endpoint}"
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
