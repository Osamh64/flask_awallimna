# app/routes/auth.py
from flask import render_template, redirect, url_for, flash, request, Blueprint, current_app
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse, urljoin
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
# لا حاجة لاستيراد is_safe_url هنا لأنه يستخدم فقط داخل login عبر utils
# from app.utils import is_safe_url # , send_password_reset_email

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """معالجة تسجيل الدخول (تقابل login.php)."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # إذا كان مسجلاً بالفعل، اذهب للصفحة الرئيسية

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
            return redirect(url_for('auth.login'))

        # تسجيل دخول المستخدم وتذكر حالته إذا اختار ذلك
        login_user(user, remember=form.remember_me.data)
        flash(f'مرحباً بعودتك، {user.username}!', 'success')

        # تحديث وقت آخر ظهور
        user.last_seen = db.func.now()
        db.session.commit()

        # إعادة التوجيه إلى الصفحة المطلوبة سابقاً أو الرئيسية
        next_page = request.args.get('next')
        if not next_page or not is_safe_url(next_page):
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('login.html', title='تسجيل الدخول', form=form)

@bp.route('/logout')
@login_required # يجب أن يكون مسجلاً ليقوم بتسجيل الخروج
def logout():
    """تسجيل خروج المستخدم (تقابل logout.php)."""
    logout_user()
    flash('تم تسجيل خروجك بنجاح.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """معالجة إنشاء حساب جديد (تقابل register.php الفارغ أو انشاء حساب.php)."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('تهانينا، لقد قمت بالتسجيل بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
        # يمكن إرسال بريد ترحيبي أو تفعيل هنا
        # login_user(user) # تسجيل دخوله تلقائياً بعد التسجيل (اختياري)
        return redirect(url_for('auth.login')) # توجيه لصفحة الدخول بعد التسجيل

    return render_template('register.html', title='إنشاء حساب جديد', form=form)

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """طلب استعادة كلمة المرور (تقابل forgot_password.php)."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
             # --- منطق إرسال بريد إعادة التعيين ---
             # 1. توليد رمز آمن (token)
             # token = user.get_reset_password_token() # ستحتاج لإضافة هذه الدالة في models.py
             # 2. إرسال البريد الإلكتروني باستخدام Token
             # send_password_reset_email(user) # ستحتاج لدالة الإرسال في utils.py
             flash('تم إرسال تعليمات استعادة كلمة المرور إلى بريدك الإلكتروني.', 'info')
             return redirect(url_for('auth.login'))
        else:
             # حتى لو لم يكن البريد موجودًا، نعرض نفس الرسالة لعدم كشف الإيميلات المسجلة
             flash('تم إرسال تعليمات استعادة كلمة المرور إلى بريدك الإلكتروني.', 'info')
             return redirect(url_for('auth.login'))

    return render_template('forgot_password.html', title='نسيت كلمة المرور', form=form)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """صفحة إعادة تعيين كلمة المرور بعد الضغط على الرابط في البريد."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # --- التحقق من صحة الـ Token ---
    # user = User.verify_reset_password_token(token) # ستحتاج لهذه الدالة في models.py
    # if not user:
    #    flash('رابط إعادة تعيين كلمة المرور غير صالح أو منتهي الصلاحية.', 'warning')
    #    return redirect(url_for('auth.forgot_password'))

    # --- فقط ك Placeholder حاليا بدون التحقق الفعلي من token ---
    user = None # !! Replace with actual user fetched via token verification !!
    # This part below assumes user is found and token is valid
    if user is None:
         flash('محاكاة: للعمل، يجب التحقق من صحة التوكن أولاً وإيجاد المستخدم.', 'danger')
         # return redirect(url_for('main.index')) # أو صفحة خطأ

    form = ResetPasswordForm()
    if form.validate_on_submit():
        # !! This part will only execute if `user` is NOT None above !!
        if user:
             user.set_password(form.password.data)
             db.session.commit()
             flash('تم تغيير كلمة المرور بنجاح. يمكنك الآن تسجيل الدخول.', 'success')
             return redirect(url_for('auth.login'))
        else:
             # Should not happen if token verification is correct
             flash('حدث خطأ أثناء إعادة تعيين كلمة المرور.', 'danger')
             return redirect(url_for('auth.forgot_password'))

    return render_template('reset_password.html', title='إعادة تعيين كلمة المرور', form=form)


@bp.route('/confirmation-sent')
def confirmation_sent_email():
    """عرض صفحة تم إرسال التأكيد (تقابل confirmation_sent_email.php)."""
    email = request.args.get('email') # يمكن تمرير الإيميل للعرض
    return render_template('confirmations/email_sent.html', title='تم إرسال التأكيد', email=email)

@bp.route('/account-deleted')
def deleted_confirmation():
    """عرض صفحة تم حذف الحساب (تقابل deleted_confirmation.php)."""
    return render_template('confirmations/account_deleted.html', title='تم حذف الحساب')