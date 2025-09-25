"""
نماذج المستخدمين المحدثة - خدمة المصادقة - مشروع نائبك
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField


class Party(models.Model):
    """نموذج الأحزاب السياسية"""
    
    name = models.CharField('اسم الحزب', max_length=200, unique=True)
    name_en = models.CharField('الاسم بالإنجليزية', max_length=200, blank=True)
    abbreviation = models.CharField('الاختصار', max_length=10, blank=True)
    description = models.TextField('الوصف', blank=True)
    
    # الشعار والألوان
    logo = models.ImageField('الشعار', upload_to='parties/logos/', blank=True, null=True)
    primary_color = models.CharField('اللون الأساسي', max_length=7, default='#007BFF')
    secondary_color = models.CharField('اللون الثانوي', max_length=7, default='#6C757D')
    
    # معلومات التأسيس
    founded_date = models.DateField('تاريخ التأسيس', blank=True, null=True)
    headquarters = models.CharField('المقر الرئيسي', max_length=200, blank=True)
    website = models.URLField('الموقع الإلكتروني', blank=True)
    
    # إعدادات العرض
    is_active = models.BooleanField('نشط', default=True)
    display_order = models.PositiveIntegerField('ترتيب العرض', default=0)
    
    # إحصائيات
    members_count = models.PositiveIntegerField('عدد الأعضاء', default=0)
    
    # التواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        db_table = 'parties'
        verbose_name = 'حزب'
        verbose_name_plural = 'الأحزاب'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def update_members_count(self):
        """تحديث عدد الأعضاء"""
        self.members_count = self.user_set.filter(
            user_type__in=['candidate', 'current_member']
        ).count()
        self.save(update_fields=['members_count'])


class Governorate(models.Model):
    """نموذج المحافظات المصرية"""
    
    name = models.CharField('اسم المحافظة', max_length=50, unique=True)
    name_en = models.CharField('الاسم بالإنجليزية', max_length=50)
    code = models.CharField('الكود', max_length=3, unique=True)
    
    # معلومات جغرافية
    region = models.CharField('المنطقة', max_length=50, blank=True)  # شمال، جنوب، وسط، إلخ
    population = models.PositiveIntegerField('عدد السكان', null=True, blank=True)
    area_km2 = models.FloatField('المساحة (كم²)', null=True, blank=True)
    
    # إعدادات العرض
    is_active = models.BooleanField('نشط', default=True)
    display_order = models.PositiveIntegerField('ترتيب العرض', default=0)
    
    # إحصائيات
    users_count = models.PositiveIntegerField('عدد المستخدمين', default=0)
    representatives_count = models.PositiveIntegerField('عدد النواب', default=0)
    
    # التواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        db_table = 'governorates'
        verbose_name = 'محافظة'
        verbose_name_plural = 'المحافظات'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    """نموذج المستخدم المخصص"""
    
    USER_TYPES = [
        ('citizen', 'مواطن'),
        ('candidate', 'مرشح'),
        ('current_member', 'عضو حالي'),
        ('admin', 'إدارة'),
    ]
    
    COUNCIL_TYPES = [
        ('parliament', 'مجلس النواب'),
        ('senate', 'مجلس الشيوخ'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'ذكر'),
        ('female', 'أنثى'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'أعزب'),
        ('married', 'متزوج'),
        ('divorced', 'مطلق'),
        ('widowed', 'أرمل'),
    ]
    
    EDUCATION_LEVELS = [
        ('primary', 'ابتدائي'),
        ('secondary', 'ثانوي'),
        ('university', 'جامعي'),
        ('postgraduate', 'دراسات عليا'),
    ]
    
    # معلومات أساسية (مطلوبة)
    email = models.EmailField('البريد الإلكتروني', unique=True)
    phone_number = PhoneNumberField('رقم الهاتف', unique=True)
    whatsapp_number = PhoneNumberField('رقم الواتساب', blank=True, null=True)
    
    # الاسم الكامل
    first_name = models.CharField('الاسم الأول', max_length=50)
    last_name = models.CharField('الاسم الأخير', max_length=50)
    
    # الهوية
    national_id = models.CharField(
        'الرقم القومي',
        max_length=14,
        unique=True,
        validators=[RegexValidator(r'^\d{14}$', 'الرقم القومي يجب أن يكون 14 رقم')]
    )
    
    # الموقع الجغرافي
    governorate = models.ForeignKey(
        Governorate, 
        on_delete=models.PROTECT, 
        verbose_name='المحافظة'
    )
    city = models.CharField('المدينة', max_length=100)
    district = models.CharField('الحي', max_length=100, blank=True)
    street_address = models.TextField('العنوان التفصيلي', max_length=200)
    postal_code = models.CharField('الرمز البريدي', max_length=10, blank=True)
    
    # نوع المستخدم
    user_type = models.CharField('نوع المستخدم', max_length=20, choices=USER_TYPES)
    
    # معلومات شخصية
    gender = models.CharField('الجنس', max_length=10, choices=GENDER_CHOICES, blank=True)
    birth_date = models.DateField('تاريخ الميلاد', blank=True, null=True)
    marital_status = models.CharField('الحالة الاجتماعية', max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True)
    occupation = models.CharField('المهنة', max_length=100, blank=True)
    education_level = models.CharField('المستوى التعليمي', max_length=20, choices=EDUCATION_LEVELS, blank=True)
    
    # معلومات المرشح/العضو (للنواب والمرشحين فقط)
    council_type = models.CharField(
        'نوع المجلس', 
        max_length=20, 
        choices=COUNCIL_TYPES, 
        blank=True, 
        null=True
    )
    party = models.ForeignKey(
        Party, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='الحزب'
    )
    constituency = models.CharField('الدائرة الانتخابية', max_length=100, blank=True)
    
    # معلومات المرشح
    electoral_number = models.CharField('الرقم الانتخابي', max_length=20, blank=True)
    electoral_symbol = models.CharField('الرمز الانتخابي', max_length=50, blank=True)
    
    # معلومات العضو الحالي
    membership_start_date = models.DateField('تاريخ بداية العضوية', blank=True, null=True)
    term_number = models.PositiveIntegerField('رقم الدورة', null=True, blank=True)
    seat_number = models.CharField('رقم المقعد', max_length=10, blank=True)
    
    # الصورة الشخصية
    profile_picture = models.ImageField('الصورة الشخصية', upload_to='profiles/', blank=True, null=True)
    banner_image = models.ImageField('صورة البانر', upload_to='banners/', blank=True, null=True)
    
    # السيرة الذاتية والمعلومات
    bio = models.TextField('نبذة شخصية', max_length=1000, blank=True)
    achievements = models.TextField('الإنجازات', max_length=2000, blank=True)
    experience = models.TextField('الخبرات السابقة', max_length=1000, blank=True)
    
    # معلومات التواصل الاجتماعي
    facebook_url = models.URLField('فيسبوك', blank=True)
    twitter_url = models.URLField('تويتر', blank=True)
    instagram_url = models.URLField('إنستجرام', blank=True)
    linkedin_url = models.URLField('لينكد إن', blank=True)
    youtube_url = models.URLField('يوتيوب', blank=True)
    website_url = models.URLField('الموقع الشخصي', blank=True)
    
    # إعدادات الخصوصية
    show_phone_public = models.BooleanField('إظهار الهاتف للعامة', default=False)
    show_address_public = models.BooleanField('إظهار العنوان للعامة', default=False)
    allow_messages = models.BooleanField('السماح بالرسائل', default=True)
    allow_ratings = models.BooleanField('السماح بالتقييمات', default=True)
    
    # حالة التحقق
    is_verified = models.BooleanField('تم التحقق', default=False)
    email_verified = models.BooleanField('تم التحقق من البريد', default=False)
    phone_verified = models.BooleanField('تم التحقق من الهاتف', default=False)
    identity_verified = models.BooleanField('تم التحقق من الهوية', default=False)
    
    # حالة الموافقة (للمرشحين والأعضاء)
    is_approved = models.BooleanField('تمت الموافقة', default=False)
    approval_date = models.DateTimeField('تاريخ الموافقة', null=True, blank=True)
    approved_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_users',
        verbose_name='تمت الموافقة بواسطة'
    )
    
    # إحصائيات
    profile_views = models.PositiveIntegerField('مشاهدات الملف', default=0)
    messages_sent = models.PositiveIntegerField('الرسائل المرسلة', default=0)
    messages_received = models.PositiveIntegerField('الرسائل المستلمة', default=0)
    complaints_submitted = models.PositiveIntegerField('الشكاوى المقدمة', default=0)
    complaints_assigned = models.PositiveIntegerField('الشكاوى المعينة', default=0)
    complaints_solved = models.PositiveIntegerField('الشكاوى المحلولة', default=0)
    ratings_given = models.PositiveIntegerField('التقييمات المعطاة', default=0)
    rating_average = models.FloatField('متوسط التقييم', default=0.0)
    rating_count = models.PositiveIntegerField('عدد التقييمات', default=0)
    
    # تواريخ النشاط
    last_login_ip = models.GenericIPAddressField('آخر IP للدخول', blank=True, null=True)
    last_active = models.DateTimeField('آخر نشاط', auto_now=True)
    
    # إعدادات الحساب
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'phone_number', 'national_id']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['national_id']),
            models.Index(fields=['user_type']),
            models.Index(fields=['governorate']),
            models.Index(fields=['council_type']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        """إرجاع الاسم الكامل"""
        return f"{self.first_name} {self.last_name}"
    
    def get_display_name(self):
        """إرجاع الاسم للعرض حسب نوع المستخدم"""
        if self.user_type == 'candidate':
            council = 'مجلس النواب' if self.council_type == 'parliament' else 'مجلس الشيوخ'
            return f"المرشح {self.get_full_name()} - {council}"
        elif self.user_type == 'current_member':
            council = 'مجلس النواب' if self.council_type == 'parliament' else 'مجلس الشيوخ'
            return f"النائب {self.get_full_name()} - {council}"
        return self.get_full_name()
    
    def get_full_address(self):
        """إرجاع العنوان الكامل"""
        address_parts = [self.street_address, self.city, self.governorate.name]
        if self.district:
            address_parts.insert(-1, self.district)
        return ', '.join(filter(None, address_parts))
    
    def is_candidate(self):
        """التحقق من كون المستخدم مرشح"""
        return self.user_type == 'candidate'
    
    def is_current_member(self):
        """التحقق من كون المستخدم عضو حالي"""
        return self.user_type == 'current_member'
    
    def is_citizen(self):
        """التحقق من كون المستخدم مواطن"""
        return self.user_type == 'citizen'
    
    def is_representative(self):
        """التحقق من كون المستخدم نائب (مرشح أو عضو حالي)"""
        return self.user_type in ['candidate', 'current_member']
    
    def can_receive_complaints(self):
        """التحقق من إمكانية استقبال الشكاوى"""
        return self.is_representative() and self.is_approved and self.is_active
    
    def update_rating(self, new_rating):
        """تحديث متوسط التقييم"""
        total_rating = (self.rating_average * self.rating_count) + new_rating
        self.rating_count += 1
        self.rating_average = total_rating / self.rating_count
        self.save(update_fields=['rating_average', 'rating_count'])


class UserSettings(models.Model):
    """إعدادات المستخدم"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    
    # إعدادات الإشعارات
    email_notifications = models.BooleanField('إشعارات البريد الإلكتروني', default=True)
    sms_notifications = models.BooleanField('إشعارات SMS', default=False)
    push_notifications = models.BooleanField('الإشعارات المباشرة', default=True)
    
    # إعدادات الخصوصية
    profile_visibility = models.CharField(
        'ظهور الملف الشخصي',
        max_length=20,
        choices=[
            ('public', 'عام'),
            ('registered', 'للمسجلين فقط'),
            ('private', 'خاص'),
        ],
        default='public'
    )
    
    # إعدادات اللغة والعرض
    language = models.CharField(
        'اللغة',
        max_length=10,
        choices=[
            ('ar', 'العربية'),
            ('en', 'English'),
        ],
        default='ar'
    )
    timezone = models.CharField('المنطقة الزمنية', max_length=50, default='Africa/Cairo')
    
    # إعدادات التواصل
    allow_direct_messages = models.BooleanField('السماح بالرسائل المباشرة', default=True)
    allow_complaint_assignment = models.BooleanField('السماح بتعيين الشكاوى', default=True)
    
    # التواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        db_table = 'user_settings'
        verbose_name = 'إعدادات مستخدم'
        verbose_name_plural = 'إعدادات المستخدمين'
    
    def __str__(self):
        return f"إعدادات {self.user.get_full_name()}"


