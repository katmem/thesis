from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from .views import *

urlpatterns = [
    path('login/', login_view, name = 'login'),
    path('logout/', logout_view, name = 'logout'),
    path('shops/<city>/', shops_view, name='shops'),
    path('register-store/', register_store_view, name = 'register-store'),
    path('home/', home_business_view, name = 'home'),
    path('orders-by-date/', orders_by_date_view, name = 'orders-by-date'),
    path('todays-confirmed-orders/', todays_confirmed_orders_view, name = 'todays-confirmed-orders'),
    path('picked-up-orders/', picked_up_orders_view, name = 'picked-up-orders'),
    path('future-to-pick-up-orders/', future_to_pick_up_orders_view, name = 'future-to-pick-up-orders'),
    path('store-details/<store_id>/', store_details_view, name = 'store-details'),
    url(r'^store-info/(?P<id>\d+)/$', register_store_info_view, name = 'register-store-info'),
    
]
