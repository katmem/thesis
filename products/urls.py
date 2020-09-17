from django.contrib import admin
from django.urls import path
from .views import *
from django.conf.urls import url

urlpatterns = [
    path('detailpage/<slug>/', detailpage_view, name='detailpage'),
    path('price/', price_view, name = 'price'),
    path('edit-price/', edit_price_view, name = 'edit-price'),
    path('edit-menu/', edit_menu_view, name = 'edit-menu'),
    url(r'^menu-register/$', register_store_menu_view, name = 'register-store-menu'),
    url(r'^menu/edit/(?P<id>\d+)/$', register_store_menu_view, name = 'menu-edit'),
    url(r'^options-register/$', register_store_options_view, name = 'register-store-options'),
    url(r'^options/edit/(?P<id>\d+)/$', register_store_options_view, name = 'options-edit'),
    url(r'^delete-product-(?P<id>\d+)/$', delete_product_view, name = 'delete-product'),
]
