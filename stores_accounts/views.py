from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages
from customers_accounts.forms import RegisterForm
from .forms import StoreForm, OpeningTimeFormset
from .models import Store, OpeningTime, StoreCategory
from django.contrib.auth import authenticate, login, logout
from django.template.defaultfilters import slugify
from .decorators import *
from django.contrib.auth.decorators import login_required
from customers_accounts.models import User
from cart.models import Cart, CartItem, Order
from django.contrib.sessions.models import Session
import datetime
from django.core.mail import send_mail
from django.conf import settings

#View for rendering business homepage template 
@login_required(login_url = 'stores_accounts:login')
def home_business_view(request):
    subject = 'Order confirmation'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = []
    # send_mail( subject, message, email_from, recipient_list)

    now = datetime.datetime.now()
    now_minus_10 = now - datetime.timedelta(minutes = 10)

    #Get paid, unconfirmed orders that were created between the last 10 minutes
    orders = Order.objects.filter(cart__store__user = request.user, paid = True, confirmed = False, created_date__gte = now_minus_10)

    if request.method=='POST':
        input_names = [name for name in request.POST.keys() if name.startswith('response')]
        for input_name in input_names:
            soft_name = request.POST.get(input_name)
            split = soft_name.split('_')

            order = Order.objects.get(id = int(split[0]))
            order.confirmed = True

            # email = order.ordered_by.email
            # recipient_list.append(str(email))
            recipient_list.append('memousi.kat@gmail.com')

            if split[1] == 'accepted':
                order.accepted = True
                order.save()
                message = '\nYour order at {} has been accepted.\n\nOrderID: {}\n\nItems:'.format(order.cart.store, order.id)
                
                for item in order.cart.cartitem_set.all():
                    length = len(item.options.all())

                    if length != 0:
                        item_str = '\n\t {} x {}: '.format(item.quantity, item.product.name)
                    else:
                        item_str = '\n\t {} x {}: '.format(item.quantity, item.product.name)

                    option_str = ''
                    
                    for i, option in enumerate(item.options.all().order_by('ingredient__name')):
                        if i != length-1:
                            option_str += ' {},'.format(option.ingredient.name)
                        else:
                            option_str += ' {}'.format(option.ingredient.name)

                    item_str = item_str + option_str + ' ({} €)'.format(item.total_price) + '\n'
                    message += item_str
                message += '\n\nTotal: {} €\n\nPickup: {} {}\n'.format(order.cart.total, order.pickup.date, order.pickup.hour)
                # send_mail( subject, message, email_from, recipient_list)

                 
            if split[1] == 'rejected':
                order.accepted = False
                message = '\nYour order at {} has been rejected.\n\nOrderID: {}\n\nItems:'.format(order.cart.store, order.id)

                for item in order.cart.cartitem_set.all():
                    length = len(item.options.all())

                    if length != 0:
                        item_str = '\n\t {} x {}: '.format(item.quantity, item.product.name)
                    else:
                        item_str = '\n\t {} x {}: '.format(item.quantity, item.product.name)

                    option_str = ''
                    
                    for i, option in enumerate(item.options.all().order_by('ingredient__name')):
                        if i != length-1:
                            option_str += ' {},'.format(option.ingredient.name)
                        else:
                            option_str += ' {}'.format(option.ingredient.name)

                    item_str = item_str + option_str + ' ({} €)'.format(item.total_price) + '\n'
                    message += item_str
                message += '\n\nTotal: {} €\n\nPickup: {} {}\n'.format(order.cart.total, order.pickup.date, order.pickup.hour)
                # send_mail( subject, message, email_from, recipient_list)
                order.cart.delete()

        return redirect('stores_accounts:home')
        
    context = {'orders':orders}
    return render(request, 'stores_accounts/index_business.html', context)


