from django.forms import ModelForm, Textarea, DateTimeInput
from .models import Musician, MusicianComment, Event, EventComment

class MusicianForm(ModelForm):
    class Meta:
        model = Musician
        fields = [
            "name",
            "bio",
            "city",
            "headshot",
        ]
# These next two can be used to tweak the size of the text area if we don't do
# it with CSS or add/remove a custom label.
        widgets = {
          'bio': Textarea(attrs={'rows':4, 'cols':50},),
        }
        # labels = {
        #     "bio": ""
        # }


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "date_time",
            "description",
            "cover_photo",
        ]
        widgets = {
            'date_time': DateTimeInput(attrs={"placeholder": "MM/DD/YYYY HH:MM"}),
        }
        labels = {
            "date_time" : "Date and time:",
            "description": "",
            "title": "         Title"
        }