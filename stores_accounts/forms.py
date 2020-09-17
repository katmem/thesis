from django import forms
from .models import Store, OpeningTime
from django.forms import modelformset_factory
from customers_accounts.models import User


"""
Form used for registering or updating a store's info. It contains the following fields: name, phone, email, description, categories,
city, address, address number, zipcode and photo of the store. "clean_email" method checks whether the email entered in ths form
is different than the logged in user's email. If so, a query is used for finding if entered email is already used by another user,
so that a validation error is raised. 
"""
class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'phone', 'email', 'description', 'categories', 'city', 'address', 'addressNum', 'postcode', 'photo']

        labels = {'name':'', 'phone':'', 'email':'', 'description':'', 'categories':'', 
        'city': '', 'address':'', 'addressNum':'', 'postcode':'', 'photo':'',}

        widgets = {
        'categories': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user') 
        super(StoreForm, self).__init__(*args, **kwargs) 
      

    def clean_email(self):
        email = self.cleaned_data['email']
        if email != self.user.email:
            if User.objects.filter(email = email):
                raise forms.ValidationError('This email already exists.')

        return email

"""
Formset for registering or updating store's opening hours. It consists of 14 forms, of which at least one should not be empty. For
every day of the week there can be filled two forms. For example, Monday 08:00-13:00 and Monday 17:00-21:00.
"""
OpeningTimeFormset = modelformset_factory(
    OpeningTime,
    fields=('weekday', 'from_hour', 'to_hour', ),
    labels = {'weekday':'','from_hour':'', 'to_hour':'',},
    min_num=1,    
    extra=13,
    widgets={'weekday': forms.Select(),
    'from_hour': forms.TextInput(attrs = {'placeholder':'Opening Hour'}),
    'to_hour': forms.TextInput(attrs = {'placeholder':'Closing Hour'}),
    },
)
