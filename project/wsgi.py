"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import socketio

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

sio = socketio.Server()

application = socketio.WSGIApp(sio, get_wsgi_application())

@sio.event
def connect(sid, env):
    print("socket connected:", sid)