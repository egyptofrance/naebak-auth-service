# 🔐 LEADER - دليل خدمة المصادقة والمستخدمين

**اسم الخدمة:** naebak-auth-service  
**المنفذ:** 8001  
**الإطار:** Django 4.2 + Django REST Framework  
**قاعدة البيانات:** PostgreSQL (للمستخدمين والجلسات)  
**التخزين المؤقت:** Redis (للجلسات والتوكنات)  
**المصادقة:** JWT + Session-based  

---

## 📋 **نظرة عامة على الخدمة**

### **🎯 الغرض الأساسي:**
خدمة المصادقة هي **البوابة الأمنية الرئيسية** لمنصة نائبك، مسؤولة عن إدارة جميع المستخدمين، تسجيل الدخول، التحقق من الهوية، وإدارة الصلاحيات عبر المنصة.

### **👥 أنواع المستخدمين المُدارة:**
1. **المواطنين (Citizens):**
   - تسجيل حساب جديد بالرقم القومي أو Google
   - تحديد المحافظة التابع لها
   - إدخال رقم التليفون والواتساب
   - تقديم الشكاوى والتقييمات
   - متابعة النواب والأخبار

2. **المرشحين (Candidates):**
   - تسجيل عبر Google أو البريد التقليدي
   - تحديد نوع المجلس المرشح له (النواب/الشيوخ)
   - تحديد المحافظة المرشح عنها
   - تحديد الانتماء السياسي (مستقل/حزبي)
   - إدخال رقم التليفون والواتساب للتواصل
   - ملفات شخصية مفصلة وبرامج انتخابية

3. **الأعضاء الحاليين (Current Members):**
   - نواب مجلس النواب (596 مقعد)
   - أعضاء مجلس الشيوخ (300 مقعد)
   - تحديد نوع المجلس الحالي (النواب/الشيوخ)
   - تحديد المحافظة التي يمثلها
   - تحديد الانتماء السياسي (مستقل/حزبي)
   - أرقام التليفون والواتساب للتواصل المباشر
   - الرد على الشكاوى والتفاعل مع المواطنين

4. **الإدارة (Admins):**
   - مديري المحافظات
   - المديرين العامين
   - مديري النظام

### **🔧 الوظائف الرئيسية:**
1. **التسجيل والتحقق:**
   - تسجيل حساب جديد بالرقم القومي أو Google OAuth
   - تحديد نوع المستخدم (مواطن/مرشح/نائب)
   - تحديد المحافظة والانتماء السياسي
   - إدخال أرقام التليفون والواتساب
   - **التحقق الفوري من كلمة المرور** أثناء الكتابة
   - عرض رسائل تطابق/عدم تطابق كلمة المرور فورياً
   - التحقق من الهوية عبر الهاتف/البريد
   - التحقق من صحة البيانات الشخصية

2. **تسجيل الدخول:**
   - تسجيل دخول بالبريد/الهاتف + كلمة المرور
   - تسجيل دخول عبر Google OAuth
   - تسجيل دخول بـ OTP للأمان الإضافي
   - إدارة الجلسات المتعددة

3. **إدارة الصلاحيات:**
   - تحديد صلاحيات كل نوع مستخدم
   - التحكم في الوصول للخدمات
   - إدارة الأدوار والمناصب

4. **الأمان:**
   - حماية من محاولات الاختراق
   - قفل الحسابات المشبوهة
   - تسجيل جميع محاولات الدخول

---

## 🌐 **دور الخدمة في منصة نائبك**

### **🏛️ المكانة في النظام:**
خدمة المصادقة هي **نقطة التحكم المركزية** التي تتحكم في وصول جميع المستخدمين لكافة خدمات المنصة، وهي أول خدمة يتفاعل معها أي مستخدم.

### **📡 العلاقات مع الخدمات الأخرى:**

