from django.shortcuts import render, redirect, get_object_or_404
from .models import Musician, MusicianComment, Event, EventComment
from .forms import MusicianForm, EventForm, DonationForm, MusicianCommentForm, EventCommentForm
from users.models import User
from django.views import View
from django.contrib.auth.decorators import login_required 
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.postgres.search import SearchVector
from random import shuffle
import json
import datetime
import os
from django import forms
from django.views.decorators.csrf import csrf_exempt
from geopy.geocoders import MapBox
from django.conf import settings
from django.core.mail import send_mail
from project.settings import EMAIL_HOST_USER
from django.utils.translation import gettext



# Create your views here.
class Homepage(View):
    def get(self, request):
        events = Event.objects.all().order_by("date_time")
        live_events = Event.objects.all().filter(in_progress=True)
        return render(request, 'core/homepage.html', {'events': events, 'live_events': live_events})

class HomepageRandom(View):
    def get(self, request):
        events = list(Event.objects.all())
        shuffle(events)
        return render(request, 'core/homepage_search.html', {'events': events, 'page_header': "Random Order:"})

class HomepageInProgress(View):
    def get(self, request):
        events = Event.objects.all().filter(in_progress=True)
        return render(request, 'core/homepage_search.html', {'events': events, 'page_header': "Live Now:"})

class HomepagePastEvents(View):
    def get(self, request):
        events = Event.objects.all().order_by("-date_time")
        return render(request, 'core/homepage_search.html', {'events': events, 'page_header': "Past Events:", "past_events" : True})



