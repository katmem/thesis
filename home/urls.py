from .views import *
from django.conf.urls import url

urlpatterns = [
	url(r'^city-autocomplete/$', CityAutocomplete.as_view(), name='city-autocomplete',),
    url(r'^$', home_view, name = 'home'),
]