#### **🔗 جميع الخدمات تعتمد عليها:**
- **خدمة الإدارة (8002)** - التحقق من صلاحيات الأدمن
- **خدمة الشكاوى (8003)** - التحقق من هوية مقدم الشكوى
- **خدمة الرسائل (8004)** - التحقق من هوية المرسل والمستقبل
- **خدمة التقييمات (8005)** - التحقق من هوية المُقيِّم
- **خدمة الأخبار (8007)** - التحقق من صلاحيات النشر
- **خدمة الإشعارات (8008)** - التحقق من هوية المستقبل
- **خدمة البنرات (8009)** - التحقق من صلاحيات الإدارة
- **خدمة المحتوى (8010)** - التحقق من صلاحيات التحرير
- **خدمة البوابة (8013)** - توجيه الطلبات حسب الهوية

#### **🔄 تدفق البيانات:**
```
User Login → Auth Service (8001) → JWT Token Generation
                    ↓
All Services ← Token Validation ← Every API Request
                    ↓
User Permissions ← Role Check ← Service Authorization
                    ↓
Audit Logs ← Security Monitoring ← Suspicious Activity
```

#### **📊 أنماط التفاعل:**
1. **تسجيل الدخول:** POST /api/auth/login/
2. **التحقق من التوكن:** POST /api/auth/verify-token/
3. **تجديد التوكن:** POST /api/auth/refresh-token/
4. **تسجيل الخروج:** POST /api/auth/logout/
5. **التحقق من الصلاحيات:** GET /api/auth/permissions/

---

## 📦 **البيانات والنماذج من المستودع المخزن**

### **🏛️ المحافظات المصرية (27 محافظة):**
```python
GOVERNORATES = [
    {"name": "القاهرة", "name_en": "Cairo", "code": "CAI"},
    {"name": "الجيزة", "name_en": "Giza", "code": "GIZ"},
    {"name": "الإسكندرية", "name_en": "Alexandria", "code": "ALX"},
    # ... باقي المحافظات الـ 27
]
```
**الاستخدام:** تحديد محافظة المستخدم عند التسجيل

### **🎭 الأحزاب السياسية (16 حزب):**
```python
POLITICAL_PARTIES = [
    {"name": "حزب مستقبل وطن", "abbreviation": "FN"},
    {"name": "حزب الوفد", "abbreviation": "WP"},
    {"name": "الحزب المصري الديمقراطي الاجتماعي", "abbreviation": "ESDP"},
    # ... باقي الأحزاب الـ 16
]
```
**الاستخدام:** تحديد الانتماء الحزبي للمرشحين والأعضاء

### **👥 أنواع المستخدمين:**
```python
USER_TYPES = [
    {
        "type": "citizen",
        "name": "مواطن",
        "required_fields": ["governorate", "phone", "whatsapp"],
        "permissions": [
            "view_representatives",
            "submit_complaint",
            "rate_representative",
            "view_news",
            "send_message"
        ]
    },
    {
        "type": "candidate", 
        "name": "مرشح",
        "required_fields": [
            "governorate", "phone", "whatsapp", 
            "council_type", "political_affiliation"
        ],
        "permissions": [
            "view_representatives",
            "create_campaign",
            "respond_to_citizens",
            "view_analytics"
        ]
    },
    {
        "type": "current_member",
        "name": "عضو حالي",
        "required_fields": [
            "governorate", "phone", "whatsapp",
            "council_type", "political_affiliation"
        ],
        "permissions": [
            "respond_to_complaints",
            "publish_news",
            "send_notifications",
            "view_constituency_data",
            "manage_profile"
        ]
    },
    {
        "type": "admin",
        "name": "إدارة",
        "required_fields": ["governorate", "phone"],
        "permissions": ["all"]
    }
]
```

### **🏛️ أنواع الانتماء السياسي:**
```python
POLITICAL_AFFILIATION = [
    {
        "type": "independent",
        "name": "مستقل",
        "description": "غير منتمي لأي حزب سياسي"
    },
    {
        "type": "party_member",
        "name": "حزبي",
        "description": "منتمي لحزب سياسي",
        "requires_party_selection": True
    }
]
```

