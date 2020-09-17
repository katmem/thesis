from django.contrib import admin
from .models import StoreCategory, Store, OpeningTime
from products.models import Product

# Register your models here.
#Δημιουργία inline ώστε να μπορώ να βλέπω ποια καταστήματα ανήκουν σε κάθε κατηγορία και όχι μόνο το αντίθετο
class StoreInline(admin.StackedInline):
    model = Store.categories.through

######οι 3 παρακάτω συναρτήσεις είναι για να μην μπορεί να γίνει αλλαγή στα καταστήματα που ανήκουν σε κάποια κατηγορία, όταν είμαι στο 'Store Category'
    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False


class StoreCategoryAdmin(admin.ModelAdmin):
    model = StoreCategory
    inlines = [StoreInline]


class ProductInline(admin.StackedInline):
    model = Product

class StoreAdmin(admin.ModelAdmin):
    inlines = [ProductInline]


admin.site.register(Store, StoreAdmin)
admin.site.register(StoreCategory, StoreCategoryAdmin)
admin.site.register(OpeningTime)