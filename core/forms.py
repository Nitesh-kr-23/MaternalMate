# core/forms.py
"""
Django forms with Tailwind CSS styling for MaternalMate
Forms include validation and user-friendly error messages
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import HealthLog, MedicalReport, UserProfile


class UserRegistrationForm(UserCreationForm):
    """
    Extended registration form with maternal care fields
    """
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    emergency_contact_email = forms.EmailField(required=False)
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        help_text="You can add this later in your profile"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind CSS classes to all fields
        tailwind_classes = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent'
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = tailwind_classes
            field.widget.attrs['placeholder'] = field.label


class HealthLogForm(forms.ModelForm):
    """
    Form for logging patient vitals
    Matches the Kaggle Maternal Health Risk Dataset structure
    """
    
    class Meta:
        model = HealthLog
        fields = ['age', 'systolic_bp', 'diastolic_bp', 'bs', 'body_temp', 'heart_rate', 'notes']
        
        labels = {
            'age': 'Age (years)',
            'systolic_bp': 'Systolic Blood Pressure (mmHg)',
            'diastolic_bp': 'Diastolic Blood Pressure (mmHg)',
            'bs': 'Blood Glucose (mmol/L)',
            'body_temp': 'Body Temperature (°F)',
            'heart_rate': 'Heart Rate (bpm)',
            'notes': 'Additional Notes (Optional)',
        }
        
        help_texts = {
            'age': 'Enter your current age (18-70)',
            'systolic_bp': 'Normal range: 90-120 mmHg',
            'diastolic_bp': 'Normal range: 60-80 mmHg',
            'bs': 'Normal fasting: 4.0-5.4 mmol/L',
            'body_temp': 'Normal: 97.0-99.0°F',
            'heart_rate': 'Normal: 60-100 bpm',
        }
        
        widgets = {
            'age': forms.NumberInput(attrs={
                'min': '18',
                'max': '70',
                'step': '1',
            }),
            'systolic_bp': forms.NumberInput(attrs={
                'min': '70',
                'max': '220',
                'step': '1',
            }),
            'diastolic_bp': forms.NumberInput(attrs={
                'min': '40',
                'max': '140',
                'step': '1',
            }),
            'bs': forms.NumberInput(attrs={
                'min': '4.0',
                'max': '20.0',
                'step': '0.1',
            }),
            'body_temp': forms.NumberInput(attrs={
                'min': '95.0',
                'max': '105.0',
                'step': '0.1',
            }),
            'heart_rate': forms.NumberInput(attrs={
                'min': '40',
                'max': '140',
                'step': '1',
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Tailwind CSS styling for form fields
        input_classes = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent transition duration-200'
        
        for field_name, field in self.fields.items():
            if field_name == 'notes':
                field.widget.attrs['class'] = input_classes + ' resize-none'
            else:
                field.widget.attrs['class'] = input_classes
            
            # Add placeholder with normal range
            if field_name in self.Meta.help_texts:
                field.widget.attrs['placeholder'] = self.Meta.help_texts[field_name]
    
    def clean(self):
        """
        Custom validation to ensure BP readings are logical
        """
        cleaned_data = super().clean()
        systolic = cleaned_data.get('systolic_bp')
        diastolic = cleaned_data.get('diastolic_bp')
        
        if systolic and diastolic:
            if systolic <= diastolic:
                raise forms.ValidationError(
                    "Systolic BP must be higher than Diastolic BP"
                )
        
        return cleaned_data


class MedicalReportForm(forms.ModelForm):
    """
    Form for uploading medical reports (PDF/Images)
    Files are analyzed using Google Gemini API
    """
    
    class Meta:
        model = MedicalReport
        fields = ['report_file', 'report_type']
        
        labels = {
            'report_file': 'Upload Medical Report',
            'report_type': 'Report Type (Optional)',
        }
        
        help_texts = {
            'report_file': 'Supported formats: PDF, JPG, PNG (Max 10MB)',
            'report_type': 'E.g., Blood Test, Ultrasound, Urine Analysis',
        }
        
        widgets = {
            'report_file': forms.FileInput(attrs={
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'report_type': forms.TextInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Tailwind CSS styling
        self.fields['report_file'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 cursor-pointer file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-pink-50 file:text-pink-700 hover:file:bg-pink-100'
        })
        
        self.fields['report_type'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent',
            'placeholder': 'E.g., Blood Test Report'
        })
    
    def clean_report_file(self):
        """
        Validate file size and type
        """
        file = self.cleaned_data.get('report_file')
        
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:  # 10MB in bytes
                raise forms.ValidationError(
                    "File size must be less than 10MB"
                )
            
            # Check file extension
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            file_ext = '.' + file.name.split('.')[-1].lower()
            
            if file_ext not in allowed_extensions:
                raise forms.ValidationError(
                    f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
                )
        
        return file


class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information
    """
    
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'emergency_contact_email', 'due_date']
        
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply Tailwind styling
        input_classes = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent'
        
        for field in self.fields.values():
            field.widget.attrs['class'] = input_classes