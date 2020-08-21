from django.shortcuts import render, redirect, get_object_or_404
from .models import Musician, MusicianComment, Event, EventComment
from .forms import MusicianForm, EventForm, DonationForm
from users.models import User
from django.views import View
from django.contrib.auth.decorators import login_required 
import json
import datetime
import os

# Create your views here.
class Homepage(View):
    def get(self, request):
        today_date_time = datetime.datetime.now()
        events = Event.objects.all()
        return render(request, 'core/homepage.html', {'events': events})


class EventPage(View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        # Passing data through to react via json. MUST USE DOUBLE QUOTES
        return render(request, 'core/event.html', {
            'data': json.dumps({
                "pk": pk,
                "ownerId": event.owner.user.id,
                "userId": request.user.id,
                "port": os.getenv('PORT') if os.getenv('PORT') else 3000
            }), 
            "event": event,
        })


class AddEvent(View):
    form_title = "Add an Event:"

    def get(self, request, musician_pk):
        musician = get_object_or_404(Musician, pk=musician_pk)
        if musician.user == request.user:
            form = EventForm()
            return render(request, 'core/event_add_edit.html', 
                            {"form": form, "musician": musician, "form_title": self.form_title, "edit": False})
        return redirect(to="show-musician", musician_pk=musician_pk)

    def post(self, request, musician_pk):
        musician = get_object_or_404(Musician, pk=musician_pk)
        if musician.user == request.user:
            form = EventForm(data=request.POST, files=request.FILES)
            print(request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.owner = musician
                event.save()
                return redirect(to="event", pk=event.pk)
            return redirect(to="show-musician", musician_pk=musician_pk)
        return redirect(to="show-musician", musician_pk=musician_pk)


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


class AddDonationInfo(View):
    def get(self, request, musician_pk):
        print("post attempt")        
        musician = get_object_or_404(Musician, pk=musician_pk)
        if musician.user == request.user:
            form = DonationForm(instance=musician)
            return render(request, 'core/donation_form.html', {"form": form , "musician": musician})
        return redirect(to="homepage")

    def post(self, request, musician_pk):
        musician = get_object_or_404(Musician, pk=musician_pk)
        print("post attempt")
        # if musician.user == request.user:
        form = DonationForm(instance=musician, data=request.POST, files=request.FILES)
        if form.is_valid():
            musician = form.save(commit=False)
            musician.user = request.user
            musician.save()
            return redirect(to='show-musician', musician_pk=musician_pk)
            # return redirect(to="homepage")
        return redirect(to="homepage")


def edit_event(request, event_pk):
    form_title = "Edit Event:"
    event = get_object_or_404(Event, pk=event_pk)
    musician = event.owner
    if request.method == "POST":
        form = EventForm(instance=event, data=request.POST, files=request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.owner = musician
            event = form.save()
            return redirect(to="show-musician", musician_pk=event.owner.pk)
    else:
        form = EventForm(instance=event)

    return render(
        request,
        "core/event_add_edit.html",
        {"form": form, "event": event, "musician": musician, "form_title": form_title, "edit": True}  
    )


