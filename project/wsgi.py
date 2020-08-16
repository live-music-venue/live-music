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

# Keep track of viewer counts on the server. This may not be the best idea but idk
viewer_counts = {}

# Join event room
@sio.event
def join_event(sid, eventId, userId, peerId):
    event = Event.objects.filter(pk=eventId).first()
    sio.save_session(sid, { 'userId': userId, 'eventId': eventId, 'peerId': peerId})
    sio.enter_room(sid, eventId)
    if event.owner.user.id == userId:
        viewer_counts[eventId] = 0
    else:
        viewer_counts[eventId] += 1
    sio.emit('user-connected', peerId, to=eventId, skip_sid=sid)
    sio.emit('update-viewer-count', viewer_counts[eventId], to=eventId)

# Send chat message. Possibly save as comment?
@sio.event
def send_chat(sid, message):
    session = sio.get_session(sid)
    sio.emit('recieve-chat-message', {'userId': session['userId'], 'message': message}, to=session['eventId'])

# Leave room on disconnect
@sio.event
def disconnect(sid):
    session = sio.get_session(sid)
    eventId = session['eventId']
    peerId = session['peerId']
    userId = session['userId']
    event = Event.objects.filter(pk=eventId).first()
    if event.owner.user.id == userId:
        del viewer_counts[eventId]
    else:
        viewer_counts[eventId] -= 1
    sio.emit('user-disconnected', peerId, to=eventId)
    sio.emit('update-viewer-count', viewer_counts[eventId], to=eventId)
    sio.leave_room(sid, eventId)