### **📱 حقول التواصل المطلوبة:**
```python
CONTACT_FIELDS = [
    {
        "field": "phone",
        "name": "رقم التليفون",
        "type": "phone_number",
        "required": True,
        "format": "+20XXXXXXXXX"
    },
    {
        "field": "whatsapp",
        "name": "رقم الواتساب",
        "type": "phone_number", 
        "required": True,
        "format": "+20XXXXXXXXX",
        "note": "يمكن أن يكون نفس رقم التليفون"
    }
]
```

### **🏛️ أنواع المجالس:**
```python
COUNCIL_TYPES = [
    {
        "type": "parliament",
        "name": "مجلس النواب",
        "total_seats": 596,
        "term_years": 5
    },
    {
        "type": "senate",
        "name": "مجلس الشيوخ", 
        "total_seats": 300,
        "term_years": 5
    }
]
```

### **🔐 مستويات الصلاحيات:**
```python
PERMISSION_LEVELS = [
    {"level": "read", "name": "قراءة", "description": "عرض المحتوى فقط"},
    {"level": "write", "name": "كتابة", "description": "إنشاء وتعديل المحتوى"},
    {"level": "delete", "name": "حذف", "description": "حذف المحتوى"},
    {"level": "admin", "name": "إدارة", "description": "إدارة كاملة"},
    {"level": "super_admin", "name": "إدارة عليا", "description": "تحكم كامل"}
]
```

---

## ⚙️ **إعدادات Google Cloud Run**

### **🛠️ بيئة التطوير (Development):**
```yaml
service_name: naebak-auth-service-dev
image: gcr.io/naebak-472518/auth-service:dev
cpu: 0.5
memory: 512Mi
min_instances: 0
max_instances: 3
concurrency: 100
timeout: 300s

environment_variables:
  - DJANGO_SETTINGS_MODULE=app.settings.development
  - DEBUG=true
  - DATABASE_URL=postgresql://localhost:5432/naebak_auth_dev
  - REDIS_URL=redis://localhost:6379/1
  - JWT_SECRET_KEY=${JWT_SECRET_DEV}
  - GOOGLE_OAUTH_CLIENT_ID=${GOOGLE_CLIENT_ID_DEV}
  - GOOGLE_OAUTH_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET_DEV}
  - ALLOWED_HOSTS=localhost,127.0.0.1
  - MAX_LOGIN_ATTEMPTS=5
  - LOCKOUT_DURATION_MINUTES=30
```

### **🏭 إعدادات بيئة الإنتاج:**
```yaml
service_name: naebak-auth-service
image: gcr.io/naebak-472518/auth-service:latest
cpu: 1
memory: 1Gi
min_instances: 1
max_instances: 10
concurrency: 500
timeout: 60s

environment_variables:
  - DJANGO_SETTINGS_MODULE=app.settings.production
  - DEBUG=false
  - DATABASE_URL=${DATABASE_URL}
  - REDIS_URL=${REDIS_URL}
  - JWT_SECRET_KEY=${JWT_SECRET_PROD}
  - GOOGLE_OAUTH_CLIENT_ID=${GOOGLE_CLIENT_ID_PROD}
  - GOOGLE_OAUTH_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET_PROD}
  - ALLOWED_HOSTS=${ALLOWED_HOSTS}
  - MAX_LOGIN_ATTEMPTS=3
  - LOCKOUT_DURATION_MINUTES=60
```

### **🔧 إعدادات قاعدة البيانات:**
```yaml
# بيئة التطوير
DATABASE_URL: postgresql://localhost:5432/naebak_auth_dev
DB_POOL_SIZE: 5
DB_MAX_OVERFLOW: 10

# بيئة الإنتاج
DATABASE_URL: postgresql://user:pass@host:5432/naebak_auth_prod
DB_POOL_SIZE: 20
DB_MAX_OVERFLOW: 30
DB_POOL_TIMEOUT: 30
```

---

## 🔐 **الأمان والصلاحيات**

