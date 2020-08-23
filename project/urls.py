"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from core import views as core_views
from django.conf.urls.static import static



urlpatterns = [ 
    path('admin/', admin.site.urls),
    path('', core_views.Homepage.as_view(), name="homepage"),
    path('event/<int:pk>', core_views.EventPage.as_view(), name="event"),
    path('event/<int:event_pk>/edit', core_views.edit_event, name="edit-event"),
    path('musician/<int:musician_pk>/favorite', core_views.FavoriteMusician.as_view(), name='favorite-musician'),
    path('musician/<int:musician_pk>/event/add', core_views.AddEvent.as_view(), name="add-event"),
    path('musician/add/<int:user_pk>', core_views.AddMusicianInfo.as_view(), name="add-musician"),
    path('musician/<int:musician_pk>', core_views.ShowMusician.as_view(), name="show-musician"),
    path('musician/<int:musician_pk>/edit', core_views.edit_musician, name="edit-musician"),
    path('musician/<int:musician_pk>/donation/add', core_views.AddDonationInfo.as_view(), name="add-donation"),
    path('accounts/', include('allauth.urls')),
    path('donation-tutorial/', core_views.donation_tutorial, name="donation-tutorial"),
    path('favorite-musicians/', core_views.FavoriteMusician.as_view(), name="favorite-musicians"),    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
