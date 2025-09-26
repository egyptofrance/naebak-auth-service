# ADR-003: استراتيجية أنواع المستخدمين وإدارة الصلاحيات

**التاريخ:** 2025-09-26  
**الحالة:** مقبول  
**المقرر:** فريق تطوير نائبك  

## السياق والمشكلة

منصة نائبك تحتاج لدعم أنواع مختلفة من المستخدمين مع صلاحيات وقدرات متنوعة:

### أنواع المستخدمين المطلوبة:
1. **المواطن العادي (CITIZEN):** له حق التصويت والتواصل
2. **مرشح البرلمان (PARLIAMENT_CANDIDATE):** يخوض انتخابات البرلمان
3. **مرشح الشيوخ (SENATE_CANDIDATE):** يخوض انتخابات مجلس الشيوخ
4. **عضو البرلمان (PARLIAMENT_MEMBER):** عضو حالي في البرلمان
5. **عضو الشيوخ (SENATE_MEMBER):** عضو حالي في مجلس الشيوخ

### التحديات:
- **إدارة الصلاحيات:** كل نوع له صلاحيات مختلفة
- **التحقق من الهوية:** مستويات تحقق مختلفة حسب النوع
- **تغيير الأنواع:** إمكانية تحول المرشح لعضو حالي
- **المرونة:** سهولة إضافة أنواع جديدة مستقبلاً

## البدائل المدروسة

### 1. Role-Based Access Control (RBAC)
**الفكرة:** استخدام نظام أدوار منفصل عن أنواع المستخدمين

**المزايا:**
- مرونة عالية في إدارة الصلاحيات
- إمكانية تعيين أدوار متعددة للمستخدم الواحد
- سهولة تعديل الصلاحيات دون تغيير الكود

**العيوب:**
- تعقيد إضافي في التطبيق
- صعوبة في فهم العلاقات
- إمكانية تضارب الأدوار

### 2. Attribute-Based Access Control (ABAC)
**الفكرة:** استخدام خصائص المستخدم لتحديد الصلاحيات

**المزايا:**
- مرونة قصوى في تحديد الصلاحيات
- دعم للقواعد المعقدة
- قابلية التوسع العالية

**العيوب:**
- تعقيد كبير في التطبيق
- صعوبة في الفهم والصيانة
- أداء أبطأ في التحقق من الصلاحيات

### 3. Type-Based Permissions (الصلاحيات حسب النوع)
**الفكرة:** ربط الصلاحيات مباشرة بنوع المستخدم

## القرار المتخذ

**تم اختيار Type-Based Permissions مع إمكانيات محدودة للتخصيص**

### تصميم أنواع المستخدمين:

```python
class User(AbstractUser):
    class UserType(models.TextChoices):
        # المواطنون العاديون
        CITIZEN = 'citizen', _('مواطن له صوت انتخابي')
        
        # المرشحون
        PARLIAMENT_CANDIDATE = 'parliament_candidate', _('مرشح لعضوية مجلس النواب')
        SENATE_CANDIDATE = 'senate_candidate', _('مرشح لعضوية مجلس الشيوخ')
        
        # الأعضاء الحاليون
        PARLIAMENT_MEMBER = 'parliament_member', _('عضو حالي في مجلس النواب')
        SENATE_MEMBER = 'senate_member', _('عضو حالي في مجلس الشيوخ')
    
    class VerificationStatus(models.TextChoices):
        PENDING = 'pending', _('في انتظار التحقق')
        VERIFIED = 'verified', _('تم التحقق')
        REJECTED = 'rejected', _('مرفوض')
```

## مبررات القرار

### 1. **البساطة والوضوح**
- كل نوع مستخدم له صلاحيات واضحة ومحددة
- سهولة فهم النظام للمطورين والمستخدمين
- تقليل احتمالية الأخطاء في إدارة الصلاحيات

### 2. **الأداء المحسن**
- التحقق من الصلاحيات سريع (مقارنة enum بسيطة)
- لا حاجة لاستعلامات معقدة لتحديد الصلاحيات
- cache-friendly للصلاحيات

### 3. **متطلبات المشروع المحددة**
- أنواع المستخدمين محددة ومعروفة مسبقاً
- الصلاحيات مرتبطة بشكل وثيق بنوع المستخدم
- لا حاجة لمرونة مفرطة في هذه المرحلة

## تفصيل الصلاحيات لكل نوع

### المواطن العادي (CITIZEN):
```python
def citizen_permissions():
    return [
        'can_vote',                    # التصويت في الانتخابات
        'can_send_messages',           # إرسال رسائل للممثلين
        'can_file_complaints',         # تقديم شكاوى
        'can_rate_representatives',    # تقييم الممثلين
        'can_view_news',              # مشاهدة الأخبار
        'can_update_profile',         # تحديث الملف الشخصي
    ]
```

### المرشح (CANDIDATE):
```python
def candidate_permissions():
    return [
        'can_create_campaign',         # إنشاء حملة انتخابية
        'can_publish_content',         # نشر محتوى الحملة
        'can_respond_to_messages',     # الرد على رسائل المواطنين
        'can_view_analytics',          # مشاهدة إحصائيات الحملة
        'can_manage_campaign_team',    # إدارة فريق الحملة
        'can_update_campaign_info',    # تحديث معلومات الحملة
    ]
```

