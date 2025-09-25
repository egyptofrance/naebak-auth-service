# -*- coding: utf-8 -*-
"""
نماذج المستخدمين لتطبيق نائبك - محدث بالبيانات الكاملة من المخزن
Updated User Models for Naebak Application with Complete Data from Almakhzan
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
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
    first_name = models.CharField(_('الاسم الأول'), max_length=50)
    last_name = models.CharField(_('الاسم الأخير'), max_length=50)
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
    
    # تاريخ آخر نشاط
    last_active = models.DateTimeField(_('آخر نشاط'), auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمون')
        db_table = 'auth_user'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_display_name(self):
        return self.get_full_name()


class Governorate(models.Model):
    """نموذج المحافظات المصرية (27 محافظة)"""
    
    name = models.CharField(_('اسم المحافظة'), max_length=50, unique=True)
    name_en = models.CharField(_('الاسم بالإنجليزية'), max_length=50)
    code = models.CharField(_('كود المحافظة'), max_length=3, unique=True)
    
    class Meta:
        verbose_name = _('محافظة')
        verbose_name_plural = _('المحافظات')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Party(models.Model):
    """نموذج الأحزاب السياسية المصرية"""
    
    name = models.CharField(_('اسم الحزب'), max_length=100, unique=True)
    name_en = models.CharField(_('الاسم بالإنجليزية'), max_length=100)
    abbreviation = models.CharField(_('الاختصار'), max_length=20)
    
    class Meta:
        verbose_name = _('حزب')
        verbose_name_plural = _('الأحزاب')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CitizenProfile(models.Model):
    """نموذج بيانات المواطن الكامل"""
    
    class Gender(models.TextChoices):
        MALE = 'male', _('ذكر')
        FEMALE = 'female', _('أنثى')
    
    class MaritalStatus(models.TextChoices):
        SINGLE = 'single', _('أعزب')
        MARRIED = 'married', _('متزوج')
        DIVORCED = 'divorced', _('مطلق')
        WIDOWED = 'widowed', _('أرمل')
    
    class EducationLevel(models.TextChoices):
        PRIMARY = 'primary', _('ابتدائي')
        SECONDARY = 'secondary', _('ثانوي')
        UNIVERSITY = 'university', _('جامعي')
        POSTGRADUATE = 'postgraduate', _('دراسات عليا')
    
    class VerificationMethod(models.TextChoices):
        PHONE = 'phone', _('رقم الهاتف')
        EMAIL = 'email', _('البريد الإلكتروني')
        NATIONAL_ID = 'national_id', _('الرقم القومي')
    
    # ربط بالمستخدم الأساسي
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='citizen_profile')
    
    # الموقع (مطلوب)
    governorate = models.ForeignKey(Governorate, on_delete=models.PROTECT, verbose_name=_('المحافظة'))
    city = models.CharField(_('المدينة'), max_length=100)
    district = models.CharField(_('الحي'), max_length=100, blank=True)
    street_address = models.CharField(_('العنوان التفصيلي'), max_length=200)
    postal_code = models.CharField(_('الرمز البريدي'), max_length=10, blank=True)
    
    # البيانات الشخصية
    national_id = models.CharField(
        _('الرقم القومي'), 
        max_length=14, 
        unique=True,
        validators=[RegexValidator(regex=r'^\d{14}$', message='الرقم القومي يجب أن يكون 14 رقم')]
    )
    gender = models.CharField(_('النوع'), max_length=10, choices=Gender.choices)
    birth_date = models.DateField(_('تاريخ الميلاد'))
    marital_status = models.CharField(_('الحالة الاجتماعية'), max_length=10, choices=MaritalStatus.choices, blank=True)
    
    # معلومات إضافية
    whatsapp_number = PhoneNumberField(_('رقم الواتساب'), blank=True, null=True)
    occupation = models.CharField(_('المهنة'), max_length=100, blank=True)
    education_level = models.CharField(_('المستوى التعليمي'), max_length=15, choices=EducationLevel.choices, blank=True)
    profile_picture = models.URLField(_('صورة الملف الشخصي'), blank=True)
    
    # إعدادات الخصوصية
    show_phone_public = models.BooleanField(_('إظهار الهاتف للعامة'), default=False)
    show_address_public = models.BooleanField(_('إظهار العنوان للعامة'), default=False)
    allow_messages = models.BooleanField(_('السماح بالرسائل'), default=True)
    
    # الحالة
    is_verified = models.BooleanField(_('تم التحقق'), default=False)
    verification_method = models.CharField(_('طريقة التحقق'), max_length=15, choices=VerificationMethod.choices, blank=True)
    
    # التواريخ
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    # إحصائيات
    messages_sent = models.PositiveIntegerField(_('الرسائل المرسلة'), default=0)
    complaints_submitted = models.PositiveIntegerField(_('الشكاوى المقدمة'), default=0)
    ratings_given = models.PositiveIntegerField(_('التقييمات المعطاة'), default=0)
    
    class Meta:
        verbose_name = _('ملف المواطن')
        verbose_name_plural = _('ملفات المواطنين')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.governorate.name}"
    
    def get_full_address(self):
        """الحصول على العنوان الكامل"""
        address_parts = [self.street_address, self.city, self.governorate.name]
        if self.district:
            address_parts.insert(1, self.district)
        return ", ".join(address_parts)
    
    def get_display_name(self):
        """الحصول على الاسم للعرض"""
        return self.user.get_full_name()


class CandidateProfile(models.Model):
    """نموذج بيانات المرشح الكامل"""
    
    class CouncilType(models.TextChoices):
        PARLIAMENT = 'parliament', _('مجلس النواب')
        SENATE = 'senate', _('مجلس الشيوخ')
    
    # ربط بالمستخدم الأساسي
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    
    # الموقع (مطلوب)
    governorate = models.ForeignKey(Governorate, on_delete=models.PROTECT, verbose_name=_('المحافظة'))
    city = models.CharField(_('المدينة'), max_length=100)
    district = models.CharField(_('الحي'), max_length=100, blank=True)
    street_address = models.CharField(_('العنوان التفصيلي'), max_length=200)
    
    # البيانات الشخصية
    national_id = models.CharField(
        _('الرقم القومي'), 
        max_length=14, 
        unique=True,
        validators=[RegexValidator(regex=r'^\d{14}$', message='الرقم القومي يجب أن يكون 14 رقم')]
    )
    gender = models.CharField(_('النوع'), max_length=10, choices=CitizenProfile.Gender.choices)
    birth_date = models.DateField(_('تاريخ الميلاد'))
    marital_status = models.CharField(_('الحالة الاجتماعية'), max_length=10, choices=CitizenProfile.MaritalStatus.choices, blank=True)
    
    # البيانات السياسية (مطلوبة للمرشح)
    council_type = models.CharField(_('نوع المجلس'), max_length=15, choices=CouncilType.choices)
    party = models.ForeignKey(Party, on_delete=models.PROTECT, verbose_name=_('الحزب'))
    constituency = models.CharField(_('الدائرة الانتخابية'), max_length=100)
    electoral_number = models.CharField(_('الرقم الانتخابي'), max_length=20)
    electoral_symbol = models.CharField(_('الرمز الانتخابي'), max_length=50)
    
    # معلومات المرشح
    whatsapp_number = PhoneNumberField(_('رقم الواتساب'), blank=True, null=True)
    bio = models.TextField(_('السيرة الذاتية'), max_length=1000)
    electoral_program = models.TextField(_('البرنامج الانتخابي'), max_length=2000)
    education = models.CharField(_('المؤهل العلمي'), max_length=200)
    occupation = models.CharField(_('المهنة'), max_length=100)
    experience = models.TextField(_('الخبرات السابقة'), max_length=1000)
    
    # الصور والملفات
    profile_picture = models.URLField(_('صورة الملف الشخصي'))
    banner_image = models.URLField(_('صورة البانر'), blank=True)
    cv_document = models.URLField(_('السيرة الذاتية PDF'), blank=True)
    
    # إعدادات الحملة
    campaign_slogan = models.CharField(_('شعار الحملة'), max_length=200, blank=True)
    campaign_website = models.URLField(_('موقع الحملة'), blank=True)
    campaign_facebook = models.URLField(_('فيسبوك الحملة'), blank=True)
    campaign_twitter = models.URLField(_('تويتر الحملة'), blank=True)
    
    # الحالة
    is_approved = models.BooleanField(_('موافقة الإدارة'), default=False)
    approval_date = models.DateTimeField(_('تاريخ الموافقة'), blank=True, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='approved_candidates')
    
    # إحصائيات
    rating_average = models.FloatField(_('متوسط التقييم'), default=0.0)
    rating_count = models.PositiveIntegerField(_('عدد التقييمات'), default=0)
    messages_received = models.PositiveIntegerField(_('الرسائل المستلمة'), default=0)
    complaints_assigned = models.PositiveIntegerField(_('الشكاوى المعينة'), default=0)
    complaints_solved = models.PositiveIntegerField(_('الشكاوى المحلولة'), default=0)
    
    # التواريخ
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('ملف المرشح')
        verbose_name_plural = _('ملفات المرشحين')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - مرشح {self.get_council_type_display()}"
    
    def get_membership_description(self):
        """وصف العضوية"""
        council_name = "مجلس النواب" if self.council_type == "parliament" else "مجلس الشيوخ"
        return f"مرشح لعضوية {council_name}"
    
    def get_electoral_info(self):
        """معلومات انتخابية"""
        return f"رقم {self.electoral_number} - رمز {self.electoral_symbol}"


class CurrentMemberProfile(models.Model):
    """نموذج بيانات العضو الحالي الكامل"""
    
    # ربط بالمستخدم الأساسي
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')
    
    # الموقع (مطلوب)
    governorate = models.ForeignKey(Governorate, on_delete=models.PROTECT, verbose_name=_('المحافظة'))
    city = models.CharField(_('المدينة'), max_length=100)
    district = models.CharField(_('الحي'), max_length=100, blank=True)
    street_address = models.CharField(_('العنوان التفصيلي'), max_length=200)
    
    # البيانات الشخصية
    national_id = models.CharField(
        _('الرقم القومي'), 
        max_length=14, 
        unique=True,
        validators=[RegexValidator(regex=r'^\d{14}$', message='الرقم القومي يجب أن يكون 14 رقم')]
    )
    gender = models.CharField(_('النوع'), max_length=10, choices=CitizenProfile.Gender.choices)
    birth_date = models.DateField(_('تاريخ الميلاد'))
    marital_status = models.CharField(_('الحالة الاجتماعية'), max_length=10, choices=CitizenProfile.MaritalStatus.choices, blank=True)
    
    # البيانات السياسية (للعضو الحالي)
    council_type = models.CharField(_('نوع المجلس'), max_length=15, choices=CandidateProfile.CouncilType.choices)
    party = models.ForeignKey(Party, on_delete=models.PROTECT, verbose_name=_('الحزب'))
    constituency = models.CharField(_('الدائرة الانتخابية'), max_length=100)
    
    # معلومات العضوية
    membership_start_date = models.DateField(_('تاريخ بداية العضوية'))
    term_number = models.PositiveIntegerField(_('رقم الدورة'))
    seat_number = models.CharField(_('رقم المقعد'), max_length=10, blank=True)
    
    # اللجان والمناصب
    committees = models.TextField(_('اللجان المشارك فيها'), max_length=500, blank=True)
    positions = models.TextField(_('المناصب الحالية'), max_length=300, blank=True)
    
    # معلومات العضو
    whatsapp_number = PhoneNumberField(_('رقم الواتساب'), blank=True, null=True)
    bio = models.TextField(_('السيرة الذاتية'), max_length=1000)
    achievements = models.TextField(_('الإنجازات'), max_length=2000)
    education = models.CharField(_('المؤهل العلمي'), max_length=200)
    occupation = models.CharField(_('المهنة'), max_length=100)
    experience = models.TextField(_('الخبرات السابقة'), max_length=1000)
    
    # الصور والملفات
    profile_picture = models.URLField(_('صورة الملف الشخصي'))
    banner_image = models.URLField(_('صورة البانر'), blank=True)
    official_cv = models.URLField(_('السيرة الذاتية الرسمية'), blank=True)
    
    # إعدادات المكتب
    office_address = models.TextField(_('عنوان المكتب'), max_length=300, blank=True)
    office_phone = PhoneNumberField(_('هاتف المكتب'), blank=True, null=True)
    office_hours = models.CharField(_('ساعات العمل'), max_length=100, blank=True)
    
    # إحصائيات
    rating_average = models.FloatField(_('متوسط التقييم'), default=0.0)
    rating_count = models.PositiveIntegerField(_('عدد التقييمات'), default=0)
    messages_received = models.PositiveIntegerField(_('الرسائل المستلمة'), default=0)
    complaints_handled = models.PositiveIntegerField(_('الشكاوى المعالجة'), default=0)
    complaints_solved = models.PositiveIntegerField(_('الشكاوى المحلولة'), default=0)
    
    # التواريخ
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('ملف العضو الحالي')
        verbose_name_plural = _('ملفات الأعضاء الحاليين')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - عضو {self.get_council_type_display()}"
    
    def get_membership_description(self):
        """وصف العضوية"""
        council_name = "مجلس النواب" if self.council_type == "parliament" else "مجلس الشيوخ"
        return f"عضو {council_name} - الدورة {self.term_number}"
