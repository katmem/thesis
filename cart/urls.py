from django.urls import path
from .views import *

urlpatterns = [
    path('add_to_cart/<cart_id>/<id>/<quantity>/<options>', add_to_cart_view, name='add-to-cart'),
    path('update-product/<cart_item_id>/', update_product_view, name='update-product'),
    path('delete-product/<cart_item_id>/', delete_product_view, name='delete-product'),
    path('order-details/<cart_id>/', order_view, name='order'),
    path('pickup-time/<cart_id>/<pickup_id>/', order_time_view, name='order-time'),
    path('payment/<cart_id>/<pickup_id>/', payment_view, name='payment'),
]
