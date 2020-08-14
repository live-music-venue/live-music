from django.contrib import admin
from .models import Musician, MusicianComment, Event, EventComment

# Register your models here.
admin.site.register(MusicianComment)
admin.site.register(EventComment)
admin.site.register(Musician)
admin.site.register(Event)
