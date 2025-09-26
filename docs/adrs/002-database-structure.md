# ADR-002: هيكل قاعدة البيانات للمستخدمين والملفات الشخصية

**التاريخ:** 2025-09-26  
**الحالة:** مقبول  
**المقرر:** فريق تطوير نائبك  

## السياق والمشكلة

منصة نائبك تحتاج لدعم أنواع مختلفة من المستخدمين مع بيانات شخصية متنوعة:

1. **المواطنون العاديون:** لهم حق التصويت والتواصل مع الممثلين
2. **المرشحون:** للبرلمان أو مجلس الشيوخ (بيانات حملة انتخابية)
3. **الأعضاء الحاليون:** أعضاء البرلمان أو الشيوخ (بيانات رسمية)

التحدي هو تصميم هيكل قاعدة بيانات يدعم هذا التنوع مع الحفاظ على:
- **المرونة:** سهولة إضافة أنواع مستخدمين جديدة
- **الأداء:** استعلامات سريعة وفعالة
- **تكامل البيانات:** منع التضارب والتكرار
- **سهولة الصيانة:** كود واضح وقابل للفهم

## البدائل المدروسة

### 1. Single Table Inheritance (جدول واحد)
**الفكرة:** جدول واحد يحتوي على جميع الحقول لكل أنواع المستخدمين

**المزايا:**
- بساطة الاستعلامات
- سرعة في الـ JOIN operations
- سهولة البحث عبر جميع المستخدمين

**العيوب:**
- هدر في المساحة (حقول فارغة كثيرة)
- صعوبة في إضافة حقول جديدة
- تعقيد في validation rules
- مشاكل في الأداء مع نمو البيانات

### 2. Table Per Type (جدول لكل نوع)
**الفكرة:** جدول منفصل لكل نوع مستخدم

**المزايا:**
- لا هدر في المساحة
- مرونة في إضافة حقول خاصة
- validation rules واضحة

**العيوب:**
- تعقيد في الاستعلامات العامة
- صعوبة في البحث الموحد
- تكرار في الكود

### 3. Hybrid Approach (النهج المختلط)
**الفكرة:** جدول أساسي للمستخدم + جداول منفصلة للملفات الشخصية

## القرار المتخذ

**تم اختيار النهج المختلط (Hybrid Approach)** مع التصميم التالي:

### هيكل قاعدة البيانات:

```
User (الجدول الأساسي)
├── id, email, password, first_name, last_name
├── user_type (CITIZEN, PARLIAMENT_CANDIDATE, etc.)
├── verification_status (PENDING, VERIFIED, REJECTED)
├── national_id, phone_number, governorate
└── created_at, updated_at, last_active

CitizenProfile (1:1 مع User)
├── user_id (FK)
├── gender, birth_date, marital_status
├── city, district, street_address
├── occupation, education_level
└── whatsapp_number, profile_picture

CandidateProfile (1:1 مع User)
├── user_id (FK)
├── campaign_name, campaign_slogan
├── party_id (FK), is_independent
├── election_type (PARLIAMENT, SENATE)
├── campaign_budget, campaign_start_date
└── political_experience, education_background

CurrentMemberProfile (1:1 مع User)
├── user_id (FK)
├── position (PARLIAMENT_MEMBER, SENATE_MEMBER)
├── party_id (FK), committee_memberships
├── term_start_date, term_end_date
├── office_address, office_phone
└── achievements, voting_record_summary

Governorate (جدول مرجعي)
├── id, name, name_en, code
└── المحافظات المصرية الـ 27

Party (جدول مرجعي)
├── id, name, name_en, abbreviation
└── الأحزاب السياسية المصرية
```

## مبررات القرار

### 1. **فصل الاهتمامات (Separation of Concerns)**
- الجدول الأساسي يحتوي على البيانات المشتركة فقط
- كل ملف شخصي يحتوي على البيانات الخاصة بنوع المستخدم
- سهولة في إدارة وصيانة كل جزء بشكل منفصل

### 2. **الأداء المحسن**
- استعلامات سريعة للبيانات الأساسية
- لا حاجة لتحميل بيانات غير ضرورية
- إمكانية فهرسة مخصصة لكل جدول

### 3. **المرونة في التطوير**
- سهولة إضافة حقول جديدة لأي نوع مستخدم
- إمكانية إضافة أنواع مستخدمين جديدة
- validation rules مخصصة لكل ملف شخصي

### 4. **تكامل البيانات**
- Foreign Key constraints تضمن تكامل البيانات
- OneToOne relationships تمنع التكرار
- Cascade deletes تضمن تنظيف البيانات

## التطبيق التقني

### Django Models Implementation:

```python
class User(AbstractUser):
    class UserType(models.TextChoices):
        CITIZEN = 'citizen', 'مواطن'
        PARLIAMENT_CANDIDATE = 'parliament_candidate', 'مرشح برلمان'
        # ... باقي الأنواع
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(choices=UserType.choices)
    # ... باقي الحقول

class CitizenProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, 
                               related_name='citizen_profile')
    # ... حقول المواطن

class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                               related_name='candidate_profile')
    # ... حقول المرشح
```

### استراتيجية الاستعلامات:

```python
# الحصول على مستخدم مع ملفه الشخصي
def get_user_with_profile(user_id):
    user = User.objects.get(id=user_id)
    profile = user.get_profile()  # method يرجع الملف المناسب
    return user, profile

# البحث في نوع معين من المستخدمين
def get_candidates_in_governorate(governorate_id):
    return User.objects.filter(
        user_type__in=[User.UserType.PARLIAMENT_CANDIDATE, 
                      User.UserType.SENATE_CANDIDATE],
        governorate_id=governorate_id
    ).select_related('candidate_profile')
```

## العواقب

### الإيجابية:
- **أداء محسن:** استعلامات أسرع وأكثر كفاءة
- **مرونة عالية:** سهولة التطوير والتوسع
- **كود نظيف:** فصل واضح للمسؤوليات
- **صيانة سهلة:** كل جزء يمكن تطويره بشكل مستقل

### السلبية:
- **تعقيد أولي:** حاجة لفهم العلاقات بين الجداول
- **استعلامات معقدة:** بعض الاستعلامات تحتاج JOINs
- **إدارة العلاقات:** الحاجة لضمان تكامل البيانات

### استراتيجيات التخفيف:
1. **Helper Methods:** إنشاء methods مساعدة في النماذج
2. **Manager Classes:** استخدام custom managers للاستعلامات المعقدة
3. **Documentation:** توثيق شامل للعلاقات والاستعلامات
4. **Testing:** اختبارات شاملة لضمان تكامل البيانات

## قواعد العمل

### 1. **إنشاء المستخدمين:**
- يجب إنشاء User أولاً، ثم الملف الشخصي المناسب
- استخدام database transactions لضمان التكامل
- التحقق من نوع المستخدم قبل إنشاء الملف الشخصي

### 2. **تحديث البيانات:**
- البيانات الأساسية تُحدث في جدول User
- البيانات الخاصة تُحدث في الملف الشخصي المناسب
- التحقق من الصلاحيات قبل أي تحديث

### 3. **حذف المستخدمين:**
- حذف User يؤدي لحذف الملف الشخصي تلقائياً (CASCADE)
- الاحتفاظ بسجل للمستخدمين المحذوفين للمراجعة

## المراجعة والتحديث

هذا التصميم سيتم مراجعته عند:
- إضافة أنواع مستخدمين جديدة
- ظهور مشاكل في الأداء
- تغيير متطلبات العمل بشكل جذري

**آخر مراجعة:** 2025-09-26  
**المراجعة القادمة:** 2026-03-26
