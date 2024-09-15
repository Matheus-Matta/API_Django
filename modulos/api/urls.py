from django.urls import path
from . import views

urlpatterns = [
    path('api', views.index, name='index'),  # Acessado através de '/api/'
    path('api/sendMsg', views.send_msg, name='send_msg'),  # Acessado através de '/api/sendMsg/'
    path('api/doc', views.doc, name='doc'),  # documentação da api
]