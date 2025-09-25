"""
أمر Django لتحميل البيانات الأساسية لخدمة المصادقة
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.users.models import Governorate, Party


class Command(BaseCommand):
    help = 'تحميل البيانات الأساسية لخدمة المصادقة'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='إعادة تحميل البيانات حتى لو كانت موجودة',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        with transaction.atomic():
            # تحميل المحافظات
            self.load_governorates(force)
            
            # تحميل الأحزاب السياسية
            self.load_parties(force)
        
        self.stdout.write(
            self.style.SUCCESS('تم تحميل البيانات الأساسية بنجاح!')
        )

    def load_governorates(self, force=False):
        """تحميل المحافظات المصرية"""
        governorates_data = [
            {"name": "القاهرة", "name_en": "Cairo", "code": "CAI", "region": "القاهرة الكبرى", "display_order": 1},
            {"name": "الجيزة", "name_en": "Giza", "code": "GIZ", "region": "القاهرة الكبرى", "display_order": 2},
            {"name": "الإسكندرية", "name_en": "Alexandria", "code": "ALX", "region": "الساحل الشمالي", "display_order": 3},
            {"name": "الدقهلية", "name_en": "Dakahlia", "code": "DAK", "region": "الدلتا", "display_order": 4},
            {"name": "البحر الأحمر", "name_en": "Red Sea", "code": "RSS", "region": "الصحراء الشرقية", "display_order": 5},
            {"name": "البحيرة", "name_en": "Beheira", "code": "BEH", "region": "الدلتا", "display_order": 6},
            {"name": "الفيوم", "name_en": "Fayoum", "code": "FAY", "region": "الصعيد", "display_order": 7},
            {"name": "الغربية", "name_en": "Gharbia", "code": "GHR", "region": "الدلتا", "display_order": 8},
            {"name": "الإسماعيلية", "name_en": "Ismailia", "code": "ISM", "region": "القناة", "display_order": 9},
            {"name": "المنوفية", "name_en": "Monufia", "code": "MNF", "region": "الدلتا", "display_order": 10},
            {"name": "المنيا", "name_en": "Minya", "code": "MNY", "region": "الصعيد", "display_order": 11},
            {"name": "القليوبية", "name_en": "Qalyubia", "code": "QLY", "region": "القاهرة الكبرى", "display_order": 12},
            {"name": "الوادي الجديد", "name_en": "New Valley", "code": "WAD", "region": "الصحراء الغربية", "display_order": 13},
            {"name": "شمال سيناء", "name_en": "North Sinai", "code": "NSI", "region": "سيناء", "display_order": 14},
            {"name": "جنوب سيناء", "name_en": "South Sinai", "code": "SSI", "region": "سيناء", "display_order": 15},
            {"name": "الشرقية", "name_en": "Sharqia", "code": "SHR", "region": "الدلتا", "display_order": 16},
            {"name": "سوهاج", "name_en": "Sohag", "code": "SOH", "region": "الصعيد", "display_order": 17},
            {"name": "السويس", "name_en": "Suez", "code": "SUZ", "region": "القناة", "display_order": 18},
            {"name": "أسوان", "name_en": "Aswan", "code": "ASW", "region": "الصعيد", "display_order": 19},
            {"name": "أسيوط", "name_en": "Asyut", "code": "ASY", "region": "الصعيد", "display_order": 20},
            {"name": "بني سويف", "name_en": "Beni Suef", "code": "BNS", "region": "الصعيد", "display_order": 21},
            {"name": "بورسعيد", "name_en": "Port Said", "code": "PTS", "region": "القناة", "display_order": 22},
            {"name": "دمياط", "name_en": "Damietta", "code": "DAM", "region": "الدلتا", "display_order": 23},
            {"name": "كفر الشيخ", "name_en": "Kafr El Sheikh", "code": "KFS", "region": "الدلتا", "display_order": 24},
            {"name": "مطروح", "name_en": "Matrouh", "code": "MAT", "region": "الساحل الشمالي", "display_order": 25},
            {"name": "الأقصر", "name_en": "Luxor", "code": "LUX", "region": "الصعيد", "display_order": 26},
            {"name": "قنا", "name_en": "Qena", "code": "QEN", "region": "الصعيد", "display_order": 27}
        ]
        
        created_count = 0
        for gov_data in governorates_data:
            gov, created = Governorate.objects.get_or_create(
                code=gov_data['code'],
                defaults=gov_data
            )
            if created or force:
                if force and not created:
                    for key, value in gov_data.items():
                        setattr(gov, key, value)
                    gov.save()
                created_count += 1
        
        self.stdout.write(f'تم تحميل {created_count} محافظة')

    def load_parties(self, force=False):
        """تحميل الأحزاب السياسية المصرية"""
        parties_data = [
            {
                "name": "حزب مستقبل وطن",
                "name_en": "Future of a Nation Party",
                "abbreviation": "مستقبل وطن",
                "description": "حزب سياسي مصري تأسس عام 2014",
                "primary_color": "#1E3A8A",
                "secondary_color": "#3B82F6",
                "founded_date": "2014-09-15",
                "headquarters": "القاهرة",
                "website": "https://www.mostaqbalwatan.org",
                "display_order": 1
            },
            {
                "name": "الحزب الجمهوري الشعبي",
                "name_en": "Republican People's Party",
                "abbreviation": "الجمهوري",
                "description": "حزب سياسي مصري",
                "primary_color": "#DC2626",
                "secondary_color": "#EF4444",
                "founded_date": "2012-06-01",
                "headquarters": "القاهرة",
                "display_order": 2
            },
            {
                "name": "حزب الوفد",
                "name_en": "Wafd Party",
                "abbreviation": "الوفد",
                "description": "حزب سياسي مصري عريق تأسس عام 1919",
                "primary_color": "#059669",
                "secondary_color": "#10B981",
                "founded_date": "1919-11-13",
                "headquarters": "القاهرة",
                "website": "https://www.alwafd.org",
                "display_order": 3
            },
            {
                "name": "حزب الحرية المصري",
                "name_en": "Egyptian Freedom Party",
                "abbreviation": "الحرية",
                "description": "حزب سياسي مصري",
                "primary_color": "#7C3AED",
                "secondary_color": "#8B5CF6",
                "founded_date": "2011-05-01",
                "headquarters": "القاهرة",
                "display_order": 4
            },
            {
                "name": "حزب المؤتمر",
                "name_en": "Conference Party",
                "abbreviation": "المؤتمر",
                "description": "حزب سياسي مصري",
                "primary_color": "#EA580C",
                "secondary_color": "#F97316",
                "founded_date": "2012-03-15",
                "headquarters": "القاهرة",
                "display_order": 5
            },
            {
                "name": "حزب التجمع الوطني التقدمي الوحدوي",
                "name_en": "National Progressive Unionist Party",
                "abbreviation": "التجمع",
                "description": "حزب سياسي مصري يساري",
                "primary_color": "#B91C1C",
                "secondary_color": "#DC2626",
                "founded_date": "1976-07-01",
                "headquarters": "القاهرة",
                "display_order": 6
            },
            {
                "name": "حزب الناصريين",
                "name_en": "Nasserist Party",
                "abbreviation": "الناصريين",
                "description": "حزب سياسي مصري ناصري",
                "primary_color": "#166534",
                "secondary_color": "#16A34A",
                "founded_date": "1992-04-19",
                "headquarters": "القاهرة",
                "display_order": 7
            },
            {
                "name": "حزب الغد",
                "name_en": "Al-Ghad Party",
                "abbreviation": "الغد",
                "description": "حزب سياسي مصري ليبرالي",
                "primary_color": "#0891B2",
                "secondary_color": "#06B6D4",
                "founded_date": "2004-10-27",
                "headquarters": "القاهرة",
                "display_order": 8
            },
            {
                "name": "حزب الدستور",
                "name_en": "Constitution Party",
                "abbreviation": "الدستور",
                "description": "حزب سياسي مصري ليبرالي",
                "primary_color": "#7C2D12",
                "secondary_color": "#EA580C",
                "founded_date": "2012-04-30",
                "headquarters": "القاهرة",
                "display_order": 9
            },
            {
                "name": "حزب الإصلاح والتنمية",
                "name_en": "Reform and Development Party",
                "abbreviation": "الإصلاح والتنمية",
                "description": "حزب سياسي مصري",
                "primary_color": "#4338CA",
                "secondary_color": "#6366F1",
                "founded_date": "2009-04-01",
                "headquarters": "القاهرة",
                "display_order": 10
            },
            {
                "name": "مستقل",
                "name_en": "Independent",
                "abbreviation": "مستقل",
                "description": "للمرشحين المستقلين غير المنتمين لأحزاب",
                "primary_color": "#6B7280",
                "secondary_color": "#9CA3AF",
                "display_order": 99
            }
        ]
        
        created_count = 0
        for party_data in parties_data:
            party, created = Party.objects.get_or_create(
                name=party_data['name'],
                defaults=party_data
            )
            if created or force:
                if force and not created:
                    for key, value in party_data.items():
                        if key == 'founded_date' and value:
                            from datetime import datetime
                            value = datetime.strptime(value, '%Y-%m-%d').date()
                        setattr(party, key, value)
                    party.save()
                created_count += 1
        
        self.stdout.write(f'تم تحميل {created_count} حزب سياسي')
