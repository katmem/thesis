from django.shortcuts import render, redirect
from .forms import CityForm
from cities_light.models import City
from django.contrib import messages
from dal import autocomplete
from stores_accounts.models import Store
from customers_accounts.models import User
from cart.models import Order

# View that handles city insertion on the homepage
def home_view(request):
    if request.user.is_authenticated:
        if request.user.business is True:
            return redirect('stores_accounts:home')
    if request.method == 'POST' and 'city_submit' in request.POST:
        city_form = CityForm(request.POST)
        if city_form.is_valid():
            city = City.objects.filter(id=request.POST.get('city')).first().display_name
            city_form.save()
            messages.success(request, 'Form successfully submited')
            return redirect('stores_accounts:shops', city=city)
        else:
            messages.error(request, 'Please fix your error')
    else:
        city_form = CityForm()

    num_store = Store.objects.all().count()
    num_people_served = Order.objects.all().count()
    num_registerd_users = User.objects.all().count()

    context = {'city_form':city_form, 'num_store':num_store, 'num_registerd_users':num_registerd_users, 'num_people_served':num_people_served}

    return render(request, 'home/index.html', context)


#Filters cities that start with the letters typed by the user
class CityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = City.objects.all()

        if self.q:
            qs = qs.filter(display_name__istartswith=self.q)

        return qs
