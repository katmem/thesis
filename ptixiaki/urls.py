from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from home.views import CityAutocomplete


urlpatterns = [
    path('admin/', admin.site.urls),
    path('customers_accounts/', include(('customers_accounts.urls', 'customers_accounts'), namespace = 'customers_accounts')),
    path('stores_accounts/', include(('stores_accounts.urls', 'stores_accounts'), namespace = 'stores_accounts')),
    path('products/', include(('products.urls', 'products'), namespace = 'products')),
    path('cart/', include(('cart.urls', 'cart'), namespace = 'cart')),
    path('', include(('home.urls', 'home'), namespace = '')),
    url(r'^city-autocomplete/$', CityAutocomplete.as_view(), name='city-autocomplete',),
]

urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)