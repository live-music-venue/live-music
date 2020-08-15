from django.shortcuts import render
from .models import Musician, MusicianComment, Event, EventComment
from users.models import User
from django.views import View


# Create your views here.
class Homepage(View):
    def get(self, request):
        return render(request, 'core/homepage.html')