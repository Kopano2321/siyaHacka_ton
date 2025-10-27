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
    picture = models.ImageField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50, blank=False, null=False)


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
    
class MyCrops(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='myCrops')
    crop = models.ForeignKey(Crops, on_delete=models.CASCADE, related_name='myCrop')
    planted = models.DateField()
    lastWatered = models.DateField()
    need_watering = models.BooleanField()
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mature = models.BooleanField()

    def last_watering(self):
        return (date.today() - self.lastWatered)
    
    def days_since_planted(self):
        return (date.today() - self.planted).days
    
    def harvest(self):
        return (self.crop.timeToMaturity - date.today())
    
    def days_since_last_water(self):
        """Return the number of days since the crop was last watered."""
        return (date.today() - self.lastWatered).days
    
    def days_until_maturity(self):
        # positive -> still growing; zero/negative -> mature
        return self.crop.timeToMaturity - self.days_since_planted()

    def compute_need_watering(self):
        """
        Simple rule:
         - Map crop.waterLevel.waterLevel to watering interval in days.
         - If days since last water >= interval -> needs watering
        """
        mapping = {
            'Low': 7,     # water every 7 days for 'Low' water need
            'Medium': 4,  # every 4 days
            'High': 2,    # every 2 days
        }
        level = self.crop.waterLevel.waterLevel
        interval = mapping.get(level, 4)  # default 4 days if unknown
        needs = self.days_since_last_water() >= interval
        # update boolean but do not save automatically
        self.need_watering = needs
        return needs

    def compute_mature_flag(self):
        is_mature = self.days_until_maturity() <= 0
        self.mature = is_mature
        self.save()
        return is_mature

    def __str__(self):
        return f"{self.user.username} - {self.crop.name}"