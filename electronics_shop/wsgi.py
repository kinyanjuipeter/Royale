"""
WSGI config for electronics_shop project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import logging
import time
from django.core.wsgi import get_wsgi_application
from django.db import connection
from django.db.utils import OperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electronics_shop.settings')

logger = logging.getLogger(__name__)
logger.info('Starting WSGI application initialization')

# Test database connection
max_retries = 5
retry_delay = 2

for i in range(max_retries):
    try:
        connection.ensure_connection()
        logger.info('Database connection successful')
        break
    except OperationalError as e:
        if i == max_retries - 1:
            logger.error('Failed to connect to database after %s attempts: %s', max_retries, str(e))
            raise
        logger.warning('Database connection failed (attempt %s/%s), retrying...', i+1, max_retries)
        time.sleep(retry_delay)

# Initialize WSGI application
try:
    application = get_wsgi_application()
    logger.info('WSGI application initialized successfully')
except Exception as e:
    logger.error('Failed to initialize WSGI application: %s', str(e))
    raise

logger.info('Application is ready to serve requests')
