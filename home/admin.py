from django.contrib import admin
from .forms import CityForm
from .models import City

class CityAdmin(admin.ModelAdmin):
    form = CityForm
admin.site.register(City, CityAdmin)