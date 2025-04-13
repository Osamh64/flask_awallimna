# app/utils.py
from datetime import datetime, timezone, timedelta
from math import floor
import random
import string
from urllib.parse import urlparse, urljoin
from flask import request, url_for, current_app
from werkzeug.utils import secure_filename
import os


def format_timedelta(delta):
    """Formats a timedelta object into a human-readable 'time ago' string (Arabic)."""
    if not isinstance(delta, timedelta):
        return "غير معروف"

    seconds = int(delta.total_seconds())

    if seconds < 0:
        return "في المستقبل" # أو تعامل معها بشكل مختلف
    if seconds < 10:
        return "الآن"
    if seconds < 60:
        return f"منذ {seconds} ثواني"
    if seconds < 120:
        return "منذ دقيقة"
    if seconds < 3600: # أقل من ساعة
        minutes = floor(seconds / 60)
        return f"منذ {minutes} دقائق"
    if seconds < 7200: # أقل من ساعتين
        return "منذ ساعة"
    if seconds < 86400: # أقل من يوم
        hours = floor(seconds / 3600)
        return f"منذ {hours} ساعات"
    if seconds < 172800: # أقل من يومين
        return "منذ يوم"
    if seconds < 604800: # أقل من أسبوع
        days = floor(seconds / 86400)
        return f"منذ {days} أيام"
    if seconds < 1209600: # أقل من أسبوعين
        return "منذ أسبوع"
    if seconds < 2592000: # أقل من شهر (تقريبا 30 يومًا)
        weeks = floor(seconds / 604800)
        return f"منذ {weeks} أسابيع"
    if seconds < 5184000: # أقل من شهرين
        return "منذ شهر"
    if seconds < 31536000: # أقل من سنة (تقريبا 365 يومًا)
        months = floor(seconds / 2592000)
        return f"منذ {months} أشهر"
    if seconds < 63072000: # أقل من سنتين
        return "منذ سنة"
    else:
        years = floor(seconds / 31536000)
        return f"منذ {years} سنوات"


def format_time_ago(dt):
    """Calculates the difference between a datetime object and now, and formats it."""
    if dt is None:
        return "غير متوفر"
    now = datetime.now(timezone.utc)
     # Ensure dt is offset-aware (assuming it's UTC if naive)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return format_timedelta(now - dt)


def generate_random_password(length=12):
    """Generates a random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def is_safe_url(target):
    """Checks if a target URL is safe for redirection."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def save_file(file_storage, subfolder=''):
    """Saves a FileStorage object securely."""
    if not file_storage or file_storage.filename == '':
        return None

    filename = secure_filename(file_storage.filename)
    target_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)

    # Create subfolder if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    file_path = os.path.join(target_dir, filename)

    # Prevent overwriting? Generate unique name?
    # Simple approach: add timestamp if file exists
    base, extension = os.path.splitext(filename)
    counter = 1
    while os.path.exists(file_path):
        file_path = os.path.join(target_dir, f"{base}_{counter}{extension}")
        counter += 1

    try:
        file_storage.save(file_path)
        # Return the path relative to the UPLOAD_FOLDER for database storage
        relative_path = os.path.join(subfolder, os.path.basename(file_path))
        # Ensure consistent use of forward slashes for web paths
        return relative_path.replace("\\", "/")
    except Exception as e:
        current_app.logger.error(f"Failed to save file {filename}: {e}")
        return None


def get_country_list():
    """Returns a list of countries (value, label) for select fields."""
    # This can be loaded from a file or defined here
    return [
        ("", "اختر البلد"),
        ('SA', 'السعودية'),
        ('EG', 'مصر'),
        ('AE', 'الإمارات العربية المتحدة'),
        ('KW', 'الكويت'),
        ('QA', 'قطر'),
        ('BH', 'البحرين'),
        ('OM', 'عمان'),
        ('JO', 'الأردن'),
        ('LB', 'لبنان'),
        ('SY', 'سوريا'),
        ('IQ', 'العراق'),
        ('YE', 'اليمن'),
        ('PS', 'فلسطين'),
        ('DZ', 'الجزائر'),
        ('MA', 'المغرب'),
        ('TN', 'تونس'),
        ('LY', 'ليبيا'),
        ('SD', 'السودان'),
        ('SO', 'الصومال'),
        ('DJ', 'جيبوتي'),
        ('KM', 'جزر القمر'),
        # Add all other countries as needed from the original PHP
        ('Afghanistan', 'Afghanistan - أفغانستان'),
        ('Albania', 'Albania - ألبانيا'),
        # ... (continue adding all countries from center_country.php)
        ('Zimbabwe', 'Zimbabwe - زيمبابوي') # Example end
    ]

# --- Decorators for Authorization ---
from functools import wraps
from flask_login import current_user
from flask import abort

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def writer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_writer():
             # Maybe redirect to profile or specific page instead of 403
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function