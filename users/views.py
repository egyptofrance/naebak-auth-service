# -*- coding: utf-8 -*-
"""
واجهات برمجة التطبيقات لخدمة المصادقة - نائبك
Authentication API Views for Naebak Application
"""

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import User, CitizenProfile, CandidateProfile, CurrentMemberProfile, Governorate, Party
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    CitizenProfileSerializer,
    CandidateProfileSerializer,
    CurrentMemberProfileSerializer
)


from drf_spectacular.utils import extend_schema

@extend_schema(
    summary="Register a new user",
    description="Create a new user account with a unique username and email.",
    request=UserRegistrationSerializer,
    responses={201: UserRegistrationSerializer}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    تسجيل مستخدم جديد في النظام - Register a new user in the system
    
    Business Logic:
        1. التحقق من صحة البيانات الأساسية (email, password, names)
        2. إنشاء المستخدم الأساسي مع نوع المستخدم المحدد
        3. إنشاء الملف الشخصي المناسب حسب نوع المستخدم:
           - CitizenProfile للمواطنين العاديين
           - CandidateProfile للمرشحين (برلمان/شيوخ)
           - CurrentMemberProfile للأعضاء الحاليين
        4. إنشاء JWT tokens للمصادقة الفورية
        5. إرجاع بيانات المستخدم مع الـ tokens
    
    Security Considerations:
        - كلمة المرور يتم تشفيرها تلقائياً بواسطة Django
        - البريد الإلكتروني يجب أن يكون فريد في النظام
        - الرقم القومي يجب أن يكون فريد (للمواطنين)
        - استخدام database transaction لضمان تكامل البيانات
    
    Args:
        request (HttpRequest): طلب HTTP يحتوي على بيانات التسجيل
        
    Returns:
        Response: JSON response يحتوي على:
            - success (bool): حالة نجاح العملية
            - message (str): رسالة توضيحية
            - data (dict): بيانات المستخدم والـ tokens (في حالة النجاح)
            - errors (dict): أخطاء التحقق (في حالة الفشل)
    
    HTTP Status Codes:
        - 201: تم إنشاء المستخدم بنجاح
        - 400: بيانات غير صحيحة أو ناقصة
        - 500: خطأ في الخادم
    """
    try:
        with transaction.atomic():
            serializer = UserRegistrationSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.save()
                
                # إنشاء الملف الشخصي حسب نوع المستخدم
                profile_data = request.data.copy()
                profile_data['user'] = user.id
                
                if user.user_type == User.UserType.CITIZEN:
                    profile_serializer = CitizenProfileSerializer(data=profile_data)
                elif user.user_type in [User.UserType.PARLIAMENT_CANDIDATE, User.UserType.SENATE_CANDIDATE]:
                    profile_serializer = CandidateProfileSerializer(data=profile_data)
                elif user.user_type in [User.UserType.PARLIAMENT_MEMBER, User.UserType.SENATE_MEMBER]:
                    profile_serializer = CurrentMemberProfileSerializer(data=profile_data)
                else:
                    profile_serializer = CitizenProfileSerializer(data=profile_data)
                
                if profile_serializer.is_valid():
                    profile_serializer.save()
                else:
                    return Response({
                        'success': False,
                        'message': 'خطأ في بيانات الملف الشخصي',
                        'errors': profile_serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # إنشاء JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                return Response({
                    'success': True,
                    'message': 'تم تسجيل المستخدم بنجاح',
                    'data': {
                        'user': {
                            'id': user.id,
                            'name': user.get_full_name(),
                            'email': user.email,
                            'phone': str(user.phone_number) if user.phone_number else None,
                            'user_type': user.get_user_type_display(),
                            'verification_status': user.get_verification_status_display(),
                            'created_at': user.date_joined.isoformat()
                        },
                        'tokens': {
                            'access': str(access_token),
                            'refresh': str(refresh),
                            'expires_in': 3600  # 1 hour
                        }
                    }
                }, status=status.HTTP_201_CREATED)
            
            else:
                return Response({
                    'success': False,
                    'message': 'بيانات غير صحيحة',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        return Response({
            'success': False,
            'message': 'حدث خطأ أثناء التسجيل',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Login a user",
    description="Authenticate a user and return a JWT token.",
    request=UserLoginSerializer,
    responses={200: UserLoginSerializer}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    تسجيل دخول المستخدم - User authentication and login
    
    Business Logic:
        1. التحقق من صحة بيانات تسجيل الدخول (email, password)
        2. محاولة مصادقة المستخدم باستخدام Django authentication
        3. التحقق من أن الحساب نشط (is_active=True)
        4. تحديث آخر نشاط للمستخدم (last_active)
        5. إنشاء JWT tokens جديدة (access + refresh)
        6. إرجاع بيانات المستخدم مع الـ tokens
    
    Security Considerations:
        - كلمة المرور يتم التحقق منها بشكل آمن (hashed comparison)
        - JWT tokens لها مدة انتهاء صلاحية محددة
        - تسجيل محاولات تسجيل الدخول الفاشلة (للمراقبة)
        - التحقق من حالة تفعيل الحساب قبل السماح بالدخول
    
    Args:
        request (HttpRequest): طلب HTTP يحتوي على email و password
        
    Returns:
        Response: JSON response يحتوي على:
            - success (bool): حالة نجاح العملية
            - message (str): رسالة توضيحية
            - data (dict): بيانات المستخدم والـ tokens (في حالة النجاح)
    
    HTTP Status Codes:
        - 200: تم تسجيل الدخول بنجاح
        - 400: بيانات غير صحيحة
        - 401: بيانات مصادقة خاطئة أو حساب غير مفعل
        - 500: خطأ في الخادم
    """
    try:
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(email=email, password=password)
            
            if user:
                if user.is_active:
                    # تحديث آخر نشاط
                    user.save(update_fields=['last_active'])
                    
                    # إنشاء JWT tokens
                    refresh = RefreshToken.for_user(user)
                    access_token = refresh.access_token
                    
                    return Response({
                        'success': True,
                        'message': 'تم تسجيل الدخول بنجاح',
                        'data': {
                            'user': {
                                'id': user.id,
                                'name': user.get_full_name(),
                                'email': user.email,
                                'phone': str(user.phone_number) if user.phone_number else None,
                                'user_type': user.get_user_type_display(),
                                'verification_status': user.get_verification_status_display(),
                                'last_active': user.last_active.isoformat()
                            },
                            'tokens': {
                                'access': str(access_token),
                                'refresh': str(refresh),
                                'expires_in': 3600  # 1 hour
                            }
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'success': False,
                        'message': 'الحساب غير مفعل'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({
                    'success': False,
                    'message': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            return Response({
                'success': False,
                'message': 'بيانات غير صحيحة',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': 'حدث خطأ أثناء تسجيل الدخول',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Logout a user",
    description="Blacklist the user's refresh token to log them out.",
    request=None,
    responses={200: None}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    تسجيل خروج المستخدم
    User logout
    """
    try:
        refresh_token = request.data.get('refresh_token')
        
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'success': True,
                'message': 'تم تسجيل الخروج بنجاح'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'مطلوب رمز التحديث'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': 'حدث خطأ أثناء تسجيل الخروج',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Get user profile",
    description="Get the profile of the currently authenticated user.",
    request=None,
    responses={200: UserProfileSerializer}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    الحصول على ملف المستخدم الشخصي
    Get user profile
    """
    try:
        user = request.user
        
        # الحصول على الملف الشخصي حسب نوع المستخدم
        profile_data = None
        
        if user.user_type == User.UserType.CITIZEN:
            if hasattr(user, 'citizen_profile'):
                profile_serializer = CitizenProfileSerializer(user.citizen_profile)
                profile_data = profile_serializer.data
        
        elif user.user_type in [User.UserType.PARLIAMENT_CANDIDATE, User.UserType.SENATE_CANDIDATE]:
            if hasattr(user, 'candidate_profile'):
                profile_serializer = CandidateProfileSerializer(user.candidate_profile)
                profile_data = profile_serializer.data
        
        elif user.user_type in [User.UserType.PARLIAMENT_MEMBER, User.UserType.SENATE_MEMBER]:
            if hasattr(user, 'member_profile'):
                profile_serializer = CurrentMemberProfileSerializer(user.member_profile)
                profile_data = profile_serializer.data
        
        return Response({
            'success': True,
            'data': {
                'user': {
                    'id': user.id,
                    'name': user.get_full_name(),
                    'email': user.email,
                    'phone': str(user.phone_number) if user.phone_number else None,
                    'user_type': user.get_user_type_display(),
                    'verification_status': user.get_verification_status_display(),
                    'last_active': user.last_active.isoformat(),
                    'created_at': user.date_joined.isoformat()
                },
                'profile': profile_data
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'حدث خطأ أثناء جلب الملف الشخصي',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_governorates(request):
    """
    الحصول على قائمة المحافظات المصرية
    Get list of Egyptian governorates
    """
    try:
        governorates = Governorate.objects.all().order_by('name')
        
        data = [
            {
                'id': gov.id,
                'name': gov.name,
                'name_en': gov.name_en,
                'code': gov.code
            }
            for gov in governorates
        ]
        
        return Response({
            'success': True,
            'data': {
                'governorates': data,
                'count': len(data)
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'حدث خطأ أثناء جلب المحافظات',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_parties(request):
    """
    الحصول على قائمة الأحزاب السياسية المصرية
    Get list of Egyptian political parties
    """
    try:
        parties = Party.objects.all().order_by('name')
        
        data = [
            {
                'id': party.id,
                'name': party.name,
                'name_en': party.name_en,
                'abbreviation': party.abbreviation
            }
            for party in parties
        ]
        
        return Response({
            'success': True,
            'data': {
                'parties': data,
                'count': len(data)
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'حدث خطأ أثناء جلب الأحزاب',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """
    التحقق من صحة الرمز المميز
    Verify JWT token
    """
    try:
        user = request.user
        
        return Response({
            'success': True,
            'message': 'الرمز المميز صحيح',
            'data': {
                'user_id': user.id,
                'email': user.email,
                'name': user.get_full_name(),
                'user_type': user.get_user_type_display(),
                'is_active': user.is_active,
                'verified_at': user.last_active.isoformat()
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'حدث خطأ أثناء التحقق من الرمز',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