### **🛡️ آليات الحماية:**
1. **JWT Authentication** - توكنات آمنة مع انتهاء صلاحية
2. **Rate Limiting** - حماية من هجمات القوة الغاشمة
3. **Account Lockout** - قفل الحسابات بعد محاولات فاشلة
4. **Password Hashing** - تشفير كلمات المرور بـ bcrypt
5. **Two-Factor Authentication** - التحقق الثنائي عبر SMS/Email
6. **Session Management** - إدارة الجلسات المتعددة
7. **Audit Logging** - تسجيل جميع العمليات الأمنية

### **🔒 إعدادات الأمان:**
```python
SECURITY_SETTINGS = {
    'PASSWORD_MIN_LENGTH': 8,
    'PASSWORD_REQUIRE_UPPERCASE': True,
    'PASSWORD_REQUIRE_LOWERCASE': True,
    'PASSWORD_REQUIRE_NUMBERS': True,
    'PASSWORD_REQUIRE_SYMBOLS': True,
    'MAX_LOGIN_ATTEMPTS': 3,
    'LOCKOUT_DURATION_MINUTES': 60,
    'JWT_EXPIRY_HOURS': 24,
    'REFRESH_TOKEN_EXPIRY_DAYS': 30,
    'SESSION_TIMEOUT_MINUTES': 120,
    'REQUIRE_EMAIL_VERIFICATION': True,
    'REQUIRE_PHONE_VERIFICATION': True,
    'REAL_TIME_PASSWORD_VALIDATION': True,
    'PASSWORD_CONFIRMATION_REQUIRED': True
}
```

### **🔍 رسائل التحقق من كلمة المرور:**
```python
PASSWORD_VALIDATION_MESSAGES = {
    'ar': {
        'too_short': 'كلمة المرور قصيرة جداً (الحد الأدنى 8 أحرف)',
        'missing_uppercase': 'يجب أن تحتوي على حرف كبير واحد على الأقل',
        'missing_lowercase': 'يجب أن تحتوي على حرف صغير واحد على الأقل',
        'missing_number': 'يجب أن تحتوي على رقم واحد على الأقل',
        'missing_symbol': 'يجب أن تحتوي على رمز خاص واحد على الأقل (!@#$%^&*)',
        'passwords_match': '✅ كلمات المرور متطابقة',
        'passwords_not_match': '❌ كلمات المرور غير متطابقة',
        'password_strong': '✅ كلمة مرور قوية',
        'password_weak': '⚠️ كلمة مرور ضعيفة',
        'password_medium': '🔶 كلمة مرور متوسطة القوة'
    },
    'en': {
        'too_short': 'Password is too short (minimum 8 characters)',
        'missing_uppercase': 'Must contain at least one uppercase letter',
        'missing_lowercase': 'Must contain at least one lowercase letter',
        'missing_number': 'Must contain at least one number',
        'missing_symbol': 'Must contain at least one special character (!@#$%^&*)',
        'passwords_match': '✅ Passwords match',
        'passwords_not_match': '❌ Passwords do not match',
        'password_strong': '✅ Strong password',
        'password_weak': '⚠️ Weak password',
        'password_medium': '🔶 Medium strength password'
    }
}
```

### **🔍 مثال التحقق الفوري من كلمة المرور:**
```json
POST /api/auth/validate-password/
Content-Type: application/json

{
  "password": "MyPass123!"
}

Response:
{
  "status": "success",
  "data": {
    "is_valid": true,
    "strength": "strong",
    "score": 85,
    "messages": {
      "ar": "✅ كلمة مرور قوية",
      "en": "✅ Strong password"
    },
    "requirements_met": {
      "min_length": true,
      "has_uppercase": true,
      "has_lowercase": true,
      "has_number": true,
      "has_symbol": true
    }
  }
}
```

### **🔍 مثال التحقق من تطابق كلمات المرور:**
```json
POST /api/auth/check-password-match/
Content-Type: application/json

{
  "password": "MyPass123!",
  "confirm_password": "MyPass123!"
}

Response:
{
  "status": "success",
  "data": {
    "passwords_match": true,
    "message": {
      "ar": "✅ كلمات المرور متطابقة",
      "en": "✅ Passwords match"
    }
  }
}
```

---