class LoginHistory(models.Model):
    """سجل تسجيل الدخول"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField('عنوان IP')
    user_agent = models.TextField('معلومات المتصفح')
    device_type = models.CharField('نوع الجهاز', max_length=50, blank=True)
    location = models.CharField('الموقع', max_length=100, blank=True)
    
    login_time = models.DateTimeField('وقت الدخول', auto_now_add=True)
    logout_time = models.DateTimeField('وقت الخروج', blank=True, null=True)
    session_duration = models.DurationField('مدة الجلسة', blank=True, null=True)
    
    is_successful = models.BooleanField('نجح الدخول', default=True)
    failure_reason = models.CharField('سبب الفشل', max_length=200, blank=True)
    
    class Meta:
        db_table = 'login_history'
        verbose_name = 'سجل دخول'
        verbose_name_plural = 'سجلات الدخول'
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', '-login_time']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.login_time}"


class VerificationCode(models.Model):
    """رموز التحقق"""
    
    CODE_TYPES = [
        ('email', 'تحقق البريد الإلكتروني'),
        ('phone', 'تحقق الهاتف'),
        ('password_reset', 'إعادة تعيين كلمة المرور'),
        ('account_activation', 'تفعيل الحساب'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField('الرمز', max_length=6)
    code_type = models.CharField('نوع الرمز', max_length=20, choices=CODE_TYPES)
    
    is_used = models.BooleanField('تم الاستخدام', default=False)
    expires_at = models.DateTimeField('ينتهي في')
    
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    used_at = models.DateTimeField('تاريخ الاستخدام', blank=True, null=True)
    
    class Meta:
        db_table = 'verification_codes'
        verbose_name = 'رمز تحقق'
        verbose_name_plural = 'رموز التحقق'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'code_type']),
            models.Index(fields=['code']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_code_type_display()}"
    
    def is_valid(self):
        """التحقق من صحة الرمز"""
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()
    
    def mark_as_used(self):
        """تمييز الرمز كمستخدم"""
        from django.utils import timezone
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])
