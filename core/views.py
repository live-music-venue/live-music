from django.shortcuts import render, get_object_or_404
from .models import Musician, MusicianComment, Event, EventComment
from users.models import User
from django.views import View
import json

# Create your views here.
class Homepage(View):
    def get(self, request):
        return render(request, 'core/homepage.html')

class EventPage(View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        # Passing data through to react via json. MUST USE DOUBLE QUOTES
        return render(request, 'core/event.html', {
            'data': json.dumps({
                "pk": pk,
                "ownerId": event.owner.user.id,
                "userId": request.user.id
            })
        })