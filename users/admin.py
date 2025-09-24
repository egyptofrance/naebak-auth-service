"""
إعدادات لوحة الإدارة لنماذج المستخدمين
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserSession, AnonymousSession, LoginAttempt


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """إعدادات لوحة إدارة المستخدمين"""
    
    list_display = (
        'email', 'first_name', 'last_name', 'user_type', 
        'verification_status', 'is_active', 'created_at'
    )
    list_filter = (
        'user_type', 'verification_status', 'is_active', 
        'is_email_verified', 'is_phone_verified', 'created_at'
    )
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('المعلومات الشخصية'), {
            'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture', 'bio', 'birth_date')
        }),
        (_('معلومات الحساب'), {
            'fields': ('user_type', 'verification_status', 'national_id')
        }),
        (_('الموقع'), {
            'fields': ('governorate', 'city')
        }),
        (_('التحقق'), {
            'fields': ('is_email_verified', 'is_phone_verified')
        }),
        (_('الصلاحيات'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('تواريخ مهمة'), {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        (_('معلومات إضافية'), {
            'fields': ('google_id', 'last_login_ip', 'receive_notifications'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'user_type', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """إعدادات لوحة إدارة جلسات المستخدمين"""
    
    list_display = ('user', 'ip_address', 'is_active', 'created_at', 'last_activity')
    list_filter = ('is_active', 'created_at', 'last_activity')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'ip_address')
    ordering = ('-last_activity',)
    readonly_fields = ('session_key', 'created_at', 'last_activity')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(AnonymousSession)
class AnonymousSessionAdmin(admin.ModelAdmin):
    """إعدادات لوحة إدارة الجلسات المجهولة"""
    
    list_display = ('session_key', 'ip_address', 'created_at', 'last_activity', 'pages_count')
    list_filter = ('created_at', 'last_activity')
    search_fields = ('ip_address', 'session_key')
    ordering = ('-last_activity',)
    readonly_fields = ('session_key', 'created_at', 'last_activity')
    
    def pages_count(self, obj):
        """عدد الصفحات المزارة"""
        return len(obj.pages_visited)
    pages_count.short_description = _('عدد الصفحات المزارة')


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """إعدادات لوحة إدارة محاولات تسجيل الدخول"""
    
    list_display = ('email', 'ip_address', 'success', 'failure_reason', 'created_at')
    list_filter = ('success', 'created_at')
    search_fields = ('email', 'ip_address')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        """منع إضافة محاولات تسجيل دخول يدوياً"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """منع تعديل محاولات تسجيل الدخول"""
        return False
