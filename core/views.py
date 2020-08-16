from django.shortcuts import render, redirect, get_object_or_404
from .models import Musician, MusicianComment, Event, EventComment
from .forms import MusicianForm
from users.models import User
from django.views import View
import json

# Create your views here.
class Homepage(View):
    def get(self, request):
        return render(request, 'core/homepage.html')

class EventPage(View):
    def get(self, request, pk):

        return render(request, 'core/event.html')

class AddMusicianInfo(View):
    def get(self, request, user_pk):
        if get_object_or_404(User, pk=user_pk) == request.user:
            form = MusicianForm()
            return render(request, 'core/musician_form.html', {"form": form})
        return redirect(to="homepage")

    def post(self, request, user_pk):
        if get_object_or_404(User, pk=user_pk) == request.user:
            form = MusicianForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                musician = form.save(commit=False)
                musician.user = request.user
                musician.save()
                return redirect(to='show-musician', musician_pk=musician.pk)
            return redirect(to="homepage")
        return redirect(to="homepage")

class ShowMusician(View):
    def get(self, request, musician_pk):
        musician = get_object_or_404(Musician, pk=musician_pk)
        return render(request, 'core/show_musician.html', {"musician": musician})

        event = get_object_or_404(Event, pk=pk)
        # Passing data through to react via json. MUST USE DOUBLE QUOTES
        return render(request, 'core/event.html', {
            'data': json.dumps({
                "pk": pk,
                "ownerId": event.owner.user.id,
                "userId": request.user.id
            })
        })

