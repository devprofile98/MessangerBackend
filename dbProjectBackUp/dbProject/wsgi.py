"""
WSGI config for dbProject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

#sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dbProject.settings')

application = get_wsgi_application()
