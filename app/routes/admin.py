# app/routes/admin.py
from flask import render_template, Blueprint, flash, redirect, url_for, request
from flask_login import login_required
from app import db
from app.models import Story, User, EducationalCenter
from app.utils import admin_required, format_time_ago

bp = Blueprint('admin', __name__)

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """لوحة تحكم المسؤول."""
    # يمكن جلب إحصائيات سريعة هنا
    pending_story_count = Story.query.filter_by(status='pending').count()
    pending_center_count = EducationalCenter.query.filter_by(status='pending').count()
    user_count = User.query.count()

    return render_template('admin/dashboard.html',
                           title='لوحة تحكم المشرف',
                           pending_story_count=pending_story_count,
                           pending_center_count=pending_center_count,
                           user_count=user_count)

@bp.route('/pending-stories')
@login_required
@admin_required
def pending_stories():
    """صفحة مراجعة القصص المعلقة (تقابل admin_page.php)."""
    page = request.args.get('page', 1, type=int)
    stories = Story.query.filter_by(status='pending') \
                         .order_by(Story.submission_date.asc()) \
                         .paginate(page=page, per_page=15, error_out=False) # عرض 15 قصة بالصفحة كمثال

    # الترقيم
    next_url = url_for('admin.pending_stories', page=stories.next_num) if stories.has_next else None
    prev_url = url_for('admin.pending_stories', page=stories.prev_num) if stories.has_prev else None

    return render_template('admin/pending_stories.html',
                           title='مراجعة القصص المعلقة',
                           stories=stories.items,
                           pagination=stories, # تمرير كائن الترقيم للقالب
                           next_url=next_url,
                           prev_url=prev_url,
                           format_time_ago=format_time_ago) # تمرير الدالة للقالب


@bp.route('/pending-centers')
@login_required
@admin_required
def pending_centers():
    """صفحة مراجعة طلبات المراكز التعليمية."""
    centers = EducationalCenter.query.filter_by(status='pending') \
                                      .order_by(EducationalCenter.submission_date.asc()).all()
    return render_template('admin/pending_centers.html',
                           title='مراجعة طلبات المراكز',
                           centers=centers,
                           format_time_ago=format_time_ago)


@bp.route('/center/<int:center_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_center(center_id):
    """الموافقة على طلب مركز تعليمي."""
    center = EducationalCenter.query.get_or_404(center_id)
    if center.status == 'pending':
        center.status = 'approved'
        # يمكن إضافة منطق إرسال إيميل للمركز هنا
        # أو تفعيل حساب المدير المرتبط بالمركز
        user_admin = center.admins.first() # افتراض وجود مدير واحد مرتبط عند الإنشاء
        if user_admin:
            user_admin.role = 'center_admin' # تغيير دور المستخدم
        db.session.commit()
        flash(f'تمت الموافقة على مركز "{center.name}" بنجاح.', 'success')
    else:
        flash('لا يمكن الموافقة على هذا المركز (الحالة ليست معلقة).', 'warning')
    return redirect(url_for('admin.pending_centers'))


@bp.route('/center/<int:center_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_center(center_id):
    """رفض طلب مركز تعليمي."""
    center = EducationalCenter.query.get_or_404(center_id)
    if center.status == 'pending':
        center.status = 'rejected'
        # يمكن إضافة منطق إرسال إيميل للمركز لإبلاغه بالرفض وسببه
        db.session.commit()
        flash(f'تم رفض طلب مركز "{center.name}".', 'info')
    else:
        flash('لا يمكن رفض هذا المركز (الحالة ليست معلقة).', 'warning')
    return redirect(url_for('admin.pending_centers'))


# يمكن إضافة صفحات إدارة أخرى مثل إدارة المستخدمين، التصنيفات، إلخ.