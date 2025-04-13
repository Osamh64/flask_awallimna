# run.py
from app import create_app, db
from app.models import User, Story, Category # استيراد النماذج الرئيسية

# إنشاء مثيل للتطبيق باستخدام دالة المصنع
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """إضافة كائنات لقشرة الأوامر (flask shell) لتسهيل الاختبار."""
    return {'db': db, 'User': User, 'Story': Story, 'Category': Category}

# تشغيل الخادم (للتطوير فقط)
if __name__ == '__main__':
    app.run() # سيستخدم الإعدادات من .env مثل FLASK_DEBUG