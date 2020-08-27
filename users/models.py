from django.db import models
from django.contrib.auth.models import AbstractUser

# Consider creating a custom user model from scratch as detailed at
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#specifying-a-custom-user-model


class User(AbstractUser):
    def is_favorite_musician(self, musician):
        return self.favorite_musician.filter(pk=musician.pk).count() == 1


    def is_save_event(self, event):
        return self.save_event.filter(pk=event.pk).count() == 1
