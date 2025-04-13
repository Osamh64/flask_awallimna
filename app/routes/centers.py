# app/routes/centers.py
from flask import (render_template, Blueprint, flash, redirect, url_for,
                   request, current_app, abort)
from flask_login import login_required, current_user
from app import db
from app.models import Center, User # افترض وجود نموذج Center
from app.forms import CenterRegistrationForm, CenterEditForm # افترض وجود هذه النماذج

# إنشاء Blueprint الخاص بالمراكز
# url_prefix يجعل كل المسارات في هذا الملف تبدأ بـ /centers
# في app/routes/centers.py
bp = Blueprint('centers', __name__, url_prefix='/centers') # <-- تأكد أن الاسم هنا هو 'centers'

# --- 1. عرض قائمة بجميع المراكز ---
@bp.route('/') # المسار سيكون /centers/
def list_centers():
    """عرض قائمة بجميع المراكز التعليمية المسجلة."""
    page = request.args.get('page', 1, type=int) # لدعم التقسيم لصفحات (Pagination)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 10) # عدد العناصر لكل صفحة (حددها في config.py)

    # جلب المراكز مع التقسيم لصفحات
    centers_pagination = Center.query.order_by(Center.name.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    centers = centers_pagination.items
    # تمرير كائن التقسيم كاملاً للقالب للتحكم بالصفحات التالية/السابقة
    return render_template('centers/list.html',
                           title='المراكز التعليمية',
                           centers=centers,
                           pagination=centers_pagination)

# --- 2. عرض تفاصيل مركز معين ---
@bp.route('/<int:center_id>') # المسار سيكون /centers/1, /centers/2 ...
def view_center(center_id):
    """عرض صفحة التفاصيل لمركز تعليمي معين."""
    center = Center.query.get_or_404(center_id) # يجلب المركز أو يعرض خطأ 404 إذا لم يوجد
    # يمكنك هنا جلب معلومات إضافية متعلقة بالمركز (مثل الدورات، المدرسين، إلخ)
    return render_template('centers/detail.html',
                           title=f'تفاصيل مركز: {center.name}',
                           center=center)

# --- 3. تسجيل مركز جديد ---
@bp.route('/register', methods=['GET', 'POST'])
@login_required # يتطلب تسجيل الدخول لإضافة مركز جديد
def register():
    """معالجة تسجيل مركز تعليمي جديد."""
    form = CenterRegistrationForm()
    if form.validate_on_submit():
        try:
            # إنشاء كائن مركز جديد من بيانات النموذج
            new_center = Center(
                name=form.name.data,
                description=form.description.data,
                address=form.address.data,
                city=form.city.data,
                phone=form.phone.data,
                website=form.website.data,
                # قم بإضافة أي حقول أخرى من النموذج هنا
                # ربط المركز بالمستخدم الحالي كمالك (اختياري، تحتاج لحقل owner_id في Center)
                # owner_id=current_user.id
            )
            db.session.add(new_center)
            db.session.commit()
            flash(f'تم تسجيل المركز "{new_center.name}" بنجاح!', 'success')
            # إعادة التوجيه إلى صفحة تفاصيل المركز الجديد
            return redirect(url_for('centers.view_center', center_id=new_center.id))
        except Exception as e:
            db.session.rollback() # التراجع عن التغييرات في حالة حدوث خطأ
            flash('حدث خطأ غير متوقع أثناء تسجيل المركز. يرجى المحاولة مرة أخرى.', 'danger')
            current_app.logger.error(f"Error registering center by user {current_user.id}: {e}")

    # عرض النموذج (لطلب GET أو إذا فشل التحقق في طلب POST)
    # !!! هذا السطر هو الذي يحل مشكلة TypeError السابقة !!!
    return render_template('centers/register.html', title='تسجيل مركز جديد', form=form)

# --- 4. تعديل بيانات مركز قائم ---
@bp.route('/<int:center_id>/edit', methods=['GET', 'POST'])
@login_required # يتطلب تسجيل الدخول للتعديل
def edit_center(center_id):
    """معالجة تعديل بيانات مركز تعليمي قائم."""
    center = Center.query.get_or_404(center_id)

    # !!! التحقق من الصلاحية: هل المستخدم الحالي هو مالك المركز أو لديه صلاحية التعديل؟ !!!
    # افترض أن لديك حقل owner_id في نموذج Center يربطه بـ User.id
    # if center.owner_id != current_user.id and not current_user.is_admin(): # افترض وجود دور admin
    #     abort(403) # Forbidden - ليس لديك صلاحية

    form = CenterEditForm(obj=center) # استخدم نموذج التعديل واملأه ببيانات المركز الحالية

    if form.validate_on_submit():
        try:
            # تحديث بيانات المركز من النموذج
            center.name = form.name.data
            center.description = form.description.data
            center.address = form.address.data
            center.city = form.city.data
            center.phone = form.phone.data
            center.website = form.website.data
            # تحديث أي حقول أخرى هنا

            db.session.commit() # حفظ التغييرات في قاعدة البيانات
            flash(f'تم تحديث بيانات المركز "{center.name}" بنجاح.', 'success')
            return redirect(url_for('centers.view_center', center_id=center.id))
        except Exception as e:
            db.session.rollback()
            flash('حدث خطأ غير متوقع أثناء تحديث المركز. يرجى المحاولة مرة أخرى.', 'danger')
            current_app.logger.error(f"Error editing center {center_id} by user {current_user.id}: {e}")

    # عرض النموذج (لطلب GET أو إذا فشل التحقق في طلب POST)
    return render_template('centers/edit.html',
                           title=f'تعديل مركز: {center.name}',
                           form=form,
                           center=center) # قد تحتاج لتمرير المركز للقالب أيضًا

# --- 5. حذف مركز (اختياري) ---
@bp.route('/<int:center_id>/delete', methods=['POST']) # استخدم POST للحذف لتجنب الحذف العرضي
@login_required # يتطلب تسجيل الدخول للحذف
def delete_center(center_id):
    """معالجة حذف مركز تعليمي."""
    center = Center.query.get_or_404(center_id)

    # !!! التحقق من الصلاحية: هل المستخدم الحالي هو مالك المركز أو لديه صلاحية الحذف؟ !!!
    # if center.owner_id != current_user.id and not current_user.is_admin():
    #     abort(403) # Forbidden

    try:
        center_name = center.name # حفظ الاسم لعرضه في الرسالة قبل الحذف
        # يمكنك هنا إضافة منطق لحذف البيانات المرتبطة (مثل الدورات) إذا لزم الأمر
        db.session.delete(center)
        db.session.commit()
        flash(f'تم حذف المركز "{center_name}" بنجاح.', 'success')
        # إعادة التوجيه إلى قائمة المراكز بعد الحذف
        return redirect(url_for('centers.list_centers'))
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ غير متوقع أثناء حذف المركز.', 'danger')
        current_app.logger.error(f"Error deleting center {center_id} by user {current_user.id}: {e}")
        # في حالة الخطأ، أعد التوجيه إلى صفحة المركز أو القائمة
        return redirect(url_for('centers.view_center', center_id=center_id))

# يمكنك إضافة المزيد من المسارات هنا (مثل إدارة الدورات، المدرسين، الخ)