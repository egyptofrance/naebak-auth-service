#!/usr/bin/env python3
"""
خدمة المصادقة المبسطة - نائبك
============================

خدمة مصادقة بسيطة وموثوقة باستخدام Flask + SQLite + JWT.
تدعم جميع أنواع المستخدمين مع إمكانية الانتقال السهل لـ PostgreSQL لاحقاً.

الميزات:
- تسجيل دخول وخروج آمن
- إدارة أنواع المستخدمين المختلفة
- التحقق من الهوية
- إدارة الملفات الشخصية
- API بسيط وواضح
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import re
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['CORS_HEADERS'] = 'Content-Type'

# Database configuration - easy to switch to PostgreSQL later
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///naebak_auth.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)

# Models
class User(db.Model):
    """نموذج المستخدم الأساسي"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    
    # نوع المستخدم
    user_type = db.Column(db.String(20), nullable=False, default='citizen')
    # citizen, parliament_candidate, senate_candidate, parliament_member, senate_member
    
    # حالة التحقق
    verification_status = db.Column(db.String(10), nullable=False, default='pending')
    # pending, verified, rejected
    
    # الحالة
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # التواريخ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    citizen_profile = db.relationship('CitizenProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    candidate_profile = db.relationship('CandidateProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def __str__(self):
        return self.full_name
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'user_type': self.user_type,
            'verification_status': self.verification_status,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }

class Governorate(db.Model):
    """نموذج المحافظات المصرية"""
    __tablename__ = 'governorates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    name_en = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(3), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Governorate {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'code': self.code
        }

