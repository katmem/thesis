from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser
from phonenumber_field.modelfields import PhoneNumberField
from .managers import *
from django.conf import settings

class User(AbstractBaseUser):
    email = models.EmailField(max_length = 255, unique = True)
    active = models.BooleanField(default = True)
    staff = models.BooleanField(default = False)
    admin = models.BooleanField(default = False)
    business = models.BooleanField(default = False)
    timestamp = models.DateTimeField(auto_now_add = True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):            
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `store`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        "Is the user active?"
        return self.active

    @property
    def is_business(self):
        "Is the user business?"
        return self.business
    
    objects = UserManager()


class CustomerProfile(models.Model):
    user        =   models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, blank = True, null= True)
    first_name  =   models.CharField(max_length = 20, blank = False)
    last_name   =   models.CharField(max_length = 20, blank = False)
    phone       =   PhoneNumberField(blank = False)
    email       =   models.EmailField(blank = True, null = True)

    class Meta:
        verbose_name_plural = "Customer Profiles"
