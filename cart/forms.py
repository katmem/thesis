from django import forms
from .models import PickUpTime
from customers_accounts.models import CustomerProfile
from creditcards.forms import CardNumberField, CardExpiryField, SecurityCodeField

#Used by users for submiting personal data on checkout. If user is authenticated, form is auto-filled. 
class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ('first_name', 'last_name', 'phone', 'email',)

        widgets = {
            'first_name': forms.TextInput(attrs = {'placeholder': 'First Name...'}),
            'last_name': forms.TextInput(attrs = {'placeholder': 'Last Name...'}),
            'phone': forms.TextInput(attrs = {'placeholder':'Phone...'}),
            'email': forms.EmailInput(attrs = {'placeholder':'Email...'})
        }


    def __init__(self, *args, **kwargs):
        self.authenticated = kwargs.pop('authenticated')
        super(CustomerProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True 
        if self.authenticated is True:
            self.fields['email'].widget.attrs['readonly'] = True
        
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


#Used for choosing pickup date on checkout
class PickupDateForm(forms.Form):
    date = forms.DateField()

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', None)
        super(PickupDateForm, self).__init__(*args, **kwargs)

        if choices:
            self.fields['date'] = forms.ChoiceField(choices = choices)
            self.fields['date'].label = 'Pickup Date'

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


#Used for choosing pickup hour on checkout
class PickupTimeForm(forms.Form):
    hour = forms.TimeField()

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', None)
        super(PickupTimeForm, self).__init__(*args, **kwargs)

        if choices:
            self.fields['hour'] = forms.ChoiceField(choices = choices)
            self.fields['hour'].label = 'Pickup Hour'

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


#Used for submiting credit card information on checkout
class PaymentForm(forms.Form):
    cc_number = CardNumberField(label='Card Number')
    cc_expiry = CardExpiryField(label='Expiration Date')
    cc_code = SecurityCodeField(label='CVV/CVC')

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'