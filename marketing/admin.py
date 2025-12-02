from django.contrib import admin
from .models import (
    MarketingDashboard,
    MarketingReport,
    TeamPerformanceBreakdown,
    StaffOpsBreakdown
)


@admin.register(MarketingDashboard)
class MarketingDashboardAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'date', 'weekly_sales',
        'customer_satisfaction', 'cost_efficiency', 'extracted_at'
    )
    list_filter = ('date', 'extracted_at', 'user')
    search_fields = ('user__email', 'user__user_profile__full_name')
    readonly_fields = ('extracted_at', 'updated_at')
    ordering = ('-date', '-extracted_at')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Dashboard Metrics', {
            'fields': (
                'weekly_sales',
                'customer_satisfaction',
                'cost_efficiency'
            )
        }),
        ('AI Extraction Data', {
            'fields': ('source_document', 'extracted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MarketingReport)
class MarketingReportAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'date', 'weekly_sales', 'cost_efficiency',
        'staff_performance_score', 'customer_satisfaction', 'extracted_at'
    )
    list_filter = ('date', 'extracted_at', 'user')
    search_fields = ('user__email', 'user__user_profile__full_name')
    readonly_fields = ('extracted_at', 'updated_at')
    ordering = ('-date', '-extracted_at')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Report Metrics', {
            'fields': (
                'weekly_sales',
                'cost_efficiency',
                'staff_performance_score',
                'customer_satisfaction'
            )
        }),
        ('AI Extraction Data', {
            'fields': ('source_document', 'extracted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TeamPerformanceBreakdown)
class TeamPerformanceBreakdownAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'date', 'staff_attendance', 'sales_performance',
        'inventory_status', 'issues_complaints', 'extracted_at'
    )
    list_filter = ('date', 'extracted_at', 'user')
    search_fields = ('user__email', 'user__user_profile__full_name')
    readonly_fields = ('extracted_at', 'updated_at')
    ordering = ('-date', '-extracted_at')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Team Performance Metrics', {
            'fields': (
                'staff_attendance',
                'sales_performance',
                'inventory_status',
                'issues_complaints'
            )
        }),
        ('AI Extraction Data', {
            'fields': ('source_document', 'extracted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StaffOpsBreakdown)
class StaffOpsBreakdownAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'date', 'category', 'source',
        'amount', 'percentage_of_total', 'extracted_at'
    )
    list_filter = ('date', 'category', 'source', 'extracted_at', 'user')
    search_fields = (
        'user__email', 'user__user_profile__full_name',
        'category', 'source'
    )
    readonly_fields = ('extracted_at', 'updated_at')
    ordering = ('-date', '-amount')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Staff & Ops Breakdown', {
            'fields': (
                'category',
                'source',
                'amount',
                'percentage_of_total'
            )
        }),
        ('AI Extraction Data', {
            'fields': ('source_document', 'extracted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
