from django.contrib import admin
from django.urls import path
from .views.campaign import *

urlpatterns = [
    
    path('dashboard/campaign', dashboard_campaign, name="dashboard_campaign"),
    path('dashboard/campaign/<int:campaign_id>', details_campaign, name="details_campaign"),

    
]