## 🔗 **واجهات برمجة التطبيقات (APIs)**

### **📡 نقاط النهاية الرئيسية:**
```
POST /api/auth/register/                        - تسجيل حساب جديد (تقليدي)
POST /api/auth/google-register/                 - تسجيل حساب جديد عبر Google
POST /api/auth/login/                           - تسجيل الدخول (تقليدي)
POST /api/auth/google-login/                    - تسجيل الدخول عبر Google
POST /api/auth/logout/                          - تسجيل الخروج
POST /api/auth/refresh-token/                   - تجديد التوكن
POST /api/auth/verify-token/                    - التحقق من التوكن
POST /api/auth/forgot-password/                 - نسيان كلمة المرور
POST /api/auth/reset-password/                  - إعادة تعيين كلمة المرور
POST /api/auth/change-password/                 - تغيير كلمة المرور
POST /api/auth/verify-email/                    - التحقق من البريد الإلكتروني
POST /api/auth/verify-phone/                    - التحقق من رقم الهاتف
POST /api/auth/validate-password/               - التحقق الفوري من قوة كلمة المرور
POST /api/auth/check-password-match/            - التحقق من تطابق كلمات المرور
GET  /api/auth/profile/                         - بيانات المستخدم الحالي
PUT  /api/auth/profile/                         - تحديث بيانات المستخدم
GET  /api/auth/permissions/                     - صلاحيات المستخدم
GET  /api/auth/governorates/                    - قائمة المحافظات
GET  /api/auth/parties/                         - قائمة الأحزاب السياسية
GET  /health                                    - فحص صحة الخدمة
```

### **📥 مثال تسجيل حساب جديد (تقليدي):**
```json
POST /api/auth/register/
Content-Type: application/json

{
  "email": "citizen@example.com",
  "phone_number": "+201234567890",
  "whatsapp_number": "+201234567890",
  "password": "SecurePass123!",
  "first_name": "أحمد",
  "last_name": "محمد",
  "national_id": "12345678901234",
  "governorate": "القاهرة",
  "user_type": "citizen"
}
```

### **📥 مثال تسجيل مرشح/نائب:**
```json
POST /api/auth/register/
Content-Type: application/json

{
  "email": "candidate@example.com",
  "phone_number": "+201234567890",
  "whatsapp_number": "+201987654321",
  "password": "SecurePass123!",
  "first_name": "محمد",
  "last_name": "أحمد",
  "national_id": "12345678901234",
  "governorate": "الإسكندرية",
  "user_type": "candidate",
  "council_type": "parliament",
  "political_affiliation": "party_member",
  "political_party": "حزب مستقبل وطن"
}
```

### **📥 مثال تسجيل دخول عبر Google:**
```json
POST /api/auth/google-register/
Content-Type: application/json

{
  "google_token": "ya29.a0AfH6SMC...",
  "phone_number": "+201234567890",
  "whatsapp_number": "+201234567890",
  "national_id": "12345678901234",
  "governorate": "القاهرة",
  "user_type": "citizen"
}
```

### **📤 مثال استجابة تسجيل الدخول:**
```json
POST /api/auth/login/

{
  "status": "success",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 12345,
      "email": "citizen@example.com",
      "first_name": "أحمد",
      "last_name": "محمد",
      "user_type": "citizen",
      "governorate": "القاهرة",
      "phone_number": "+201234567890",
      "whatsapp_number": "+201234567890",
      "council_type": null,
      "political_affiliation": null,
      "political_party": null,
      "is_verified": true
    },
    "permissions": [
      "view_representatives",
      "submit_complaint",
      "rate_representative"
    ],
    "expires_at": "2025-01-02T12:00:00Z"
  }
}
```

### **🔍 مثال التحقق الفوري من كلمة المرور:**
```json
POST /api/auth/validate-password/
Content-Type: application/json

{
  "password": "MyPass123!"
}

Response:
{
  "status": "success",
  "data": {
    "is_valid": true,
    "strength": "strong",
    "score": 85,
    "messages": {
      "ar": "✅ كلمة مرور قوية",
      "en": "✅ Strong password"
    },
    "requirements_met": {
      "min_length": true,
      "has_uppercase": true,
      "has_lowercase": true,
      "has_number": true,
      "has_symbol": true
    }
  }
}
```

