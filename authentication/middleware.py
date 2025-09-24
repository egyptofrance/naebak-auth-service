"""
Middleware للمصادقة المرنة في تطبيق نائبك
"""

import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
from users.models import UserSession, AnonymousSession, LoginAttempt

logger = logging.getLogger(__name__)


class FlexibleAuthMiddleware(MiddlewareMixin):
    """
    Middleware للمصادقة المرنة
    - يتتبع الجلسات المجهولة
    - يسمح بالتصفح بدون مصادقة
    - يطلب المصادقة عند الحاجة
    """
    
    # المسارات التي تتطلب مصادقة إجبارية
    PROTECTED_PATHS = [
        '/api/ratings/',
        '/api/messages/',
        '/api/complaints/',
        '/api/profile/',
        '/api/dashboard/',
    ]
    
    # المسارات العامة المسموحة بدون مصادقة
    PUBLIC_PATHS = [
        '/api/candidates/',
        '/api/news/',
        '/api/public/',
        '/api/auth/',
        '/api/health/',
        '/metrics/',
        '/admin/',
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        """معالجة الطلب الوارد"""
        
        # تتبع الجلسة
        self._track_session(request)
        
        # التحقق من الحاجة للمصادقة
        if self._requires_authentication(request):
            if not request.user.is_authenticated:
                return self._authentication_required_response(request)
        
        return None
    
    def _track_session(self, request):
        """تتبع جلسة المستخدم أو الجلسة المجهولة"""
        
        if request.user.is_authenticated:
            self._track_user_session(request)
        else:
            self._track_anonymous_session(request)
    
    def _track_user_session(self, request):
        """تتبع جلسة المستخدم المُسجل"""
        
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # إنشاء أو تحديث جلسة المستخدم
        user_session, created = UserSession.objects.get_or_create(
            session_key=session_key,
            defaults={
                'user': request.user,
                'ip_address': ip_address,
                'user_agent': user_agent,
            }
        )
        
        if not created:
            user_session.last_activity = timezone.now()
            user_session.save(update_fields=['last_activity'])
        
        # تحديث آخر IP للدخول
        if request.user.last_login_ip != ip_address:
            request.user.last_login_ip = ip_address
            request.user.save(update_fields=['last_login_ip'])
    
    def _track_anonymous_session(self, request):
        """تتبع الجلسة المجهولة"""
        
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # إنشاء أو تحديث الجلسة المجهولة
        anonymous_session, created = AnonymousSession.objects.get_or_create(
            session_key=session_key,
            defaults={
                'ip_address': ip_address,
                'user_agent': user_agent,
            }
        )
        
        if not created:
            anonymous_session.last_activity = timezone.now()
            anonymous_session.save(update_fields=['last_activity'])
        
        # إضافة الصفحة المزارة
        if request.path.startswith('/api/candidates/'):
            anonymous_session.add_visited_page(request.path)
    
    def _requires_authentication(self, request):
        """التحقق من الحاجة للمصادقة"""
        
        # السماح بالمسارات العامة
        if any(request.path.startswith(path) for path in self.PUBLIC_PATHS):
            return False
        
        # طلب المصادقة للمسارات المحمية
        if any(request.path.startswith(path) for path in self.PROTECTED_PATHS):
            return True
        
        # طلب المصادقة للعمليات غير GET/OPTIONS/HEAD
        if request.method not in ['GET', 'OPTIONS', 'HEAD']:
            return True
        
        return False
    
    def _authentication_required_response(self, request):
        """إرجاع رد يطلب المصادقة"""
        
        return JsonResponse({
            'error': 'authentication_required',
            'message': 'يجب تسجيل الدخول للوصول لهذه الخدمة',
            'message_en': 'Authentication required to access this service',
            'login_url': '/api/auth/login/',
            'register_url': '/api/auth/register/',
            'google_login_url': '/api/auth/google/',
        }, status=401)
    
    def _get_client_ip(self, request):
        """الحصول على IP العميل"""
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware للأمان
    - تتبع محاولات تسجيل الدخول
    - حماية من الهجمات
    - تنظيف الجلسات المنتهية الصلاحية
    """
    
    def process_request(self, request):
        """معالجة الطلب للأمان"""
        
        # تنظيف الجلسات المنتهية الصلاحية (كل ساعة)
        if hasattr(request, '_security_cleanup_done'):
            return None
        
        request._security_cleanup_done = True
        self._cleanup_expired_sessions()
        
        return None
    
    def process_response(self, request, response):
        """معالجة الرد"""
        
        # تسجيل محاولات تسجيل الدخول
        if request.path.startswith('/api/auth/login/') and request.method == 'POST':
            self._log_login_attempt(request, response)
        
        return response
    
    def _log_login_attempt(self, request, response):
        """تسجيل محاولة تسجيل الدخول"""
        
        try:
            if hasattr(request, 'body') and request.body:
                data = json.loads(request.body.decode('utf-8'))
                email = data.get('email', '')
            else:
                email = request.POST.get('email', '')
            
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            success = response.status_code == 200
            failure_reason = ''
            
            if not success and hasattr(response, 'data'):
                failure_reason = str(response.data.get('error', ''))[:100]
            
            LoginAttempt.objects.create(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                failure_reason=failure_reason,
            )
            
        except Exception as e:
            logger.error(f"Error logging login attempt: {e}")
    
    def _cleanup_expired_sessions(self):
        """تنظيف الجلسات المنتهية الصلاحية"""
        
        try:
            # حذف الجلسات المجهولة القديمة (أكثر من 7 أيام)
            cutoff_date = timezone.now() - timedelta(days=7)
            AnonymousSession.objects.filter(last_activity__lt=cutoff_date).delete()
            
            # حذف جلسات المستخدمين غير النشطة (أكثر من 30 يوم)
            cutoff_date = timezone.now() - timedelta(days=30)
            UserSession.objects.filter(last_activity__lt=cutoff_date).delete()
            
            # حذف محاولات تسجيل الدخول القديمة (أكثر من 90 يوم)
            cutoff_date = timezone.now() - timedelta(days=90)
            LoginAttempt.objects.filter(created_at__lt=cutoff_date).delete()
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
    
    def _get_client_ip(self, request):
        """الحصول على IP العميل"""
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
