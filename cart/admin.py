from django.contrib import admin
from .models import CartItem, Cart, PickUpTime, Order

admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(PickUpTime)
admin.site.register(Order)