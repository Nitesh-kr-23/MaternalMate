# maternalmate/asgi.py
"""
ASGI config for maternalmate project.

ASGI (Asynchronous Server Gateway Interface) is the spiritual successor to WSGI,
designed to handle asynchronous web applications.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see:
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maternalmate.settings')

# Create ASGI application
application = get_asgi_application()


# ============================================================================
# ASGI vs WSGI:
# - ASGI: Supports async operations (WebSockets, HTTP/2, long polling)
# - WSGI: Traditional synchronous request/response
#
# For deployment with async features (like WebSockets), use ASGI servers:
# - Daphne
# - Uvicorn
# - Hypercorn
#
# Example deployment command:
# daphne -b 0.0.0.0 -p 8000 maternalmate.asgi:application
# ============================================================================