from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import date

User = settings.AUTH_USER_MODEL #sets user to the custom user field

class CustomUser(AbstractUser):
    first_name=models.CharField(max_length=100, blank=False, null=False)
    last_name=models.CharField(max_length=100)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def __str__(self):
        return f"{self.username}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    picture = models.ImageField()
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}"

class Seasons(models.Model):
    season = models.CharField(max_length=25, blank=False, null=False)
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.season}"

class Water(models.Model):
    waterLevel = models.CharField(max_length=10, blank=False, null=False)
    litresPerWeek = models.IntegerField(blank=False, null=False)
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.waterLevel} = {self.litresPerWeek}"

class Light(models.Model):
    levels = models.CharField(max_length=10, blank=False, null=False)
    lightHours = models.IntegerField(blank=False, null=False)
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.levels} = {self.lightHours}"

class Soil(models.Model):
    soil = models.CharField(max_length=20, blank=False, null=False)
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.soil}"

class Crops(models.Model):
    name = models.CharField(max_length=20, blank=False, null=False)
    season = models.ForeignKey(Seasons, on_delete=models.CASCADE, related_name='crops')
    soilType = models.ForeignKey(Soil, on_delete=models.CASCADE, related_name='crops')
    waterLevel = models.ForeignKey(Water, on_delete=models.CASCADE, related_name='crops')
    lightLevel = models.ForeignKey(Light, on_delete=models.CASCADE, related_name='crops')
    temperatureL = models.IntegerField()
    temperatureH = models.IntegerField()
    timeToMaturity = models.IntegerField()

    def __str__(self):
        return f"{self.name}"
    
    #def last(self):
    #    return (date.today() - self.).days
    #    pass

class MyCrops(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='myCrops')