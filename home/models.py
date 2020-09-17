from django.db import models

class City(models.Model):
    city = models.ForeignKey('cities_light.City', verbose_name='city', on_delete = models.CASCADE)

    class Meta:
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.city.display_name