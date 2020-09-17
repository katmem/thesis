from django import forms
from .models import User, CustomerProfile
from django.core.exceptions import ValidationError

#Form used for submiting and checking validity of a user's password
class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs = {'placeholder':'Password...'}))
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput(attrs = {'placeholder':'Password confirmation...'}))

    class Meta:
        model = User
        fields = ('email',)

        widgets = {'email':forms.EmailInput(attrs = {'placeholder': 'Email...'})}


    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    #Checks if email field is valid.
    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("Email is taken")
        return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


#Used for user registration. 
class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ('first_name', 'last_name', 'phone', 'email',)

        widgets = {
            'first_name': forms.TextInput(attrs = {'placeholder': 'First Name...'}),
            'last_name': forms.TextInput(attrs = {'placeholder': 'Last Name...'}),
            'phone': forms.TextInput(attrs = {'placeholder':'Phone...'}),
            'email': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(CustomerProfileForm, self).__init__(*args, **kwargs)        
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    def save(self, commit = True):
        profile = super(CustomerProfileForm, self).save(commit = False)
        profile.first_name = self.cleaned_data['first_name']
        profile.last_name = self.cleaned_data['last_name']
        profile.phone = self.cleaned_data['phone']

        if commit:
            profile.save()

        return profile


#Used for updating user's firstname, lastname, phone and email
class UpdateProfileForm(forms.Form):
    email       =   forms.EmailField(required = True, label = "Email")
    first_name  =   forms.CharField(required = True, label = "First Name")
    last_name   =   forms.CharField(required = True,label = "Last Name")
    phone       =   forms.CharField(required = True, label = "Phone")


    #Pass current user's id from view to form, because request.user does not work in forms.py
    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        self.profile = kwargs.pop('profile', None)
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
       
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


    #Check if updated email already belongs to another user. If so, raise ValidationError.
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email = email).exclude(id = self.user_id).exists():
            raise ValidationError('Email already exists.')

        return email

    #Find current User object and update its email field. Then update fields to CustomerProfile object and save.
    def save(self, commit = True):
        current_user = User.objects.get(id = self.user_id)
        current_user.email = self.cleaned_data['email']

        updated_profile = self.profile
        updated_profile.first_name = self.cleaned_data['first_name']
        updated_profile.last_name = self.cleaned_data['last_name']
        updated_profile.phone = self.cleaned_data['phone']
        updated_profile.email = self.cleaned_data['email']
        
        if commit:
            current_user.save()
            updated_profile.save()

        return updated_profile
