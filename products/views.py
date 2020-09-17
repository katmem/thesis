from django.shortcuts import render, redirect
from .models import *
from .forms import *
from .decorators import *
from stores_accounts.models import Store
from cart.models import CartItem, Cart
from django.template.defaultfilters import slugify
from django.forms import modelformset_factory
from cart.views import add_to_cart_view
import time
from django.contrib.sessions.models import Session


#Used for finding a restaurant's menu and creating a new session when user enters the restaurant's page
def detailpage_view(request, slug):
   
    store = Store.objects.filter(slug = slug).first()
    
    if request.user.is_authenticated:
        session = Session.objects.get(session_key = request.session.session_key)
        cart, created = Cart.objects.get_or_create(user = request.user, session = session, store = store)
    
    else:
        if request.session.session_key:
            session = Session.objects.get(session_key = request.session.session_key)
            cart, created = Cart.objects.get_or_create(session = session, store = store)
        else:
            request.session.save()
            session = Session.objects.get(session_key = request.session.session_key)
            cart, created = Cart.objects.get_or_create(store = store, session = session)
        if not cart.session:
            if request.session.session_key is None:
                request.session.save()
            session = Session.objects.get(session_key = request.session.session_key)
            cart.session = session
            cart.save()

    products = Product.objects.filter(store__slug = slug).order_by('name')

    start_time = time.time()
    product_categories = products.values_list('category__name', flat = True).distinct().order_by('name')      #fing all product categories of the store that we visit
    product_categories = list(sorted(set(product_categories)))

    end_time = time.time()

    ingredients = IngredientPrice.objects.filter(product__in = products).values_list('ingredient', flat = True).distinct()

    ingredients_categories = []
    for id in ingredients:
        category_id = Ingredients.objects.get(id = id).category.id
        ingredients_categories.append(category_id)
    categories = IngredientsCategory.objects.filter(id__in = ingredients_categories)

    request.session['cat'] = categories

    if request.method == 'POST':
        ids = request.POST.getlist('id')
        quantity = request.POST.get('quantity')
        
        my_list = []
        for id in ids:
            my_list.append(id)

        if request.POST.get('product_id'):
            product_id = request.POST.get('product_id')
            return add_to_cart_view(request, cart_id = cart.id, id=product_id, quantity=quantity, options=False)

        return add_to_cart_view(request, cart_id = cart.id, id=my_list, quantity=quantity, options=True)


    cart_items = CartItem.objects.filter(cart = cart)
    if cart_items:
        total = Cart.objects.get(id = cart.id).total
        context = {'products':products, 'store':store, 'product_categories':product_categories, 'categories':categories, 'cart_items': cart_items, 'total':total}
    else:
        context = {'products':products, 'store':store, 'product_categories':product_categories, 'categories':categories}
    
    return render(request, "products/detail_page.html", context)


#Used for registering a restaurant's menu
@business_required(redirect_url = 'home:home')
def register_store_menu_view(request, id = None):
    store_info = Store.objects.filter(user = request.user).first()

    if id:
        instance = Product.objects.filter(id = id).first()
    else:
        instance = Product()

    if request.method == 'POST':
        if instance:
            product_form = ProductForm(request.POST, request.FILES, instance = instance)
        else:
            product_form = ProductForm(request.POST, request.FILES)
        
        if product_form.is_valid() and 'topping' in request.POST:
            product = product_form.save()

            name = product_form.cleaned_data.get('name')
            description = product_form.cleaned_data.get('description')
            price = product_form.cleaned_data.get('price')
            quantity = product_form.cleaned_data.get('quantity')
            category = product_form.cleaned_data.get('category')
            product.store = Store.objects.filter(user = request.user).first()               #find name of store that is logged in
            product.save()
            photo = product_form.cleaned_data.get('photo')
            new_product = Product.objects.get(id = product.id)
            new_product.slug = slugify(new_product.name)+slugify(new_product.id)
            request.session['category'] = category
            request.session['product'] = new_product

            return redirect('products:register-store-options')

        if product_form.is_valid() and 'new' in request.POST:
            product = product_form.save()

            name = product_form.cleaned_data.get('name')
            description = product_form.cleaned_data.get('description')
            price = product_form.cleaned_data.get('price')
            quantity = product_form.cleaned_data.get('quantity')
            category = product_form.cleaned_data.get('category')
            product.store = Store.objects.filter(user = request.user).first()
            product.save()
            photo = product_form.cleaned_data.get('photo')
            new_product = Product.objects.get(id = product.id)
            new_product.slug = slugify(new_product.name)+slugify(new_product.id)
            request.session['category'] = category
            request.session['product'] = product

            return redirect('products:menu-edit', product.id)

        if product_form.is_valid() and 'update' in request.POST:
            product = product_form.save()
            name = product_form.cleaned_data.get('name')
            description = product_form.cleaned_data.get('description')
            price = product_form.cleaned_data.get('price')
            quantity = product_form.cleaned_data.get('quantity')
            category = product_form.cleaned_data.get('category')
            product.store = Store.objects.filter(user = request.user).first()               #find name of store that is logged in
            product.save()
            photo = product_form.cleaned_data.get('photo')
            new_product = Product.objects.get(id = product.id)
            new_product.slug = slugify(new_product.name)+slugify(new_product.id)
            request.session['category'] = category
            request.session['product'] = new_product
            if new_product.options.all():
                return redirect('products:options-edit', id = new_product.id)
            else:
                return redirect('products:edit-menu')

    else:
        if instance:
            product_form = ProductForm(instance = instance)
        else:
            product_form = ProductForm()

    context = {'product_form':product_form, 'store_info':store_info, 'id':id}

    return render(request, "products/register_store_menu.html", context)


