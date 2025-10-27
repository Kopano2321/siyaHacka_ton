from django.shortcuts import render

# Create your views here.
# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MyCropsForm, UserRegisterForm, MyCropForm
from .models import MyCrops, Crops
from datetime import date
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from .models import Task, ClimateData

##############################################################################################################################
#def add_crop(request):
#@login_required
#    if request.method == "POST":
#        form = MyCropsForm(request.POST)
#        if form.is_valid():
#            form.save(user=request.user)
#            return redirect('plants/my_crops_dashboard')
#    else:
#        form = MyCropsForm()
#    return render(request, 'plants/add_crop.html', {'form': form})
#
#@login_required
#def my_crops_dashboard(request):
#
#    my_crops = MyCrops.objects.filter(user=request.user)
#    for crop in my_crops:
#        # Check if crop needs watering (e.g., if not watered for 5 days)
#
#        days_since_water = (date.today() - crop.lastWatered).days
#        crop.need_watering = days_since_water > 5
#        crop.mature = (date.today() - crop.planted).days >= crop.crop.timeToMaturity
#        crop.save()
#    return render(request, 'plants/my_crops_dashboard.html', {'my_crops': my_crops})



###########################################################################################################################
# farm/views.py

def signup_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email')
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()
            # Profile fields: address, city, picture
            profile = user.profile
            profile.address = form.cleaned_data.get('address') or ''
            profile.city = form.cleaned_data.get('city') or ''
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            login(request, user)
            messages.success(request, 'Account created and logged in.')
            return redirect('plants:dashboard')                             #this was farm:dashboard'
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = UserRegisterForm()
    return render(request, 'plants/signup.html', {'form': form})

from django.contrib.auth.views import LoginView, LogoutView

class CustomLoginView(LoginView):
    template_name = 'plants/login.html'

class CustomLogoutView(LogoutView):
    template_name = 'plants/logout.html'

@login_required
def dashboard(request):
    mycrops = MyCrops.objects.filter(user=request.user).select_related('crop__waterLevel')
    # compute flags for display (but avoid saving unless required)
    for mc in mycrops:
        mc.compute_need_watering()
        mc.compute_mature_flag()
    return render(request, 'plants/dashboard.html', {'mycrops': mycrops})

@login_required
def add_mycrop(request):
    if request.method == 'POST':
        form = MyCropForm(request.POST)
        if form.is_valid():
            mycrop = form.save(commit=False)
            mycrop.user = request.user
            # compute flags initially
            mycrop.compute_need_watering()
            mycrop.compute_mature_flag()
            mycrop.save()
            messages.success(request, 'Crop added.')
            return redirect('plants:dashboard')
        else:
            messages.error(request, 'Please fix the errors.')
    else:
        form = MyCropForm()
    return render(request, 'plants/add_mycrop.html', {'form': form})

@login_required
def edit_mycrop(request, pk):
    mycrop = get_object_or_404(MyCrops, pk=pk, user=request.user)
    if request.method == 'POST':
        form = MyCropForm(request.POST, instance=mycrop)
        if form.is_valid():
            mycrop = form.save(commit=False)
            mycrop.compute_need_watering()
            mycrop.compute_mature_flag()
            mycrop.save()
            messages.success(request, 'Crop updated.')
            return redirect('plants:dashboard')
    else:
        form = MyCropForm(instance=mycrop)
    return render(request, 'plants/edit_mycrop.html', {'form': form, 'mycrop': mycrop})

@login_required
def mark_watered(request, pk):
    """
    Called when the farmer waters the crop manually — sets lastWatered to today
    """
    mycrop = get_object_or_404(MyCrops, pk=pk, user=request.user)
    mycrop.lastWatered = date.today()
    mycrop.compute_need_watering()
    mycrop.save()
    messages.success(request, f'Marked {mycrop.crop.name} as watered today.')
    return redirect('plants:crop_detail', pk=pk)

@login_required
def crop_detail(request, pk):
    mycrop = get_object_or_404(MyCrops.objects.select_related('crop__waterLevel'), pk=pk, user=request.user)
    needs_water = mycrop.compute_need_watering()
    is_mature = mycrop.compute_mature_flag()
    days_since_water = mycrop.days_since_last_water()
    days_until_maturity = mycrop.days_until_maturity()

    # Harvest suggestion: If extreme weather expected (placeholder), suggest harvesting earlier.
    weather_alert = get_weather_alert_placeholder(mycrop)  # placeholder to be implemented
    harvest_suggestion = None
    if is_mature:
        harvest_suggestion = "Crop is mature — harvest now."
    elif days_until_maturity <= 7:
        harvest_suggestion = f"Crop will be mature in {days_until_maturity} days — consider harvesting soon."
    # If a severe weather alert exists, suggest harvest if within 14 days to maturity
    if weather_alert and days_until_maturity <= 14:
        harvest_suggestion = (harvest_suggestion or "") + " Severe weather is expected — consider harvesting earlier."

    context = {
        'mycrop': mycrop,
        'needs_water': needs_water,
        'is_mature': is_mature,
        'days_since_water': days_since_water,
        'days_until_maturity': days_until_maturity,
        'weather_alert': weather_alert,
        'harvest_suggestion': harvest_suggestion
    }
    return render(request, 'farm/crop_detail.html', context)

def get_weather_alert_placeholder(mycrop):
    """
    Placeholder — integrate weather API here.
    Example: call OpenWeather API with location (profile.address / city) and check upcoming forecast for heavy rain, heatwave.
    Return a dict like:
      {'type': 'heavy_rain', 'message': 'Heavy rain expected on 2025-10-30'}
    Or return None if no alert.
    """
    # For hackathon MVP you can leave this as None and add actual API code later.
    return None

def logout_view(request):
    logout(request)
    return render(request, 'plants/logout.html')

@login_required
def dashboard(request):
    # Get climate data (latest entry)
    climate = ClimateData.objects.last()

    # Get all tasks
    all_tasks = Task.objects.all()
    completed_tasks = all_tasks.filter(completed=True).count()
    total_tasks = all_tasks.count()
    urgent_tasks = all_tasks.filter(priority='urgent').count()

    # Calculate completion percentage
    completion_rate = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

    priorities = [
        ('urgent', 'red'),
        ('high', 'brown'),
        ('medium', '#81c784'),
        ('low', '#bdbdbd'),
    ]

    context = {
        'climate': climate,
        'urgent_tasks': urgent_tasks,
        'completed_tasks': completed_tasks,
        'total_tasks': total_tasks,
        'completion_rate': completion_rate,
        'tasks': all_tasks,
        'priorities': priorities,
    }

    return render(request, 'plants/dashboard2.html', context)
