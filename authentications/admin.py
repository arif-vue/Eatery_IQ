from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import (
    CustomUser, UserProfile, OTP, OnboardingProgress,
    UserDocument, Subscription, CalendarEvent
)


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


@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'file_name', 'document_type', 'file_format',
        'file_size_display', 'upload_date'
    )
    list_filter = ('document_type', 'file_format', 'upload_date', 'user__role')
    search_fields = ('user__email', 'file_name', 'document_type')
    readonly_fields = ('upload_date', 'updated_at', 'file_size')
    ordering = ('-upload_date',)
    date_hierarchy = 'upload_date'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Document Details', {
            'fields': ('file_name', 'document_type', 'file_format', 'file')
        }),
        ('Metadata', {
            'fields': ('file_size', 'upload_date', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_size_display(self, obj):
        """Display file size in MB"""
        if obj.file_size:
            size_mb = obj.file_size / (1024 * 1024)
            return f"{size_mb:.2f} MB"
        return "0 MB"
    file_size_display.short_description = 'File Size'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'plan', 'price', 'status',
        'start_date', 'end_date', 'is_trial', 'auto_renew', 'days_left'
    )
    list_filter = ('plan', 'status', 'is_trial', 'auto_renew', 'start_date')
    search_fields = ('user__email', 'plan')
    readonly_fields = ('start_date',)
    ordering = ('-start_date',)
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Subscription Details', {
            'fields': ('plan', 'price', 'status', 'is_trial', 'auto_renew')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date')
        }),
    )
    
    def days_left(self, obj):
        """Display days remaining in subscription"""
        from django.utils import timezone
        if obj.status == 'active' and obj.end_date > timezone.now():
            delta = obj.end_date - timezone.now()
            return f"{delta.days} days"
        return "Expired"
    days_left.short_description = 'Days Left'


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'title', 'event_type', 'start_date',
        'end_date', 'is_all_day', 'created_at'
    )
    list_filter = ('event_type', 'is_all_day', 'start_date', 'user__role')
    search_fields = ('user__email', 'title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('start_date',)
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Event Details', {
            'fields': ('title', 'description', 'event_type', 'location')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'is_all_day', 'reminder_minutes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )