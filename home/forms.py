from django import forms
from dal import autocomplete
from .models import City


#Form used for searching for a city on the homepage of the app
class CityForm(forms.ModelForm):
    class Meta:
        model = City

        fields = {'city',}
        labels = {'city':'',}

        widgets = {'city': autocomplete.ModelSelect2(
                    url='city-autocomplete', 
                    attrs={
                    'data-placeholder': 'Enter a city',
                    'data-minimum-input-length': 1,
                    'data-html': True,
                    },)
                  }
