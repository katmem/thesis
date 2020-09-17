from django.contrib import admin
from .models import *

admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(IngredientsCategory)
admin.site.register(Ingredients)
admin.site.register(IngredientPrice)