from django import forms
from .models import Product

#Form used for inserting product information when adding the product to the menu
class ProductForm(forms.ModelForm):
    price = forms.DecimalField(required=True, max_digits=4, decimal_places = 2, min_value=0, label='')
    class Meta:
        model = Product
        fields = ['name', 'description', 'photo', 'price', 'quantity', 'category', ]
        widgets = {'category':forms.Select(),}

        labels = {'name':'', 'description':'', 'photo':'', 'price':'', 'quantity':'', 'category':'', }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Select category'


#Used for selecting multiple options for a certain product        
class OptionsForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['options',]
        widgets = {'options': forms.CheckboxSelectMultiple(),}
        labels = {'options':'',}

