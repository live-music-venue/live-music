import socketio
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .models import Event
from users.models import User

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
    print(peerId, "joining stream", eventId, flush=True)
    filtered = Event.objects.filter(pk=eventId)
    if filtered.exists():
        event = filtered.first()
        if event.owner.user.id == userId:
            path = default_storage.save(f'videos/{eventId}.webm', ContentFile(b''))
            sio.save_session(sid, { 'userId': userId, 'eventId': eventId, 'peerId': peerId, 'archiveFile': default_storage.open(path, 'rwb') })
            viewer_counts[eventId] = 0
            event.in_progress = True
            event.save()
            sio.emit('host-connected', to=eventId)
        else:
            sio.save_session(sid, { 'userId': userId, 'eventId': eventId, 'peerId': peerId })
            viewer_counts[eventId] += 1
    else:
        return
    sio.emit('user-connected', peerId, to=eventId, skip_sid=sid)
    sio.emit('update-viewer-count', viewer_counts[eventId], to=eventId)

# Append stream bytes to archive video file
@sio.event
def save_blob(sid, eventId, blob):
    with open('/Users/tgrantham/video.webm', 'ab') as f:
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
    if session:
        eventId = session['eventId']
        peerId = session['peerId']
        userId = session['userId']
        filtered = Event.objects.filter(pk=eventId)
        if filtered.exists():
            event = filtered.first()
            if event.owner.user.id == userId:
                sio.emit('host-disconnected', to=eventId)
                del viewer_counts[eventId]
                event.in_progress = False
                event.save()
            else:
                viewer_counts[eventId] -= 1
        else:
            return
        if peerId:
            sio.emit('user-disconnected', peerId, to=eventId)
            sio.emit('update-viewer-count', viewer_counts[eventId], to=eventId)
        sio.leave_room(sid, eventId)