class CitizenProfile(db.Model):
    """ملف المواطن الشخصي"""
    __tablename__ = 'citizen_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # الموقع
    governorate_id = db.Column(db.Integer, db.ForeignKey('governorates.id'), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    street_address = db.Column(db.String(200), nullable=True)
    
    # البيانات الشخصية
    national_id = db.Column(db.String(14), unique=True, nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # male, female
    birth_date = db.Column(db.Date, nullable=True)
    marital_status = db.Column(db.String(10), nullable=True)  # single, married, divorced, widowed
    
    # معلومات إضافية
    whatsapp_number = db.Column(db.String(20), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    education_level = db.Column(db.String(15), nullable=True)  # primary, secondary, university, postgraduate
    profile_picture = db.Column(db.String(255), nullable=True)
    
    # إعدادات الخصوصية
    show_phone_public = db.Column(db.Boolean, default=False)
    show_address_public = db.Column(db.Boolean, default=False)
    allow_messages = db.Column(db.Boolean, default=True)
    
    # إحصائيات
    messages_sent = db.Column(db.Integer, default=0)
    complaints_submitted = db.Column(db.Integer, default=0)
    ratings_given = db.Column(db.Integer, default=0)
    
    # التواريخ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    governorate = db.relationship('Governorate', backref='citizens')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'governorate': self.governorate.to_dict() if self.governorate else None,
            'city': self.city,
            'district': self.district,
            'street_address': self.street_address,
            'national_id': self.national_id,
            'gender': self.gender,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'marital_status': self.marital_status,
            'whatsapp_number': self.whatsapp_number,
            'occupation': self.occupation,
            'education_level': self.education_level,
            'profile_picture': self.profile_picture,
            'show_phone_public': self.show_phone_public,
            'show_address_public': self.show_address_public,
            'allow_messages': self.allow_messages,
            'messages_sent': self.messages_sent,
            'complaints_submitted': self.complaints_submitted,
            'ratings_given': self.ratings_given
        }

class CandidateProfile(db.Model):
    """ملف المرشح الشخصي"""
    __tablename__ = 'candidate_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # الموقع
    governorate_id = db.Column(db.Integer, db.ForeignKey('governorates.id'), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    constituency = db.Column(db.String(100), nullable=True)
    
    # البيانات الشخصية
    national_id = db.Column(db.String(14), unique=True, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    
    # البيانات السياسية
    council_type = db.Column(db.String(15), nullable=True)  # parliament, senate
    party_name = db.Column(db.String(100), nullable=True)
    electoral_number = db.Column(db.String(20), nullable=True)
    electoral_symbol = db.Column(db.String(50), nullable=True)
    
    # معلومات المرشح
    bio = db.Column(db.Text, nullable=True)
    electoral_program = db.Column(db.Text, nullable=True)
    education = db.Column(db.String(200), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    experience = db.Column(db.Text, nullable=True)
    
    # الصور والملفات
    profile_picture = db.Column(db.String(255), nullable=True)
    banner_image = db.Column(db.String(255), nullable=True)
    
    # إعدادات الحملة
    campaign_slogan = db.Column(db.String(200), nullable=True)
    campaign_website = db.Column(db.String(255), nullable=True)
    
    # الحالة
    is_approved = db.Column(db.Boolean, default=False)
    approval_date = db.Column(db.DateTime, nullable=True)
    
    # إحصائيات
    rating_average = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    messages_received = db.Column(db.Integer, default=0)
    
    # التواريخ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    governorate = db.relationship('Governorate', backref='candidates')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'governorate': self.governorate.to_dict() if self.governorate else None,
            'city': self.city,
            'constituency': self.constituency,
            'national_id': self.national_id,
            'gender': self.gender,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'council_type': self.council_type,
            'party_name': self.party_name,
            'electoral_number': self.electoral_number,
            'electoral_symbol': self.electoral_symbol,
            'bio': self.bio,
            'electoral_program': self.electoral_program,
            'education': self.education,
            'occupation': self.occupation,
            'experience': self.experience,
            'profile_picture': self.profile_picture,
            'banner_image': self.banner_image,
            'campaign_slogan': self.campaign_slogan,
            'campaign_website': self.campaign_website,
            'is_approved': self.is_approved,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'rating_average': self.rating_average,
            'rating_count': self.rating_count,
            'messages_received': self.messages_received
        }

# Helper functions
def validate_email(email):
    """التحقق من صحة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_national_id(national_id):
    """التحقق من صحة الرقم القومي المصري"""
    if not national_id or len(national_id) != 14:
        return False
    return national_id.isdigit()

def init_database():
    """إنشاء قاعدة البيانات والجداول"""
    with app.app_context():
        db.create_all()
        
        # إضافة المحافظات المصرية إذا لم تكن موجودة
        if Governorate.query.count() == 0:
            governorates = [
                {'name': 'القاهرة', 'name_en': 'Cairo', 'code': 'CAI'},
                {'name': 'الجيزة', 'name_en': 'Giza', 'code': 'GIZ'},
                {'name': 'الإسكندرية', 'name_en': 'Alexandria', 'code': 'ALX'},
                {'name': 'الدقهلية', 'name_en': 'Dakahlia', 'code': 'DKH'},
                {'name': 'البحر الأحمر', 'name_en': 'Red Sea', 'code': 'RSE'},
                {'name': 'البحيرة', 'name_en': 'Beheira', 'code': 'BHR'},
                {'name': 'الفيوم', 'name_en': 'Fayoum', 'code': 'FYM'},
                {'name': 'الغربية', 'name_en': 'Gharbia', 'code': 'GHR'},
                {'name': 'الإسماعيلية', 'name_en': 'Ismailia', 'code': 'ISM'},
                {'name': 'المنوفية', 'name_en': 'Monufia', 'code': 'MNF'},
                {'name': 'المنيا', 'name_en': 'Minya', 'code': 'MNY'},
                {'name': 'القليوبية', 'name_en': 'Qalyubia', 'code': 'QLY'},
                {'name': 'الوادي الجديد', 'name_en': 'New Valley', 'code': 'NVL'},
                {'name': 'شمال سيناء', 'name_en': 'North Sinai', 'code': 'NSI'},
                {'name': 'بورسعيد', 'name_en': 'Port Said', 'code': 'PTS'},
                {'name': 'قنا', 'name_en': 'Qena', 'code': 'QNA'},
                {'name': 'الشرقية', 'name_en': 'Sharqia', 'code': 'SHR'},
                {'name': 'سوهاج', 'name_en': 'Sohag', 'code': 'SOH'},
                {'name': 'جنوب سيناء', 'name_en': 'South Sinai', 'code': 'SSI'},
                {'name': 'السويس', 'name_en': 'Suez', 'code': 'SUZ'},
                {'name': 'أسوان', 'name_en': 'Aswan', 'code': 'ASW'},
                {'name': 'أسيوط', 'name_en': 'Asyut', 'code': 'ASY'},
                {'name': 'بني سويف', 'name_en': 'Beni Suef', 'code': 'BSW'},
                {'name': 'دمياط', 'name_en': 'Damietta', 'code': 'DMT'},
                {'name': 'كفر الشيخ', 'name_en': 'Kafr El Sheikh', 'code': 'KFS'},
                {'name': 'الأقصر', 'name_en': 'Luxor', 'code': 'LXR'},
                {'name': 'مطروح', 'name_en': 'Matrouh', 'code': 'MTR'}
            ]
            
            for gov_data in governorates:
                gov = Governorate(**gov_data)
                db.session.add(gov)
            
            db.session.commit()
            logger.info("تم إضافة المحافظات المصرية")
        
        logger.info("تم إنشاء قاعدة البيانات بنجاح")

# API Routes

@app.route('/health', methods=['GET'])
def health_check():
    """فحص حالة الخدمة"""
    return jsonify({
        'status': 'healthy',
        'service': 'naebak-auth-service',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'SQLite' if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI'] else 'PostgreSQL',
        'features': {
            'user_registration': True,
            'user_authentication': True,
            'profile_management': True,
            'multiple_user_types': True,
            'governorate_support': True
        }
    }), 200

@app.route('/api/register', methods=['POST'])
def register():
    """تسجيل مستخدم جديد"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400
        
        # التحقق من البيانات المطلوبة
        required_fields = ['email', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} مطلوب'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        full_name = data['full_name'].strip()
        user_type = data.get('user_type', 'citizen')
        phone_number = data.get('phone_number', '').strip()
        
        # التحقق من صحة البيانات
        if not validate_email(email):
            return jsonify({'error': 'البريد الإلكتروني غير صحيح'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'كلمة المرور يجب أن تكون 6 أحرف على الأقل'}), 400
        
        if user_type not in ['citizen', 'parliament_candidate', 'senate_candidate', 'parliament_member', 'senate_member']:
            return jsonify({'error': 'نوع المستخدم غير صحيح'}), 400
        
        # التحقق من عدم وجود المستخدم
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'البريد الإلكتروني مستخدم بالفعل'}), 400
        
        # إنشاء المستخدم الجديد
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            phone_number=phone_number if phone_number else None,
            user_type=user_type
        )
        
        db.session.add(user)
        db.session.commit()
        
        # إنشاء الملف الشخصي حسب نوع المستخدم
        if user_type == 'citizen':
            profile = CitizenProfile(user_id=user.id)
            db.session.add(profile)
        elif user_type in ['parliament_candidate', 'senate_candidate', 'parliament_member', 'senate_member']:
            profile = CandidateProfile(
                user_id=user.id,
                council_type='parliament' if 'parliament' in user_type else 'senate'
            )
            db.session.add(profile)
        
        db.session.commit()
        
        # إنشاء JWT token
        access_token = create_access_token(identity=user.id)
        
        logger.info(f"تم تسجيل مستخدم جديد: {email}")
        
        return jsonify({
            'message': 'تم التسجيل بنجاح',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في التسجيل: {str(e)}")
        return jsonify({'error': 'حدث خطأ في التسجيل'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """تسجيل الدخول"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400
        
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'البريد الإلكتروني وكلمة المرور مطلوبان'}), 400
        
        # البحث عن المستخدم
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'الحساب غير نشط'}), 401
        
        # تحديث آخر نشاط
        user.last_active = datetime.utcnow()
        db.session.commit()
        
        # إنشاء JWT token
        access_token = create_access_token(identity=user.id)
        
        logger.info(f"تم تسجيل دخول المستخدم: {email}")
        
        return jsonify({
            'message': 'تم تسجيل الدخول بنجاح',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"خطأ في تسجيل الدخول: {str(e)}")
        return jsonify({'error': 'حدث خطأ في تسجيل الدخول'}), 500

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """الحصول على الملف الشخصي"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'المستخدم غير موجود'}), 404
        
        # الحصول على الملف الشخصي حسب نوع المستخدم
        profile_data = None
        if user.user_type == 'citizen' and user.citizen_profile:
            profile_data = user.citizen_profile.to_dict()
        elif user.user_type in ['parliament_candidate', 'senate_candidate', 'parliament_member', 'senate_member'] and user.candidate_profile:
            profile_data = user.candidate_profile.to_dict()
        
        return jsonify({
            'user': user.to_dict(),
            'profile': profile_data
        }), 200
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على الملف الشخصي: {str(e)}")
        return jsonify({'error': 'حدث خطأ في الحصول على الملف الشخصي'}), 500

@app.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """تحديث الملف الشخصي"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'المستخدم غير موجود'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400
        
        # تحديث بيانات المستخدم الأساسية
        if 'full_name' in data:
            user.full_name = data['full_name'].strip()
        if 'phone_number' in data:
            user.phone_number = data['phone_number'].strip() if data['phone_number'] else None
        
        user.updated_at = datetime.utcnow()
        
        # تحديث الملف الشخصي حسب نوع المستخدم
        if user.user_type == 'citizen':
            profile = user.citizen_profile
            if not profile:
                profile = CitizenProfile(user_id=user.id)
                db.session.add(profile)
            
            # تحديث بيانات المواطن
            if 'governorate_id' in data:
                profile.governorate_id = data['governorate_id']
            if 'city' in data:
                profile.city = data['city']
            if 'district' in data:
                profile.district = data['district']
            if 'street_address' in data:
                profile.street_address = data['street_address']
            if 'national_id' in data:
                national_id = data['national_id'].strip()
                if national_id and not validate_national_id(national_id):
                    return jsonify({'error': 'الرقم القومي غير صحيح'}), 400
                profile.national_id = national_id if national_id else None
            if 'gender' in data:
                profile.gender = data['gender']
            if 'birth_date' in data:
                if data['birth_date']:
                    profile.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                else:
                    profile.birth_date = None
            if 'marital_status' in data:
                profile.marital_status = data['marital_status']
            if 'whatsapp_number' in data:
                profile.whatsapp_number = data['whatsapp_number']
            if 'occupation' in data:
                profile.occupation = data['occupation']
            if 'education_level' in data:
                profile.education_level = data['education_level']
            if 'profile_picture' in data:
                profile.profile_picture = data['profile_picture']
            
            # إعدادات الخصوصية
            if 'show_phone_public' in data:
                profile.show_phone_public = data['show_phone_public']
            if 'show_address_public' in data:
                profile.show_address_public = data['show_address_public']
            if 'allow_messages' in data:
                profile.allow_messages = data['allow_messages']
            
            profile.updated_at = datetime.utcnow()
        
        elif user.user_type in ['parliament_candidate', 'senate_candidate', 'parliament_member', 'senate_member']:
            profile = user.candidate_profile
            if not profile:
                profile = CandidateProfile(
                    user_id=user.id,
                    council_type='parliament' if 'parliament' in user.user_type else 'senate'
                )
                db.session.add(profile)
            
            # تحديث بيانات المرشح
            if 'governorate_id' in data:
                profile.governorate_id = data['governorate_id']
            if 'city' in data:
                profile.city = data['city']
            if 'constituency' in data:
                profile.constituency = data['constituency']
            if 'national_id' in data:
                national_id = data['national_id'].strip()
                if national_id and not validate_national_id(national_id):
                    return jsonify({'error': 'الرقم القومي غير صحيح'}), 400
                profile.national_id = national_id if national_id else None
            if 'gender' in data:
                profile.gender = data['gender']
            if 'birth_date' in data:
                if data['birth_date']:
                    profile.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                else:
                    profile.birth_date = None
            if 'party_name' in data:
                profile.party_name = data['party_name']
            if 'electoral_number' in data:
                profile.electoral_number = data['electoral_number']
            if 'electoral_symbol' in data:
                profile.electoral_symbol = data['electoral_symbol']
            if 'bio' in data:
                profile.bio = data['bio']
            if 'electoral_program' in data:
                profile.electoral_program = data['electoral_program']
            if 'education' in data:
                profile.education = data['education']
            if 'occupation' in data:
                profile.occupation = data['occupation']
            if 'experience' in data:
                profile.experience = data['experience']
            if 'profile_picture' in data:
                profile.profile_picture = data['profile_picture']
            if 'banner_image' in data:
                profile.banner_image = data['banner_image']
            if 'campaign_slogan' in data:
                profile.campaign_slogan = data['campaign_slogan']
            if 'campaign_website' in data:
                profile.campaign_website = data['campaign_website']
            
            profile.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"تم تحديث الملف الشخصي للمستخدم: {user.email}")
        
        return jsonify({
            'message': 'تم تحديث الملف الشخصي بنجاح',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في تحديث الملف الشخصي: {str(e)}")
        return jsonify({'error': 'حدث خطأ في تحديث الملف الشخصي'}), 500

@app.route('/api/governorates', methods=['GET'])
def get_governorates():
    """الحصول على قائمة المحافظات"""
    try:
        governorates = Governorate.query.order_by(Governorate.name).all()
        return jsonify({
            'governorates': [gov.to_dict() for gov in governorates]
        }), 200
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على المحافظات: {str(e)}")
        return jsonify({'error': 'حدث خطأ في الحصول على المحافظات'}), 500

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    """الحصول على قائمة المستخدمين (للإدارة)"""
    try:
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)
        
        # التحقق من الصلاحيات (يمكن تطويرها لاحقاً)
        if not current_user or current_user.user_type not in ['parliament_member', 'senate_member']:
            return jsonify({'error': 'غير مصرح لك بالوصول'}), 403
        
        # معاملات البحث والتصفية
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        user_type = request.args.get('user_type')
        governorate_id = request.args.get('governorate_id', type=int)
        
        # بناء الاستعلام
        query = User.query
        
        if user_type:
            query = query.filter(User.user_type == user_type)
        
        if governorate_id:
            if user_type == 'citizen':
                query = query.join(CitizenProfile).filter(CitizenProfile.governorate_id == governorate_id)
            else:
                query = query.join(CandidateProfile).filter(CandidateProfile.governorate_id == governorate_id)
        
        # التصفح
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على المستخدمين: {str(e)}")
        return jsonify({'error': 'حدث خطأ في الحصول على المستخدمين'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """إحصائيات الخدمة"""
    try:
        stats = {
            'total_users': User.query.count(),
            'citizens': User.query.filter_by(user_type='citizen').count(),
            'parliament_candidates': User.query.filter_by(user_type='parliament_candidate').count(),
            'senate_candidates': User.query.filter_by(user_type='senate_candidate').count(),
            'parliament_members': User.query.filter_by(user_type='parliament_member').count(),
            'senate_members': User.query.filter_by(user_type='senate_member').count(),
            'verified_users': User.query.filter_by(verification_status='verified').count(),
            'active_users': User.query.filter_by(is_active=True).count()
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على الإحصائيات: {str(e)}")
        return jsonify({'error': 'حدث خطأ في الحصول على الإحصائيات'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'الصفحة غير موجودة'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'خطأ داخلي في الخادم'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'طلب غير صحيح'}), 400

if __name__ == '__main__':
    # إنشاء قاعدة البيانات
    init_database()
    
    logger.info("=" * 50)
    logger.info("🚀 بدء تشغيل خدمة المصادقة المبسطة v2.0")
    logger.info("=" * 50)
    logger.info("✅ قاعدة البيانات: SQLite (قابلة للانتقال لـ PostgreSQL)")
    logger.info("✅ المصادقة: JWT")
    logger.info("✅ أنواع المستخدمين: مواطن، مرشح، عضو")
    logger.info("✅ الملفات الشخصية: مدعومة")
    logger.info("✅ المحافظات: 27 محافظة مصرية")
    logger.info("=" * 50)
    
    # إنشاء قاعدة البيانات والبيانات الأولية
    with app.app_context():
        # إنشاء الجداول
        db.create_all()
        
        # التحقق من وجود البيانات الأولية
        if Governorate.query.count() == 0:
            logger.info("🔄 إضافة البيانات الأولية...")
            
            # إضافة جميع المحافظات المصرية
            governorates = [
                ('القاهرة', 'Cairo', 'CAI'),
                ('الجيزة', 'Giza', 'GIZ'),
                ('الإسكندرية', 'Alexandria', 'ALX'),
                ('الدقهلية', 'Dakahlia', 'DK'),
                ('البحر الأحمر', 'Red Sea', 'BA'),
                ('البحيرة', 'Beheira', 'BH'),
                ('الفيوم', 'Fayoum', 'FYM'),
                ('الغربية', 'Gharbia', 'GH'),
                ('الإسماعيلية', 'Ismailia', 'IS'),
                ('المنوفية', 'Monufia', 'MN'),
                ('المنيا', 'Minya', 'MNY'),
                ('القليوبية', 'Qalyubia', 'KB'),
                ('الوادي الجديد', 'New Valley', 'WAD'),
                ('السويس', 'Suez', 'SUZ'),
                ('أسوان', 'Aswan', 'ASN'),
                ('أسيوط', 'Asyut', 'AST'),
                ('بني سويف', 'Beni Suef', 'BNS'),
                ('بورسعيد', 'Port Said', 'PTS'),
                ('دمياط', 'Damietta', 'DT'),
                ('الشرقية', 'Sharqia', 'SH'),
                ('جنوب سيناء', 'South Sinai', 'JS'),
                ('كفر الشيخ', 'Kafr El Sheikh', 'KFS'),
                ('مطروح', 'Matrouh', 'MT'),
                ('الأقصر', 'Luxor', 'LXR'),
                ('قنا', 'Qena', 'QNA'),
                ('شمال سيناء', 'North Sinai', 'SIN'),
                ('سوهاج', 'Sohag', 'SHG')
            ]
            
            for gov_name, gov_name_en, gov_code in governorates:
                gov = Governorate(name=gov_name, name_en=gov_name_en, code=gov_code)
                db.session.add(gov)
            
            db.session.commit()
            logger.info(f"✅ تم إضافة {len(governorates)} محافظة")
        else:
            logger.info(f"✅ البيانات الأولية موجودة ({Governorate.query.count()} محافظة)")
    
    app.run(host='0.0.0.0', port=8001, debug=True)
