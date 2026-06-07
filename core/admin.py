"""
Django Admin Configuration for MaternalMate
Customizes the admin interface for easy data management
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, HealthLog, MedicalReport


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for User Profiles
    """
    list_display = ['user', 'phone_number', 'due_date', 'current_week', 'trimester', 'created_at']
    list_filter = ['created_at', 'due_date']
    search_fields = ['user__username', 'user__email', 'phone_number', 'emergency_contact_email']
    readonly_fields = ['created_at', 'updated_at', 'current_week', 'trimester']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Contact Details', {
            'fields': ('phone_number', 'emergency_contact_email')
        }),
        ('Pregnancy Information', {
            'fields': ('due_date', 'current_week', 'trimester')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def current_week(self, obj):
        """Display current pregnancy week"""
        return f"Week {obj.current_week}" if obj.current_week else "N/A"
    current_week.short_description = "Current Week"


@admin.register(HealthLog)
class HealthLogAdmin(admin.ModelAdmin):
    """
    Admin interface for Health Logs
    Displays vitals with color-coded risk levels
    """
    list_display = [
        'user', 'timestamp', 'age', 'blood_pressure', 
        'bs', 'heart_rate', 'body_temp', 'risk_level_badge'
    ]
    list_filter = ['risk_level', 'timestamp', 'user']
    search_fields = ['user__username', 'notes']
    readonly_fields = ['timestamp', 'bp_status']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('user', 'age', 'timestamp')
        }),
        ('Vital Signs', {
            'fields': (
                ('systolic_bp', 'diastolic_bp', 'bp_status'),
                'bs',
                'body_temp',
                'heart_rate'
            )
        }),
        ('Risk Assessment', {
            'fields': ('risk_level',),
            'classes': ('wide',)
        }),
        ('Additional Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def blood_pressure(self, obj):
        """Display BP in standard format"""
        return f"{obj.systolic_bp}/{obj.diastolic_bp} mmHg"
    blood_pressure.short_description = "Blood Pressure"
    
    def risk_level_badge(self, obj):
        """Display risk level with color coding"""
        colors = {
            'low risk': '#10b981',    # Green
            'mid risk': '#f59e0b',    # Yellow/Orange
            'high risk': '#ef4444',   # Red
        }
        color = colors.get(obj.risk_level, '#6b7280')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 5px; font-weight: bold;">{}</span>',
            color,
            obj.get_risk_level_display() if obj.risk_level else 'Pending'
        )
    risk_level_badge.short_description = "Risk Level"
    
    # Enable actions
    actions = ['mark_as_reviewed']
    
    def mark_as_reviewed(self, request, queryset):
        """Custom admin action"""
        count = queryset.count()
        self.message_user(request, f'{count} health log(s) marked as reviewed.')
    mark_as_reviewed.short_description = "Mark selected logs as reviewed"


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    """
    Admin interface for Medical Reports
    """
    list_display = [
        'user', 'report_type', 'file_extension', 
        'is_analyzed_badge', 'created_at'
    ]
    list_filter = ['created_at', 'report_type']
    search_fields = ['user__username', 'report_type', 'ai_summary']
    readonly_fields = ['created_at', 'updated_at', 'file_extension', 'ai_summary_preview']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('user', 'report_type', 'report_file', 'file_extension')
        }),
        ('AI Analysis', {
            'fields': ('ai_summary', 'ai_summary_preview'),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_analyzed_badge(self, obj):
        """Display analysis status with badge"""
        if obj.is_analyzed:
            return format_html(
                '<span style="background-color: #10b981; color: white; padding: 5px 10px; '
                'border-radius: 5px; font-weight: bold;">✓ Analyzed</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6b7280; color: white; padding: 5px 10px; '
                'border-radius: 5px; font-weight: bold;">⏳ Pending</span>'
            )
    is_analyzed_badge.short_description = "Analysis Status"
    
    def ai_summary_preview(self, obj):
        """Display AI summary in a formatted box"""
        if obj.ai_summary:
            return format_html(
                '<div style="background-color: #f3f4f6; padding: 15px; '
                'border-left: 4px solid #8b5cf6; border-radius: 5px; '
                'max-width: 600px;">{}</div>',
                obj.ai_summary
            )
        return "No AI analysis available"
    ai_summary_preview.short_description = "AI Summary Preview"


# Customize Admin Site Headers
admin.site.site_header = "MaternalMate Administration"
admin.site.site_title = "MaternalMate Admin Portal"
admin.site.index_title = "Welcome to MaternalMate Admin Dashboard"