# app/routes/main.py
from flask import render_template, Blueprint, current_app, redirect, url_for, request
from app.models import Story, Category
from app import db # للوصول إلى db.session عند الحاجة (مثل إحصائيات بسيطة هنا)
from app.utils import format_time_ago # استيراد الدالة المساعدة

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    """الصفحة الرئيسية (تقابل website.php والموقع.php)."""
    # جلب أحدث القصص المنشورة
    page = request.args.get('page', 1, type=int)
    latest_stories = Story.query.filter_by(status='approved') \
                              .order_by(Story.publish_date.desc()) \
                              .paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('main.index', page=latest_stories.next_num) if latest_stories.has_next else None
    prev_url = url_for('main.index', page=latest_stories.prev_num) if latest_stories.has_prev else None

    # لا نحتاج لجلب التصنيفات هنا لأنها تُحقن عبر context_processor

    return render_template('index.html',
                           title='عوالمنا - الصفحة الرئيسية',
                           stories=latest_stories.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           format_time_ago=format_time_ago) # تمرير الدالة للقالب


@bp.route('/category/<category_slug>')
def category_page(category_slug):
    """عرض القصص حسب التصنيف (تقابل comedy.php, romance.php...)."""
    category = Category.query.filter_by(slug=category_slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    stories_in_category = category.stories.filter_by(status='approved') \
                                       .order_by(Story.publish_date.desc()) \
                                       .paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('main.category_page', category_slug=category_slug, page=stories_in_category.next_num) if stories_in_category.has_next else None
    prev_url = url_for('main.category_page', category_slug=category_slug, page=stories_in_category.prev_num) if stories_in_category.has_prev else None

    return render_template('category_page.html',
                           title=f'قصص {category.name}',
                           category=category,
                           stories=stories_in_category.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           format_time_ago=format_time_ago)

@bp.route('/children') # مسار مخصص للأطفال إذا كان المنطق مختلفاً
def children_page():
    """صفحة الأطفال (تقابل children.php)."""
    # يمكن تطبيق فلترة إضافية هنا بناءً على فئات عمرية لو خزنت في القصص
    age_filter = request.args.get('age', None) # Example: ?age=0-6
    # Implement filtering logic based on age_filter if applicable
    # For now, show all 'children' category stories

    children_category = Category.query.filter_by(slug='children').first() # Assume slug 'children' exists
    if not children_category:
         return render_template('category_page.html', title='قصص أطفال', category=None, stories=[]) # Handle if category not found


    page = request.args.get('page', 1, type=int)
    stories_query = children_category.stories.filter_by(status='approved')

    # Optional: Apply age filtering here if you add age fields to Story model
    # if age_filter == '0-6':
    #     stories_query = stories_query.filter(Story.min_age <= 6)
    # elif age_filter == '7-12':
    #    # ... etc

    stories_for_children = stories_query.order_by(Story.publish_date.desc()) \
                                        .paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('main.children_page', age=age_filter, page=stories_for_children.next_num) if stories_for_children.has_next else None
    prev_url = url_for('main.children_page', age=age_filter, page=stories_for_children.prev_num) if stories_for_children.has_prev else None

    return render_template('children.html', # Use a specific template if layout differs
                           title='قصص أطفال',
                           age_filter=age_filter,
                           stories=stories_for_children.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           format_time_ago=format_time_ago)

@bp.route('/subscriptions')
def subscriptions():
    """صفحة عرض الاشتراكات (تقابل subscriptions.php)."""
    # يمكن جلب تفاصيل الخطط من قاعدة البيانات أو عرضها مباشرة
    return render_template('subscriptions.html', title='الاشتراكات')

@bp.route('/terms')
def terms_conditions():
    """صفحة الشروط والأحكام (تقابل terms_conditions.php)."""
    return render_template('terms_conditions.html', title='الشروط والأحكام')

@bp.route('/statistics')
# @admin_required # قد تحتاج لحماية هذه الصفحة
def statistics():
    """صفحة الإحصائيات (تقابل statistics.php)."""
    # --- جلب الإحصائيات (أمثلة بسيطة) ---
    stats = {}

    try:
        # إحصائيات القصص
        stats['total_stories'] = Story.query.count()
        stats['pending_stories'] = Story.query.filter_by(status='pending').count()
        stats['approved_stories'] = Story.query.filter_by(status='approved').count()
        stats['stories_by_category'] = db.session.query(Category.name, db.func.count(story_category_association.c.story_id)) \
            .join(story_category_association, Category.id == story_category_association.c.category_id) \
            .group_by(Category.name).all()

        # إحصائيات المستخدمين
        stats['total_users'] = User.query.count()
        stats['readers'] = User.query.filter_by(role='reader').count()
        stats['writers'] = User.query.filter_by(role='writer').count()
        stats['admins'] = User.query.filter(User.role.in_(['admin', 'super_admin'])).count()
        stats['centers'] = EducationalCenter.query.filter_by(status='approved').count()

        # إحصائيات أخرى يمكن إضافتها...

    except Exception as e:
        current_app.logger.error(f"Error fetching statistics: {e}")
        stats = {} # اعرض صفحة فارغة أو رسالة خطأ

    return render_template('statistics.html', title='الإحصائيات', stats=stats)