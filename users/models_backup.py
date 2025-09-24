"""
نماذج المستخدمين المبسطة لتطبيق نائبك
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    نموذج المستخدم المبسط لتطبيق نائبك
    """
    
    class UserType(models.TextChoices):
        CITIZEN = 'citizen', _('مواطن')
        CANDIDATE = 'candidate', _('مرشح')
    
    # إزالة username واستخدام email
    username = None
    email = models.EmailField(_('البريد الإلكتروني'), unique=True)
    
    # البيانات الأساسية
    first_name = models.CharField(_('الاسم الأول'), max_length=150)
    last_name = models.CharField(_('الاسم الأخير'), max_length=150)
    phone_number = PhoneNumberField(_('رقم الهاتف'), blank=True, null=True)
    
    # نوع المستخدم - مبسط
    user_type = models.CharField(
        _('نوع المستخدم'),
        max_length=20,
        choices=UserType.choices,
        default=UserType.CITIZEN
    )
    
    # الرقم القومي
    national_id = models.CharField(
        _('الرقم القومي'),
        max_length=14,
        unique=True,
        blank=True,
        null=True
    )
    
    # المحافظة
    governorate = models.CharField(
        _('المحافظة'),
        max_length=50,
        blank=True
    )
    
    # حالة التحقق - مبسط
    is_verified = models.BooleanField(_('تم التحقق'), default=False)
    
    # تاريخ الإنشاء
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمون')
        db_table = 'auth_user'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class UserProfile(models.Model):
    """
    الملف الشخصي للمستخدم - مبسط
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('المستخدم')
    )
    
    bio = models.TextField(_('نبذة شخصية'), max_length=500, blank=True)
    avatar = models.ImageField(
        _('الصورة الشخصية'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    
    # للمرشحين فقط
    party = models.CharField(_('الحزب'), max_length=100, blank=True)
    constituency = models.CharField(_('الدائرة الانتخابية'), max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('ملف شخصي')
        verbose_name_plural = _('الملفات الشخصية')
    
    def __str__(self):
        return f"ملف {self.user.full_name}"


# المحافظات المصرية
class Governorate(models.Model):
    """
    المحافظات المصرية
    """
    name = models.CharField(_('اسم المحافظة'), max_length=50, unique=True)
    name_en = models.CharField(_('الاسم بالإنجليزية'), max_length=50)
    code = models.CharField(_('الكود'), max_length=3, unique=True)
    
    class Meta:
        verbose_name = _('محافظة')
        verbose_name_plural = _('المحافظات')
        ordering = ['name']
    
    def __str__(self):
        return self.name
