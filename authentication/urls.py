"""
URLs للمصادقة في تطبيق نائبك
"""

from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    # تسجيل وتسجيل دخول
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    
    # Google OAuth
    path('google/', views.GoogleOAuthView.as_view(), name='google_oauth'),
    
    # JWT Token Management
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # الملف الشخصي
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # إدارة كلمة المرور
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    
    # حالة المستخدم
    path('status/', views.user_status, name='user_status'),
    path('welcome/', views.welcome_modal_data, name='welcome_modal'),
    
    # فحص الصحة
    path('health/', views.health_check, name='health_check'),
]
