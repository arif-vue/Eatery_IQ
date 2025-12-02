from rest_framework import serializers
from .models import CustomUser, OTP, UserProfile, OnboardingProgress
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_verified', 'user_profile',]
        read_only_fields = ['id', 'is_active', 'is_staff', 'is_superuser']

    def get_user_profile(self, obj):
        try:
            profile = obj.user_profile
            return UserProfileSerializer(profile).data
        except UserProfile.DoesNotExist:
            return None

class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True)
    full_name = serializers.CharField(write_only=True, required=True)
    business_name = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(choices=['operations', 'marketing manager', 'executive'], required=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'confirm_password', 'role', 'full_name', 'business_name']
        extra_kwargs = {
            'email': {'required': True},
            'password': {'required': True}
        }

    def validate(self, data):
        errors = {}
        
        # Required field validation
        if not data.get('email'):
            errors['email'] = ['This field is required']
        if not data.get('password'):
            errors['password'] = ['This field is required']
        if not data.get('confirm_password'):
            errors['confirm_password'] = ['This field is required']
        if not data.get('full_name'):
            errors['full_name'] = ['This field is required']
        if not data.get('business_name'):
            errors['business_name'] = ['This field is required']
        if not data.get('role'):
            errors['role'] = ['This field is required']
        
        # Password match validation
        if data.get('password') and data.get('confirm_password'):
            if data['password'] != data['confirm_password']:
                errors['confirm_password'] = ['Passwords do not match']
        
        # Email uniqueness validation
        if data.get('email') and User.objects.filter(email=data['email'], is_verified=True).exists():
            errors['email'] = ['A user with this email already exists']
        
        # Role validation - block 'admin' role during registration
        if data.get('role') and data.get('role') not in ['operations', 'marketing manager', 'executive']:
            errors['role'] = ['Only operations, marketing manager, and executive roles are allowed during registration']
        
        if errors:
            raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        business_name = validated_data.pop('business_name')
        validated_data.pop('confirm_password')  # Remove confirm_password as it's not needed
        
        received_role = validated_data.get('role', 'operations')
        
        # Delete any unverified users with same email
        User.objects.filter(email=validated_data['email'], is_verified=False).delete()
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=received_role
        )
        
        # Create user profile with full_name and business_name
        UserProfile.objects.create(
            user=user, 
            full_name=full_name, 
            business_name=business_name
        )
        return user

class OTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)

    class Meta:
        model = OTP
        fields = ['id', 'email', 'otp', 'created_at', 'attempts']
        read_only_fields = ['id', 'created_at', 'attempts']

    def validate(self, data):
        errors = {}
        if not data.get('email'):
            errors['email'] = ['This field is required']
        if not data.get('otp'):
            errors['otp'] = ['This field is required']
        if errors:
            raise serializers.ValidationError(errors)
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'email', 'role', 'full_name', 'phone_number', 
            'country', 'profile_picture', 'profile_picture_url', 
            'business_name', 'restaurant_address', 'joined_date', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'role', 'joined_date', 'updated_at', 'profile_picture_url']

    def get_profile_picture_url(self, obj):
        """Return full URL for profile picture"""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and len(value.strip()) > 0:
            # Basic phone number validation - adjust regex as needed
            import re
            pattern = r'^[\+]?[1-9][\d]{0,15}$'
            if not re.match(pattern, value.replace(' ', '').replace('-', '')):
                raise serializers.ValidationError("Enter a valid phone number")
        return value

    def validate_profile_picture(self, value):
        """Validate profile picture size and format"""
        if value:
            # Check file size (5MB limit)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Image size cannot exceed 5MB")
            
            # Check file format
            allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if value.content_type not in allowed_formats:
                raise serializers.ValidationError("Only JPEG, PNG, and WebP images are allowed")
        
        return value

    def validate(self, data):
        """Additional validation for profile data"""
        errors = {}
        
        # Validate full name if provided
        if 'full_name' in data:
            full_name = data['full_name']
            if full_name and len(full_name.strip()) < 2:
                errors['full_name'] = ['Full name must be at least 2 characters long']
            elif full_name and len(full_name.strip()) > 200:
                errors['full_name'] = ['Full name cannot exceed 200 characters']
        
        # Validate country if provided
        if 'country' in data:
            country = data['country']
            if country and len(country.strip()) > 100:
                errors['country'] = ['Country name cannot exceed 100 characters']
        
        # Validate business name if provided
        if 'business_name' in data:
            business_name = data['business_name']
            if business_name and len(business_name.strip()) > 200:
                errors['business_name'] = ['Business name cannot exceed 200 characters']
        
        # Validate restaurant address if provided
        if 'restaurant_address' in data:
            address = data['restaurant_address']
            if address and len(address.strip()) > 1000:
                errors['restaurant_address'] = ['Restaurant address cannot exceed 1000 characters']
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        errors = {}
        email = data.get('email')
        password = data.get('password')

        if not email:
            errors['email'] = ['This field is required']
        if not password:
            errors['password'] = ['This field is required']
        if errors:
            raise serializers.ValidationError(errors)

        user = authenticate(email=email, password=password)
        if not user:
            errors['credentials'] = ['Invalid email or password']
            raise serializers.ValidationError(errors)
        if not user.is_active:
            errors['credentials'] = ['Account not verified. Please verify your email with the OTP sent']
            raise serializers.ValidationError(errors)
        return user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        errors = {}
        
        if not data.get('email'):
            errors['email'] = ['This field is required']
        if not data.get('otp'):
            errors['otp'] = ['This field is required']
        if not data.get('new_password'):
            errors['new_password'] = ['This field is required']
        if not data.get('confirm_password'):
            errors['confirm_password'] = ['This field is required']
        
        # Password match validation
        if data.get('new_password') and data.get('confirm_password'):
            if data['new_password'] != data['confirm_password']:
                errors['confirm_password'] = ['Passwords do not match']
        
        if errors:
            raise serializers.ValidationError(errors)
        return data


class OnboardingProgressSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    menu_file_url = serializers.SerializerMethodField()
    document_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = OnboardingProgress
        fields = [
            'id', 'user_email', 'current_step', 'is_completed',
            # Onboarding 1: Account Setup
            'owner_name', 'brand_name_dba', 'email',
            # Onboarding 2: Business Location
            'business_name', 'address', 'time_zone', 'service_model',
            # Onboarding 3: Franchise & Brand
            'is_franchise', 'franchise_brand_name', 'locations_owned_operated', 'region_market',
            # Onboarding 4: Menu Upload
            'menu_url', 'menu_file', 'menu_file_url',
            # Onboarding 5: Sales & Baseline
            'estimated_instore_sales_last_month', 'estimated_online_3p_sales_last_month',
            'estimated_instore_sales_last_12_months', 'estimated_online_3p_sales_last_12_months',
            # Onboarding 6: Labor & Staff
            'foh_employees', 'boh_employees', 'pay_cadence',
            # Onboarding 7: Documents
            'document_file', 'document_file_url',
            # Onboarding 8: Marketing & Policies
            'monthly_marketing_budget', 'key_policies',
            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_email', 'created_at', 'updated_at', 'menu_file_url', 'document_file_url']

    def get_menu_file_url(self, obj):
        """Return full URL for menu file"""
        if obj.menu_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.menu_file.url)
            return obj.menu_file.url
        return None

    def get_document_file_url(self, obj):
        """Return full URL for document file"""
        if obj.document_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.document_file.url)
            return obj.document_file.url
        return None

    def validate_menu_file(self, value):
        """Validate menu file size and format"""
        if value:
            # Check file size (10MB limit for menu files)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("Menu file size cannot exceed 10MB")
            
            # Check file format
            allowed_formats = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if value.content_type not in allowed_formats:
                raise serializers.ValidationError("Only PDF, JPEG, PNG, and WebP files are allowed for menu upload")
        
        return value

    def validate_document_file(self, value):
        """Validate document file size and format"""
        if value:
            # Check file size (15MB limit for documents)
            if value.size > 15 * 1024 * 1024:
                raise serializers.ValidationError("Document file size cannot exceed 15MB")
            
            # Check file format - allow more formats for documents
            allowed_formats = [
                'application/pdf', 'application/msword', 
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'image/jpeg', 'image/jpg', 'image/png', 'image/webp'
            ]
            if value.content_type not in allowed_formats:
                raise serializers.ValidationError("Only PDF, DOC, DOCX, JPEG, PNG, and WebP files are allowed for document upload")
        
        return value

    def validate_menu_url(self, value):
        """Validate menu URL format"""
        if value:
            import re
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            if not url_pattern.match(value):
                raise serializers.ValidationError("Enter a valid URL")
        
        return value

    def validate(self, data):
        """Additional validation for onboarding data"""
        errors = {}
        
        # Validate franchise-related fields
        if data.get('is_franchise') == 'YES':
            if 'franchise_brand_name' in data and not data.get('franchise_brand_name'):
                errors['franchise_brand_name'] = ['This field is required when franchise is YES']
            if 'locations_owned_operated' in data and not data.get('locations_owned_operated'):
                errors['locations_owned_operated'] = ['This field is required when franchise is YES']
            if 'region_market' in data and not data.get('region_market'):
                errors['region_market'] = ['This field is required when franchise is YES']
        
        # Validate step completion logic
        current_step = data.get('current_step', 1)
        if current_step < 1 or current_step > 9:
            errors['current_step'] = ['Current step must be between 1 and 9']
        
        # Validate email field if provided
        if 'email' in data and data.get('email'):
            from django.core.validators import validate_email
            try:
                validate_email(data['email'])
            except:
                errors['email'] = ['Enter a valid email address']
        
        # Validate integer fields
        integer_fields = [
            'estimated_instore_sales_last_month', 
            'estimated_online_3p_sales_last_month',
            'estimated_instore_sales_last_12_months', 
            'estimated_online_3p_sales_last_12_months',
            'monthly_marketing_budget'
        ]
        
        for field in integer_fields:
            if field in data and data.get(field) is not None:
                if data[field] < 0:
                    errors[field] = ['This value cannot be negative']
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data

    def create(self, validated_data):
        """Create onboarding progress for the authenticated user"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update onboarding progress"""
        # Mark as completed if current_step is 9 and user is updating
        if validated_data.get('current_step') == 9:
            validated_data['is_completed'] = True
        
        return super().update(instance, validated_data)