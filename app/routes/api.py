# app/routes/api.py
from flask import Blueprint, jsonify, request, abort, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Story
from app.utils import admin_required # استيراد decorator للتحقق من الادمن

bp = Blueprint('api', __name__)

@bp.route('/stories/<int:story_id>/status', methods=['POST'])
@login_required
@admin_required # فقط الادمن يمكنه تغيير حالة القصة
def update_story_status(story_id):
    """نقطة نهاية API لتحديث حالة القصة (قبول/رفض) (تقابل update_story_status.php)."""

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'الطلب يجب أن يكون JSON.'}), 400

    action = data.get('action') # 'approve' or 'reject'

    if action not in ['approve', 'reject']:
        return jsonify({'success': False, 'message': 'الإجراء غير صالح. يجب أن يكون approve أو reject.'}), 400

    story = Story.query.get_or_404(story_id)

    if story.status != 'pending':
        # إذا لم تكن معلقة، قد تكون تمت معالجتها بالفعل
        return jsonify({'success': False, 'message': 'لا يمكن تغيير حالة هذه القصة (ليست معلقة).'}), 409 # 409 Conflict

    try:
        if action == 'approve':
            story.status = 'approved'
            story.publish_date = db.func.now() # تحديد تاريخ النشر عند الموافقة
            message = f'تمت الموافقة على القصة "{story.title}" بنجاح.'
        else: # action == 'reject'
            story.status = 'rejected'
            message = f'تم رفض القصة "{story.title}".'

        db.session.commit()
        return jsonify({'success': True, 'message': message, 'new_status': story.status})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"API Error updating story status {story_id}: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ في الخادم أثناء تحديث الحالة.'}), 500


# --- يمكن إضافة نقاط API أخرى هنا ---
# مثال: API لجلب قائمة القصص للتعبئة الديناميكية (Load More)
@bp.route('/stories', methods=['GET'])
def get_stories_api():
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category', None)
    per_page = 10 # عدد القصص لكل طلب API

    query = Story.query.filter_by(status='approved')
    if category_slug:
         category = Category.query.filter_by(slug=category_slug).first()
         if category:
              query = query.join(story_category_association).filter(story_category_association.c.category_id == category.id)

    paginated_stories = query.order_by(Story.publish_date.desc()).paginate(page=page, per_page=per_page, error_out=False)

    stories_data = []
    for story in paginated_stories.items:
        stories_data.append({
            'id': story.id,
            'title': story.title,
            'author': story.author_name,
            'submission_date': story.submission_date.isoformat() + 'Z' if story.submission_date else None,
            'publish_date': story.publish_date.isoformat() + 'Z' if story.publish_date else None,
            'short_description': story.short_description,
            'url': url_for('stories.read_story', story_id=story.id),
            'avg_rating': story.average_rating()
        })

    return jsonify({
        'stories': stories_data,
        'has_next': paginated_stories.has_next,
        'next_page': paginated_stories.next_num,
        'total_pages': paginated_stories.pages
        })