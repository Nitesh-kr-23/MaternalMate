"""
URL patterns for the core application
Maps URLs to specific view functions
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard & Main Features
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Update user profile
    path('profile/update/', views.update_profile_view, name='update_profile'),
    
    # Health Logging
    path('log-health/', views.log_health_view, name='log_health'),
    
    # Medical Reports
    path('upload-report/', views.upload_report_view, name='upload_report'),
]

