from django.contrib import admin
from django.urls import path
from student import views

urlpatterns = [
    path('profile/', views.profile),
    path('logout/', views.logoutuser),
    #path('notifications/', views.notifications),
]
