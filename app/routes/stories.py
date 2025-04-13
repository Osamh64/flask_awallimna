# app/routes/stories.py
from flask import (render_template, Blueprint, flash, redirect, url_for,
                   request, current_app, send_from_directory, abort)
from flask_login import login_required, current_user
from app import db
from app.models import Story, Category, Rating
from app.forms import StoryForm, RatingForm # ستحتاج لإنشاء RatingForm
from app.utils import writer_required, save_file, format_time_ago
import os

bp = Blueprint('stories', __name__)

@bp.route('/write', methods=['GET', 'POST'])
@login_required
@writer_required # يجب أن يكون المستخدم كاتباً ليكتب قصة
def write_story():
    """صفحة كتابة قصة جديدة (تقابل write_story.php)."""
    form = StoryForm()
    if form.validate_on_submit():
        pdf_path = None
        if form.pdf_file.data:
            # حفظ الملف في مجلد فرعي للقصص داخل مجلد التحميلات
            pdf_path = save_file(form.pdf_file.data, subfolder='story_pdfs')
            if not pdf_path:
                flash('حدث خطأ أثناء رفع ملف PDF.', 'danger')
                return render_template('stories/write_story.html', title='كتابة قصة جديدة', form=form)

        # إنشاء كائن القصة
        story = Story(
            title=form.title.data,
            short_description=form.short_description.data,
            content=form.content.data if form.content.data else None, # حفظ المحتوى النصي إن وجد
            author_id=current_user.id,
            author_name=current_user.username, # حفظ اسم المؤلف لسهولة العرض
            status=form.status.data, # pending or draft
            pdf_path=pdf_path
        )

        # ربط التصنيفات المختارة
        selected_categories = Category.query.filter(Category.id.in_(form.categories.data)).all()
        for category in selected_categories:
            story.categories.append(category)

        db.session.add(story)
        db.session.commit()

        if story.status == 'pending':
             flash(f'تم إرسال قصتك "{story.title}" للمراجعة بنجاح!', 'success')
        else:
             flash(f'تم حفظ مسودة القصة "{story.title}" بنجاح. يمكنك إرسالها للمراجعة لاحقاً.', 'info')

        return redirect(url_for('user.profile')) # توجيه لملف الكاتب الشخصي بعد الحفظ

    return render_template('stories/write_story.html', title='كتابة قصة جديدة', form=form)


@bp.route('/<int:story_id>')
def read_story(story_id):
    """صفحة عرض تفاصيل وقراءة القصة (تحسين لـ read_story.php)."""
    story = Story.query.get_or_404(story_id)

    # التأكد من أن القصة منشورة أو أن المستخدم الحالي هو المؤلف أو أدمن
    if story.status != 'approved' and (not current_user.is_authenticated or \
       (current_user.id != story.author_id and not current_user.is_admin())):
        abort(404) # أو 403

    # زيادة عدد المشاهدات (بطريقة بسيطة)
    story.view_count = (story.view_count or 0) + 1
    db.session.commit()

    # --- جلب التقييمات ---
    ratings = story.ratings_received.order_by(Rating.timestamp.desc()).all()
    avg_rating_value = story.average_rating()

    # --- نموذج إضافة تقييم (إذا كان المستخدم مسجل ولم يقيم بعد) ---
    rating_form = None
    can_rate = False
    if current_user.is_authenticated:
         existing_rating = Rating.query.filter_by(user_id=current_user.id, story_id=story.id).first()
         if not existing_rating:
              can_rate = True
              # rating_form = RatingForm() # تحتاج لإنشاء هذا النموذج في forms.py

    # --- مسار ملف PDF للعرض ---
    pdf_url = None
    if story.pdf_path:
        # تأكد من أن المسار آمن ويتطلب ربما حماية إضافية
        # يقدم رابط مباشر حالياً
        pdf_url = url_for('stories.serve_story_pdf', filename=story.pdf_path, _external=True) # المسار الكامل مهم لل JavaScript
        # أو استخدم الرابط النسبي إذا كان JavaScript يعمل من نفس المصدر
        # pdf_url = url_for('stories.serve_story_pdf', filename=story.pdf_path)


    return render_template('stories/read_story.html',
                           title=story.title,
                           story=story,
                           pdf_url=pdf_url,
                           ratings=ratings,
                           avg_rating=avg_rating_value,
                           can_rate=can_rate,
                           # rating_form=rating_form,
                           format_time_ago=format_time_ago)


# Route to serve PDF files securely from the uploads folder
@bp.route('/uploads/story_pdfs/<path:filename>')
@login_required # أضف الحماية المناسبة هنا (هل هو للاعضاء فقط؟ المشتركين؟)
def serve_story_pdf(filename):
    """Route لتقديم ملفات PDF من مجلد الـ uploads الخاص بالقصص."""
    # filename should include the subfolder 'story_pdfs/' passed during saving
    # but the route handles the first part '/uploads/story_pdfs/'
    pdf_directory = os.path.join(current_app.config['UPLOAD_FOLDER'])
    # The filename coming from url_for already has 'story_pdfs/...'
    # So we serve from UPLOAD_FOLDER using the full path in filename
    try:
        # Serve the file. We assume 'filename' correctly includes 'story_pdfs/actual_file.pdf'
        # as generated by save_file and passed to url_for.
        return send_from_directory(pdf_directory, filename, as_attachment=False) # Display inline
    except FileNotFoundError:
        abort(404)


