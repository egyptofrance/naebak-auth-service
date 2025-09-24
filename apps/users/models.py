"""
نماذج المستخدمين لمنصة نائبك
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    """نموذج المستخدم المخصص"""
    
    USER_TYPES = [
        ('citizen', 'مواطن'),
        ('candidate', 'مرشح'),
        ('member', 'عضو حالي'),
    ]
    
    COUNCIL_TYPES = [
        ('parliament', 'مجلس النواب'),
        ('senate', 'مجلس الشيوخ'),
    ]
    
    MEMBERSHIP_STATUS = [
        ('candidate', 'مرشح للعضوية'),
        ('current_member', 'عضو حالي'),
    ]
    
    # معلومات أساسية
    email = models.EmailField('البريد الإلكتروني', unique=True)
    phone_number = PhoneNumberField('رقم الهاتف', unique=True)
    whatsapp_number = PhoneNumberField('رقم الواتساب', blank=True, null=True)
    
    # معلومات شخصية
    first_name = models.CharField('الاسم الأول', max_length=100)
    last_name = models.CharField('الاسم الأخير', max_length=100)
    national_id = models.CharField(
        'الرقم القومي',
        max_length=14,
        unique=True,
        validators=[RegexValidator(r'^\d{14}$', 'الرقم القومي يجب أن يكون 14 رقم')]
    )
    
    # العنوان
    governorate = models.CharField('المحافظة', max_length=50)
    city = models.CharField('المدينة', max_length=100)
    address = models.TextField('العنوان التفصيلي')
    
    # نوع المستخدم
    user_type = models.CharField('نوع المستخدم', max_length=20, choices=USER_TYPES)
    
    # معلومات المرشح/العضو (اختيارية)
    council_type = models.CharField(
        'نوع المجلس', 
        max_length=20, 
        choices=COUNCIL_TYPES, 
        blank=True, 
        null=True
    )
    membership_status = models.CharField(
        'حالة العضوية',
        max_length=20,
        choices=MEMBERSHIP_STATUS,
        blank=True,
        null=True
    )
    electoral_district = models.CharField('الدائرة الانتخابية', max_length=100, blank=True)
    electoral_number = models.CharField('الرقم الانتخابي', max_length=20, blank=True)
    electoral_symbol = models.CharField('الرمز الانتخابي', max_length=100, blank=True)
    party = models.ForeignKey(
        'Party', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='الحزب'
    )
    
    # تواريخ مهمة
    membership_start_date = models.DateField('تاريخ بداية العضوية', blank=True, null=True)
    
    # إعدادات الحساب
    is_verified = models.BooleanField('تم التحقق', default=False)
    is_active = models.BooleanField('نشط', default=True)
    email_verified = models.BooleanField('تم التحقق من البريد', default=False)
    phone_verified = models.BooleanField('تم التحقق من الهاتف', default=False)
    
    # تواريخ النظام
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    last_login_ip = models.GenericIPAddressField('آخر IP للدخول', blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'phone_number']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['user_type']),
            models.Index(fields=['governorate']),
            models.Index(fields=['council_type']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        """إرجاع الاسم الكامل"""
        return f"{self.first_name} {self.last_name}"
    
    def get_display_name(self):
        """إرجاع الاسم للعرض حسب نوع المستخدم"""
        if self.user_type in ['candidate', 'member']:
            title = 'المرشح' if self.user_type == 'candidate' else 'النائب'
            council = 'مجلس النواب' if self.council_type == 'parliament' else 'مجلس الشيوخ'
            return f"{title} {self.get_full_name()} - {council}"
        return self.get_full_name()
    
    def is_candidate(self):
        """التحقق من كون المستخدم مرشح"""
        return self.user_type == 'candidate'
    
    def is_member(self):
        """التحقق من كون المستخدم عضو حالي"""
        return self.user_type == 'member'
    
    def is_citizen(self):
        """التحقق من كون المستخدم مواطن"""
        return self.user_type == 'citizen'


class Party(models.Model):
    """نموذج الأحزاب السياسية"""
    
    name = models.CharField('اسم الحزب', max_length=200, unique=True)
    abbreviation = models.CharField('الاختصار', max_length=10, blank=True)
    description = models.TextField('الوصف', blank=True)
    logo = models.ImageField('الشعار', upload_to='parties/logos/', blank=True, null=True)
    website = models.URLField('الموقع الإلكتروني', blank=True)
    
    # معلومات التأسيس
    founded_date = models.DateField('تاريخ التأسيس', blank=True, null=True)
    headquarters = models.CharField('المقر الرئيسي', max_length=200, blank=True)
    
    # إعدادات
    is_active = models.BooleanField('نشط', default=True)
    display_order = models.PositiveIntegerField('ترتيب العرض', default=0)
    
    # تواريخ النظام
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        db_table = 'parties'
        verbose_name = 'حزب'
        verbose_name_plural = 'الأحزاب'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_members_count(self):
        """عدد أعضاء الحزب"""
        return self.user_set.filter(user_type__in=['candidate', 'member']).count()


class UserProfile(models.Model):
    """ملف المستخدم الشخصي"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # الصورة الشخصية
    avatar = models.ImageField('الصورة الشخصية', upload_to='avatars/', blank=True, null=True)
    
    # معلومات إضافية
    bio = models.TextField('نبذة شخصية', max_length=500, blank=True)
    birth_date = models.DateField('تاريخ الميلاد', blank=True, null=True)
    gender = models.CharField(
        'الجنس',
        max_length=10,
        choices=[('male', 'ذكر'), ('female', 'أنثى')],
        blank=True
    )
    
    # معلومات التواصل الاجتماعي
    facebook_url = models.URLField('فيسبوك', blank=True)
    twitter_url = models.URLField('تويتر', blank=True)
    instagram_url = models.URLField('إنستجرام', blank=True)
    linkedin_url = models.URLField('لينكد إن', blank=True)
    youtube_url = models.URLField('يوتيوب', blank=True)
    
    # إحصائيات
    profile_views = models.PositiveIntegerField('مشاهدات الملف', default=0)
    messages_received = models.PositiveIntegerField('الرسائل المستلمة', default=0)
    complaints_submitted = models.PositiveIntegerField('الشكاوى المقدمة', default=0)
    
    # إعدادات الخصوصية
    show_phone = models.BooleanField('إظهار الهاتف', default=False)
    show_email = models.BooleanField('إظهار البريد', default=False)
    allow_messages = models.BooleanField('السماح بالرسائل', default=True)
    
    # تواريخ النظام
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'ملف شخصي'
        verbose_name_plural = 'الملفات الشخصية'
    
    def __str__(self):
        return f"ملف {self.user.get_full_name()}"
    
    def get_age(self):
        """حساب العمر"""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None


class LoginHistory(models.Model):
    """سجل تسجيل الدخول"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField('عنوان IP')
    user_agent = models.TextField('معلومات المتصفح')
    login_time = models.DateTimeField('وقت الدخول', auto_now_add=True)
    logout_time = models.DateTimeField('وقت الخروج', blank=True, null=True)
    is_successful = models.BooleanField('نجح الدخول', default=True)
    failure_reason = models.CharField('سبب الفشل', max_length=200, blank=True)
    
    class Meta:
        db_table = 'login_history'
        verbose_name = 'سجل دخول'
        verbose_name_plural = 'سجلات الدخول'
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.login_time}"
