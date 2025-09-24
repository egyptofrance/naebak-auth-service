"""
مدير نماذج المستخدمين المخصص
"""

from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    مدير مخصص لنموذج المستخدم الذي يستخدم البريد الإلكتروني بدلاً من اسم المستخدم
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        إنشاء وحفظ مستخدم عادي بالبريد الإلكتروني وكلمة المرور
        """
        if not email:
            raise ValueError(_('يجب إدخال البريد الإلكتروني'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        إنشاء وحفظ مستخدم إداري بالبريد الإلكتروني وكلمة المرور
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('verification_status', 'verified')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('المستخدم الإداري يجب أن يكون is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('المستخدم الإداري يجب أن يكون is_superuser=True'))
        
        return self.create_user(email, password, **extra_fields)