#View for displaying all stores in a city, defined by the parameter "city"
def shops_view(request, city):
    if not request.user.is_authenticated:
        """
        If user is not authenticated and already has a session key, find all carts that belong to that session key and
        get the orders that include these carts. Delete all unpaid orders that were made with this session key and remove
        the session from the paid orders so that the user can order again using the same session.
        """
        if request.session.session_key:
            session = Session.objects.filter(session_key = request.session.session_key).first()
            carts = Cart.objects.filter(session = session)
            paid_orders = Order.objects.filter(cart__in = carts, paid = True)
            empty_carts = Cart.objects.filter(session = session)
            if paid_orders:
                for paid_order in paid_orders:
                    paid_order.cart.session = None
                    paid_order.cart.save()

            if empty_carts:
                for empty_cart in empty_carts:
                    empty_cart.delete()

        else:
            request.session.save()
    else:
        session = Session.objects.filter(session_key = request.session.session_key).first()
        carts = Cart.objects.filter(user = request.user, session = session)
        paid_orders = Order.objects.filter(cart__in = carts, paid = True)
        empty_carts = Cart.objects.filter(session = session)
        if paid_orders:
            for paid_order in paid_orders:
                paid_order.cart.session = None
                paid_order.cart.save()

        if empty_carts:
            for empty_cart in empty_carts:
                if not Order.objects.filter(cart = empty_cart):
                    empty_cart.delete()
        
    stores = Store.objects.filter(city__display_name = city)
    categories = StoreCategory.objects.all().order_by('name')
    
    if request.method == 'POST':
        selected_categories = request.POST.getlist('categories')
        selected_all = request.POST.get('all')

        if selected_all == 'on':
            stores = Store.objects.filter(city__display_name = city)
        else:
            categories_list = []
            slug_list = []
            for category in selected_categories:
                store_category = StoreCategory.objects.get(slug = category)
                categories_list.append(store_category)
            stores = Store.objects.filter(city__display_name = city, categories__in = categories_list)

    context = {'stores':stores, 'city':city, 'categories':categories}
    return render(request, "stores_accounts/list_page.html", context)


"""
View for registering a store by using RegisterForm which is defined in the app "customers_accounts". If form's data are valid,
then authenticate the user and log the store in.
"""
def register_store_view(request):
    if request.method == 'POST':
        register_store_form = RegisterForm(request.POST)
        if register_store_form.is_valid():
            new_store = register_store_form.save(commit = False)
            new_store.business = True
            new_store.save()
            email = register_store_form.cleaned_data.get('email')
            password = register_store_form.cleaned_data.get('password1')
            user = authenticate(request, email = email, password = password)
            login(request, user)
            return redirect('stores_accounts:register-store-info', id = new_store.id)
        else:
            messages.error(request, 'Please fix your error')
    else:
        register_store_form = RegisterForm()
    context = {'register_store_form':register_store_form}
    return render(request, "stores_accounts/register_store.html", context)

"""
View for registering and updating store's information including name, phone number, opening hours, etc. It takes current user's id 
as a parameter and initializes the form with store's email. If id is none, the view is called for registering info, otherwise it's
called for updating existing info by passing "instance" as a parameter to the form. StoreForm and OpeningTimeFormest are used
in this view.
"""
def register_store_info_view(request, id = None):
    instance = Store.objects.filter(user__id = id).first()

    if request.user.is_authenticated and request.user.business:
        initial = {'email': request.user.email}

    if request.method == 'POST':
        if instance:
            store_form = StoreForm(request.POST, request.FILES, instance = instance, user=request.user)
            opening_time_form = OpeningTimeFormset(request.POST, queryset = instance.opening_times.all())
        else:
            store_form = StoreForm(request.POST, request.FILES, initial = initial, user=request.user)
            opening_time_form = OpeningTimeFormset(request.POST, queryset = OpeningTime.objects.none())

        if store_form.is_valid() and opening_time_form.is_valid():
            store = store_form.save()
            store.user = request.user
            store.save()
            name = store_form.cleaned_data.get('name')
            phone = store_form.cleaned_data.get('phone')
            email = store_form.cleaned_data.get('email')
            user = User.objects.get(id=id)
            old_email = user.email
            if email != old_email:
                if not User.objects.filter(email = email):
                    user.email = email
                    user.save()
                    instance.email = email
                    instance.save()

            description = store_form.cleaned_data.get('description')
            photo = store_form.cleaned_data.get('photo')
            city = store_form.cleaned_data.get('city')
            address = store_form.cleaned_data.get('address')
            addressNum = store_form.cleaned_data.get('addressNum')
            postcode = store_form.cleaned_data.get('postcode')

            new_store = Store.objects.get(id = store.id)  
            new_store.categories.add(*store_form.cleaned_data['categories'])
            new_store.slug = slugify(new_store.name)


            for form in opening_time_form:
                if form.cleaned_data.get('weekday') and form.cleaned_data.get('from_hour') and form.cleaned_data.get('to_hour'):
                    openingtime = form.save()
                    weekday = form.cleaned_data.get('weekday')
                    from_hour = form.cleaned_data.get('from_hour')
                    to_hour = form.cleaned_data.get('to_hour')

                    new_openinghours = OpeningTime.objects.get(id = openingtime.id)
                    new_store.opening_times.add(new_openinghours.id)

            if instance:
                return redirect('stores_accounts:home')
            else:
                return redirect('products:register-store-menu')  
    else:
        if instance:
            store_form = StoreForm(instance = instance, user=request.user)
            opening_time_form = OpeningTimeFormset(queryset = instance.opening_times.all())
        else:
            store_form = StoreForm(initial = initial, user=request.user)
            opening_time_form = OpeningTimeFormset(queryset = OpeningTime.objects.none())  #OpeningTime._meta.get_field('weekday').choices

    context = {'store_form':store_form, 'opening_time_form':opening_time_form, 
    'choices':OpeningTime._meta.get_field('weekday').choices}

    return render(request, "stores_accounts/register_store_info.html", context)


