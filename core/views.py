# core/views.py
"""
View functions for MaternalMate AI-Based Maternal Care Monitoring System
Handles dashboard, risk prediction, report analysis, and user authentication
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Avg, Count
import pickle
import pandas as pd
from google import genai
from google.genai import types
import mimetypes
import os
from datetime import datetime, timedelta

from .models import HealthLog, MedicalReport, UserProfile
from .forms import UserRegistrationForm, HealthLogForm, MedicalReportForm, UserProfileForm


# ===================== AI PREDICTION SERVICE =====================

def load_prediction_model():
    """
    Load the trained Random Forest model and label encoder
    Returns: (model, encoder) tuple or (None, None) if not found
    """
    try:
        model_path = os.path.join(settings.BASE_DIR, 'models', 'maternal_risk_model.pkl')
        encoder_path = os.path.join(settings.BASE_DIR, 'models', 'label_encoder.pkl')
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        with open(encoder_path, 'rb') as f:
            encoder = pickle.load(f)
        
        return model, encoder
    except FileNotFoundError:
        print("ERROR: Model files not found. Please run utils/train_model.py first.")
        return None, None


def predict_risk(age, systolic_bp, diastolic_bp, bs, body_temp, heart_rate):
    """
    Predict maternal health risk using the trained ML model
    
    Args:
        age: Patient age
        systolic_bp: Systolic blood pressure
        diastolic_bp: Diastolic blood pressure
        bs: Blood glucose level
        body_temp: Body temperature
        heart_rate: Heart rate
    
    Returns:
        str: Risk level ('low risk', 'mid risk', 'high risk') or None if error
    """
    model, encoder = load_prediction_model()
    
    if model is None or encoder is None:
        return None
    
    # Prepare input data matching training format
    input_data = pd.DataFrame({
        'Age': [age],
        'SystolicBP': [systolic_bp],
        'DiastolicBP': [diastolic_bp],
        'BS': [bs],
        'BodyTemp': [body_temp],
        'HeartRate': [heart_rate]
    })
    
    # Make prediction
    prediction = model.predict(input_data)
    risk_level = encoder.inverse_transform(prediction)[0]
    
    return risk_level


# ===================== GEMINI AI REPORT ANALYSIS =====================

def analyze_report_with_gemini(file_path, file_type):
    """
    Analyze medical report using Google GenAI with structured output
    
    Args:
        file_path: Path to the uploaded file
        file_type: Type of file (pdf, jpg, png)
    
    Returns:
        str: Formatted HTML summary with highlighted findings
    """
    try:
        # Initialize the GenAI client
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Enhanced prompt for structured, concise output
        prompt = """
        You are a maternal health AI assistant. Analyze this medical report and respond ONLY with the following structure. Do not use markdown, asterisks, or special formatting.
        
        VITAL SIGNS:
        - Blood Pressure: [value if mentioned, or "Not mentioned"]
        - Blood Glucose: [value if mentioned, or "Not mentioned"]
        - Hemoglobin: [value if mentioned, or "Not mentioned"]
        - Other vitals: [list any other mentioned vitals]
        
        ABNORMAL FINDINGS:
        [List each abnormal finding on a new line starting with a dash. If none, write "None detected"]
        
        SUMMARY:
        [Write EXACTLY 2 short sentences.
        Use very simple, non-medical language.
        Assume the reader is a pregnant mother with no medical background.
        Do NOT use scientific terms.
        If a medical condition is present, explain it in everyday words.
        Keep the tone calm and reassuring.]
        
        RISK LEVEL:
        [Write ONLY one word: "Low", "Mid", or "High"]
        
        Do not add any extra text.
        """
        
        # Determine MIME type based on file extension
        mime_type_map = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
        }
        
        file_ext = file_type.lower()
        mime_type = mime_type_map.get(file_ext)
        
        if not mime_type:
            return format_error_response("File type not supported. Please upload PDF, JPG, or PNG files.")
        
        # Upload file to Gemini with explicit MIME type
        with open(file_path, 'rb') as f:
            uploaded_file = client.files.upload(
                file=f,
                config={
                    'mime_type': mime_type,
                    'display_name': os.path.basename(file_path)
                }
            )
        
        print(f"✓ File uploaded: {uploaded_file.name} (MIME: {mime_type})")
        
        # Generate content using the uploaded file
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_uri(
                    file_uri=uploaded_file.uri,
                    mime_type=mime_type
                ),
                prompt
            ]
        )
        
        # Extract the raw text
        raw_summary = response.text.strip()
        
        print(f"✓ AI Analysis completed: {len(raw_summary)} characters")
        
        # Parse and format the response
        formatted_summary = parse_and_format_ai_response(raw_summary)
        
        # Clean up: delete the uploaded file from Gemini servers
        try:
            client.files.delete(name=uploaded_file.name)
            print(f"✓ File cleanup successful")
        except Exception as cleanup_error:
            print(f"⚠ Cleanup warning: {cleanup_error}")
        
        return formatted_summary
        
    except Exception as e:
        print(f"❌ Gemini API Error: {str(e)}")
        return format_error_response(f"AI analysis temporarily unavailable. Your report has been saved for manual review.")


def parse_and_format_ai_response(raw_text):
    """
    Parse AI response and format it into beautiful HTML
    Highlights abnormal findings and adds visual indicators
    
    Args:
        raw_text: Raw text from Gemini API
    
    Returns:
        str: Formatted HTML with cards, badges, and highlights
    """
    try:
        # Split into sections
        sections = {}
        current_section = None
        
        for line in raw_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            if 'VITAL SIGNS:' in line.upper():
                current_section = 'vitals'
                sections[current_section] = []
            elif 'ABNORMAL FINDINGS:' in line.upper() or 'ABNORMAL:' in line.upper():
                current_section = 'abnormal'
                sections[current_section] = []
            elif 'SUMMARY:' in line.upper():
                current_section = 'summary'
                sections[current_section] = []
            elif 'RISK LEVEL:' in line.upper() or 'RISK:' in line.upper():
                current_section = 'risk'
                sections[current_section] = []
            elif current_section:
                sections[current_section].append(line)
        
        # Build formatted HTML
        html_parts = []
        
        # Risk Level Badge (at the top)
        risk_level = 'Normal'
        if 'risk' in sections:
            risk_text = ' '.join(sections['risk']).strip()
            if 'alert' in risk_text.lower() or 'high' in risk_text.lower():
                risk_level = 'Alert'
            elif 'caution' in risk_text.lower() or 'mid' in risk_text.lower():
                risk_level = 'Caution'
        
        # Risk badge
        risk_colors = {
            'Normal': ('bg-green-100', 'text-green-800', 'border-green-300', '✓'),
            'Caution': ('bg-yellow-100', 'text-yellow-800', 'border-yellow-300', '⚠'),
            'Alert': ('bg-red-100', 'text-red-800', 'border-red-300', '⚠')
        }
        
        bg_color, text_color, border_color, icon = risk_colors.get(risk_level, risk_colors['Normal'])
        
        html_parts.append(f'''
        <div class="mb-4 p-3 {bg_color} border-l-4 {border_color} rounded-lg">
            <div class="flex items-center justify-between">
                <span class="{text_color} font-bold text-lg">{icon} Risk Level: {risk_level}</span>
                {'<span class="' + text_color + ' text-sm font-semibold px-3 py-1 bg-white rounded-full">Doctor Review Required</span>' if risk_level != 'Normal' else ''}
            </div>
        </div>
        ''')
        
        # Summary Section
        if 'summary' in sections and sections['summary']:
            summary_text = ' '.join(sections['summary']).strip()
            html_parts.append(f'''
        <div class="mb-4 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
            <h4 class="font-bold text-blue-900 mb-2">📋 Summary</h4>
            <p class="text-blue-800">{summary_text}</p>
        </div>
            ''')
        
        # Vital Signs Section
        if 'vitals' in sections and sections['vitals']:
            html_parts.append('<div class="mb-4"><h4 class="font-bold text-gray-800 mb-2">💉 Vital Signs</h4><div class="grid grid-cols-1 md:grid-cols-2 gap-2">')
            
            for vital in sections['vitals']:
                if vital.startswith('-'):
                    vital = vital[1:].strip()
                if vital and 'not mentioned' not in vital.lower():
                    html_parts.append(f'''
                    <div class="p-2 bg-gray-100 rounded-lg text-sm">
                        <span class="text-gray-700">{vital}</span>
                    </div>
                    ''')
            
            html_parts.append('</div></div>')
        
        # Abnormal Findings Section (HIGHLIGHTED IN RED)
        if 'abnormal' in sections and sections['abnormal']:
            findings = sections['abnormal']
            
            # Check if there are actual findings (not just "None detected")
            has_findings = any(f.strip() and 'none' not in f.lower() for f in findings)
            
            if has_findings:
                html_parts.append('<div class="mb-4 p-4 bg-red-50 rounded-lg border-l-4 border-red-500">')
                html_parts.append('<h4 class="font-bold text-red-900 mb-3">⚠️ Abnormal Findings</h4>')
                html_parts.append('<div class="space-y-2">')
                
                for finding in findings:
                    if finding.startswith('-'):
                        finding = finding[1:].strip()
                    if finding and 'none' not in finding.lower():
                        html_parts.append(f'''
                        <div class="flex items-start">
                            <span class="text-red-500 mr-2 font-bold">●</span>
                            <span class="text-red-800 font-semibold">{finding}</span>
                        </div>
                        ''')
                
                html_parts.append('</div></div>')
            else:
                html_parts.append('''
                <div class="mb-4 p-3 bg-green-50 rounded-lg border-l-4 border-green-500">
                    <span class="text-green-800 font-semibold">✓ No abnormal findings detected</span>
                </div>
                ''')
        
        return ''.join(html_parts)
        
    except Exception as e:
        print(f"❌ Parsing error: {str(e)}")
        # Fallback: show raw text in a clean format
        return f'''
        <div class="p-4 bg-gray-100 rounded-lg">
            <h4 class="font-bold text-gray-800 mb-2">AI Analysis</h4>
            <p class="text-gray-700 whitespace-pre-wrap">{raw_text}</p>
        </div>
        '''


def format_error_response(error_message):
    """
    Format error messages in a user-friendly HTML format
    
    Args:
        error_message: Error message string
    
    Returns:
        str: Formatted HTML error message
    """
    return f'''
    <div class="p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
        <div class="flex items-start">
            <span class="text-yellow-600 text-2xl mr-3">⚠</span>
            <div>
                <h4 class="font-bold text-yellow-900 mb-1">Analysis Unavailable</h4>
                <p class="text-yellow-800">{error_message}</p>
                <p class="text-yellow-700 text-sm mt-2">Your report has been saved and will be reviewed by your healthcare provider.</p>
            </div>
        </div>
    </div>
    '''


# ===================== AUTHENTICATION VIEWS =====================

def register_view(request):
    """User registration with profile creation"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save()
            
            # Update the auto-created profile with additional data
            # Profile is created automatically via signals
            profile = user.profile
            
            # Only update fields if they were provided
            if form.cleaned_data.get('phone_number'):
                profile.phone_number = form.cleaned_data.get('phone_number')
            if form.cleaned_data.get('emergency_contact_email'):
                profile.emergency_contact_email = form.cleaned_data.get('emergency_contact_email')
            if form.cleaned_data.get('due_date'):
                profile.due_date = form.cleaned_data.get('due_date')
            
            profile.save()
            
            # Auto login
            login(request, user)
            
            # Show different messages based on whether due_date was provided
            if profile.due_date:
                messages.success(request, 'Welcome to MaternalMate! Your account has been created.')
            else:
                messages.info(request, 'Welcome to MaternalMate! Please update your profile with your due date to enable pregnancy tracking.')
            
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')


