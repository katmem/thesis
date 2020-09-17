from django.shortcuts import render, redirect
from products.models import *
from products.forms import *
from products.decorators import *
from stores_accounts.models import Store
from django.contrib import messages
from .models import *
import time
from .forms import *
from customers_accounts.models import CustomerProfile
import datetime

#View called when a product is added to the cart.
def add_to_cart_view(request, cart_id, id, quantity, options):

    if options is False:
        product = Product.objects.get(id=id)
    else:
        options_list = []
        for i in id:
            option = IngredientPrice.objects.get(id = i)
            options_list.append(option)
        product = option.product
    slug = product.store.slug

    cart = Cart.objects.get(id=cart_id)
    
    #if there are no options for this product, get or create product
    if options is False:
        cart_item, created = CartItem.objects.get_or_create(product = product, cart=cart)
    #if there are options for this product, filter the database to find if product exists
    else:
        cart_item = CartItem.objects.filter(product = product, cart=cart).first()
        """
        if product exists, set var to true and for every option of the product found check if it exists in options_list. If 
        at least one option does not exist in list, set var to false.
        """  
        if cart_item:
            var = True
            for option in cart_item.options.all():
                if option not in options_list:
                    var = False
            """
            If var is false it means that the user added an already existing product in cart but with different options. If so,
            create another instance for this new product and set options to the options of the options_list
            """
            if var is False:
                cart_item = CartItem.objects.create(product = product, cart=cart)
                for option in options_list:
                    cart_item.options.add(option)
                cart_item.save()
                created = True
            
            #If var is true it means that the user added an already existing product in cart with the same options. In this case,
            #do not create another instance. Use the instance that exists in the database for this product, which is cart_item.
            
            else:
                created = False
        #If chosen product does not exist in the cart items,create an instance for it and set options_list as options.
        else:
            cart_item = CartItem.objects.create(product = product, cart=cart)
            for option in options_list:
                cart_item.options.add(option)
            cart_item.save()
            created = True
    
    #If there are options for the added-to-cart product get their total price and save it to "options_price".
    options_price = 0
    if options is True:
        for i in id:
            option = IngredientPrice.objects.get(id = i)
            options_price = options_price + float(option.price)

    if created is True:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        old_qty = cart_item.quantity
        cart_item.quantity = old_qty + int(quantity)
        cart_item.save()

    added_price = (float(product.price) + options_price)*float(quantity)

    old_total_price = cart_item.total_price
    cart_item.total_price = float(old_total_price) + added_price
    cart_item.save()

    cart.update_total()

    return redirect('products:detailpage', slug=slug)

"""
View called when a product in the cart is updated. Update can be increasing/decreasing quantity or 
changing its extra options. 
"""
def update_product_view(request, cart_item_id):
    start_time = time.time()
    cart_item = CartItem.objects.get(id = cart_item_id)
    cart = cart_item.cart
    total = cart.total
    cart_items = CartItem.objects.filter(cart = cart)
    store = cart_item.product.store
      
    categories = request.session.get('cat')

    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        cart_item.quantity = quantity
        cart_item.save()
        options = request.POST.getlist('options')
      
        options_list = []
        for id in options:
            ingredient_price = IngredientPrice.objects.get(id = id)
            options_list.append(ingredient_price)
            if ingredient_price not in cart_item.options.all():
                cart_item.options.add(ingredient_price)
                cart_item.save()

        for option in cart_item.options.all():
            if option not in options_list:
                cart_item.options.remove(option)
                cart_item.save()

        options_price = 0
        for option in cart_item.options.all():
            options_price = options_price + float(option.price)

        added_price = (float(cart_item.product.price) + options_price)*float(quantity)

        cart_item.total_price = added_price
        cart_item.save()

        cart_item.cart.update_total()

        return redirect('products:detailpage', slug = cart_item.product.store.slug)

    context = {'store':store, 'cart_items':cart_items, 'total':total, 'cart_item':cart_item, 'categories':categories}
    return render(request, 'cart/update_product.html', context)


