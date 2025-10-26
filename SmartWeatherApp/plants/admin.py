from django.contrib import admin

# Register your models here.
from .models import CustomUser, Profile, Seasons, Water, Light, Soil, Crops

admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Seasons)
admin.site.register(Water)
admin.site.register(Light)
admin.site.register(Soil)
admin.site.register(Crops)