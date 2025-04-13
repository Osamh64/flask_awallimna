# config.py
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """إعدادات التطبيق الأساسية."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess' # استخدم متغير البيئة أولاً

    # إعدادات قاعدة البيانات SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db') # افتراضي إلى SQLite إذا لم يحدد
    SQLALCHEMY_TRACK_MODIFICATIONS = False # تعطيل التتبع غير الضروري

    # مجلد رفع الملفات
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(basedir, 'app/uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 * 1024 # الحد الأقصى لحجم الملف المرفوع (5 GB كمثال) - يجب ضبط خادم الويب أيضًا

    # إعدادات أخرى محتملة
    POSTS_PER_PAGE = 10

    # إعدادات البريد (إذا كنت ستستخدم Flask-Mail)
    # MAIL_SERVER = os.environ.get('MAIL_SERVER')
    # MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # ADMINS = ['your-admin-email@example.com'] # لتلقي تقارير الأخطاء

    LANGUAGES = ['en', 'ar'] # دعم اللغات (إذا لزم الأمر لـ i18n)

# تأكد من وجود مجلد التحميلات
if not os.path.exists(Config.UPLOAD_FOLDER):
    os.makedirs(Config.UPLOAD_FOLDER)