#Used for registering options for a product
@business_required(redirect_url = 'home:home')
def register_store_options_view(request, id=None):
    category = request.session.get('category')
    product = request.session.get('product')
    store = Store.objects.get(user = request.user)
    if id:
        product = Product.objects.get(id=id)
        category = product.category
        instance = Product.objects.get(id = id)
    else:
        instance = IngredientPrice()

    ingredients_category = IngredientsCategory.objects.filter(product_category = category)
    ingredient = Ingredients.objects.filter(category__in = ingredients_category)

    if request.method == 'POST':
        if instance:
            options_form = OptionsForm(request.POST, instance = instance)
        else:
            options_form = OptionsForm(request.POST)

        if options_form.is_valid():
            """
            if id exists, that is, the view is called to edit product options, find all stored options for this product. 
            For every option submitted by the user find the corresponding IngredientPrice object. If object already exists, 
            add it to the new options' list, otherwise create a new IngredientPrice object. Check if store contains same 
            ingredient. If so, copy price, otherwise leave price empty. For every stored option check if it is contained in the
            new options' list. If it's not, delete the stored object. 
            """
            #If id does not exists, that is, the view is called to create product options.
            if id:
                old_options = IngredientPrice.objects.filter(product = product, ingredient__in = product.options.all())

                new_options = []
                for option in options_form.cleaned_data['options'].all():
                    ingredient_obj = IngredientPrice.objects.filter(ingredient = option, product__id = id).first()
                    if ingredient_obj:
                        new_options.append(ingredient_obj)
                for option in old_options:
                    if option not in new_options:
                        option.delete() 

                for option in options_form.cleaned_data['options'].all():
                    ingredient_obj = IngredientPrice.objects.filter(ingredient = option, product__id = id).first()
                    if not ingredient_obj:
                        ingredient_in_store = IngredientPrice.objects.filter(ingredient = option, product__store = store).first()
                   
                        if ingredient_in_store:
                            price = ingredient_in_store.price
                            new_ingredient_price_obj = IngredientPrice.objects.create(ingredient = option, product = product, price = price)
                        else:
                            new_ingredient_price_obj = IngredientPrice.objects.create(ingredient = option, product = product)

                return redirect('products:edit-price')
                               
            else:
                for option in options_form.cleaned_data['options'].all():
                    ingredient_in_store = IngredientPrice.objects.filter(ingredient = option, product__store = store).first()
                    if ingredient_in_store:
                        price = ingredient_in_store.price
                        new_ingredient_price_obj = IngredientPrice.objects.create(ingredient = option, product = product, price = price)
                    else:
                        new_ingredient_price_obj = IngredientPrice.objects.create(ingredient = option, product = product)
                    
                return redirect('products:register-store-menu')

    else:
        if instance:
            options_form = OptionsForm(instance = instance)
            context = {'options_form':options_form, 'product':product, 'id':id}
        else:
            options_form = OptionsForm()
            context = {'options_form':options_form, 'product':product}
        options_form.fields["options"].queryset = ingredient

    return render(request, "products/register_store_options.html", context)