#View for logging in stores using Django's built in "login" function.
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            if user.business:
                return redirect('stores_accounts:home')
            else:
                return redirect('home:home')

        else:
            messages.info(request, 'Username or password is incorrect.')
            return render(request, 'stores_accounts/store_login.html', {})

    return render(request, 'stores_accounts/store_login.html', {})


#View for logging out.
def logout_view(request):
    logout(request)
    return redirect('home:home')


def orders_by_date_view(request):
    context = {}
    return render(request, 'stores_accounts/orders_by_date.html', context)


#View for showing today's orders which have a pickup time after the time of the request 
def todays_confirmed_orders_view(request):
    store = Store.objects.get(user = request.user)

    today = datetime.date.today()
    now = datetime.datetime.now().time()
    orders = Order.objects.filter(accepted = True, paid = True, cart__store = store, pickup__date = today, pickup__hour__gte = now).order_by('pickup__date', 'pickup__hour')

    if request.method == 'POST':
        prepared_orders = request.POST.getlist('prepared')
        for order_id in prepared_orders:
            order = Order.objects.get(id = order_id)
            order.prepared = True
            order.save()
        return redirect('stores_accounts:todays-confirmed-orders')

    context = {'orders': orders}
    return render(request, 'stores_accounts/confirmed_todays_orders.html', context)


#View for showing picked up orders 
def picked_up_orders_view(request):
    store = Store.objects.get(user = request.user)

    today = datetime.date.today()
    now = datetime.datetime.now().time()
    past_orders = Order.objects.filter(accepted = True, paid = True, cart__store = store, pickup__date__lt = today).order_by('-pickup__date', '-pickup__hour')

    todays_past_orders = Order.objects.filter(accepted = True, paid = True, cart__store = store, pickup__date = today, pickup__hour__lt = now).order_by('-pickup__date', '-pickup__hour')

    orders = todays_past_orders | past_orders

    context = {'orders': orders}
    return render(request, 'stores_accounts/picked_up_orders.html', context)


#View for showing orders with pickup time after the time of the request 
def future_to_pick_up_orders_view(request):
    store = Store.objects.get(user = request.user)

    today = datetime.date.today()
    now = datetime.datetime.now().time()
    orders = Order.objects.filter(accepted = True, paid = True, cart__store = store, pickup__date__gt = today).order_by('pickup__date', 'pickup__hour')

    context = {'orders': orders}
    return render(request, 'stores_accounts/future_to_pick_up_orders.html', context)


#View for displaying the page with a restaurant's opening hours
def store_details_view(request, store_id):
    store = Store.objects.get(id = store_id)
    opening_times = store.opening_times.all().order_by('weekday', 'from_hour')
   
    context = {'store':store, 'opening_times':opening_times}
    return render(request, 'stores_accounts/store_details.html', context)