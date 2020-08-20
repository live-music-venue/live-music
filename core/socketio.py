import socketio
from .models import Event

sio = socketio.Server(async_mode=None, cors_allowed_origins='*')

# Keep track of viewer counts on the server. This may not be the best idea but idk
viewer_counts = {}

# Join event room
@sio.event
def join_event(sid, eventId, userId, peerId):
    print(peerId, "joining", eventId)
    event = Event.objects.filter(pk=eventId).first()
    if event.owner.user.id == userId:
        viewer_counts[eventId] = 0
    else:
        viewer_counts[eventId] += 1
    sio.save_session(sid, { 'userId': userId, 'eventId': eventId, 'peerId': peerId})
    sio.enter_room(sid, eventId)
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
    print(peerId, "leaving", eventId)
    event = Event.objects.filter(pk=eventId).first()
    if event.owner.user.id == userId:
        viewer_counts[eventId] = None
    else:
        viewer_counts[eventId] -= 1
    sio.emit('user-disconnected', peerId, to=eventId)
    sio.emit('update-viewer-count', viewer_counts[eventId], to=eventId)
    del viewer_counts[eventId]
    sio.leave_room(sid, eventId)
