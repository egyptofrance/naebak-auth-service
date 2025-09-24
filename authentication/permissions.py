"""
نظام الصلاحيات المرن لتطبيق نائبك
يسمح بالتصفح بدون مصادقة ويطلب المصادقة عند الحاجة
"""

from rest_framework.permissions import BasePermission
from django.conf import settings


class FlexiblePermission(BasePermission):
    """
    صلاحية مرنة تسمح بالتصفح العام وتطلب المصادقة للعمليات الحساسة
    """
    
    # العمليات المسموحة بدون مصادقة
    PUBLIC_ACTIONS = [
        'list',      # عرض القوائم
        'retrieve',  # عرض التفاصيل
        'options',   # خيارات API
        'head',      # معلومات الرأس
    ]
    
    # المسارات المسموحة بدون مصادقة
    PUBLIC_PATHS = [
        '/api/candidates/',
        '/api/news/',
        '/api/public/',
        '/api/auth/register/',
        '/api/auth/login/',
        '/api/auth/google/',
        '/api/health/',
        '/metrics/',
    ]
    
    def has_permission(self, request, view):
        """
        تحديد ما إذا كان المستخدم لديه صلاحية للوصول
        """
        # السماح بالوصول للمسارات العامة
        if self._is_public_path(request.path):
            return True
        
        # السماح بالعمليات العامة (GET, OPTIONS, HEAD)
        if self._is_public_action(view):
            return True
        
        # طلب المصادقة للعمليات الحساسة
        return request.user and request.user.is_authenticated
    
    def _is_public_path(self, path):
        """التحقق من كون المسار عام"""
        return any(path.startswith(public_path) for public_path in self.PUBLIC_PATHS)
    
    def _is_public_action(self, view):
        """التحقق من كون العملية عامة"""
        if hasattr(view, 'action'):
            return view.action in self.PUBLIC_ACTIONS
        return False


class AuthenticatedOnlyPermission(BasePermission):
    """
    صلاحية تتطلب المصادقة دائماً
    تُستخدم للعمليات الحساسة مثل التقييم والرسائل والشكاوى
    """
    
    def has_permission(self, request, view):
        """طلب المصادقة دائماً"""
        return request.user and request.user.is_authenticated


class VerifiedUserPermission(BasePermission):
    """
    صلاحية تتطلب مستخدم مُتحقق من هويته
    """
    
    def has_permission(self, request, view):
        """طلب مستخدم مُتحقق من هويته"""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_verified
        )


class CandidatePermission(BasePermission):
    """
    صلاحية خاصة بالمرشحين
    """
    
    def has_permission(self, request, view):
        """طلب مستخدم مرشح"""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_candidate
        )


class MemberPermission(BasePermission):
    """
    صلاحية خاصة بأعضاء البرلمان
    """
    
    def has_permission(self, request, view):
        """طلب مستخدم عضو في البرلمان"""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_member
        )


class VoterPermission(BasePermission):
    """
    صلاحية خاصة بالناخبين
    """
    
    def has_permission(self, request, view):
        """طلب مستخدم له حق التصويت"""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.can_vote
        )
