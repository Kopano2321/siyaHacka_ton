# forms.py

from django import forms
from .models import MyCrops, Crops, CustomUser, Profile
from datetime import date
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import DateInput

class MyCropsForm(forms.ModelForm):
    crop = forms.ModelChoiceField(
        queryset=Crops.objects.all(),
        label="Select Crop",
        empty_label="Select a crop"
    )

    class Meta:
        model = MyCrops
        fields = ['crop', 'planted', 'lastWatered']

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if user:
            instance.user = user
        instance.need_watering = instance.lastWatered < date.today()
        instance.mature = (date.today() - instance.planted).days >= instance.crop.timeToMaturity
        if commit:
            instance.save()
        return instance

#################################################################################################################################
# farm/forms.py

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(required=False)
    city = forms.CharField(required=True)
    picture = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class MyCropForm(forms.ModelForm):
    planted = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    lastWatered = forms.DateField(widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        model = MyCrops
        fields = ['crop', 'planted', 'lastWatered']
