from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_verified', True)  # Auto-verify admin users
        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('operations', 'Operations'),
        ('marketing manager', 'Marketing Manager'),
        ('executive', 'Executive'),
        ('admin', 'Admin'),
    )
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLES, default='operations')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        # Auto-verify admin users
        if self.role == 'admin':
            self.is_verified = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role})"

class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)

    def __str__(self):
        return f'OTP for {self.email}: {self.otp}'

    def save(self, *args, **kwargs):
        with transaction.atomic():
            OTP.objects.filter(email=self.email).delete()
            super().save(*args, **kwargs)

    def is_expired(self):
        from django.utils import timezone
        return (timezone.now() - self.created_at).seconds > 600

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_profile'
    )
    
    # Personal Information
    full_name = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile/%Y/%m/", 
        blank=True, 
        null=True,
        help_text="Profile picture (max 5MB)"
    )
    
    # Business Information  
    business_name = models.CharField(max_length=200, blank=True, null=True)
    restaurant_address = models.TextField(blank=True, null=True, help_text="Full restaurant address")
    
    # Timestamps
    joined_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        if self.user:
            if self.full_name:
                return f"{self.full_name} ({self.user.email})"
            return self.user.email
        return "No User"


class OnboardingProgress(models.Model):
    TIME_ZONE_CHOICES = (
        ('America/Los_Angeles', 'America/Los_Angeles'),
        ('America/Denver', 'America/Denver'), 
        ('America/Chicago', 'America/Chicago'),
        ('America/New_York', 'America/New_York'),
    )
    
    SERVICE_MODEL_CHOICES = (
        ('QSR', 'QSR'),
        ('Fast Casual', 'Fast Casual'),
        ('Full Service', 'Full Service'),
        ('Cafe', 'Cafe'),
        ('Bar', 'Bar'),
        ('Catering', 'Catering'),
        ('Ghost Kitchen', 'Ghost Kitchen'),
    )
    
    FRANCHISE_CHOICES = (
        ('YES', 'YES'),
        ('NO', 'NO'),
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='onboarding_progress'
    )
    
    # Onboarding 1: Account Setup
    owner_name = models.CharField(max_length=200, blank=True, null=True)
    brand_name_dba = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Onboarding 2: Business Location
    business_name = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    time_zone = models.CharField(max_length=50, choices=TIME_ZONE_CHOICES, blank=True, null=True)
    service_model = models.CharField(max_length=50, choices=SERVICE_MODEL_CHOICES, blank=True, null=True)
    
    # Onboarding 3: Franchise & Brand
    is_franchise = models.CharField(max_length=3, choices=FRANCHISE_CHOICES, blank=True, null=True)
    franchise_brand_name = models.CharField(max_length=200, blank=True, null=True)
    locations_owned_operated = models.TextField(blank=True, null=True)
    region_market = models.CharField(max_length=200, blank=True, null=True)
    
    # Onboarding 4: Menu Upload
    menu_url = models.URLField(blank=True, null=True)
    menu_file = models.FileField(
        upload_to="onboarding/menus/%Y/%m/", 
        blank=True, 
        null=True,
        help_text="Menu file upload"
    )
    
    # Onboarding 5: Sales & Baseline
    estimated_instore_sales_last_month = models.PositiveIntegerField(blank=True, null=True)
    estimated_online_3p_sales_last_month = models.PositiveIntegerField(blank=True, null=True)
    estimated_instore_sales_last_12_months = models.PositiveIntegerField(blank=True, null=True)
    estimated_online_3p_sales_last_12_months = models.PositiveIntegerField(blank=True, null=True)
    
    # Onboarding 6: Labor & Staff
    foh_employees = models.TextField(blank=True, null=True)
    boh_employees = models.TextField(blank=True, null=True)
    pay_cadence = models.TextField(blank=True, null=True)
    
    # Onboarding 7: Documents
    document_file = models.FileField(
        upload_to="onboarding/documents/%Y/%m/", 
        blank=True, 
        null=True,
        help_text="Document file upload"
    )
    
    # Onboarding 8: Marketing & Policies
    monthly_marketing_budget = models.PositiveIntegerField(blank=True, null=True)
    key_policies = models.TextField(blank=True, null=True)
    
    # Onboarding 9: Completion
    is_completed = models.BooleanField(default=False)
    current_step = models.PositiveIntegerField(default=1)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Onboarding Progress for {self.user.email} - Step {self.current_step}"
    
    class Meta:
        verbose_name = "Onboarding Progress"
        verbose_name_plural = "Onboarding Progresses"


# Signal to clean up profile picture when UserProfile is deleted
@receiver(post_delete, sender=UserProfile)
def delete_profile_picture(sender, instance, **kwargs):
    """Delete profile picture file when UserProfile is deleted"""
    if instance.profile_picture:
        if os.path.isfile(instance.profile_picture.path):
            os.remove(instance.profile_picture.path)

# Signal to clean up files when OnboardingProgress is deleted
@receiver(post_delete, sender=OnboardingProgress)
def delete_onboarding_files(sender, instance, **kwargs):
    """Delete uploaded files when OnboardingProgress is deleted"""
    if instance.menu_file:
        if os.path.isfile(instance.menu_file.path):
            os.remove(instance.menu_file.path)
    
    if instance.document_file:
        if os.path.isfile(instance.document_file.path):
            os.remove(instance.document_file.path)


class UserDocument(models.Model):
    """
    Document management for all users
    Users can upload documents with metadata
    """
    DOCUMENT_TYPES = (
        ('all', 'All'),
        ('operations', 'Operations'),
        ('compliance', 'Compliance'),
        ('finance', 'Finance'),
        ('legal', 'Legal'),
        ('hr_staff', 'HR/Staff'),
    )
    
    FILE_FORMATS = (
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
        ('docs', 'Docs'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    file_name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file_format = models.CharField(max_length=10, choices=FILE_FORMATS)
    file = models.FileField(
        upload_to="user_documents/%Y/%m/",
        help_text="Upload your document"
    )
    file_size = models.BigIntegerField(help_text="File size in bytes")
    upload_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Document"
        verbose_name_plural = "User Documents"
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.file_name} - {self.user.email}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class Subscription(models.Model):
    """
    Subscription plans for users
    Three tiers: Starter, Professional, Enterprise
    """
    PLAN_CHOICES = (
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='starter')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_trial = models.BooleanField(default=False)
    auto_renew = models.BooleanField(default=False)
    
    # Stripe integration fields
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True, help_text="Stripe Price ID")
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, help_text="Stripe Checkout Session ID")
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True, help_text="Stripe Payment Intent ID")
    
    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.user.email} - {self.plan} ({self.status})"
    
    def is_active(self):
        from django.utils import timezone
        return self.status == 'active' and self.end_date > timezone.now()


class CalendarEvent(models.Model):
    """
    Calendar events for all users
    Users can create, view, and manage events
    """
    EVENT_TYPES = (
        ('meeting', 'Meeting'),
        ('reminder', 'Reminder'),
        ('task', 'Task'),
        ('appointment', 'Appointment'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calendar_events'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, null=True)
    is_all_day = models.BooleanField(default=False)
    reminder_minutes = models.IntegerField(
        default=15,
        help_text="Reminder time in minutes before event"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Calendar Event"
        verbose_name_plural = "Calendar Events"
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.title} - {self.user.email} - {self.start_date}"


# Signal to clean up document file when UserDocument is deleted
@receiver(post_delete, sender=UserDocument)
def delete_user_document(sender, instance, **kwargs):
    """Delete document file when UserDocument is deleted"""
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)