### **🔍 مثال التحقق من تطابق كلمات المرور:**
```json
POST /api/auth/check-password-match/
Content-Type: application/json

{
  "password": "MyPass123!",
  "confirm_password": "MyPass123!"
}

Response:
{
  "status": "success",
  "data": {
    "passwords_match": true,
    "message": {
      "ar": "✅ كلمات المرور متطابقة",
      "en": "✅ Passwords match"
    }
  }
}
```

---

## 🔄 **الفروق بين بيئات التشغيل**

### **🛠️ بيئة التطوير (Development):**
- **قاعدة البيانات:** PostgreSQL محلي
- **محاولات الدخول:** 5 محاولات (أكثر تساهلاً)
- **مدة القفل:** 30 دقيقة (أقل)
- **التحقق:** اختياري للاختبار
- **التسجيل:** مفصل (DEBUG level)
- **الموارد:** 0.5 CPU, 512Mi Memory

### **🏭 بيئة الإنتاج (Production):**
- **قاعدة البيانات:** Cloud SQL PostgreSQL
- **محاولات الدخول:** 3 محاولات (أكثر صرامة)
- **مدة القفل:** 60 دقيقة (أطول)
- **التحقق:** إجباري للبريد والهاتف
- **التسجيل:** أخطاء فقط (WARNING level)
- **الموارد:** 1 CPU, 1Gi Memory (أقوى)

---

## 📈 **المراقبة والتحليلات**

### **📊 المقاييس المهمة:**
- **معدل تسجيل الدخول الناجح** - يجب أن يكون أعلى من 95%
- **زمن الاستجابة** - يجب أن يكون أقل من 200ms
- **محاولات الاختراق** - مراقبة المحاولات المشبوهة
- **الحسابات المقفلة** - عدد الحسابات المقفلة يومياً
- **التوكنات المنتهية** - معدل انتهاء صلاحية التوكنات

### **🚨 التنبيهات:**
- **محاولات اختراق** - تنبيه فوري
- **فشل في قاعدة البيانات** - تنبيه فوري
- **ارتفاع محاولات الدخول الفاشلة** - تنبيه خلال 5 دقائق
- **انقطاع خدمة التحقق** - تنبيه فوري

---

## 🚀 **خطوات التطوير المطلوبة**

### **🎯 المرحلة الأولى - الأساسيات:**
1. ✅ إعداد Django + DRF
2. ✅ إنشاء نماذج المستخدمين
3. ⏳ تطبيق JWT Authentication
4. ⏳ إنشاء APIs التسجيل والدخول
5. ⏳ ربط PostgreSQL و Redis

### **🎯 المرحلة الثانية - الأمان:**
1. ⏳ تطبيق Rate Limiting
2. ⏳ إضافة Account Lockout
3. ⏳ تطبيق التحقق الثنائي
4. ⏳ إضافة Audit Logging
5. ⏳ تطبيق Password Policies

### **🎯 المرحلة الثالثة - التكامل:**
1. ⏳ ربط جميع الخدمات الأخرى
2. ⏳ تطبيق إدارة الصلاحيات
3. ⏳ اختبار الأمان والأداء
4. ⏳ تحسين الاستعلامات
5. ⏳ نشر بيئة الإنتاج

---

## 📚 **الموارد والمراجع**

### **🔧 أدوات التطوير:**
- **Django 4.2** - إطار العمل الأساسي
- **Django REST Framework** - واجهات برمجة التطبيقات
- **PostgreSQL** - قاعدة البيانات الرئيسية
- **Redis** - التخزين المؤقت والجلسات
- **JWT** - المصادقة والتوكنات
- **Celery** - المهام غير المتزامنة

---

**📝 ملاحظة:** هذا الملف هو الدليل الشامل لخدمة المصادقة - البوابة الأمنية الرئيسية لمنصة نائبك.
