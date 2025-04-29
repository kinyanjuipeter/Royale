"""
WSGI config for electronics_shop project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import logging
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electronics_shop.settings')

logger = logging.getLogger(__name__)
logger.info('Starting WSGI application initialization')

try:
    application = get_wsgi_application()
    logger.info('WSGI application initialized successfully')
except Exception as e:
    logger.error('Failed to initialize WSGI application: %s', str(e))
    raise

logger.info('Application is ready to serve requests')
