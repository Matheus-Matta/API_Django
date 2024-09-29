from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    
    path('dashboard/campaign', views.dashboard_campaign, name="dashboard_campaign"),

    
]