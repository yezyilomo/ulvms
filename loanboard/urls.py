from django.contrib import admin
from django.urls import path
from loanboard import views

urlpatterns = [
    path('profile/', views.profile),
    path('logout/', views.logoutuser),
    path('notifications/', views.notifications),
    path('file/<file_name>', views.showfile),
    path('view-beneficiaries/', views.view_beneficiaries),
    path('unadmited-beneficiaries/', views.new_beneficiaries),
    path('active-beneficiaries/', views.active_beneficiaries),
    path('fill-data/', views.filldata),
    path('import-beneficiaries/', views.import_beneficiaries),
    path('view-changes/<file_name>', views.view_changes),
    path('loanbeneficiary/update-status/<file_name>/<reg_no>', views.update_status),
    path("initiate-signing/", views.send_beneficiaries),
]