@bp.route('/<int:story_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_story(story_id):
    """صفحة تعديل قصة موجودة."""
    story = Story.query.get_or_404(story_id)

    # التحقق من أن المستخدم الحالي هو المؤلف أو أدمن
    if current_user.id != story.author_id and not current_user.is_admin():
        abort(403) # غير مسموح

    form = StoryForm(obj=story) # تحميل بيانات القصة الحالية في النموذج

    # تحميل التصنيفات الحالية للقصة لتحديدها في النموذج
    if request.method == 'GET':
        form.categories.data = [c.id for c in story.categories]


    if form.validate_on_submit():
        # --- التعامل مع ملف PDF ---
        pdf_path = story.pdf_path # الاحتفاظ بالمسار القديم افتراضياً
        if form.pdf_file.data:
            # إذا تم رفع ملف جديد، احفظه واحذف القديم إن وجد
            new_pdf_path = save_file(form.pdf_file.data, subfolder='story_pdfs')
            if new_pdf_path:
                # حذف الملف القديم (اختياري وبحذر)
                if story.pdf_path:
                    old_file_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], story.pdf_path)
                    if os.path.exists(old_file_full_path):
                        try:
                            os.remove(old_file_full_path)
                        except OSError as e:
                            current_app.logger.error(f"Could not delete old PDF {old_file_full_path}: {e}")
                pdf_path = new_pdf_path
            else:
                flash('حدث خطأ أثناء رفع ملف PDF الجديد.', 'danger')
                # البقاء في نفس الصفحة لإعادة المحاولة
                return render_template('stories/write_story.html', title=f'تعديل: {story.title}', form=form, story=story)


        # --- تحديث بيانات القصة ---
        story.title = form.title.data
        story.short_description = form.short_description.data
        story.content = form.content.data if form.content.data else None
        story.status = form.status.data # تحديث الحالة (قد يكون للادمن صلاحية تغييرها مباشرة ل approved)
        story.pdf_path = pdf_path

        # --- تحديث التصنيفات ---
        # إزالة التصنيفات القديمة وإضافة الجديدة (طريقة بسيطة)
        story.categories = []
        selected_categories = Category.query.filter(Category.id.in_(form.categories.data)).all()
        for category in selected_categories:
            story.categories.append(category)

        db.session.commit()
        flash(f'تم تحديث القصة "{story.title}" بنجاح.', 'success')
        return redirect(url_for('user.profile')) # العودة لملف الكاتب

    return render_template('stories/write_story.html', # إعادة استخدام نفس النموذج
                            title=f'تعديل: {story.title}',
                            form=form,
                            story=story) # تمرير القصة للقالب يمكن أن يفيد


@bp.route('/<int:story_id>/delete', methods=['POST'])
@login_required
def delete_story(story_id):
    """حذف قصة."""
    story = Story.query.get_or_404(story_id)

    # التحقق من أن المستخدم الحالي هو المؤلف أو أدمن
    if current_user.id != story.author_id and not current_user.is_admin():
        abort(403) # غير مسموح

    try:
        # حذف ملف PDF المرتبط (اختياري وبحذر)
        if story.pdf_path:
            pdf_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], story.pdf_path)
            if os.path.exists(pdf_full_path):
                os.remove(pdf_full_path)

        # حذف التقييمات المرتبطة (SQLAlchemy cascade يمكن أن يقوم بذلك)
        Rating.query.filter_by(story_id=story.id).delete()

        # حذف القصة من قاعدة البيانات
        db.session.delete(story)
        db.session.commit()
        flash(f'تم حذف القصة "{story.title}" بنجاح.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء محاولة حذف القصة.', 'danger')
        current_app.logger.error(f"Error deleting story {story_id}: {e}")


    # إعادة التوجيه (إلى ملف الكاتب إذا هو من حذف، أو للوحة التحكم إذا أدمن)
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard')) # أو صفحة إدارة القصص
    else:
        return redirect(url_for('user.profile'))


@bp.route('/submission-accepted')
def submission_accepted():
    """ صفحة تأكيد نجاح تقديم الطلب (مثل طلب مركز) (تقابل accept_educational_center.php) """
    center_name = request.args.get('center_name') # أو أي رسالة أخرى
    message = request.args.get('message', 'تم استلام طلبكم بنجاح.')
    details = request.args.get('details', 'سيتم مراجعة الطلب والتواصل معكم قريباً.')
    title = request.args.get('title', 'تم الإرسال بنجاح')

    return render_template('stories/success.html',
                           page_title=title,
                           message=message,
                           center_name=center_name,
                           details=details)