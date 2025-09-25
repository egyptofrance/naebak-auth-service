# -*- coding: utf-8 -*-
"""
مسارات URL لخدمة المصادقة - نائبك
URL patterns for Naebak Authentication Service
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/verify-token/', views.verify_token, name='verify_token'),
    
    # User profile endpoints
    path('profile/', views.get_user_profile, name='user_profile'),
    
    # Data endpoints
    path('governorates/', views.get_governorates, name='governorates'),
    path('parties/', views.get_parties, name='parties'),
]
