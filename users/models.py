"""
نماذج المستخدمين لتطبيق نائبك
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from .managers import UserManager


class User(AbstractUser):
    """
    نموذج المستخدم المخصص لتطبيق نائبك
    يدعم أنواع مختلفة من المستخدمين مع مرونة في المصادقة
    """
    
    class UserType(models.TextChoices):
        CITIZEN = 'citizen', _('مواطن له صوت انتخابي')
        PARLIAMENT_CANDIDATE = 'parliament_candidate', _('مرشح لعضوية مجلس النواب')
        SENATE_CANDIDATE = 'senate_candidate', _('مرشح لعضوية مجلس الشيوخ')
        PARLIAMENT_MEMBER = 'parliament_member', _('عضو حالي في مجلس النواب')
        SENATE_MEMBER = 'senate_member', _('عضو حالي في مجلس الشيوخ')
    
    class VerificationStatus(models.TextChoices):
        PENDING = 'pending', _('في انتظار التحقق')
        VERIFIED = 'verified', _('تم التحقق')
        REJECTED = 'rejected', _('مرفوض')
    
    # إزالة username واستخدام email كمعرف رئيسي
    username = None
    email = models.EmailField(_('البريد الإلكتروني'), unique=True)
    
    # البيانات الأساسية
    first_name = models.CharField(_('الاسم الأول'), max_length=150)
    last_name = models.CharField(_('الاسم الأخير'), max_length=150)
    phone_number = PhoneNumberField(_('رقم الهاتف'), blank=True, null=True)
    
    # نوع المستخدم
    user_type = models.CharField(
        _('نوع المستخدم'),
        max_length=20,
        choices=UserType.choices,
        default=UserType.CITIZEN
    )
    
    # حالة التحقق
    verification_status = models.CharField(
        _('حالة التحقق'),
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )
    
    # الصورة الشخصية
    profile_picture = models.ImageField(
        _('الصورة الشخصية'),
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    
    # معلومات إضافية
    bio = models.TextField(_('نبذة شخصية'), blank=True, max_length=500)
    birth_date = models.DateField(_('تاريخ الميلاد'), blank=True, null=True)
    national_id = models.CharField(_('الرقم القومي'), max_length=14, blank=True, unique=True, null=True)
    
    # معلومات الموقع
    governorate = models.CharField(_('المحافظة'), max_length=100, blank=True)
    city = models.CharField(_('المدينة'), max_length=100, blank=True)
    
    # إعدادات الحساب
    is_email_verified = models.BooleanField(_('تم التحقق من البريد'), default=False)
    is_phone_verified = models.BooleanField(_('تم التحقق من الهاتف'), default=False)
    receive_notifications = models.BooleanField(_('استقبال الإشعارات'), default=True)
    
    # معلومات Google OAuth
    google_id = models.CharField(_('معرف Google'), max_length=100, blank=True, null=True, unique=True)
    
    # تواريخ مهمة
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    last_login_ip = models.GenericIPAddressField(_('آخر IP للدخول'), blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمون')
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
            models.Index(fields=['verification_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """إرجاع الاسم الكامل للمستخدم"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """إرجاع الاسم الأول فقط"""
        return self.first_name
    
    @property
    def is_verified(self):
        """التحقق من حالة التحقق من الهوية"""
        return self.verification_status == self.VerificationStatus.VERIFIED
    
    @property
    def is_candidate(self):
        """التحقق من كون المستخدم مرشح"""
        return self.user_type in [
            self.UserType.PARLIAMENT_CANDIDATE,
            self.UserType.SENATE_CANDIDATE
        ]
    
    @property
    def is_member(self):
        """التحقق من كون المستخدم عضو في البرلمان"""
        return self.user_type in [
            self.UserType.PARLIAMENT_MEMBER,
            self.UserType.SENATE_MEMBER
        ]
    
    @property
    def can_vote(self):
        """التحقق من حق التصويت"""
        return self.user_type == self.UserType.CITIZEN and self.is_verified
    
    def get_user_type_display_ar(self):
        """إرجاع نوع المستخدم بالعربية"""
        type_mapping = {
            self.UserType.CITIZEN: 'مواطن له صوت انتخابي',
            self.UserType.PARLIAMENT_CANDIDATE: 'مرشح لعضوية مجلس النواب',
            self.UserType.SENATE_CANDIDATE: 'مرشح لعضوية مجلس الشيوخ',
            self.UserType.PARLIAMENT_MEMBER: 'عضو حالي في مجلس النواب',
            self.UserType.SENATE_MEMBER: 'عضو حالي في مجلس الشيوخ',
        }
        return type_mapping.get(self.user_type, self.user_type)


class UserSession(models.Model):
    """
    نموذج لتتبع جلسات المستخدمين
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(_('مفتاح الجلسة'), max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(_('عنوان IP'))
    user_agent = models.TextField(_('معلومات المتصفح'), blank=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    last_activity = models.DateTimeField(_('آخر نشاط'), auto_now=True)
    
    class Meta:
        verbose_name = _('جلسة مستخدم')
        verbose_name_plural = _('جلسات المستخدمين')
        db_table = 'user_sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"جلسة {self.user.get_full_name()} - {self.ip_address}"


class AnonymousSession(models.Model):
    """
    نموذج لتتبع الجلسات المجهولة (للتصفح بدون تسجيل)
    """
    session_key = models.CharField(_('مفتاح الجلسة'), max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(_('عنوان IP'))
    user_agent = models.TextField(_('معلومات المتصفح'), blank=True)
    pages_visited = models.JSONField(_('الصفحات المزارة'), default=list)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    last_activity = models.DateTimeField(_('آخر نشاط'), auto_now=True)
    
    class Meta:
        verbose_name = _('جلسة مجهولة')
        verbose_name_plural = _('الجلسات المجهولة')
        db_table = 'anonymous_sessions'
        indexes = [
            models.Index(fields=['session_key']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"جلسة مجهولة - {self.ip_address}"
    
    def add_visited_page(self, page_url):
        """إضافة صفحة مزارة"""
        if page_url not in self.pages_visited:
            self.pages_visited.append(page_url)
            self.save(update_fields=['pages_visited', 'last_activity'])


class LoginAttempt(models.Model):
    """
    نموذج لتتبع محاولات تسجيل الدخول
    """
    email = models.EmailField(_('البريد الإلكتروني'))
    ip_address = models.GenericIPAddressField(_('عنوان IP'))
    user_agent = models.TextField(_('معلومات المتصفح'), blank=True)
    success = models.BooleanField(_('نجح'), default=False)
    failure_reason = models.CharField(_('سبب الفشل'), max_length=100, blank=True)
    created_at = models.DateTimeField(_('تاريخ المحاولة'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('محاولة تسجيل دخول')
        verbose_name_plural = _('محاولات تسجيل الدخول')
        db_table = 'login_attempts'
        indexes = [
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['success']),
        ]
    
    def __str__(self):
        status = "نجح" if self.success else "فشل"
        return f"{status} - {self.email} - {self.ip_address}"
