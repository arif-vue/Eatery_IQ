from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class OperationDashboard(models.Model):
    """
    Dashboard data for Operations users
    Data extracted from uploaded documents via AI
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='operation_dashboards'
    )
    date = models.DateField(auto_now_add=True)
    today_sales = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    staff_attendance = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    labor_cost_vs_budget = models.IntegerField(default=0)
    
    # AI extraction metadata
    source_document = models.FileField(
        upload_to="operations/documents/%Y/%m/",
        blank=True,
        null=True,
        help_text="Document uploaded by user for AI extraction"
    )
    extracted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Operation Dashboard"
        verbose_name_plural = "Operation Dashboards"
        ordering = ['-date']
    
    def __str__(self):
        return f"Dashboard - {self.user.email} - {self.date}"


class OperationReport(models.Model):
    """
    Reports data for Operations users
    Data extracted from uploaded documents via AI
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='operation_reports'
    )
    date = models.DateField(auto_now_add=True)
    today_sales = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    order_completed = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    delivery_on_time_rate = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage (0-100)"
    )
    shift_attendance = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # AI extraction metadata
    source_document = models.FileField(
        upload_to="operations/reports/%Y/%m/",
        blank=True,
        null=True,
        help_text="Document uploaded by user for AI extraction"
    )
    extracted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Operation Report"
        verbose_name_plural = "Operation Reports"
        ordering = ['-date']
    
    def __str__(self):
        return f"Report - {self.user.email} - {self.date}"


class DailyOperationBreakdown(models.Model):
    """
    Daily operation breakdown for Operations users
    Data extracted from uploaded documents via AI
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_operation_breakdowns'
    )
    date = models.DateField(auto_now_add=True)
    in_store_orders = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    online_orders = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    third_party_delivery = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="3PD - Third Party Delivery"
    )
    discounts_and_refunds = models.IntegerField(default=0)
    
    # AI extraction metadata
    source_document = models.FileField(
        upload_to="operations/daily_breakdown/%Y/%m/",
        blank=True,
        null=True,
        help_text="Document uploaded by user for AI extraction"
    )
    extracted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Daily Operation Breakdown"
        verbose_name_plural = "Daily Operation Breakdowns"
        ordering = ['-date']
    
    def __str__(self):
        return f"Daily Breakdown - {self.user.email} - {self.date}"


class FinancialPerformanceBreakdown(models.Model):
    """
    Financial performance breakdown for Operations users
    Data extracted from uploaded documents via AI
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='financial_performance_breakdowns'
    )
    date = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=200)
    source = models.CharField(max_length=200)
    amount = models.IntegerField(default=0)
    percentage_of_total = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of total (0-100)"
    )
    
    # AI extraction metadata
    source_document = models.FileField(
        upload_to="operations/financial_breakdown/%Y/%m/",
        blank=True,
        null=True,
        help_text="Document uploaded by user for AI extraction"
    )
    extracted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Financial Performance Breakdown"
        verbose_name_plural = "Financial Performance Breakdowns"
        ordering = ['-date', '-amount']
    
    def __str__(self):
        return f"Financial - {self.category} - {self.user.email} - {self.date}"