### العضو الحالي (CURRENT_MEMBER):
```python
def member_permissions():
    return [
        'can_publish_official_content', # نشر محتوى رسمي
        'can_respond_to_complaints',    # الرد على الشكاوى
        'can_create_polls',            # إنشاء استطلاعات رأي
        'can_view_constituency_data',   # مشاهدة بيانات الدائرة
        'can_manage_office_info',      # إدارة معلومات المكتب
        'can_report_activities',       # تقرير الأنشطة البرلمانية
    ]
```

## آلية التحقق من الهوية

### مستويات التحقق:
1. **المواطن العادي:** تحقق أساسي (رقم الهاتف + البريد الإلكتروني)
2. **المرشح:** تحقق متقدم (وثائق رسمية + رقم قومي)
3. **العضو الحالي:** تحقق رسمي (من الجهات المختصة)

### عملية التحقق:
```python
def requires_verification(user_type):
    """تحديد مستوى التحقق المطلوب حسب نوع المستخدم"""
    verification_levels = {
        UserType.CITIZEN: 'basic',
        UserType.PARLIAMENT_CANDIDATE: 'advanced',
        UserType.SENATE_CANDIDATE: 'advanced',
        UserType.PARLIAMENT_MEMBER: 'official',
        UserType.SENATE_MEMBER: 'official',
    }
    return verification_levels.get(user_type, 'basic')
```

## إدارة تحول أنواع المستخدمين

### السيناريوهات المدعومة:
1. **مرشح → عضو حالي:** عند الفوز في الانتخابات
2. **عضو حالي → مواطن عادي:** عند انتهاء المدة
3. **مواطن → مرشح:** عند الترشح للانتخابات

### آلية التحول:
```python
def change_user_type(user, new_type, verification_documents=None):
    """تغيير نوع المستخدم مع التحقق المناسب"""
    
    # التحقق من صحة التحول
    if not is_valid_transition(user.user_type, new_type):
        raise InvalidTransitionError()
    
    # التحقق من الوثائق المطلوبة
    if requires_documents(new_type) and not verification_documents:
        raise DocumentsRequiredError()
    
    # تحديث نوع المستخدم
    user.user_type = new_type
    user.verification_status = VerificationStatus.PENDING
    user.save()
    
    # إنشاء الملف الشخصي الجديد
    create_profile_for_type(user, new_type)
    
    # بدء عملية التحقق
    start_verification_process(user, verification_documents)
```

## التطبيق التقني

### Permission Decorators:
```python
def require_user_type(*allowed_types):
    """Decorator للتحقق من نوع المستخدم"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.user_type not in allowed_types:
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# الاستخدام
@require_user_type(UserType.PARLIAMENT_MEMBER, UserType.SENATE_MEMBER)
def create_official_announcement(request):
    # فقط الأعضاء الحاليون يمكنهم إنشاء إعلانات رسمية
    pass
```

### Permission Checking Methods:
```python
class User(AbstractUser):
    def can_vote(self):
        """التحقق من أهلية التصويت"""
        return (
            self.user_type == self.UserType.CITIZEN and
            self.verification_status == self.VerificationStatus.VERIFIED and
            self.is_active
        )
    
    def can_create_campaign(self):
        """التحقق من إمكانية إنشاء حملة"""
        return (
            self.user_type in [
                self.UserType.PARLIAMENT_CANDIDATE,
                self.UserType.SENATE_CANDIDATE
            ] and
            self.verification_status == self.VerificationStatus.VERIFIED
        )
```

## العواقب

### الإيجابية:
- **بساطة التطبيق:** كود واضح وسهل الفهم
- **أداء عالي:** تحقق سريع من الصلاحيات
- **أمان محكم:** صلاحيات محددة بوضوح
- **سهولة الاختبار:** سيناريوهات واضحة للاختبار

### السلبية:
- **مرونة محدودة:** صعوبة في إضافة صلاحيات مخصصة
- **تعديل الكود:** الحاجة لتعديل الكود عند إضافة أنواع جديدة
- **تعقيد التحولات:** إدارة تحول أنواع المستخدمين معقدة

### استراتيجيات التخفيف:
1. **Extensible Design:** تصميم قابل للتوسع للأنواع الجديدة
2. **Configuration:** استخدام إعدادات خارجية للصلاحيات البسيطة
3. **Audit Trail:** تسجيل جميع تغييرات أنواع المستخدمين
4. **Gradual Migration:** إمكانية التحول التدريجي لـ RBAC مستقبلاً

## قواعد العمل

### 1. **إنشاء المستخدمين:**
- نوع المستخدم يُحدد عند التسجيل
- التحقق من الهوية مطلوب حسب النوع
- الملف الشخصي يُنشأ تلقائياً حسب النوع

### 2. **تغيير الأنواع:**
- يجب الموافقة الإدارية على التحولات الحساسة
- الاحتفاظ بسجل كامل للتغييرات
- إعادة التحقق من الهوية عند الحاجة

### 3. **إدارة الصلاحيات:**
- التحقق من الصلاحيات في كل API call
- استخدام middleware للتحقق التلقائي
- تسجيل محاولات الوصول غير المصرح بها

## المراجعة والتحديث

هذه الاستراتيجية ستتم مراجعتها عند:
- الحاجة لأنواع مستخدمين جديدة
- تعقيد متطلبات الصلاحيات
- مشاكل في الأداء أو الأمان

**آخر مراجعة:** 2025-09-26  
**المراجعة القادمة:** 2026-03-26
