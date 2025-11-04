from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, UserProfile, OTP, OnboardingProgress


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'role')
        help_texts = {
            'role': 'Available roles: Operator, Manager, Franchisee, Admin'
        }


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'role', 'is_active', 'is_staff', 'is_superuser')
        help_texts = {
            'role': 'Available roles: Operator, Manager, Franchisee, Admin'
        }


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'role', 'is_staff', 'is_active', 'is_verified')
    list_filter = ('role', 'is_staff', 'is_active', 'is_superuser', 'is_verified')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('role', 'is_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_active', 'is_superuser'),
            'description': 'Available roles: Operator (default), Manager, Franchisee, Admin'}),
    )
    
    search_fields = ('email',)
    ordering = ('email',)
    readonly_fields = ('last_login',)
    filter_horizontal = ('groups', 'user_permissions',)

    def save_model(self, request, obj, form, change):
        """Ensure password is properly hashed when saving through admin"""
        if not change:  # Creating new user
            if form.cleaned_data.get('password1'):
                obj.set_password(form.cleaned_data['password1'])
        
        # Auto-verify admin users
        if obj.role == 'admin':
            obj.is_verified = True
            
        super().save_model(request, obj, form, change)

# Register CustomUser with proper admin
admin.site.register(CustomUser, CustomUserAdmin)

# Register other models
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_user_role', 'full_name', 'business_name', 'phone_number', 'country', 'joined_date')
    search_fields = ('user__email', 'full_name', 'business_name', 'phone_number', 'country', 'restaurant_address')
    list_filter = ('joined_date', 'user__role', 'country')
    readonly_fields = ('joined_date', 'updated_at')
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('full_name', 'phone_number', 'country')
        }),
        ('Business Information', {
            'fields': ('business_name', 'restaurant_address')
        }),
        ('Media', {
            'fields': ('profile_picture',)
        }),
        ('Timestamps', {
            'fields': ('joined_date', 'updated_at')
        }),
    )
    
    def get_user_role(self, obj):
        """Display user role in list view"""
        if obj.user:
            return obj.user.get_role_display()
        return '-'
    get_user_role.short_description = 'Role'
    get_user_role.admin_order_field = 'user__role'

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'created_at', 'attempts', 'is_expired_status')
    list_filter = ('created_at',)
    search_fields = ('email', 'otp')
    readonly_fields = ('created_at',)
    
    def is_expired_status(self, obj):
        """Show if OTP is expired"""
        return obj.is_expired()
    is_expired_status.short_description = 'Expired'
    is_expired_status.boolean = True


@admin.register(OnboardingProgress)
class OnboardingProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_user_role', 'owner_name', 'business_name', 'current_step', 'is_completed', 'created_at')
    list_filter = ('current_step', 'is_completed', 'is_franchise', 'service_model', 'time_zone', 'created_at', 'user__role')
    search_fields = ('user__email', 'owner_name', 'business_name', 'brand_name_dba', 'franchise_brand_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Progress Tracking', {
            'fields': ('current_step', 'is_completed', 'created_at', 'updated_at')
        }),
        ('Onboarding 1: Account Setup', {
            'fields': ('owner_name', 'brand_name_dba', 'email'),
            'classes': ('collapse',)
        }),
        ('Onboarding 2: Business Location', {
            'fields': ('business_name', 'address', 'time_zone', 'service_model'),
            'classes': ('collapse',)
        }),
        ('Onboarding 3: Franchise & Brand', {
            'fields': ('is_franchise', 'franchise_brand_name', 'locations_owned_operated', 'region_market'),
            'classes': ('collapse',)
        }),
        ('Onboarding 4: Menu Upload', {
            'fields': ('menu_url', 'menu_file'),
            'classes': ('collapse',)
        }),
        ('Onboarding 5: Sales & Baseline', {
            'fields': (
                'estimated_instore_sales_last_month', 
                'estimated_online_3p_sales_last_month',
                'estimated_instore_sales_last_12_months', 
                'estimated_online_3p_sales_last_12_months'
            ),
            'classes': ('collapse',)
        }),
        ('Onboarding 6: Labor & Staff', {
            'fields': ('foh_employees', 'boh_employees', 'pay_cadence'),
            'classes': ('collapse',)
        }),
        ('Onboarding 7: Documents', {
            'fields': ('document_file',),
            'classes': ('collapse',)
        }),
        ('Onboarding 8: Marketing & Policies', {
            'fields': ('monthly_marketing_budget', 'key_policies'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_role(self, obj):
        """Display user role in list view"""
        if obj.user:
            return obj.user.get_role_display()
        return '-'
    get_user_role.short_description = 'User Role'
    get_user_role.admin_order_field = 'user__role'