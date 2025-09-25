# -*- coding: utf-8 -*-
"""
مسلسلات البيانات لخدمة المصادقة - نائبك
Data Serializers for Naebak Authentication Service
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, CitizenProfile, CandidateProfile, CurrentMemberProfile, Governorate, Party


class UserRegistrationSerializer(serializers.ModelSerializer):
    """مسلسل تسجيل المستخدم الجديد"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirmation = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone_number', 
            'user_type', 'password', 'password_confirmation'
        ]
    
    def validate(self, attrs):
        """التحقق من صحة البيانات"""
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError("كلمات المرور غير متطابقة")
        return attrs
    
    def create(self, validated_data):
        """إنشاء مستخدم جديد"""
        validated_data.pop('password_confirmation')
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """مسلسل تسجيل الدخول"""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """مسلسل ملف المستخدم الأساسي"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    verification_status_display = serializers.CharField(source='get_verification_status_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'user_type', 'user_type_display',
            'verification_status', 'verification_status_display',
            'last_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined', 'last_active']


class GovernorateSerializer(serializers.ModelSerializer):
    """مسلسل المحافظات"""
    
    class Meta:
        model = Governorate
        fields = ['id', 'name', 'name_en', 'code']


class PartySerializer(serializers.ModelSerializer):
    """مسلسل الأحزاب"""
    
    class Meta:
        model = Party
        fields = ['id', 'name', 'name_en', 'abbreviation']


class CitizenProfileSerializer(serializers.ModelSerializer):
    """مسلسل ملف المواطن"""
    
    user = UserProfileSerializer(read_only=True)
    governorate = GovernorateSerializer(read_only=True)
    governorate_id = serializers.IntegerField(write_only=True)
    full_address = serializers.CharField(source='get_full_address', read_only=True)
    display_name = serializers.CharField(source='get_display_name', read_only=True)
    
    class Meta:
        model = CitizenProfile
        fields = [
            'id', 'user', 'governorate', 'governorate_id', 'city', 'district',
            'street_address', 'postal_code', 'full_address', 'display_name',
            'national_id', 'gender', 'birth_date', 'marital_status',
            'whatsapp_number', 'occupation', 'education_level', 'profile_picture',
            'show_phone_public', 'show_address_public', 'allow_messages',
            'is_verified', 'verification_method', 'created_at', 'updated_at',
            'messages_sent', 'complaints_submitted', 'ratings_given'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'messages_sent', 
            'complaints_submitted', 'ratings_given'
        ]
    
    def validate_national_id(self, value):
        """التحقق من صحة الرقم القومي"""
        if len(value) != 14 or not value.isdigit():
            raise serializers.ValidationError("الرقم القومي يجب أن يكون 14 رقم")
        return value
    
    def validate_governorate_id(self, value):
        """التحقق من وجود المحافظة"""
        try:
            Governorate.objects.get(id=value)
        except Governorate.DoesNotExist:
            raise serializers.ValidationError("المحافظة غير موجودة")
        return value


class CandidateProfileSerializer(serializers.ModelSerializer):
    """مسلسل ملف المرشح"""
    
    user = UserProfileSerializer(read_only=True)
    governorate = GovernorateSerializer(read_only=True)
    governorate_id = serializers.IntegerField(write_only=True)
    party = PartySerializer(read_only=True)
    party_id = serializers.IntegerField(write_only=True)
    membership_description = serializers.CharField(source='get_membership_description', read_only=True)
    electoral_info = serializers.CharField(source='get_electoral_info', read_only=True)
    
    class Meta:
        model = CandidateProfile
        fields = [
            'id', 'user', 'governorate', 'governorate_id', 'city', 'district',
            'street_address', 'national_id', 'gender', 'birth_date', 'marital_status',
            'council_type', 'party', 'party_id', 'constituency', 'electoral_number',
            'electoral_symbol', 'whatsapp_number', 'bio', 'electoral_program',
            'education', 'occupation', 'experience', 'profile_picture', 'banner_image',
            'cv_document', 'campaign_slogan', 'campaign_website', 'campaign_facebook',
            'campaign_twitter', 'is_approved', 'approval_date', 'approved_by',
            'rating_average', 'rating_count', 'messages_received', 'complaints_assigned',
            'complaints_solved', 'created_at', 'updated_at', 'membership_description',
            'electoral_info'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'is_approved', 'approval_date',
            'approved_by', 'rating_average', 'rating_count', 'messages_received',
            'complaints_assigned', 'complaints_solved'
        ]
    
    def validate_national_id(self, value):
        """التحقق من صحة الرقم القومي"""
        if len(value) != 14 or not value.isdigit():
            raise serializers.ValidationError("الرقم القومي يجب أن يكون 14 رقم")
        return value
    
    def validate_governorate_id(self, value):
        """التحقق من وجود المحافظة"""
        try:
            Governorate.objects.get(id=value)
        except Governorate.DoesNotExist:
            raise serializers.ValidationError("المحافظة غير موجودة")
        return value
    
    def validate_party_id(self, value):
        """التحقق من وجود الحزب"""
        try:
            Party.objects.get(id=value)
        except Party.DoesNotExist:
            raise serializers.ValidationError("الحزب غير موجود")
        return value


class CurrentMemberProfileSerializer(serializers.ModelSerializer):
    """مسلسل ملف العضو الحالي"""
    
    user = UserProfileSerializer(read_only=True)
    governorate = GovernorateSerializer(read_only=True)
    governorate_id = serializers.IntegerField(write_only=True)
    party = PartySerializer(read_only=True)
    party_id = serializers.IntegerField(write_only=True)
    membership_description = serializers.CharField(source='get_membership_description', read_only=True)
    
    class Meta:
        model = CurrentMemberProfile
        fields = [
            'id', 'user', 'governorate', 'governorate_id', 'city', 'district',
            'street_address', 'national_id', 'gender', 'birth_date', 'marital_status',
            'council_type', 'party', 'party_id', 'constituency', 'membership_start_date',
            'term_number', 'seat_number', 'committees', 'positions', 'whatsapp_number',
            'bio', 'achievements', 'education', 'occupation', 'experience',
            'profile_picture', 'banner_image', 'official_cv', 'office_address',
            'office_phone', 'office_hours', 'rating_average', 'rating_count',
            'messages_received', 'complaints_handled', 'complaints_solved',
            'created_at', 'updated_at', 'membership_description'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'rating_average', 'rating_count',
            'messages_received', 'complaints_handled', 'complaints_solved'
        ]
    
    def validate_national_id(self, value):
        """التحقق من صحة الرقم القومي"""
        if len(value) != 14 or not value.isdigit():
            raise serializers.ValidationError("الرقم القومي يجب أن يكون 14 رقم")
        return value
    
    def validate_governorate_id(self, value):
        """التحقق من وجود المحافظة"""
        try:
            Governorate.objects.get(id=value)
        except Governorate.DoesNotExist:
            raise serializers.ValidationError("المحافظة غير موجودة")
        return value
    
    def validate_party_id(self, value):
        """التحقق من وجود الحزب"""
        try:
            Party.objects.get(id=value)
        except Party.DoesNotExist:
            raise serializers.ValidationError("الحزب غير موجود")
        return value
