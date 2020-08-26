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
import json
import datetime
import os
from django import forms
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
class Homepage(View):
    def get(self, request):
        events = Event.objects.all().order_by("date_time")
        return render(request, 'core/homepage.html', {'events': events})


class EventPage(View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        comment_form = EventCommentForm()
        # Passing data through to react via json. MUST USE DOUBLE QUOTES
        return render(request, 'core/event.html', {
            'data': json.dumps({
                "eventId": pk,
                "ownerId": event.owner.user.id,
                "userId": request.user.id,
                "in_progress": event.in_progress,
                "shouldArchive": event.archive,
                "port": os.getenv('PORT') if os.getenv('PORT') else 3000
            }), 
            "event": event,
            'comment_form': comment_form
        })

    def post(self, request, pk):  
        event = get_object_or_404(Event, pk=pk)
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
                musician = form.save(commit=False)
                musician.user = request.user
                musician.save()
                return redirect(to='show-musician', musician_pk=musician.pk)
            return redirect(to="homepage")
        return redirect(to="homepage")



class ShowMusician(View):
    def get(self, request, musician_pk):
        musician = get_object_or_404(Musician, pk=musician_pk)
        if request.user.is_authenticated:
            user_favorite = request.user.is_favorite_musician(musician)
        else: 
            user_favorite = None
        comment_form = MusicianCommentForm()
        return render(request, 'core/show_musician.html', {"musician": musician,'comment_form': comment_form, 'user_favorite': user_favorite})
        
    def post(self, request, musician_pk):  
        musician = get_object_or_404(Musician, pk=musician_pk)
        user_favorite = request.user.is_favorite_musician(musician)
        comment_form = MusicianCommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.musician = musician
            new_comment.author = request.user
            new_comment.save()
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
        return render(request, "core/favorite_musicians.html", {"user":user, "favorites":favorites})
    
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


# class EditMusician(View):
#     def get(self, request, musician_pk):
#         musician = get_object_or_404(Musician, pk=musician_pk)
#         if musician == request.user:
#             form = MusicianForm(instance=musician)
#             return render(request, 'core/edit_musician.html', {"form": form, "musician": musician})
#         return redirect(to="homepage")

#     def post(self, request, musician_pk):
#         musician = get_object_or_404(Musician, pk=musician_pk)
#         if get_object_or_404(Musician, pk=musician_pk) == request.user:
#             form = MusicianForm(instance=musician, data=request.POST, files=request.FILES)
#             if form.is_valid():
#                 musician = form.save(commit=False)
#                 musician.user = request.user
#                 musician.save()
#                 return redirect(to='show-musician', musician_pk=musician.pk)
#             return redirect(to="homepage")
#         return redirect(to="homepage")

