"""
Serializers للمصادقة في تطبيق نائبك
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from users.models import User
from phonenumber_field.serializerfields import PhoneNumberField


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer لتسجيل مستخدم جديد
    """
    
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    phone_number = PhoneNumberField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number',
            'user_type', 'governorate', 'city', 'bio'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'user_type': {'required': True},
        }
    
    def validate_email(self, value):
        """التحقق من البريد الإلكتروني"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "مستخدم بهذا البريد الإلكتروني موجود بالفعل"
            )
        return value
    
    def validate_password(self, value):
        """التحقق من كلمة المرور"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """التحقق من تطابق كلمات المرور"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'كلمات المرور غير متطابقة'
            })
        return attrs
    
    def create(self, validated_data):
        """إنشاء مستخدم جديد"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer لتسجيل الدخول
    """
    
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    remember_me = serializers.BooleanField(default=False)
    
    def validate(self, attrs):
        """التحقق من بيانات تسجيل الدخول"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'بيانات تسجيل الدخول غير صحيحة'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'هذا الحساب غير مفعل'
                )
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError(
                'يجب إدخال البريد الإلكتروني وكلمة المرور'
            )
        
        return attrs


class GoogleOAuthSerializer(serializers.Serializer):
    """
    Serializer للمصادقة بـ Google
    """
    
    access_token = serializers.CharField()
    
    def validate_access_token(self, value):
        """التحقق من صحة access token من Google"""
        # سيتم تطوير هذا لاحقاً مع Google OAuth
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer لعرض وتحديث الملف الشخصي
    """
    
    phone_number = PhoneNumberField(required=False, allow_blank=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    user_type_display = serializers.CharField(source='get_user_type_display_ar', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'user_type', 'user_type_display',
            'verification_status', 'profile_picture', 'bio',
            'birth_date', 'governorate', 'city',
            'is_email_verified', 'is_phone_verified',
            'receive_notifications', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'email', 'verification_status', 'is_email_verified',
            'is_phone_verified', 'created_at', 'updated_at'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer لتغيير كلمة المرور
    """
    
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(
        min_length=8,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate_old_password(self, value):
        """التحقق من كلمة المرور القديمة"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('كلمة المرور القديمة غير صحيحة')
        return value
    
    def validate_new_password(self, value):
        """التحقق من كلمة المرور الجديدة"""
        try:
            validate_password(value, self.context['request'].user)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """التحقق من تطابق كلمات المرور الجديدة"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'كلمات المرور الجديدة غير متطابقة'
            })
        return attrs
    
    def save(self):
        """حفظ كلمة المرور الجديدة"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer لطلب إعادة تعيين كلمة المرور
    """
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """التحقق من وجود البريد الإلكتروني"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'لا يوجد حساب مرتبط بهذا البريد الإلكتروني'
            )
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer لتأكيد إعادة تعيين كلمة المرور
    """
    
    token = serializers.CharField()
    new_password = serializers.CharField(
        min_length=8,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate_new_password(self, value):
        """التحقق من كلمة المرور الجديدة"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """التحقق من تطابق كلمات المرور"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'كلمات المرور غير متطابقة'
            })
        return attrs


class WelcomeModalSerializer(serializers.Serializer):
    """
    Serializer لبيانات نافذة الترحيب
    """
    
    user_name = serializers.CharField(read_only=True)
    user_type = serializers.CharField(read_only=True)
    user_type_display = serializers.CharField(read_only=True)
    is_new_user = serializers.BooleanField(read_only=True)
    welcome_message = serializers.CharField(read_only=True)
    available_actions = serializers.ListField(read_only=True)
    
    def to_representation(self, instance):
        """تخصيص عرض البيانات"""
        user = instance
        
        # تحديد الرسالة الترحيبية
        if hasattr(user, '_is_new_registration') and user._is_new_registration:
            welcome_message = f"مرحباً بك في نائبك، {user.get_full_name()}! تم إنشاء حسابك بنجاح."
        else:
            welcome_message = f"أهلاً وسهلاً بك مرة أخرى، {user.get_full_name()}!"
        
        # تحديد الإجراءات المتاحة
        available_actions = [
            {
                'id': 'dashboard',
                'title': 'لوحة التحكم',
                'description': 'إدارة حسابك وإعداداتك الشخصية',
                'icon': 'dashboard',
                'url': '/dashboard/'
            },
            {
                'id': 'complaint',
                'title': 'تسجيل شكوى',
                'description': 'قدم شكوى أو اقتراح للمسؤولين',
                'icon': 'complaint',
                'url': '/complaints/new/'
            },
            {
                'id': 'candidates',
                'title': 'تصفح المرشحين',
                'description': 'استعرض المرشحين وبرامجهم الانتخابية',
                'icon': 'candidates',
                'url': '/candidates/'
            }
        ]
        
        return {
            'user_name': user.get_full_name(),
            'user_type': user.user_type,
            'user_type_display': user.get_user_type_display_ar(),
            'is_new_user': hasattr(user, '_is_new_registration') and user._is_new_registration,
            'welcome_message': welcome_message,
            'available_actions': available_actions
        }
