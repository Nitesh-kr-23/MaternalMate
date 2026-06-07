# core/models.py
"""
Database models for MaternalMate AI-Based Maternal Care Monitoring System
Models are designed to match the Kaggle Maternal Health Risk Dataset structure
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, timedelta


class UserProfile(models.Model):
    """
    Extended user profile for storing maternal-specific information
    One-to-One relationship with Django's built-in User model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Email for emergency notifications"
    )
    due_date = models.DateField(
        blank=True,
        null=True,
        help_text="Expected due date of delivery"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def current_week(self):
        """
        Calculate current pregnancy week based on due date
        Assumes a 40-week (280 days) pregnancy cycle
        Returns None if due_date is not set
        """
        if not self.due_date:
            return None
        
        # Calculate conception date (40 weeks before due date)
        conception_date = self.due_date - timedelta(weeks=40)
        
        # Calculate days since conception
        days_pregnant = (date.today() - conception_date).days
        
        # Convert to weeks (0-40)
        weeks = max(0, min(40, days_pregnant // 7))
        
        return weeks

    @property
    def trimester(self):
        """Return current trimester (1, 2, or 3). Returns None if no due_date."""
        week = self.current_week
        if not week:
            return None
        if week <= 13:
            return 1
        elif week <= 27:
            return 2
        else:
            return 3


class HealthLog(models.Model):
    """
    Health vitals log matching the Kaggle Maternal Health Risk Dataset
    Fields: Age, SystolicBP, DiastolicBP, BS (Blood Sugar), BodyTemp, HeartRate, RiskLevel
    """
    
    RISK_LEVEL_CHOICES = [
        ('low risk', 'Low Risk'),
        ('mid risk', 'Mid Risk'),
        ('high risk', 'High Risk'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='health_logs',
        help_text="Patient associated with this health log"
    )
    
    # Patient vitals - matching Kaggle dataset fields exactly
    age = models.IntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(70)],
        help_text="Age of the patient (18-70 years)"
    )
    
    systolic_bp = models.IntegerField(
        verbose_name="Systolic Blood Pressure",
        validators=[MinValueValidator(70), MaxValueValidator(220)],
        help_text="Upper blood pressure value (mmHg)"
    )
    
    diastolic_bp = models.IntegerField(
        verbose_name="Diastolic Blood Pressure",
        validators=[MinValueValidator(40), MaxValueValidator(140)],
        help_text="Lower blood pressure value (mmHg)"
    )
    
    bs = models.FloatField(
        verbose_name="Blood Glucose",
        validators=[MinValueValidator(4.0), MaxValueValidator(20.0)],
        help_text="Blood glucose level (mmol/L)"
    )
    
    body_temp = models.FloatField(
        verbose_name="Body Temperature",
        validators=[MinValueValidator(95.0), MaxValueValidator(105.0)],
        help_text="Body temperature (°F)"
    )
    
    heart_rate = models.IntegerField(
        validators=[MinValueValidator(40), MaxValueValidator(140)],
        help_text="Heart rate (beats per minute)"
    )
    
    # AI Prediction Result
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        blank=True,
        null=True,
        help_text="AI-predicted risk level"
    )
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, help_text="Additional observations")
    
    class Meta:
        verbose_name = "Health Log"
        verbose_name_plural = "Health Logs"
        ordering = ['-timestamp']  # Most recent first
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.risk_level or 'Pending'}"

    @property
    def is_high_risk(self):
        """Check if this log indicates high risk"""
        return self.risk_level == 'high risk'

    @property
    def bp_status(self):
        """Categorize blood pressure status"""
        if self.systolic_bp < 120 and self.diastolic_bp < 80:
            return "Normal"
        elif self.systolic_bp < 130 and self.diastolic_bp < 80:
            return "Elevated"
        elif self.systolic_bp < 140 or self.diastolic_bp < 90:
            return "High (Stage 1)"
        else:
            return "High (Stage 2)"


class MedicalReport(models.Model):
    """
    Store uploaded medical reports (PDFs/Images) with AI-generated summaries
    Uses Google Gemini API for intelligent report analysis
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medical_reports',
        help_text="Patient who uploaded this report"
    )
    
    report_file = models.FileField(
        upload_to='reports/%Y/%m/%d/',
        help_text="Medical report (PDF/Image)",
        validators=[
            # Add file size validator if needed
        ]
    )
    
    report_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Type of report (e.g., Blood Test, Ultrasound)"
    )
    
    ai_summary = models.TextField(
        blank=True,
        null=True,
        help_text="AI-generated summary from Gemini API"
    )
    
    requires_doctor_review = models.BooleanField(
        default=False,
        help_text="Flag indicating if abnormalities were detected requiring doctor review"
    )
    
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('normal', 'Normal'),
            ('caution', 'Caution'),
            ('alert', 'Alert'),
        ],
        default='normal',
        help_text="AI-assessed risk level from report"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Medical Report"
        verbose_name_plural = "Medical Reports"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - Report {self.created_at.strftime('%Y-%m-%d')}"

    @property
    def file_extension(self):
        """Get file extension"""
        return self.report_file.name.split('.')[-1].upper() if self.report_file else None

    @property
    def is_analyzed(self):
        """Check if AI analysis is complete"""
        return bool(self.ai_summary)