#View called when a product is deleted from the cart. After deletion, the cart's total is updated.
def delete_product_view(request, cart_item_id):
    cart_item = CartItem.objects.get(id = cart_item_id)
    cart = cart_item.cart
    cart_item.delete()
    cart.update_total()
    return redirect('products:detailpage', slug = cart_item.product.store.slug)


"""
View called when user is ready to proceed with his order. It handles form submission and generates
date queryset for PickupDateForm
"""
def order_view(request, cart_id):
    cart = Cart.objects.get(id = cart_id)
    total = cart.total

    cart_items = CartItem.objects.filter(cart__id = cart_id)
    cart_item = cart_items.first()
    slug = cart_item.product.store.slug

    if request.user.is_authenticated:
        user_profile = CustomerProfile.objects.get(user = request.user)
        initial = {'first_name':user_profile.first_name, 'last_name':user_profile.last_name, 'phone':user_profile.phone, 'email':request.user.email}
        authenticated = True
    else:
        authenticated = False
        initial = {}

    #Find all many to many objects that belong to this store
    opening_times = cart_item.product.store.opening_times.all()
    
    #Get "weekday" field from the above queryset
    opening_days = opening_times.values_list('weekday', flat = True)
    #Get distinct values of "opening_days"
    opening_days = list(dict.fromkeys(opening_days))

    d = datetime.date.today() 
    date_list = []
    for day in opening_days:
        next_date = next_weekday(d, day-1)    # 0 = Monday, 1=Tuesday, 2=Wednesday...
        date_list.append(next_date)
    date_list.sort()
    #create list of tuples for the "date" choices in the form. 
    choices = [(date, date) for date in date_list] 

    if request.method == 'POST':
        profile_form = CustomerProfileForm(request.POST, initial = initial, authenticated = authenticated)
        pickup_form = PickupDateForm(request.POST)
        if profile_form.is_valid() and pickup_form.is_valid():
            first_name = profile_form.cleaned_data['first_name']
            last_name = profile_form.cleaned_data['last_name']
            phone = profile_form.cleaned_data['phone']
            email = profile_form.cleaned_data['email']
            if request.user.is_authenticated:
                profile, created = CustomerProfile.objects.get_or_create(user = request.user, first_name = first_name, last_name = last_name, phone = phone)
            else:
                profile, created = CustomerProfile.objects.get_or_create(first_name = first_name, last_name = last_name, phone = phone, email = email)
            
            request.session['profile_id'] = profile.id 

            date = pickup_form.cleaned_data['date']
            pickup_obj = PickUpTime.objects.create(date = date)
            return redirect('cart:order-time', cart_id = cart_id, pickup_id = pickup_obj.id)
    else:
        profile_form = CustomerProfileForm(initial = initial, authenticated = authenticated)
        pickup_form = PickupDateForm(choices = choices)

    context = {'cart_items':cart_items, 'profile_form':profile_form, 'pickup_form':pickup_form, 'slug':slug, 'total':total}
    return render(request, 'cart/cart.html', context)