class EventPage(View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if request.user.is_authenticated:
            user_saved = request.user.is_save_event(event)
        else: 
            user_saved = None
        comment_form = EventCommentForm()
        musician = event.owner
        # Passing data through to react via json. MUST USE DOUBLE QUOTES
        return render(request, 'core/event.html', {
            'data': json.dumps({
                "eventId": pk,
                "ownerId": event.owner.user.id,
                "userId": request.user.id,
                "in_progress": event.in_progress,
                "port": os.getenv('PORT') if os.getenv('PORT') else 3000
            }), 
            "event": event,
            'comment_form': comment_form,
            'musician': musician,
            'user_saved': user_saved,
        })

    def post(self, request, pk):  
        event = get_object_or_404(Event, pk=pk)
        user_saved = request.user.is_save_event(event)
        events = Event.objects.all()
        comment_form = EventCommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.event = event
            new_comment.author = request.user
            new_comment.save()
            return redirect(to='event', pk=pk)
        else:
            comment_form = EventCommentForm()
    
        
        return render(request, 'core/event.html', {'event': event, 'comment_form': comment_form})


class AddEvent(View):
    form_title = gettext("Add an Event:")

    def get(self, request, musician_pk):
        musician = get_object_or_404(Musician, pk=musician_pk)
        if musician.user == request.user:
            form = EventForm()
            return render(request, 'core/event_add_edit.html', {"form": form, "musician": musician, "form_title": self.form_title, "edit": False})
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


def edit_event(request, event_pk):
    form_title = "Edit Event:"
    event = get_object_or_404(Event, pk=event_pk)
    musician = event.owner
    if request.user == musician.user:
        if request.method == "POST":
            form = EventForm(instance=event, data=request.POST, files=request.FILES)
            if form.is_valid():
                event = form.save(commit=False)
                event.owner = musician
                event = form.save()
                return redirect(to="event", pk=event.pk)
        else:
            form = EventForm(instance=event)
        return render(
            request,
            "core/event_add_edit.html",
            {"form": form, "event": event, "musician": musician, "form_title": form_title, "edit": True}  
        )
    return redirect(to="show-musician", musician_pk=event.owner.pk)


class SearchEvents(View):
    def get(self, request):
        query = request.GET.get('query')
        if query is not None:
            events = Event.objects.annotate(search=SearchVector("title", "description", "owner__name", "genre")).filter(search=query).distinct("id").order_by("-pk")
        else:
            events = None
        return render(request, 'core/homepage.html', {"events": events, "query": query or ""})


class AddMusicianInfo(View):
    title = "Add Musician Info:"

    def get(self, request, user_pk):
        if get_object_or_404(User, pk=user_pk) == request.user:
            form = MusicianForm()
            return render(request, 'core/musician_form.html', {"form": form, "form_title": self.title, "edit": False})
        return redirect(to="homepage")

    def post(self, request, user_pk):
        if get_object_or_404(User, pk=user_pk) == request.user:
            form = MusicianForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                mapbox_client = MapBox(settings.MAPBOX_API_KEY)
                musician = form.save(commit=False)
                result = mapbox_client.geocode(musician.city)               
                musician.latitude = result.latitude
                musician.longitude = result.longitude
                musician.user = request.user
                musician.save()
                return redirect(to='show-musician', musician_pk=musician.pk)
            return redirect(to="homepage")
        return redirect(to="homepage")


@method_decorator(csrf_exempt, name="dispatch")
class getGeocode(View):
    def post(self, request):
        mapbox_client = MapBox(settings.MAPBOX_API_KEY)
        location_json = json.loads(request.body)
        location = location_json["address"]
        result = mapbox_client.geocode(location)
        if result is None:   
            return JsonResponse({"valid": False})
        else:         
            latitude = result.latitude
            longitude = result.longitude
            return JsonResponse({"valid": True, "latitude": latitude, "longitude": longitude})


class ShowMusician(View):
    def get(self, request, musician_pk):
        musician = get_object_or_404(Musician, pk=musician_pk)
        events = list(musician.events.all())
        empty_list = []
        for event in events:
            empty_list.append({"start": event.date_time.strftime('%Y-%m-%dT%H:%M'), "url": f'/event/{event.pk}'})
        if request.user.is_authenticated:
            user_favorite = request.user.is_favorite_musician(musician)
        else: 
            user_favorite = None
        comment_form = MusicianCommentForm()
        return render(request, 'core/show_musician.html', {
                            'events': json.dumps(empty_list), 
            "musician": musician,'comment_form': comment_form, 'user_favorite': user_favorite})
        
    def post(self, request, musician_pk):  
        musician = get_object_or_404(Musician, pk=musician_pk)
        user_favorite = request.user.is_favorite_musician(musician)
        comment_form = MusicianCommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.musician = musician
            new_comment.author = request.user
            new_comment.save()
            send_mail(
                f'''{MusicianComment.author.username} has commented with the following:\n\n{MusicianComment.message}
                    \n\nYou can view all of your comments here:  http://127.0.0.1:3000/musician/{answer.question.pk}''',
                EMAIL_HOST_USER,
                [MusicianComment.message.author.email],
                fail_silently=False,
            )
            return redirect(to='show-musician', musician_pk= musician_pk)
        else:
            comment_form = MusicianCommentForm()
    
        
        return render(request, 'core/show_musician.html', {'musician': musician, 'comment_form': comment_form, 'user_favorite': user_favorite})


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


def donation_tutorial (request):
    return render(request, 'core/donation_tutorial.html')


@method_decorator(csrf_exempt, name="dispatch")
class FavoriteMusician(View):
    def get(self,request):
        user = request.user
        favorites = user.favorite_musician.all()
        saved_events = user.save_event.all()
        events = list(saved_events)
        empty_list = []
        for event in events:
            empty_list.append({"title": event.title, "start": event.date_time.strftime('%Y-%m-%dT%H:%M'), "url": f'/event/{event.pk}'})
        return render(request, "core/favorite_musicians.html", {
            'events': json.dumps(empty_list),
            "user":user, "favorites":favorites, "saved_events":saved_events,})
    
    def post(self, request, musician_pk):
        musician = get_object_or_404(Musician, pk=musician_pk)
        user = request.user
        if musician in user.favorite_musician.all():
            user.favorite_musician.remove(musician)
            return JsonResponse({"favorite": False})

        else:
            user.favorite_musician.add(musician)
            return JsonResponse({"favorite": True})


def edit_musician(request, musician_pk):
    form_title = "Edit Profile:"
    musician = get_object_or_404(Musician, pk=musician_pk)
    if request.user == musician.user:
        if request.method == "POST":
            form = MusicianForm(instance=musician, data=request.POST, files=request.FILES)
            if form.is_valid():
                musician = form.save(commit=False)
                musician.owner = musician
                musician = form.save()
                return redirect(to="show-musician", musician_pk=musician.user.pk)
        else:
            form = MusicianForm(instance=musician)
        return render(
            request,
            "core/musician_form.html",
            {"form": form, "musician": musician, "form_title": form_title, "edit": True}  
        )
    return redirect(to="show-musician", musician_pk=musician.user.pk)


def default_map(request):
    mapbox_access_token = 'pk.eyJ1IjoicmthcnVuYXJhdG5lIiwiYSI6ImNrZWFib21lYTAzYnkyc283YnQxNXcwNncifQ.sAFQ90D6ZledgFX1gaoNxw'
    musician_info = []
    musicians = Musician.objects.all()
    for musician in musicians:
        if musician.latitude:
            musician_info.append({"name": musician.name, 
                                    "latitude": musician.latitude, 
                                    "longitude": musician.longitude, 
                                    "pk": musician.pk,
                                    "hasUpcoming": musician_has_upcoming(musician),
                                    "thumb": musician.thumbnail.url})
    return render(request, 'core/map.html', 
            { 'mapbox_access_token': mapbox_access_token, "musician_info": musician_info })


@method_decorator(csrf_exempt, name="dispatch")
class SaveEvent(View):
    def post(self, request, event_pk):
        event = get_object_or_404(Event, pk=event_pk)
        user = request.user
        if event in user.save_event.all():
            user.save_event.remove(event)
            return JsonResponse({"saved": False})

        else:
            user.save_event.add(event)
            return JsonResponse({"saved": True})


@method_decorator(csrf_exempt, name="dispatch")
class SaveEventComment(View):
    def post(self, request, event_pk):
        event = get_object_or_404(Event, pk=event_pk)
        user = request.user
        message_json = json.loads(request.body)
        message = message_json["message"]
        new_comment = EventComment(message=message, author=user, event=event)
        new_comment.save()
        html = f'<p class="font-weight-bold"><span class=" text-muted font-weight-normal">{user.username} says: </span></p>{ message }'
        return JsonResponse({"html": html})


@method_decorator(csrf_exempt, name="dispatch")
class SaveMusicianComment(View):
    def post(self, request, musician_pk):
        musician = get_object_or_404(Musician, pk=musician_pk)
        user = request.user
        message_json = json.loads(request.body)
        message = message_json["message"]
        new_comment = MusicianComment(message=message, author=user, musician=musician)
        new_comment.save()
        html = f'<p class="font-weight-bold"><span class=" text-muted font-weight-normal">{user.username} says: </span></p>{ message }'
        return JsonResponse({"html": html})


def musician_has_upcoming(musician):
    events = musician.events.all()
    for event in events:
        if event.is_upcoming:
            return True
    return False
