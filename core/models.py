from django.db import models
from users.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit, Transpose, SmartCrop, SmartResize, ResizeToCover
from datetime import datetime as datetime, timezone
import pytz



# Create your models here.
class Musician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField()
    city = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    # fields having to do with money
    cashapp_name = models.CharField(max_length=255, blank=True, null=True)
    paypal_donation_url = models.CharField(max_length=255, blank=True, null=True)
    cashapp_qr = models.ImageField(upload_to="images/", null=True, blank=True)
    paypal_qr = models.ImageField(upload_to="images/", null=True, blank=True)
    venmo_qr = models.ImageField(upload_to="images/", null=True, blank=True)
    favorited_by = models.ManyToManyField(User, related_name="favorite_musician", blank=True)
    
    # fields having to do with images
    headshot = models.ImageField(upload_to="images/", null=True, blank=False)
    thumbnail = ImageSpecField(
        source="headshot",
        processors=[Transpose(), ResizeToCover(200, 200), SmartCrop(200, 200)],
        format="JPEG",
        options={"quality": 100},
    )
    full_cover = ImageSpecField(
        source="headshot",
        processors=[Transpose(), ResizeToFit(600, 600), SmartCrop(400, 400)],
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
    save_event = models.ManyToManyField(User, related_name="save_event", blank=True)
    favorited_by = models.ManyToManyField(User, related_name="favorite_event", blank=True)
    in_progress = models.BooleanField(default=False)
    genre = models.CharField(max_length=255, null=True, blank=True)

    video = models.FileField(upload_to="videos/", null=True, blank=True)
    
    cover_photo = models.ImageField(upload_to="images/", null=True, blank=False)
    thumbnail = ImageSpecField(
        source="cover_photo",
        processors=[Transpose(), SmartResize(250, 188),],
        format="JPEG",
        options={"quality": 100},
    )
    full_cover = ImageSpecField(
        source="cover_photo",
        processors=[Transpose(), SmartResize(600, 480),],
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

    @property
    def is_finished(self):
        now = datetime.now()
        timezone = pytz.timezone("America/New_York")
        now_aware = timezone.localize(now)
        return self.date_time < now_aware and not self.in_progress


class EventComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_comments")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event_comments")
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} on {self.event}'


class MusicianComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="musician_comments")
    musician = models.ForeignKey(Musician, on_delete=models.CASCADE, related_name="musician_comments")
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_created']

    def __str__(self):
        return f'{self.author.username} on {self.musician}'