#View that handles PickupTimeForm after passing a queryset to it 
def order_time_view(request, cart_id, pickup_id):

    cart_items = CartItem.objects.filter(cart__id = cart_id)
    
    cart = Cart.objects.get(id = cart_id)
    total = cart.total
    pickup_obj = PickUpTime.objects.get(id = pickup_id)

    #Get selected day's opening hours
    opening_times = cart.store.opening_times.filter(weekday = pickup_obj.date.weekday()+1).values_list('from_hour','to_hour')

    #Get last day's opening hours
    yesterday_opening_times = cart.store.opening_times.filter(weekday = pickup_obj.date.weekday()).values_list('from_hour','to_hour')

    time_list = []

    """
    For last day's opening hours check if store was open after midnight. If so, add hours from midnight till closing hour 
    in time_list 
    """
    for y_opening_time in yesterday_opening_times:
        y_opening_hour = y_opening_time[0]
        y_closing_hour = y_opening_time[1]
        now = datetime.datetime.now()

        if y_closing_hour > datetime.time(now.hour, now.minute, now.second):
            if y_closing_hour > datetime.time(0, 0) and y_closing_hour < y_opening_hour:
                opening_datetime = datetime.datetime.combine(pickup_obj.date, datetime.time(0,0))
                closing_datetime = datetime.datetime.combine(pickup_obj.date, y_closing_hour)
                for time in perdelta(opening_datetime, closing_datetime, datetime.timedelta(minutes = 15)):
                    time_list.append(time)
    """
    For today's opening hours check if closing hour is after midnight and is less than opening hour. (For example, 
    16:00-03:00 means that 03:00 is the day after.) If so, show only hours till midnight. The open hours after midnight will
    be shown in next day's opening hours.
    """
    for opening_time in opening_times:
        opening_hour = opening_time[0]
        closing_hour = opening_time[1]
        if opening_hour < closing_hour:
            opening_datetime = datetime.datetime.combine(pickup_obj.date, opening_hour)
            closing_datetime = datetime.datetime.combine(pickup_obj.date, closing_hour)
        else:
            d = datetime.timedelta(days=1)
            opening_datetime = datetime.datetime.combine(pickup_obj.date, opening_hour)
            closing_datetime = datetime.datetime.combine(pickup_obj.date+d, closing_hour)

        if closing_hour > datetime.time(0, 0) and closing_hour < opening_hour:
            closing_datetime = datetime.datetime.combine(pickup_obj.date, datetime.time(23, 59))
            
        
        """
        If pickup day is today find nearest hour someone can pickup an order. That hour is the ceiling to 
        the next quarter of the next hour
        """
        if pickup_obj.date == datetime.datetime.today().date():
            now = datetime.datetime.now()
            one_hour_after = now + datetime.timedelta(hours = 1)
            one_dt = datetime.datetime.combine(pickup_obj.date, datetime.time(one_hour_after.hour, one_hour_after.minute))
            opening_datetime = ceil(one_dt)

        for time in perdelta(opening_datetime, closing_datetime, datetime.timedelta(minutes = 15)):
            time_list.append(time)
        choices = [(time, time) for time in time_list] 

    if request.method == 'POST':
        pickup_form = PickupTimeForm(request.POST)
        if pickup_form.is_valid():
            hour = pickup_form.cleaned_data['hour']
            pickup_obj.hour = hour
            pickup_obj.save()
            return redirect('cart:payment', cart_id = cart_id, pickup_id = pickup_id)
    else:
        pickup_form = PickupTimeForm(choices = choices)

    context = {'pickup_form':pickup_form, 'cart_items': cart_items, 'total': total}
    return render(request, 'cart/pickup_time.html', context)


#View for handling PaymentForm when user submits his credit card information
def payment_view(request, cart_id, pickup_id):
    cart = Cart.objects.get(id = cart_id)
    pickup = PickUpTime.objects.get(id = pickup_id)
    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid:
            messages.info(request, 'Your order has been placed!')

            new_order = Order.objects.create(cart = cart, pickup = pickup, paid = True)
            profile_id = request.session['profile_id']
            profile = CustomerProfile.objects.get(id = profile_id)
            new_order.ordered_by = profile
            new_order.save() 

            return redirect('customers_accounts:my-orders')
    else:
        payment_form = PaymentForm()
    refresh = True
    context = {'payment_form':payment_form, 'refresh':refresh}
    return render(request, 'cart/payment.html', context)


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead < 0: # Target day already passed this week but today counts as if it has not passed
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


#Generates a list of datetimes between an interval
def perdelta(start, end, delta):
    curr = start
    time = start.time().strftime('%H:%M:%S')
    while curr <= end:
        yield time
        curr += delta
        time = curr.time().strftime('%H:%M:%S')


#Finds next available hour for pickup 
def ceil(dt):
    if dt.minute % 15 or dt.second:
        return dt + datetime.timedelta(minutes = 15 - dt.minute % 15,
                                       seconds = -(dt.second % 60))
    else:
        return dt