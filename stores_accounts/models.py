from django.db import models
from .choices import OPENINGTIMES_CHOICES
from django.template.defaultfilters import slugify
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings

class StoreCategory(models.Model):
    name    = models.CharField(max_length = 20, unique = True)
    slug    = models.SlugField(max_length = 20, unique = True)

    class Meta:
        verbose_name_plural = "Store Categories"
        
    def __str__(self):
        return self.name


class OpeningTime(models.Model):
    weekday = models.IntegerField(choices = OPENINGTIMES_CHOICES)
    from_hour = models.TimeField()      #for the fields to be required upon store registration, set blank=False and null=False
    to_hour = models.TimeField()

    class Meta:
        ordering = ('weekday', 'from_hour')
        verbose_name_plural = "Opening Times"

    def __unicode__(self):
        return u'%s: %s - %s' % (self.get_weekday_display(),
                                 self.from_hour, self.to_hour)

    def opening_verbose(self):
        return dict(OPENINGTIMES_CHOICES)[self.weekday]


class Store(models.Model):
    user            =   models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    name            =   models.CharField(max_length = 30, blank = False)
    phone           =   PhoneNumberField(blank = False)
    description     =   models.CharField(max_length = 255, blank = True)
    photo           =   models.ImageField(upload_to = 'img/', blank = False, null = False)
    slug            =   models.SlugField(max_length = 20, unique = True)
    categories      =   models.ManyToManyField(StoreCategory, blank = False)
    opening_times   =   models.ManyToManyField(OpeningTime, blank = False)
    city            =   models.ForeignKey('cities_light.City', verbose_name='city', on_delete = models.CASCADE)
    address         =   models.CharField(max_length = 30, blank = False)
    addressNum      =   models.CharField(max_length = 3, blank = False)
    postcode        =   models.CharField(max_length = 5, blank = False)
    email           =   models.EmailField(blank = False, null = False)

    class Meta:
        verbose_name_plural = "Stores"
        unique_together = ('name', 'phone', 'city', 'address', 'addressNum', 'postcode')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Store, self).save(*args, **kwargs)