@login_required
def logout_view(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


# ===================== DASHBOARD & MAIN VIEWS =====================

@login_required
def dashboard_view(request):
    """
    Main dashboard showing health trends, risk status, and analytics
    """
    # Get user's health logs (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    health_logs = HealthLog.objects.filter(
        user=request.user,
        timestamp__gte=thirty_days_ago
    ).order_by('-timestamp')
    
    # Get latest log for current status
    latest_log = health_logs.first()
    
    # Calculate statistics
    stats = {
        'total_logs': health_logs.count(),
        'avg_systolic': health_logs.aggregate(Avg('systolic_bp'))['systolic_bp__avg'] or 0,
        'avg_diastolic': health_logs.aggregate(Avg('diastolic_bp'))['diastolic_bp__avg'] or 0,
        'avg_heart_rate': health_logs.aggregate(Avg('heart_rate'))['heart_rate__avg'] or 0,
    }
    
    # Risk distribution
    risk_distribution = health_logs.values('risk_level').annotate(count=Count('id'))
    
    # Get recent reports
    recent_reports = MedicalReport.objects.filter(user=request.user)[:5]
    
    # User profile - handle if it doesn't exist
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist (shouldn't happen with signals)
        profile = UserProfile.objects.create(user=request.user)
    
    # Prepare data for charts - convert to list and reverse for chronological order
    chart_data = list(health_logs.values(
        'timestamp', 'systolic_bp', 'diastolic_bp', 
        'heart_rate', 'bs', 'body_temp', 'risk_level'
    ))
    chart_data.reverse()  # Oldest to newest for better chart visualization
    
    # Convert datetime objects to strings for JSON serialization
    for item in chart_data:
        item['timestamp'] = item['timestamp'].strftime('%Y-%m-%d %H:%M')
    
    context = {
        'latest_log': latest_log,
        'health_logs': health_logs[:10],  # Last 10 for table
        'all_logs_json': chart_data,
        'stats': stats,
        'risk_distribution': risk_distribution,
        'recent_reports': recent_reports,
        'profile': profile,
        'has_data': health_logs.exists(),  # Flag to show/hide empty states
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def log_health_view(request):
    """
    Log new health vitals and predict risk using AI
    """
    if request.method == 'POST':
        form = HealthLogForm(request.POST)
        if form.is_valid():
            health_log = form.save(commit=False)
            health_log.user = request.user
            
            # Predict risk using AI model
            risk_level = predict_risk(
                age=health_log.age,
                systolic_bp=health_log.systolic_bp,
                diastolic_bp=health_log.diastolic_bp,
                bs=health_log.bs,
                body_temp=health_log.body_temp,
                heart_rate=health_log.heart_rate
            )
            
            health_log.risk_level = risk_level if risk_level else 'mid risk'
            health_log.save()
            
            # Send alert if high risk
            if health_log.is_high_risk:
                send_high_risk_alert(request.user, health_log)
            
            messages.success(
                request, 
                f'Health log recorded! Risk Level: {health_log.get_risk_level_display()}'
            )
            return redirect('dashboard')
    else:
        # Pre-fill age from previous log
        last_log = HealthLog.objects.filter(user=request.user).first()
        initial_data = {'age': last_log.age} if last_log else {}
        form = HealthLogForm(initial=initial_data)
    
    return render(request, 'log_health.html', {'form': form})


@login_required
def upload_report_view(request):
    """
    Upload medical reports and analyze with Gemini AI
    """
    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            
            # Analyze with Gemini AI
            file_path = report.report_file.path
            file_type = report.file_extension.lower()
            
            ai_summary = analyze_report_with_gemini(file_path, file_type)
            report.ai_summary = ai_summary
            
            # Detect risk level from AI summary
            summary_lower = ai_summary.lower()
            if 'alert' in summary_lower or 'doctor review required' in summary_lower:
                report.risk_level = 'alert'
                report.requires_doctor_review = True
            elif 'caution' in summary_lower:
                report.risk_level = 'caution'
                report.requires_doctor_review = True
            else:
                report.risk_level = 'normal'
                report.requires_doctor_review = False
            
            report.save()
            
            # Send alert if doctor review required
            if report.requires_doctor_review:
                messages.warning(
                    request,
                    '⚠️ Your report has been analyzed. Some findings require doctor review. Please consult your healthcare provider.'
                )
            else:
                messages.success(request, '✓ Report uploaded and analyzed successfully!')
            
            return redirect('dashboard')
    else:
        form = MedicalReportForm()
    
    return render(request, 'upload_report.html', {'form': form})


@login_required
def update_profile_view(request):
    """
    Update user profile information (due date, emergency contact, etc.)
    """
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'update_profile.html', {'form': form, 'profile': profile})


# ===================== UTILITY FUNCTIONS =====================

def send_high_risk_alert(user, health_log):
    """
    Send email alert when high risk is detected
    """
    try:
        profile = user.profile
        subject = '🚨 High Risk Alert - MaternalMate'
        message = f"""
        Dear {user.username},
        
        A high-risk health condition has been detected in your latest health log.
        
        Details:
        - Blood Pressure: {health_log.systolic_bp}/{health_log.diastolic_bp} mmHg
        - Blood Glucose: {health_log.bs} mmol/L
        - Heart Rate: {health_log.heart_rate} bpm
        - Risk Level: {health_log.get_risk_level_display()}
        
        Please consult your healthcare provider immediately.
        
        Emergency Contact: {profile.emergency_contact_email}
        
        Stay safe,
        MaternalMate Team
        """
        
        # Send to user and emergency contact
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email, profile.emergency_contact_email],
            fail_silently=True,
        )
        
        print(f"✓ High-risk alert sent to {user.email}")
        
    except Exception as e:
        print(f"Email alert failed: {str(e)}")