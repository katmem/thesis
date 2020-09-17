from django.db import models
from products.models import *
from customers_accounts.models import User, CustomerProfile
from stores_accounts.models import Store
from django.contrib.sessions.models import Session


class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete = models.CASCADE, null = True, blank = True)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.IntegerField(default = 1)
    options = models.ManyToManyField(IngredientPrice)
    date_added = models.DateTimeField(auto_now_add = True, auto_now = False)
    date_updated = models.DateTimeField(auto_now_add = False, auto_now = True)
    total_price = models.DecimalField(default = 0, max_digits = 4, decimal_places = 2)

    def __unicode__(self):
        return self.product.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True)
    session = models.ForeignKey(Session, on_delete = models.CASCADE, null = True, blank = True)
    store = models.ForeignKey(Store, on_delete = models.CASCADE)
    total = models.DecimalField(max_digits = 5, decimal_places = 2)
    date_added = models.DateTimeField(auto_now_add = True, auto_now = False)
    date_updated = models.DateTimeField(auto_now_add = False, auto_now = True)

    def __unicode__(self):
        return self.id

    def update_total(self):
        print ('updating...')
        total = 0
        items = self.cartitem_set.all()
        print('items..', items)
        for item in items:
            total += float(item.total_price)
        self.total = total
        self.save()


class PickUpTime(models.Model):
    date = models.DateField()
    hour = models.TimeField()   

    class Meta:
        verbose_name_plural = "PickUpTime"

    def __unicode__(self):
        return u'%s %s' % (self.date, self.hour)


class Order(models.Model):
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
    pickup = models.ForeignKey(PickUpTime, on_delete = models.CASCADE)
    paid = models.BooleanField(default =  False)
    confirmed = models.BooleanField(default = False)    #True if restaurant has confirmed an order(it can either accept it or reject it)
    accepted = models.BooleanField(default = False)     #True if restaurant has accepted the order
    created_date = models.DateTimeField(auto_now_add=True)
    ordered_by = models.ForeignKey(CustomerProfile, on_delete = models.CASCADE) 
    prepared = models.BooleanField(default = False)     #True if restaurant has completed the making of an order 

    class Meta:
        verbose_name_plural = "Orders"

    def __unicode__(self):
        return u'%s %s' % (self.cart, self.pickup)