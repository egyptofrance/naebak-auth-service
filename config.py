# -*- coding: utf-8 -*-
"""إعدادات مبسطة لخدمة المصادقة والعضوية"""

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

class Config:
    """إعدادات التطبيق الأساسية"""
    
    # إعدادات Django الأساسية
    SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-auth-service-key')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    
    # إعدادات قاعدة البيانات
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
    
    # إعدادات Redis للجلسات والتخزين المؤقت
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # إعدادات JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_LIFETIME = int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME', 3600))  # ساعة
    JWT_REFRESH_TOKEN_LIFETIME = int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME', 604800))  # أسبوع
    
    # إعدادات الخدمة
    SERVICE_NAME = 'naebak-auth-service'
    SERVICE_PORT = int(os.environ.get('PORT', 8001))
    SERVICE_VERSION = '1.0.0'
    
    # إعدادات الأمان
    PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', 8))
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
    ACCOUNT_LOCKOUT_DURATION = int(os.environ.get('ACCOUNT_LOCKOUT_DURATION', 1800))  # 30 دقيقة
    
    # إعدادات التحقق
    PHONE_VERIFICATION_ENABLED = os.environ.get('PHONE_VERIFICATION_ENABLED', 'true').lower() == 'true'
    EMAIL_VERIFICATION_ENABLED = os.environ.get('EMAIL_VERIFICATION_ENABLED', 'false').lower() == 'true'
    
    # إعدادات الرسائل النصية (للتحقق من الهاتف)
    SMS_PROVIDER = os.environ.get('SMS_PROVIDER', 'local')  # local, twilio, etc.
    SMS_API_KEY = os.environ.get('SMS_API_KEY', '')
    SMS_API_SECRET = os.environ.get('SMS_API_SECRET', '')
    
    # إعدادات البريد الإلكتروني
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'
    
    # إعدادات CORS
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
    # إعدادات التسجيل (Logging)
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'auth_service.log')
    
    # إعدادات المراقبة
    MONITORING_ENABLED = os.environ.get('MONITORING_ENABLED', 'false').lower() == 'true'
    HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', 60))  # ثانية

class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    MONITORING_ENABLED = True

class TestingConfig(Config):
    """إعدادات بيئة الاختبار"""
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'
    PHONE_VERIFICATION_ENABLED = False
    EMAIL_VERIFICATION_ENABLED = False

# تحديد الإعدادات حسب البيئة
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """الحصول على إعدادات البيئة الحالية"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(env, config_by_name['default'])
