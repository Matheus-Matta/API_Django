from django.contrib import admin
from django.urls import path
from .views.campaign import *

urlpatterns = [
    
    path('dashboard/campaign', dashboard_campaign, name="dashboard_campaign"),
    path('dashboard/campaign/<int:campaign_id>', details_campaign, name="details_campaign"),
    path('dashboard/campaign/encerrar/<int:campaign_id>', encerrar_campaign, name="encerrar_campaign"),
    path('dashboard/campaign/del/<int:campaign_id>', delete_campaign, name="delete_campaign"),

    
]