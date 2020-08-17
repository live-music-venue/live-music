"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import socketio

from django.core.wsgi import get_wsgi_application
from core.socketio import sio

application = socketio.WSGIApp(sio, get_wsgi_application())
