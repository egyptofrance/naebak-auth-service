# -*- coding: utf-8 -*-
"""
أمر إدارة لتحميل البيانات الأولية لتطبيق نائبك
Management command to load initial data for Naebak application
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import Governorate, Party


class Command(BaseCommand):
    help = 'تحميل البيانات الأولية (المحافظات والأحزاب)'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('بدء تحميل البيانات الأولية...'))
        
        with transaction.atomic():
            # تحميل المحافظات المصرية (27 محافظة)
            self.load_governorates()
            
            # تحميل الأحزاب السياسية المصرية
            self.load_parties()
        
        self.stdout.write(self.style.SUCCESS('تم تحميل البيانات الأولية بنجاح!'))
    
    def load_governorates(self):
        """تحميل المحافظات المصرية"""
        governorates_data = [
            {"name": "القاهرة", "name_en": "Cairo", "code": "CAI"},
            {"name": "الجيزة", "name_en": "Giza", "code": "GIZ"},
            {"name": "الإسكندرية", "name_en": "Alexandria", "code": "ALX"},
            {"name": "الدقهلية", "name_en": "Dakahlia", "code": "DAK"},
            {"name": "البحر الأحمر", "name_en": "Red Sea", "code": "RSS"},
            {"name": "البحيرة", "name_en": "Beheira", "code": "BEH"},
            {"name": "الفيوم", "name_en": "Fayoum", "code": "FAY"},
            {"name": "الغربية", "name_en": "Gharbia", "code": "GHR"},
            {"name": "الإسماعيلية", "name_en": "Ismailia", "code": "ISM"},
            {"name": "المنوفية", "name_en": "Monufia", "code": "MNF"},
            {"name": "المنيا", "name_en": "Minya", "code": "MNY"},
            {"name": "القليوبية", "name_en": "Qalyubia", "code": "QLY"},
            {"name": "الوادي الجديد", "name_en": "New Valley", "code": "WAD"},
            {"name": "شمال سيناء", "name_en": "North Sinai", "code": "NSI"},
            {"name": "جنوب سيناء", "name_en": "South Sinai", "code": "SSI"},
            {"name": "الشرقية", "name_en": "Sharqia", "code": "SHR"},
            {"name": "سوهاج", "name_en": "Sohag", "code": "SOH"},
            {"name": "السويس", "name_en": "Suez", "code": "SUZ"},
            {"name": "أسوان", "name_en": "Aswan", "code": "ASW"},
            {"name": "أسيوط", "name_en": "Asyut", "code": "ASY"},
            {"name": "بني سويف", "name_en": "Beni Suef", "code": "BNS"},
            {"name": "بورسعيد", "name_en": "Port Said", "code": "PTS"},
            {"name": "دمياط", "name_en": "Damietta", "code": "DAM"},
            {"name": "كفر الشيخ", "name_en": "Kafr El Sheikh", "code": "KFS"},
            {"name": "مطروح", "name_en": "Matrouh", "code": "MAT"},
            {"name": "الأقصر", "name_en": "Luxor", "code": "LUX"},
            {"name": "قنا", "name_en": "Qena", "code": "QEN"}
        ]
        
        created_count = 0
        for gov_data in governorates_data:
            governorate, created = Governorate.objects.get_or_create(
                code=gov_data['code'],
                defaults={
                    'name': gov_data['name'],
                    'name_en': gov_data['name_en']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'تم إنشاء محافظة: {governorate.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'تم تحميل {created_count} محافظة جديدة من أصل {len(governorates_data)}')
        )
    
    def load_parties(self):
        """تحميل الأحزاب السياسية المصرية"""
        parties_data = [
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
        
        created_count = 0
        for party_data in parties_data:
            party, created = Party.objects.get_or_create(
                name=party_data['name'],
                defaults={
                    'name_en': party_data['name_en'],
                    'abbreviation': party_data['abbreviation']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'تم إنشاء حزب: {party.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'تم تحميل {created_count} حزب جديد من أصل {len(parties_data)}')
        )
