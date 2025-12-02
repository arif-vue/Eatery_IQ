from django.contrib import admin
from .models import (
    OperationDashboard,
    OperationReport,
    DailyOperationBreakdown,
    FinancialPerformanceBreakdown
)


@admin.register(OperationDashboard)
class OperationDashboardAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'date', 'today_sales',
        'staff_attendance', 'labor_cost_vs_budget', 'extracted_at'
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
                'today_sales',
                'staff_attendance',
                'labor_cost_vs_budget'
            )
        }),
        ('AI Extraction Data', {
            'fields': ('source_document', 'extracted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OperationReport)
class OperationReportAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'date', 'today_sales', 'order_completed',
        'delivery_on_time_rate', 'shift_attendance', 'extracted_at'
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
                'today_sales',
                'order_completed',
                'delivery_on_time_rate',
                'shift_attendance'
            )
        }),
        ('AI Extraction Data', {
            'fields': ('source_document', 'extracted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DailyOperationBreakdown)
class DailyOperationBreakdownAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'date', 'in_store_orders', 'online_orders',
        'third_party_delivery', 'discounts_and_refunds', 'extracted_at'
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
        ('Daily Operation Metrics', {
            'fields': (
                'in_store_orders',
                'online_orders',
                'third_party_delivery',
                'discounts_and_refunds'
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
