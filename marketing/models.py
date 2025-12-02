from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class MarketingDashboard(models.Model):
    """
    Dashboard data for Marketing Manager users
    Data extracted from uploaded documents via AI
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='marketing_dashboards'
    )
    date = models.DateField(auto_now_add=True)
    weekly_sales = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    customer_satisfaction = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage (0-100)"
    )
    cost_efficiency = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage (0-100)"
    )
    
    # AI extraction metadata
    source_document = models.FileField(
        upload_to="marketing/documents/%Y/%m/",
        blank=True,
        null=True,
        help_text="Document uploaded by user for AI extraction"
    )
    extracted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Marketing Dashboard"
        verbose_name_plural = "Marketing Dashboards"
        ordering = ['-date']
    
    def __str__(self):
        return f"Dashboard - {self.user.email} - {self.date}"


class MarketingReport(models.Model):
    """
    Reports data for Marketing Manager users
    Data extracted from uploaded documents via AI
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='marketing_reports'
    )
    date = models.DateField(auto_now_add=True)
    weekly_sales = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    cost_efficiency = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage (0-100)"
    )
    staff_performance_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score (0-100)"
    )
    customer_satisfaction = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage (0-100)"
    )
    
    # AI extraction metadata
    source_document = models.FileField(
        upload_to="marketing/reports/%Y/%m/",
        blank=True,
        null=True,
        help_text="Document uploaded by user for AI extraction"
    )
    extracted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Marketing Report"
        verbose_name_plural = "Marketing Reports"
        ordering = ['-date']
    
    def __str__(self):
        return f"Report - {self.user.email} - {self.date}"


class TeamPerformanceBreakdown(models.Model):
    """
    Team & Performance breakdown for Marketing Manager users
    Data extracted from uploaded documents via AI
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_performance_breakdowns'
    )
    date = models.DateField(auto_now_add=True)
    staff_attendance = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    sales_performance = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Performance score (0-100)"
    )
    inventory_status = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Status percentage (0-100)"
    )
    issues_complaints = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # AI extraction metadata
    source_document = models.FileField(
        upload_to="marketing/team_performance/%Y/%m/",
        blank=True,
        null=True,
        help_text="Document uploaded by user for AI extraction"
    )
    extracted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Team & Performance Breakdown"
        verbose_name_plural = "Team & Performance Breakdowns"
        ordering = ['-date']
    
    def __str__(self):
        return f"Team Performance - {self.user.email} - {self.date}"


class StaffOpsBreakdown(models.Model):
    """
    Staff & Ops breakdown for Marketing Manager users
    Data extracted from uploaded documents via AI
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_ops_breakdowns'
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
        upload_to="marketing/staff_ops_breakdown/%Y/%m/",
        blank=True,
        null=True,
        help_text="Document uploaded by user for AI extraction"
    )
    extracted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Staff & Ops Breakdown"
        verbose_name_plural = "Staff & Ops Breakdowns"
        ordering = ['-date', '-amount']
    
    def __str__(self):
        return f"Staff Ops - {self.category} - {self.user.email} - {self.date}"
