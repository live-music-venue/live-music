from django.db import models
from users.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit, Transpose
from datetime import datetime as datetime, timezone
import pytz



# Create your models here.
class Musician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField()
    city = models.CharField(max_length=255)

    headshot = models.ImageField(upload_to="images/", null=True, blank=False)
    thumbnail = ImageSpecField(
        source="headshot",
        processors=[ResizeToFit(200, 200),
                    Transpose()],
        format="JPEG",
        options={"quality": 100},
    )
    full_cover = ImageSpecField(
        source="headshot",
        processors=[ResizeToFit(400, 400),
                    Transpose()],
        format="JPEG",
        options={"quality": 100},
    )

    def __str__(self):
        return f'{self.name}'


class Event(models.Model):
    owner = models.ForeignKey(Musician, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    description = models.TextField()
    public = models.BooleanField(default=True)
    thumbs_up = models.ManyToManyField(User, related_name="thumbs_up", blank=True)
    favorited_by = models.ManyToManyField(User, related_name="favorite_event", blank=True)

    video = models.FileField(upload_to="videos/", null=True, blank=True)
    
    cover_photo = models.ImageField(upload_to="images/", null=True, blank=False)
    thumbnail = ImageSpecField(
        source="cover_photo",
        processors=[ResizeToFit(200, 200),
                    Transpose()],
        format="JPEG",
        options={"quality": 100},
    )
    full_cover = ImageSpecField(
        source="cover_photo",
        processors=[ResizeToFit(400, 400),
                    Transpose()],
        format="JPEG",
        options={"quality": 100},
    )

    def __str__(self):
        return f'{self.title} by {self.owner.user.username}'

    @property
    def is_upcoming(self):
        now = datetime.now()
        timezone = pytz.timezone("America/New_York")
        now_aware = timezone.localize(now)
        return self.date_time > now_aware

    #will need modification once in_progress is added to model
    @property
    def is_finished(self):
        now = datetime.now()
        timezone = pytz.timezone("America/New_York")
        now_aware = timezone.localize(now)
        return self.date_time < now_aware


class EventComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_comments")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event_comments")
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} on {self.event}'


class MusicianComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="musician_comments")
    musician = models.ForeignKey(Musician, on_delete=models.CASCADE, related_name="musician_comments")
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} on {self.musician}'