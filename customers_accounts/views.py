from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import  RegisterForm, CustomerProfileForm, UpdateProfileForm
from .models import CustomerProfile, User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from cart.models import Cart, Order
from django.contrib.sessions.models import Session

#Used for registering usersand logging them in the application
def register_customer_view(request):

    if request.method == 'POST' :
        register_form = RegisterForm(request.POST)
        customer_profile_form = CustomerProfileForm(request.POST)
        if register_form.is_valid() and customer_profile_form.is_valid():
            new_user = register_form.save()

            new_customer_profile = customer_profile_form.save()
            new_customer_profile.user = new_user
            new_customer_profile.save()

            password = register_form.cleaned_data.get('password1')
            
            messages.success(request, 'Account was created for '+ new_user.email)

            user = authenticate(request, email = new_user.email, password = password)
            login(request, user)
            return redirect('home:home')
    else:
        register_form = RegisterForm()
        customer_profile_form = CustomerProfileForm()
    context = {'register_form': register_form, 'customer_profile_form':customer_profile_form}
    return render(request, 'customers_accounts/register_customer.html', context)


#Used when user log in the app. It checks if username and password exist and if so, signs users in.
def login_view(request):
    if request.session.session_key:
        session = Session.objects.get(session_key = request.session.session_key)
        carts = Cart.objects.filter(session = session)
        if carts:
            for cart in carts:
                cart.session = None
                cart.save()
            
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
            return render(request, 'customers_accounts/customer_login.html', {})

    return render(request, 'customers_accounts/customer_login.html', {})


#Used for logging users out
@login_required
def logout_view(request):
    session = Session.objects.get(session_key = request.session.session_key)
    carts = Cart.objects.filter(session = session)
    if carts:
        for cart in carts:
            cart.session = None
            cart.save()
    logout(request)
    return redirect('home:home')


#Used for changing a user's password with the PasswordChangeForm
@login_required
def change_password_view(request):
    storage = messages.get_messages(request)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password changed successfully!')
            return redirect('home:home')
    else:
        form = PasswordChangeForm(request.user)

    context = {'form': form, 'messages':storage}

    return render(request, 'customers_accounts/change_password.html', context)


#Used for updating a user's information using UpdateProfileForm
@login_required
def update_profile_view(request):
    storage = messages.get_messages(request)

    profile = CustomerProfile.objects.get(user = request.user, email = request.user.email)

    initial= {'first_name':profile.first_name, 'last_name':profile.last_name, 'phone':profile.phone, 'email':request.user.email}

    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, initial, user_id = request.user.id, profile = profile)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('home:home')
    else:
        form = UpdateProfileForm(initial, user_id = request.user.id, profile = profile)

    context = {'form':form, 'messages':storage}

    return render(request, "customers_accounts/update_profile.html", context)


#Used for finding a user's orders
def my_orders_view(request):
    profile = CustomerProfile.objects.get(user = request.user)
    orders = Order.objects.filter(ordered_by = profile, accepted = True).order_by('-pickup__date', '-pickup__hour')

    context = {'orders':orders}
    return render(request, 'customers_accounts/my_orders.html', context)