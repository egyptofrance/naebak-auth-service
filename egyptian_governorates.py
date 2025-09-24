"""
بيانات المحافظات المصرية الـ 27
للاستخدام في جميع خدمات نائبك
"""

EGYPTIAN_GOVERNORATES = [
    {'name': 'القاهرة', 'name_en': 'Cairo', 'code': 'CAI'},
    {'name': 'الجيزة', 'name_en': 'Giza', 'code': 'GIZ'},
    {'name': 'الإسكندرية', 'name_en': 'Alexandria', 'code': 'ALX'},
    {'name': 'الدقهلية', 'name_en': 'Dakahlia', 'code': 'DK'},
    {'name': 'البحر الأحمر', 'name_en': 'Red Sea', 'code': 'BA'},
    {'name': 'البحيرة', 'name_en': 'Beheira', 'code': 'BH'},
    {'name': 'الفيوم', 'name_en': 'Fayoum', 'code': 'FYM'},
    {'name': 'الغربية', 'name_en': 'Gharbia', 'code': 'GH'},
    {'name': 'الإسماعيلية', 'name_en': 'Ismailia', 'code': 'IS'},
    {'name': 'المنوفية', 'name_en': 'Monufia', 'code': 'MN'},
    {'name': 'المنيا', 'name_en': 'Minya', 'code': 'MNY'},
    {'name': 'القليوبية', 'name_en': 'Qalyubia', 'code': 'QB'},
    {'name': 'الوادي الجديد', 'name_en': 'New Valley', 'code': 'WAD'},
    {'name': 'شمال سيناء', 'name_en': 'North Sinai', 'code': 'SIN'},
    {'name': 'جنوب سيناء', 'name_en': 'South Sinai', 'code': 'JS'},
    {'name': 'الشرقية', 'name_en': 'Sharqia', 'code': 'SH'},
    {'name': 'سوهاج', 'name_en': 'Sohag', 'code': 'SOH'},
    {'name': 'السويس', 'name_en': 'Suez', 'code': 'SUZ'},
    {'name': 'أسوان', 'name_en': 'Aswan', 'code': 'ASN'},
    {'name': 'أسيوط', 'name_en': 'Asyut', 'code': 'AST'},
    {'name': 'بني سويف', 'name_en': 'Beni Suef', 'code': 'BNS'},
    {'name': 'بورسعيد', 'name_en': 'Port Said', 'code': 'PTS'},
    {'name': 'دمياط', 'name_en': 'Damietta', 'code': 'DT'},
    {'name': 'كفر الشيخ', 'name_en': 'Kafr el-Sheikh', 'code': 'KFS'},
    {'name': 'مطروح', 'name_en': 'Matrouh', 'code': 'MT'},
    {'name': 'الأقصر', 'name_en': 'Luxor', 'code': 'LXR'},
    {'name': 'قنا', 'name_en': 'Qena', 'code': 'QNA'},
]

# للاستخدام في Django choices
GOVERNORATE_CHOICES = [(gov['name'], gov['name']) for gov in EGYPTIAN_GOVERNORATES]

# للاستخدام في APIs
def get_governorate_by_name(name):
    """البحث عن محافظة بالاسم"""
    for gov in EGYPTIAN_GOVERNORATES:
        if gov['name'] == name or gov['name_en'] == name:
            return gov
    return None

def get_governorate_by_code(code):
    """البحث عن محافظة بالكود"""
    for gov in EGYPTIAN_GOVERNORATES:
        if gov['code'] == code:
            return gov
    return None

# للاستخدام في قواعد البيانات
def create_governorates_fixtures():
    """إنشاء fixtures للمحافظات"""
    fixtures = []
    for i, gov in enumerate(EGYPTIAN_GOVERNORATES, 1):
        fixtures.append({
            "model": "app.governorate",
            "pk": i,
            "fields": {
                "name": gov['name'],
                "name_en": gov['name_en'],
                "code": gov['code']
            }
        })
    return fixtures
