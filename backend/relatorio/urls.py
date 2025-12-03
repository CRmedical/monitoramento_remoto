from django.urls import path
from . import views

urlpatterns = [
    path('', views.relatorio, name='relatorio')
]
