"""
Views للمصادقة في تطبيق نائبك
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from users.models import User, UserSession, LoginAttempt
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, GoogleOAuthSerializer,
    UserProfileSerializer, PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, WelcomeModalSerializer
)
from .permissions import FlexiblePermission, AuthenticatedOnlyPermission

import logging

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    """
    تسجيل مستخدم جديد
    """
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST'))
    def post(self, request, *args, **kwargs):
        """تسجيل مستخدم جديد مع حماية من التكرار"""
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # تعيين علامة للمستخدم الجديد
            user._is_new_registration = True
            
            # إنشاء JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # تسجيل دخول المستخدم
            login(request, user)
            
            # إرسال بريد ترحيبي
            self._send_welcome_email(user)
            
            # إعداد بيانات نافذة الترحيب
            welcome_data = WelcomeModalSerializer(user).data
            
            logger.info(f"New user registered: {user.email}")
            
            return Response({
                'message': 'تم إنشاء الحساب بنجاح',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh),
                },
                'welcome_modal': welcome_data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _send_welcome_email(self, user):
        """إرسال بريد ترحيبي للمستخدم الجديد"""
        try:
            subject = 'مرحباً بك في نائبك'
            message = render_to_string('emails/welcome.html', {
                'user': user,
                'site_name': 'نائبك',
            })
            
            send_mail(
                subject=subject,
                message='',
                html_message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {e}")


class UserLoginView(APIView):
    """
    تسجيل دخول المستخدم
    """
    
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='10/m', method='POST'))
    def post(self, request):
        """تسجيل دخول مع حماية من التكرار"""
        
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            remember_me = serializer.validated_data.get('remember_me', False)
            
            # تسجيل دخول المستخدم
            login(request, user)
            
            # إعداد مدة الجلسة
            if remember_me:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE * 7)  # أسبوع
            else:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)  # يوم واحد
            
            # إنشاء JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # إعداد بيانات نافذة الترحيب
            welcome_data = WelcomeModalSerializer(user).data
            
            logger.info(f"User logged in: {user.email}")
            
            return Response({
                'message': 'تم تسجيل الدخول بنجاح',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh),
                },
                'welcome_modal': welcome_data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """
    تسجيل خروج المستخدم
    """
    
    permission_classes = [AuthenticatedOnlyPermission]
    
    def post(self, request):
        """تسجيل خروج المستخدم"""
        
        try:
            # إلغاء تفعيل جلسة المستخدم
            session_key = request.session.session_key
            if session_key:
                UserSession.objects.filter(session_key=session_key).update(is_active=False)
            
            # تسجيل خروج المستخدم
            logout(request)
            
            logger.info(f"User logged out: {request.user.email}")
            
            return Response({
                'message': 'تم تسجيل الخروج بنجاح'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return Response({
                'error': 'حدث خطأ أثناء تسجيل الخروج'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleOAuthView(APIView):
    """
    المصادقة بـ Google OAuth
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """المصادقة بـ Google"""
        
        serializer = GoogleOAuthSerializer(data=request.data)
        if serializer.is_valid():
            access_token = serializer.validated_data['access_token']
            
            # التحقق من صحة التوكن والحصول على بيانات المستخدم من Google
            user_data = self._verify_google_token(access_token)
            
            if user_data:
                user = self._get_or_create_google_user(user_data)
                
                # تسجيل دخول المستخدم
                login(request, user)
                
                # إنشاء JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                # إعداد بيانات نافذة الترحيب
                welcome_data = WelcomeModalSerializer(user).data
                
                logger.info(f"User logged in via Google: {user.email}")
                
                return Response({
                    'message': 'تم تسجيل الدخول بـ Google بنجاح',
                    'user': UserProfileSerializer(user).data,
                    'tokens': {
                        'access': str(access_token),
                        'refresh': str(refresh),
                    },
                    'welcome_modal': welcome_data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'error': 'فشل في التحقق من بيانات Google'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _verify_google_token(self, access_token):
        """التحقق من صحة التوكن من Google"""
        # سيتم تطوير هذا لاحقاً مع Google OAuth API
        # هذا مثال مبدئي
        return {
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'google_id': '123456789',
        }
    
    def _get_or_create_google_user(self, user_data):
        """الحصول على المستخدم أو إنشاؤه من بيانات Google"""
        
        email = user_data['email']
        google_id = user_data['google_id']
        
        # البحث عن المستخدم بـ Google ID أو البريد الإلكتروني
        user = User.objects.filter(
            models.Q(google_id=google_id) | models.Q(email=email)
        ).first()
        
        if user:
            # تحديث Google ID إذا لم يكن موجود
            if not user.google_id:
                user.google_id = google_id
                user.save(update_fields=['google_id'])
        else:
            # إنشاء مستخدم جديد
            user = User.objects.create_user(
                email=email,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                google_id=google_id,
                is_email_verified=True,  # Google emails are verified
            )
            user._is_new_registration = True
        
        return user


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    عرض وتحديث الملف الشخصي
    """
    
    serializer_class = UserProfileSerializer
    permission_classes = [AuthenticatedOnlyPermission]
    
    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    """
    تغيير كلمة المرور
    """
    
    permission_classes = [AuthenticatedOnlyPermission]
    
    def post(self, request):
        """تغيير كلمة المرور"""
        
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            logger.info(f"Password changed for user: {request.user.email}")
            
            return Response({
                'message': 'تم تغيير كلمة المرور بنجاح'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    طلب إعادة تعيين كلمة المرور
    """
    
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='3/m', method='POST'))
    def post(self, request):
        """طلب إعادة تعيين كلمة المرور"""
        
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # إنشاء رمز إعادة التعيين
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # إرسال بريد إعادة التعيين
            self._send_reset_email(user, token, uid)
            
            logger.info(f"Password reset requested for: {email}")
            
            return Response({
                'message': 'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _send_reset_email(self, user, token, uid):
        """إرسال بريد إعادة تعيين كلمة المرور"""
        try:
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            subject = 'إعادة تعيين كلمة المرور - نائبك'
            message = render_to_string('emails/password_reset.html', {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'نائبك',
            })
            
            send_mail(
                subject=subject,
                message='',
                html_message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send reset email to {user.email}: {e}")


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """فحص صحة الخدمة"""
    return Response({
        'status': 'healthy',
        'service': 'naibak-auth-service',
        'timestamp': timezone.now().isoformat(),
    })


@api_view(['GET'])
@permission_classes([FlexiblePermission])
def user_status(request):
    """حالة المستخدم الحالي"""
    
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': UserProfileSerializer(request.user).data
        })
    else:
        return Response({
            'authenticated': False,
            'message': 'غير مسجل الدخول'
        })


@api_view(['POST'])
@permission_classes([AuthenticatedOnlyPermission])
def welcome_modal_data(request):
    """بيانات نافذة الترحيب"""
    
    welcome_data = WelcomeModalSerializer(request.user).data
    return Response(welcome_data)
