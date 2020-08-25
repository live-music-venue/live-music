import socketio
from .models import Event
from users.models import User

sio = socketio.Server(async_mode=None, cors_allowed_origins='*')

# Keep track of viewer counts on the server. This may not be the best idea but idk
viewer_counts = {}

# Join event room
@sio.event
def join_event(sid, eventId, userId, peerId):
    sio.save_session(sid, { 'userId': userId, 'eventId': eventId, 'peerId': peerId})
    filtered = Event.objects.filter(pk=eventId)
    if filtered.exists():
        sio.enter_room(sid, eventId)
        event = filtered.first()
        if event.owner.user.id == userId:
            viewer_counts[eventId] = 0
            event.in_progress = True
            event.save()
            sio.emit('host-connected', to=eventId)
        else:
            viewer_counts[eventId] += 1
    else:
        return
    sio.emit('user-connected', peerId, to=eventId, skip_sid=sid)
    sio.emit('update-viewer-count', viewer_counts[eventId], to=eventId)

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
        sio.emit('user-disconnected', peerId, to=eventId)
        sio.emit('update-viewer-count', viewer_counts[eventId], to=eventId)
        sio.leave_room(sid, eventId)
