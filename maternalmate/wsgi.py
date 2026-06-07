# maternalmate/wsgi.py
"""
WSGI config for maternalmate project.

WSGI (Web Server Gateway Interface) is the Python standard for web servers
and web applications to communicate.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see:
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Set the default Django settings module for the 'wsgi' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maternalmate.settings')

# Create WSGI application
application = get_wsgi_application()


# ============================================================================
# PRODUCTION DEPLOYMENT NOTES:
#
# For deploying with traditional web servers, use WSGI servers like:
#
# 1. Gunicorn (Recommended for production):
#    gunicorn maternalmate.wsgi:application --bind 0.0.0.0:8000
#
# 2. uWSGI:
#    uwsgi --http :8000 --module maternalmate.wsgi
#
# 3. Apache with mod_wsgi:
#    Configure in Apache's httpd.conf or virtual host file
#
# 4. Nginx + Gunicorn (Most common production setup):
#    - Nginx as reverse proxy
#    - Gunicorn serving Django application
#
# Example Gunicorn configuration (gunicorn.conf.py):
# ---------------------------------------------------
# bind = "0.0.0.0:8000"
# workers = 4
# worker_class = "sync"
# worker_connections = 1000
# timeout = 30
# keepalive = 2
# errorlog = "/var/log/gunicorn/error.log"
# accesslog = "/var/log/gunicorn/access.log"
# ============================================================================