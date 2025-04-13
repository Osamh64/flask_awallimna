# app/routes/user.py
from flask import render_template, Blueprint, flash, redirect, url_for, request, current_app, abort
from flask_login import login_required, current_user, logout_user # استيراد logout_user
from app import db
from app.models import User, Story, Rating
from app.forms import DeleteAccountForm
from app.utils import format_time_ago
import os

# --- إنشاء الـ Blueprint ---
# مثال على اسم جديد
bp = Blueprint('user_routes', __name__)

# --- ملف تعريف المستخدم الحالي ---
@bp.route('/profile')
@login_required
def profile():
    """عرض الملف الشخصي للمستخدم المسجل دخوله (تقابل writer_profile.php)."""
    # Note: current_user is available globally in templates if login_manager is setup correctly.
    # But we fetch user object again here if we need more specific data not in current_user proxy,
    # or just to be explicit. Getting by id is safer.
    user = User.query.get_or_404(current_user.id) # جلب المستخدم الحالي

    # جلب القصص التي كتبها المستخدم (إذا كان كاتباً)
    stories = []
    if user.role == 'writer':
         stories = Story.query.filter_by(author_id=user.id) \
                            .order_by(Story.submission_date.desc()).all()
         # Calculate average rating for stories here or let template/model handle it
         # for story in stories:
         #    story.avg_rating = story.average_rating() # Example pre-calculation

    return render_template('user/profile.html',
                           title=f'ملف {user.username}',
                           user=user, # Pass user object to template
                           stories=stories,
                           format_time_ago=format_time_ago) # Pass helper function

# --- عرض الملف الشخصي العام لأي كاتب ---
@bp.route('/profile/<username>')
def view_profile(username):
     """عرض ملف شخصي عام لكاتب معين."""
     user = User.query.filter_by(username=username).first_or_404()
     # التأكد من أن الحساب لكاتب للعرض العام (يمكن تعديل هذا الشرط)
     if user.role != 'writer':
          abort(404) # أو اعرض رسالة بأن هذا المستخدم ليس كاتبًا

     # عرض القصص المنشورة فقط
     stories = Story.query.filter_by(author_id=user.id, status='approved') \
                         .order_by(Story.publish_date.desc()).all()

     return render_template('user/public_profile.html', # استخدم قالب العرض العام
                            title=f'ملف الكاتب {user.username}',
                            user=user,
                            stories=stories,
                            format_time_ago=format_time_ago)


# --- معالجة طلب حذف/تجميد الحساب ---
@bp.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """معالجة طلب حذف أو تجميد الحساب (تقابل delete_account.php)."""
    form = DeleteAccountForm()
    user_to_delete = User.query.get(current_user.id) # Get the current logged-in user object

    if request.method == 'POST':
        # الحصول على الإجراء من الحقل المخفي (الذي يملؤه الـ JS)
        action = form.action.data # Read value from the hidden field

        # أولاً التحقق من صحة النموذج العام (خاصة كلمة المرور)
        # form.validate_on_submit() قد لا يكون مناسبًا إذا كان لدينا زرين منفصلين
        # التحقق من كلمة المرور يدويًا
        if form.confirm_password.validate(form): # Validate only the password field first
             if user_to_delete.check_password(form.confirm_password.data):
                 # التحقق من بقية الحقول (مثل السبب) إذا كان الحذف نهائيًا
                 if action == 'delete':
                      if not form.reason.validate(form): # Check reason validation manually if needed
                          flash('يرجى تحديد سبب الحذف.', 'warning')
                          return render_template('user/delete_account.html', title='حذف الحساب', form=form)
                      # --- منطق الحذف النهائي ---
                      try:
                         # ... (كود الحذف الكامل كما هو مفصل في الرد السابق) ...

                          # مثال: حذف القصص المرتبطة
                          stories_to_delete = Story.query.filter_by(author_id=user_to_delete.id).all()
                          for story in stories_to_delete:
                              if story.pdf_path:
                                  pdf_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], story.pdf_path)
                                  if os.path.exists(pdf_full_path):
                                      try: os.remove(pdf_full_path)
                                      except OSError as e: current_app.logger.warning(f"Could not delete PDF {pdf_full_path}: {e}")
                              Rating.query.filter_by(story_id=story.id).delete()
                              db.session.delete(story)

                          # حذف التقييمات التي قام بها المستخدم
                          Rating.query.filter_by(user_id=user_to_delete.id).delete()

                          # حذف الاشتراكات إن وجدت
                          # Subscription.query.filter_by(user_id=user_to_delete.id).delete()

                          # حذف المستخدم نفسه
                          db.session.delete(user_to_delete)
                          db.session.commit()
                          logout_user() # تسجيل خروجه بعد الحذف
                          flash('تم حذف حسابك وجميع بياناتك المرتبطة به نهائيًا.', 'success')
                          return redirect(url_for('auth.deleted_confirmation'))

                      except Exception as e:
                          db.session.rollback()
                          flash('حدث خطأ أثناء حذف الحساب.', 'danger')
                          current_app.logger.error(f"Error deleting user {user_to_delete.id}: {e}")

                 elif action == 'freeze':
                    # --- منطق التجميد (ببساطة تسجيل الخروج) ---
                    logout_user()
                    flash('تم تجميد حسابك (تسجيل الخروج). يمكنك تسجيل الدخول مرة أخرى لإعادة التنشيط.', 'info')
                    return redirect(url_for('main.index'))

                 else:
                    flash('الإجراء المطلوب غير معروف.', 'warning')

             else: # كلمة المرور خاطئة
                form.confirm_password.errors.append('كلمة المرور الحالية غير صحيحة.')
                # لا حاجة لـ flash هنا، الخطأ سيظهر تحت الحقل
        # else: # كلمة المرور فارغة أو خطأ آخر في التحقق الأولي لكلمة المرور
             # الأخطاء يجب أن تظهر بواسطة الماكرو render_field

    # For GET request or if validation fails on POST
    return render_template('user/delete_account.html', title='حذف الحساب', form=form)

# يمكن إضافة routes أخرى لتعديل الملف الشخصي، تغيير كلمة المرور، إلخ.
# @bp.route('/edit-profile', methods=['GET', 'POST'])
# @login_required
# def edit_profile():
#    pass