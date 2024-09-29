from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    
    path('accounts/login', views.login_view, name="login"), # url para pagina de login
    path('accounts/login/auth', views.login_auth, name="login_auth"),  # url para fazer o login
    path('accounts/login/logout', views.login_logout, name="login_logout"), # url para logout da conta
    
]