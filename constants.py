# -*- coding: utf-8 -*-
"""ثوابت وبيانات أساسية لخدمة المصادقة والعضوية"""

from egyptian_governorates import EGYPTIAN_GOVERNORATES

# أنواع المستخدمين
USER_TYPES = [
    {
        "type": "citizen", 
        "name": "مواطن", 
        "name_en": "Citizen",
        "description": "مواطن له صوت انتخابي",
        "required_fields": ["phone_number", "governorate"]
    },
    {
        "type": "candidate", 
        "name": "مرشح", 
        "name_en": "Candidate",
        "description": "مرشح لعضوية مجلس الشيوخ أو النواب",
        "required_fields": ["phone_number", "governorate", "council_type", "party"]
    },
    {
        "type": "current_member", 
        "name": "عضو حالي", 
        "name_en": "Current Member",
        "description": "عضو فعلي في مجلس الشيوخ أو النواب",
        "required_fields": ["phone_number", "governorate", "council_type", "party"]
    },
    {
        "type": "admin", 
        "name": "إدارة", 
        "name_en": "Admin",
        "description": "إدارة النظام",
        "required_fields": ["phone_number"]
    }
]

# الأحزاب السياسية المصرية
POLITICAL_PARTIES = [
    {"name": "حزب الوفد", "name_en": "Al-Wafd Party", "abbreviation": "الوفد"},
    {"name": "الحزب الوطني الديمقراطي", "name_en": "National Democratic Party", "abbreviation": "الوطني"},
    {"name": "حزب الغد", "name_en": "Al-Ghad Party", "abbreviation": "الغد"},
    {"name": "حزب التجمع الوطني التقدمي الوحدوي", "name_en": "National Progressive Unionist Party", "abbreviation": "التجمع"},
    {"name": "حزب الناصري", "name_en": "Nasserist Party", "abbreviation": "الناصري"},
    {"name": "حزب الكرامة", "name_en": "Al-Karama Party", "abbreviation": "الكرامة"},
    {"name": "حزب الوسط الجديد", "name_en": "New Wasat Party", "abbreviation": "الوسط"},
    {"name": "حزب الحرية المصري", "name_en": "Egyptian Freedom Party", "abbreviation": "الحرية"},
    {"name": "حزب المصريين الأحرار", "name_en": "Free Egyptians Party", "abbreviation": "المصريين الأحرار"},
    {"name": "حزب النور", "name_en": "Al-Nour Party", "abbreviation": "النور"},
    {"name": "حزب البناء والتنمية", "name_en": "Building and Development Party", "abbreviation": "البناء والتنمية"},
    {"name": "حزب الإصلاح والتنمية", "name_en": "Reform and Development Party", "abbreviation": "الإصلاح والتنمية"},
    {"name": "حزب مستقبل وطن", "name_en": "Future of a Nation Party", "abbreviation": "مستقبل وطن"},
    {"name": "حزب المؤتمر", "name_en": "Conference Party", "abbreviation": "المؤتمر"},
    {"name": "حزب الشعب الجمهوري", "name_en": "Republican People's Party", "abbreviation": "الشعب الجمهوري"},
    {"name": "مستقل", "name_en": "Independent", "abbreviation": "مستقل"}
]

# أنواع المجالس
COUNCIL_TYPES = [
    {
        "type": "parliament", 
        "name": "مجلس النواب", 
        "name_en": "Parliament",
        "description": "المجلس الأساسي للتشريع",
        "term_duration": 5,
        "total_seats": 596
    },
    {
        "type": "senate", 
        "name": "مجلس الشيوخ", 
        "name_en": "Senate",
        "description": "المجلس الاستشاري العلوي", 
        "term_duration": 5,
        "total_seats": 300
    }
]

# حالات العضوية
MEMBERSHIP_STATUS = [
    {"status": "active", "name": "نشط", "name_en": "Active"},
    {"status": "inactive", "name": "غير نشط", "name_en": "Inactive"},
    {"status": "suspended", "name": "موقوف", "name_en": "Suspended"},
    {"status": "pending", "name": "في الانتظار", "name_en": "Pending"}
]

# أنواع التحقق
VERIFICATION_TYPES = [
    {"type": "phone", "name": "رقم الهاتف", "name_en": "Phone Number"},
    {"type": "email", "name": "البريد الإلكتروني", "name_en": "Email"},
    {"type": "national_id", "name": "الرقم القومي", "name_en": "National ID"},
    {"type": "document", "name": "وثيقة رسمية", "name_en": "Official Document"}
]

# إعدادات JWT
JWT_SETTINGS = {
    'ACCESS_TOKEN_LIFETIME': 60 * 60,  # ساعة واحدة
    'REFRESH_TOKEN_LIFETIME': 60 * 60 * 24 * 7,  # أسبوع
    'ALGORITHM': 'HS256',
    'ISSUER': 'naebak-auth-service'
}

# إعدادات كلمات المرور
PASSWORD_SETTINGS = {
    'MIN_LENGTH': 8,
    'REQUIRE_UPPERCASE': True,
    'REQUIRE_LOWERCASE': True,
    'REQUIRE_NUMBERS': True,
    'REQUIRE_SPECIAL_CHARS': False,
    'MAX_ATTEMPTS': 5,
    'LOCKOUT_DURATION': 30 * 60  # 30 دقيقة
}

# رسائل الخطأ
ERROR_MESSAGES = {
    'INVALID_CREDENTIALS': 'بيانات الدخول غير صحيحة',
    'ACCOUNT_LOCKED': 'تم قفل الحساب مؤقتاً',
    'PHONE_EXISTS': 'رقم الهاتف مسجل مسبقاً',
    'WEAK_PASSWORD': 'كلمة المرور ضعيفة',
    'TOKEN_EXPIRED': 'انتهت صلاحية الرمز المميز',
    'UNAUTHORIZED': 'غير مخول للوصول',
    'VERIFICATION_REQUIRED': 'يجب التحقق من الحساب أولاً'
}

# المحافظات (من الملف الموجود)
GOVERNORATES = EGYPTIAN_GOVERNORATES

# للاستخدام في Django choices
USER_TYPE_CHOICES = [(user['type'], user['name']) for user in USER_TYPES]
PARTY_CHOICES = [(party['name'], party['name']) for party in POLITICAL_PARTIES]
COUNCIL_CHOICES = [(council['type'], council['name']) for council in COUNCIL_TYPES]
STATUS_CHOICES = [(status['status'], status['name']) for status in MEMBERSHIP_STATUS]
