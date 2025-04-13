# app/__init__.py
import os
import logging
import datetime # <-- استيراد datetime
from logging.handlers import RotatingFileHandler
from flask import Flask, request, session as flask_session, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect # <-- استيراد inspect
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect

# إنشاء مثيلات الإضافات - ضعها خارج الدالة ليكون الوصول إليها ممكناً
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # توجيه المستخدمين غير المسجلين إلى صفحة الدخول
login_manager.login_message = 'الرجاء تسجيل الدخول للوصول إلى هذه الصفحة.'
login_manager.login_message_category = 'info' # فئة رسالة flash
csrf = CSRFProtect()
# mail = Mail() # Uncomment if you configure Flask-Mail

# --- دالة إنشاء التطبيق (Application Factory) ---
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # تهيئة الإضافات مع التطبيق - تتم هنا داخل الدالة
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    # mail.init_app(app) # Uncomment if you configure Flask-Mail

    # --- تسجيل الـ Blueprints ---
    # --- >> يجب أن تكون الاستيرادات والتسجيل **داخل** دالة create_app << ---
    # هذا يتجنب مشاكل الاستيراد الدائري ويضمن أن التطبيق مهيأ قبل استيراد الـ routes

    # (هذه الاستيرادات تفترض أن لديك الملفات/المجلدات التالية ضمن مجلد app)
    try:
        from app.routes.main import bp as main_bp
        app.register_blueprint(main_bp)
    except ImportError as e:
        app.logger.error(f"Failed to import main blueprint: {e}")

    try:
        from app.routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
    except ImportError as e:
        app.logger.error(f"Failed to import auth blueprint: {e}")

    try:
        from app.routes.admin import bp as admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')
    except ImportError as e:
        app.logger.error(f"Failed to import admin blueprint: {e}")

    try:
        from app.routes.stories import bp as stories_bp
        app.register_blueprint(stories_bp, url_prefix='/stories')
    except ImportError as e:
        app.logger.error(f"Failed to import stories blueprint: {e}")

    try:
        from app.routes.centers import bp as centers_bp
        app.register_blueprint(centers_bp, url_prefix='/centers') # <-- التسجيل موجود!
    except ImportError as e:
        app.logger.error(f"Failed to import centers blueprint: {e}")

    try:
        from app.routes.user import bp as user_bp
        app.register_blueprint(user_bp, url_prefix='/user')
    except ImportError as e:
        app.logger.error(f"Failed to import user blueprint: {e}")

    try:
        from app.routes.api import bp as api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
    except ImportError as e:
        app.logger.error(f"Failed to import api blueprint: {e}")
    # --- >> نهاية قسم تسجيل Blueprints << ---


    # تسجيل الدوال المساعدة للسياق العام للقوالب Jinja
    @app.context_processor
    def utility_processor():
        """Injects common utilities like the current time and categories into template context."""
        # Use try-except blocks for imports inside functions to handle potential circular dependencies better
        # Although it's generally better to structure code to avoid them.
        categories = []
        try:
            from app.models import Category # تجنب الاستيراد الدائري قدر الإمكان
            inspector = inspect(db.engine)
             # الحصول على اسم الجدول من النموذج لتجنب الأخطاء إذا تغير الاسم
            table_name_to_check = Category.__tablename__ if hasattr(Category, '__tablename__') else 'categories' # fallback name

            # تحقق من وجود الجدول قبل محاولة الاستعلام عنه، خاصة أثناء التهيئة الأولى أو الترحيل
            if inspector.has_table(table_name_to_check):
                categories = Category.query.order_by(Category.name).all()
        except Exception as e:
             # Log detailed error to help debug issues with DB connection or model loading
             app.logger.error(f"CONTEXT PROCESSOR ERROR: Could not fetch categories. DB Ready? Models loaded? Error: {e}", exc_info=True)
             # You might return an empty list or re-raise depending on desired behavior

        return dict(
            now=datetime.datetime.utcnow(), # <-- إضافة كائن الوقت الحالي هنا
            current_user=current_user,
            categories_for_nav=categories # اسم المتغير للقوالب
            )


    # معالجات الأخطاء الشائعة
    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f"Forbidden access attempt to {request.path}")
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"Not found error for path: {request.path}")
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {error} on path {request.path}", exc_info=True) # Log stack trace
        try:
            # محاولة إلغاء أي معاملات قد تكون عالقة في الجلسة
            db.session.rollback()
            app.logger.info("Database session rolled back after 500 error.")
        except Exception as e:
             # قد تفشل هذه الخطوة إذا كانت المشكلة الأصلية في الاتصال بقاعدة البيانات
             app.logger.error(f"Error during session rollback in 500 handler: {e}", exc_info=True)
        error_info = error if app.debug else None # Show error details only in debug mode
        return render_template('errors/500.html', error=error_info), 500

    # إعداد تسجيل الأخطاء للملفات (Logging)
    if not app.debug and not app.testing:
        log_dir = app.config.get('LOG_DIR', 'logs') # Get log dir from config or default
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir) # Use makedirs to create parent dirs if needed
                app.logger.info(f"Created logs directory: {log_dir}")
            except OSError as e:
                 # Log error but don't crash the app
                 app.logger.error(f"Could not create logs directory '{log_dir}': {e}", exc_info=True)

        # Proceed with file handler only if log directory exists
        if os.path.isdir(log_dir): # Check if it's actually a directory
             try:
                log_file = os.path.join(log_dir, 'awallimna.log')
                # Rotate logs: keep 10 files of 10MB each
                file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024*10, backupCount=10, encoding='utf-8')
                log_format = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
                formatter = logging.Formatter(log_format)
                file_handler.setFormatter(formatter)
                file_handler.setLevel(logging.INFO)

                # Add handler only if a similar handler doesn't exist already
                handler_exists = any(
                    isinstance(h, RotatingFileHandler) and getattr(h, 'baseFilename', None) == file_handler.baseFilename
                    for h in app.logger.handlers
                )
                if not handler_exists:
                    app.logger.addHandler(file_handler)
                    app.logger.info(f"Added RotatingFileHandler for {log_file}")

                # Ensure root logger also gets the file handler if needed,
                # but usually Flask's app logger is sufficient.

                app.logger.setLevel(logging.INFO) # Set app logger level
                app.logger.info('------ عوالمنا Application Startup ------') # Startup message

             except Exception as e:
                 # Log this critical error to stderr as file logging setup failed
                 print(f"CRITICAL: Could not set up file logging handler: {e}")
                 app.logger.error(f"Could not set up file logging handler: {e}", exc_info=True)
        else:
            app.logger.warning(f"Logs directory '{log_dir}' does not exist or is not a directory, file logging disabled.")

    # Console logging can be useful even in production for platforms like Heroku/Docker
    # Werkzeug in debug mode might add its own handlers, leading to duplicate logs if not careful
    stream_handler = logging.StreamHandler()
    stream_format = '%(levelname)s in %(module)s: %(message)s' # Simpler format for console
    stream_handler.setFormatter(logging.Formatter(stream_format))
    stream_handler.setLevel(logging.DEBUG if app.debug else logging.INFO) # More verbose in debug

    # Avoid adding duplicate stream handlers
    if not any(isinstance(h, logging.StreamHandler) for h in app.logger.handlers):
        app.logger.addHandler(stream_handler)
        app.logger.info("Added StreamHandler for console logging.")


    app.logger.info(f"Flask App created. Debug: {app.debug}, Testing: {app.testing}")
    return app # إعادة كائن التطبيق بعد إنشائه وتكوينه

# --- >> هذا الاستيراد مهم لـ Flask-Login ---
# استيراد النماذج **خارج** دالة create_app ولكن **بعد** تعريف `db`
# يتم استخدام هذا عادةً في ملف models.py لتعريف النماذج
# ولكن نحتاج لدالة user_loader هنا (أو في auth routes)

# دالة تحميل المستخدم التي يستخدمها Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # يحتاج لاستيراد النموذج هنا أو وضعه داخل الدالة لتجنب الاستيراد الدائري
    # مع هيكلية Blueprints، من الأفضل وضعه داخل `app.routes.auth` أو هنا.
    try:
        from app.models import User
        return User.query.get(int(user_id))
    except ImportError:
        # Log this critical failure
        logging.getLogger().critical("Failed to import User model in user_loader!")
        return None
    except Exception as e:
         logging.getLogger().error(f"Error loading user {user_id}: {e}", exc_info=True)
         return None

# يمكنك استيراد النماذج هنا إذا لم تكن هناك مشكلة استيراد دائري في حالتك،
# ولكن في الغالب لا يُفضل ذلك مباشرة في __init__.py مع استخدام factory pattern.
# from app import models