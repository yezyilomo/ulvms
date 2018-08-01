from django.contrib import admin
from django.urls import path
from aris import views

urlpatterns = [
    path('', views.students),
    path('toggle-status/', views.toggle_status),
    path('get-status/', views.get_status),
    ]
