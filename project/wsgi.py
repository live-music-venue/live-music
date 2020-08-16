"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import socketio

from django.core.wsgi import get_wsgi_application
from core.models import Event

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

sio = socketio.Server()

application = socketio.WSGIApp(sio, get_wsgi_application())

# Join event room
@sio.event
def join_event(sid, eventId, userId, peerId):
    event = Event.objects.filter(pk=eventId).first()
    print(userId, "joining", eventId)
    sio.save_session(sid, { 'userId': userId, 'eventId': eventId, 'peerId': peerId})
    sio.enter_room(sid, eventId)
    sio.emit('user-connected', peerId, to=eventId, skip_sid=sid)

# Send chat message. Possibly save as comment?
@sio.event
def send_chat(sid, message):
    session = sio.get_session(sid)
    sio.emit
    sio.emit('recieve-chat-message', {'userId': session['userId']}, to=session['eventId'])

# Leave room on disconnect
@sio.event
def disconnect(sid):
    session = sio.get_session(sid)
    eventId = session['eventId']
    userId = session['userId']
    peerId = session['peerId']
    print(peerId)
    print(userId, "leaving", eventId)
    sio.leave_room(sid, eventId)