#Used for registering prices for a restaurant's ingredient options
@business_required(redirect_url = 'home:home')
def price_view(request):
    store = Store.objects.get(user = request.user)
    products = Product.objects.filter(store = store)            #find all products that a store sells
    store_ingredients  = IngredientPrice.objects.all().filter(product__store = store, price__isnull = True).values('ingredient__id').distinct()   #finds all ids of the ingredientsprice objects that a store has
    
    extra = len(store_ingredients)

    existing_slots = []
    for placeholder in IngredientPrice.objects.filter(product__in = products, price__isnull = True).distinct():
        if placeholder.ingredient.id in existing_slots:
            pass
        else:
            existing_slots.append(placeholder.ingredient.id)    #list of ids of ingredients a store has(list has ints) 

    store_ingredients = Ingredients.objects.filter(id__in = existing_slots)     #queryset containing Ingredient objects of the existing_slots

    ingredient_list = []
    for store_ingredient in store_ingredients:
        ingredient_list.append(store_ingredient.name)       #list with the names of the Ingredient Objects
    
    PriceFormset = modelformset_factory(IngredientPrice, fields = ('price',), extra = extra, min_num = extra, max_num = extra)
        
    if request.method == 'POST' :
        formset = PriceFormset(request.POST, queryset = IngredientPrice.objects.none())

        if formset.is_valid():
            for idx, form in enumerate(formset):
                if form.cleaned_data.get('price') >= 0:
                    price = form.cleaned_data.get('price')

                    ingredient = ingredient_list[idx]
                    ingredient_price_objs = IngredientPrice.objects.filter(ingredient__name = ingredient, price__isnull = True, product__in = products)
                    for ingredient_price_obj in ingredient_price_objs:
                        ingredient_price_obj.price = price
                        ingredient_price_obj.save()

            return redirect('products:register-store-menu')

    else:
        formset = PriceFormset(queryset = IngredientPrice.objects.none())

    context = {'price_form':formset, 'ingredient_list':ingredient_list}

    return render(request, "products/price.html", context)


#Used for updating prices of a restaurant's ingredient option 
@business_required(redirect_url = 'home:home')
def edit_price_view(request):
    store = Store.objects.get(user = request.user)
    products = Product.objects.filter(store = store)    #find all products a store sells

    my_list = []
    distinct_ingredients = IngredientPrice.objects.filter(product__in = products).values('ingredient', 'price').distinct()
    for obj in distinct_ingredients:
        my_list.append(IngredientPrice.objects.filter(product__in=products, ingredient=obj['ingredient']).first().id)
    queryset = IngredientPrice.objects.filter(id__in = my_list)
    extra = len(queryset)

    PriceFormset = modelformset_factory(IngredientPrice, fields = ('price',), extra = extra, min_num = extra, max_num = extra)
    
    if request.method == 'POST' :
        formset = PriceFormset(request.POST, queryset = queryset)

        if formset.is_valid():
            for idx, form in enumerate(formset):
                if form.cleaned_data.get('price') >= 0:
                    price = form.cleaned_data.get('price')

                    ingredient = queryset[idx]
                    ingredient_price_objs = IngredientPrice.objects.filter(ingredient = ingredient.ingredient, product__in = products)
                    for ingredient_price_obj in ingredient_price_objs:
                        ingredient_price_obj.price = price
                        ingredient_price_obj.save()
            return redirect('products:edit-menu')
    else:
        formset = PriceFormset(queryset = queryset)

    context = {'price_form':formset, 'ingredient_list':queryset}

    return render(request, "products/edit_price.html", context)


#Used for displaying the page where restaurants can edit their menu
@business_required(redirect_url = 'home:home')
def edit_menu_view(request):
    store = Store.objects.get(user = request.user)
    products = Product.objects.filter(store = store)

    context = {'products':products, 'store':store}

    return render(request, "products/menu.html", context)


#Used for confirming the deletion of a product from the menu
@business_required(redirect_url = 'home:home')
def delete_product_view(request, id):
    store_info = Store.objects.filter(user = request.user).first
    product = Product.objects.get(id = id)

    if request.method == 'POST':
        if 'yes' in request.POST:
            product.delete()
            return redirect('products:edit-menu')
        if 'no' in request.POST:
            return redirect('products:edit-menu')
    context = {'store_info':store_info, 'product':product}
    return render(request, "products/delete_product.html", context)
