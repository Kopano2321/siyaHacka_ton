from django.urls import path
from . import views
from .views import CustomLoginView, CustomLogoutView

app_name = 'plants'

urlpatterns = [
    #path('add-crop/', views.add_crop, name='add_crop'),
    #path('my-crops/', views.my_crops_dashboard, name='my_crops_dashboard'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_mycrop, name='add_mycrop'),
    path('edit/<int:pk>/', views.edit_mycrop, name='edit_mycrop'),
    path('crop/<int:pk>/', views.crop_detail, name='crop_detail'),
    path('crop/<int:pk>/water/', views.mark_watered, name='mark_watered'),

    path('logout/', views.logout_view, name='logout'),      #remove the duplicate
]