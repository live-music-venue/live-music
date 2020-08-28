import os
import socketio
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .models import Event
from users.models import User
import array

sio = socketio.Server(async_mode=None, cors_allowed_origins='*')

# Keep track of viewer counts on the server. This may not be the best idea but idk
viewer_counts = {}

# Join event room
@sio.event
def join_event(sid, eventId, userId):
    print(userId, "joining", eventId, flush=True)
    sio.save_session(sid, { 'userId': userId, 'eventId': eventId, 'peerId': None })
    sio.enter_room(sid, eventId)

@sio.event
def join_stream(sid, peerId):
    session = sio.get_session(sid)
    userId = session['userId']
    eventId = session['eventId']
    print(peerId, 'joining stream', eventId, flush=True)
    filtered = Event.objects.filter(pk=eventId)
    if filtered.exists():
        event = filtered.first()
        if event.owner.user.id == userId:
            if event.archive:
                if event.video:
                    event.video.delete()
                event.video.save(f'archive_{eventId}.webm', File(open(os.devnull)))
                sio.save_session(sid, { 'userId': userId, 'eventId': eventId, 'peerId': peerId, 'video': event.video.open('ab') })
            viewer_counts[eventId] = 0
            event.in_progress = True
            event.save()
            sio.emit('host-connected', to=eventId)
        else:
            sio.save_session(sid, { 'userId': userId, 'eventId': eventId, 'peerId': peerId })
            viewer_counts[eventId] += 1
        sio.emit('user-connected', peerId, to=eventId, skip_sid=sid)
        sio.emit('update-viewer-count', viewer_counts[eventId], to=eventId)

# Append stream bytes to archive video file.
@sio.event
def save_blob(sid, blob):
    session = sio.get_session(sid)
    filtered = Event.objects.filter(pk=session['eventId'])
    if filtered.exists():
        event = filtered.first()
        if event.archive:
            f = session['video']
            f.write(blob)

# Send chat message. Possibly save as comment?
@sio.event
def send_message(sid, message):
    session = sio.get_session(sid)
    user = User.objects.filter(id=session['userId']).first()
    if len(message) <= 255:
        sio.emit('recieve-chat-message', {'userId': user.pk,'username': user.username, 'message': message}, to=session['eventId'], skip_sid=None)

# Leave room on disconnect
@sio.event
def disconnect(sid):
    session = sio.get_session(sid)
    eventId = session['eventId']
    peerId = session['peerId']
    userId = session['userId']
    print(userId, "leaving", eventId)
    filtered = Event.objects.filter(pk=eventId)
    if filtered.exists():
        event = filtered.first()
        if peerId:
            if event.owner.user.id == userId:
                if event.archive:
                    f = session['video']
                    f.close()
                sio.emit('host-disconnected', to=eventId)
                del viewer_counts[eventId]
                event.in_progress = False
                event.save()
            else:
                viewer_counts[eventId] -= 1
            sio.emit('user-disconnected', peerId, to=eventId)
            sio.emit('update-viewer-count', viewer_counts[eventId], to=eventId)
        sio.leave_room(sid, eventId)
