from django.urls import path
from .views import *

urlpatterns = [
    path('register-customer/', register_customer_view, name = 'register-customer'),
    path('login/', login_view, name = 'login'),
    path('logout/', logout_view, name = 'logout'),
    path('change-password/', change_password_view, name = 'change-password'),
    path('update-profile/', update_profile_view, name = 'update-profile'),
    path('my-orders/', my_orders_view, name = 'my-orders')
]
