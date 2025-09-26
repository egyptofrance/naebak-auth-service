# 🏷️ خدمة المصادقة والتخويل (naebak-auth-service)

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/egyptofrance/naebak-auth-service/actions)
[![Coverage](https://img.shields.io/badge/coverage-92%25-green)](https://github.com/egyptofrance/naebak-auth-service)
[![Version](https://img.shields.io/badge/version-1.1.0-blue)](https://github.com/egyptofrance/naebak-auth-service/releases)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

## 📝 الوصف

خدمة المصادقة والتخويل المركزية لمنصة نائبك. تدير تسجيل المستخدمين، تسجيل الدخول، والصلاحيات عبر جميع خدمات النظام. تدعم أنواع مختلفة من المستخدمين (مواطنين، نواب، مديرين) مع نظام صلاحيات متقدم.

---

## ✨ الميزات الرئيسية

- **تسجيل المستخدمين**: نظام تسجيل آمن مع التحقق من البريد الإلكتروني
- **المصادقة المتعددة**: دعم JWT وSession-based authentication
- **إدارة الصلاحيات**: نظام صلاحيات مرن يدعم الأدوار المختلفة
- **الأمان المتقدم**: حماية من CSRF، XSS، وهجمات Brute Force

---

## 🛠️ التقنيات المستخدمة

| التقنية | الإصدار | الغرض |
|---------|---------|-------|
| **Django** | 4.2.5 | إطار العمل الأساسي |
| **Django REST Framework** | 3.14.0 | تطوير APIs |
| **PostgreSQL** | 13+ | قاعدة البيانات الرئيسية |
| **Redis** | 6+ | التخزين المؤقت والجلسات |
| **Celery** | 5.3+ | المهام غير المتزامنة |

---

## 🚀 التثبيت والتشغيل

### **المتطلبات الأساسية**

- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose

### **التثبيت المحلي**

#### **1. استنساخ المستودع**
```bash
git clone https://github.com/egyptofrance/naebak-auth-service.git
cd naebak-auth-service
```

#### **2. إعداد البيئة الافتراضية**
```bash
python -m venv venv
source venv/bin/activate
```

#### **3. تثبيت المتطلبات**
```bash
pip install -r requirements.txt
```

#### **4. إعداد متغيرات البيئة**
```bash
cp .env.example .env
# قم بتعديل ملف .env بالقيم المناسبة
```

#### **5. إعداد قاعدة البيانات**
```bash
python manage.py migrate
python manage.py createsuperuser
```

#### **6. تشغيل الخدمة**
```bash
python manage.py runserver 8000
```

### **التشغيل باستخدام Docker**

```bash
docker-compose up --build -d
```

---

## 📚 توثيق الـ API

### **الوصول للتوثيق التفاعلي**

- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **Redoc**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)

### **روابط التوثيق المفصل**

- [دليل الـ API الكامل](docs/API.md)
- [سجلات قرارات المعمارية](docs/adrs/)

---

## 🧪 الاختبارات

### **تشغيل جميع الاختبارات**
```bash
python manage.py test
```

### **تقرير التغطية**
```bash
coverage run -m pytest
coverage report
```

---

## 🚀 النشر

يتم النشر تلقائياً عند Push إلى branch `main` باستخدام GitHub Actions.

---

## 🤝 المساهمة

يرجى مراجعة [دليل المساهمة](CONTRIBUTING.md) و [معايير التوثيق الموحدة](../../naebak-almakhzan/DOCUMENTATION_STANDARDS.md).

---

## 📄 الترخيص

هذا المشروع مرخص تحت [رخصة MIT](LICENSE).

