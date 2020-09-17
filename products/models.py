from django.db import models
from django.template.defaultfilters import slugify

class ProductCategory(models.Model):
    name        =   models.CharField(max_length = 20, unique = True)
    slug        =   models.SlugField(max_length = 20, unique = True, blank = True)

    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(ProductCategory, self).save(*args, **kwargs)


class IngredientsCategory(models.Model):
    name    = models.CharField(max_length = 20, unique = True)
    slug    = models.SlugField(max_length = 20, unique = True, blank = True)
    product_category = models.ManyToManyField(ProductCategory)
    

    class Meta:
        verbose_name_plural = "Ingredients Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(IngredientsCategory, self).save(*args, **kwargs)


class Ingredients(models.Model):
    name     = models.CharField(max_length = 20) 
    slug     = models.SlugField(max_length = 20, blank = True)
    category = models.ForeignKey('IngredientsCategory', on_delete = models.CASCADE)

    class Meta:
        verbose_name_plural = "Ingredients"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category.name)+slugify('-')+slugify(self.name)
        super(Ingredients, self).save(*args, **kwargs)


class IngredientPrice(models.Model):
    product = models.ForeignKey('Product', on_delete = models.CASCADE)
    ingredient = models.ForeignKey('Ingredients', on_delete = models.CASCADE)
    price = models.DecimalField(max_digits = 4, decimal_places = 2)

    def __str__(self):
       return self.ingredient.name


class Product(models.Model):
    name        =   models.CharField(max_length = 30, blank = False)
    description =   models.CharField(max_length = 30, blank = True)
    slug        =   models.SlugField(max_length = 30, unique = True)
    price       =   models.DecimalField(max_digits = 4, decimal_places = 2, blank = False)
    quantity    =   models.PositiveIntegerField(blank = True)
    category    =   models.ForeignKey('ProductCategory', on_delete = models.CASCADE)
    photo       =   models.ImageField(upload_to = 'img/', blank = True)
    store       =   models.ForeignKey('stores_accounts.Store', on_delete = models.CASCADE, blank = False, null = False)
    options     =   models.ManyToManyField(Ingredients, blank = True, through = IngredientPrice)
    
    class Meta:
        verbose_name_plural = "Products"
        
    def __str__(self):
        return '%s, %s' % (self.name, self.store.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)+slugify(self.id)
        super(Product, self).save(*args, **kwargs)