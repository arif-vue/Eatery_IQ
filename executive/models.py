from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class ExecutiveDashboard(models.Model):
    """
    Dashboard data for Executive users
    Data extracted from uploaded documents via AI
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='executive_dashboards'
    )
    date = models.DateField(auto_now_add=True)
    total_sales_revenue = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    net_profit = models.IntegerField(default=0)
    store_growth_comparison = models.IntegerField(
        default=0,
        help_text="Growth percentage comparison"
    )
    
    # AI extraction metadata
    source_document = models.FileField(
        upload_to="executive/documents/%Y/%m/",
        blank=True,
        null=True,
        help_text="Document uploaded by user for AI extraction"
    )
    extracted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Executive Dashboard"
        verbose_name_plural = "Executive Dashboards"
        ordering = ['-date']
    
    def __str__(self):
        return f"Dashboard - {self.user.email} - {self.date}"


class ExecutiveReport(models.Model):
    """
    Reports data for Executive users
    Data extracted from uploaded documents via AI
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='executive_reports'
    )
    date = models.DateField(auto_now_add=True)
    total_revenue = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_outlets = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    branches_meeting_sales_target = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    active_promotions = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # AI extraction metadata
    source_document = models.FileField(
        upload_to="executive/reports/%Y/%m/",
        blank=True,
        null=True,
        help_text="Document uploaded by user for AI extraction"
    )
    extracted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Executive Report"
        verbose_name_plural = "Executive Reports"
        ordering = ['-date']
    
    def __str__(self):
        return f"Report - {self.user.email} - {self.date}"


class BusinessHealthBreakdown(models.Model):
    """
    Business health breakdown for Executive users
    Data extracted from uploaded documents via AI
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business_health_breakdowns'
    )
    date = models.DateField(auto_now_add=True)
    sales_revenue = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    expenses_costs = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    marketing_campaigns_roi = models.IntegerField(
        default=0,
        help_text="Return on Investment percentage"
    )
    risk_loss = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # AI extraction metadata
    source_document = models.FileField(
        upload_to="executive/business_health/%Y/%m/",
        blank=True,
        null=True,
        help_text="Document uploaded by user for AI extraction"
    )
    extracted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Business Health Breakdown"
        verbose_name_plural = "Business Health Breakdowns"
        ordering = ['-date']
    
    def __str__(self):
        return f"Business Health - {self.user.email} - {self.date}"


class FinancialPerformanceBreakdown(models.Model):
    """
    Financial performance breakdown for Executive users
    Data extracted from uploaded documents via AI
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='executive_financial_breakdowns'
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
        upload_to="executive/financial_breakdown/%Y/%m/",
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
