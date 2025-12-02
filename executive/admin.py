from django.contrib import admin
from .models import (
    ExecutiveDashboard,
    ExecutiveReport,
    BusinessHealthBreakdown,
    FinancialPerformanceBreakdown
)


@admin.register(ExecutiveDashboard)
class ExecutiveDashboardAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'date', 'total_sales_revenue', 
        'net_profit', 'store_growth_comparison', 'extracted_at'
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
                'total_sales_revenue',
                'net_profit',
                'store_growth_comparison'
            )
        }),
        ('AI Extraction Data', {
            'fields': ('source_document', 'extracted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExecutiveReport)
class ExecutiveReportAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'date', 'total_revenue', 'total_outlets',
        'branches_meeting_sales_target', 'active_promotions', 'extracted_at'
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
                'total_revenue',
                'total_outlets',
                'branches_meeting_sales_target',
                'active_promotions'
            )
        }),
        ('AI Extraction Data', {
            'fields': ('source_document', 'extracted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BusinessHealthBreakdown)
class BusinessHealthBreakdownAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'date', 'sales_revenue', 'expenses_costs',
        'marketing_campaigns_roi', 'risk_loss', 'extracted_at'
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
        ('Business Health Metrics', {
            'fields': (
                'sales_revenue',
                'expenses_costs',
                'marketing_campaigns_roi',
                'risk_loss'
            )
        }),
        ('AI Extraction Data', {
            'fields': ('source_document', 'extracted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FinancialPerformanceBreakdown)
class FinancialPerformanceBreakdownAdmin(admin.ModelAdmin):
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
        ('Financial Breakdown', {
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
