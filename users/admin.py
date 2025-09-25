"""
إعدادات لوحة الإدارة لنماذج المستخدمين
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Governorate, Party, CitizenProfile, CandidateProfile, CurrentMemberProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """إعدادات لوحة إدارة المستخدمين"""
    
    list_display = (
        'email', 'first_name', 'last_name', 'user_type', 
        'verification_status', 'is_active', 'date_joined'
    )
    list_filter = (
        'user_type', 'verification_status', 'is_active', 'date_joined'
    )
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('المعلومات الشخصية'), {
            'fields': ('first_name', 'last_name', 'phone_number')
        }),
        (_('معلومات الحساب'), {
            'fields': ('user_type', 'verification_status')
        }),
        (_('الصلاحيات'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('تواريخ مهمة'), {
            'fields': ('last_login', 'date_joined', 'last_active'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'user_type', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_active', 'last_login')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(Governorate)
class GovernorateAdmin(admin.ModelAdmin):
    """إدارة المحافظات"""
    
    list_display = ['name', 'name_en', 'code']
    search_fields = ['name', 'name_en', 'code']
    ordering = ['name']


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    """إدارة الأحزاب"""
    
    list_display = ['name', 'name_en', 'abbreviation']
    search_fields = ['name', 'name_en', 'abbreviation']
    ordering = ['name']


@admin.register(CitizenProfile)
class CitizenProfileAdmin(admin.ModelAdmin):
    """إدارة ملفات المواطنين"""
    
    list_display = ['user', 'governorate', 'city', 'is_verified', 'created_at']
    list_filter = ['governorate', 'is_verified', 'gender', 'education_level']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'national_id']
    ordering = ['-created_at']


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    """إدارة ملفات المرشحين"""
    
    list_display = ['user', 'council_type', 'party', 'constituency', 'is_approved', 'created_at']
    list_filter = ['council_type', 'party', 'is_approved', 'governorate']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'electoral_number']
    ordering = ['-created_at']


@admin.register(CurrentMemberProfile)
class CurrentMemberProfileAdmin(admin.ModelAdmin):
    """إدارة ملفات الأعضاء الحاليين"""
    
    list_display = ['user', 'council_type', 'party', 'constituency', 'term_number', 'created_at']
    list_filter = ['council_type', 'party', 'term_number', 'governorate']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']
