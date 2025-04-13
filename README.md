# شرح ملفات PHP الأصلية ومقابلها في مشروع Flask

هذا الملف يوضح وظيفة كل ملف PHP تم تقديمه وكيف يمكن تمثيل هذه الوظيفة ضمن تطبيق ويب مبني بإطار العمل Flask في بايثون.

**ملاحظة:** تم إعادة تسمية بعض الملفات واستخدام هيكلية مجلدات Flask المتعارف عليها لتحسين التنظيم.

## 1. الملفات الرئيسية ومنطق العرض (Routes & Templates)

*   **`الموقع.php` / `website.php`:**
    *   **PHP:** الصفحة الرئيسية للموقع، تعرض التصنيفات وأحدث القصص. تحتوي على منطق بسيط لعرض روابط تسجيل الدخول/الخروج بناءً على حالة الجلسة. تتضمن `header.php`.
    *   **Flask:**
        *   **Route:** دالة في `app.py` (أو ملف routes مخصص) مرتبطة بالمسار `/`.
        *   **Logic:** تستعلم عن أحدث القصص والتصنيفات من قاعدة البيانات (باستخدام `models.py`). تتحقق من حالة الجلسة (`session`).
        *   **Template:** `templates/index.html`، يرث من `templates/layout.html`. يعرض البيانات باستخدام متغيرات Jinja2 (`{{ categories }}`, `{{ latest_stories }}`) ومنطق الجلسة (`{% if session.username %}`). يتضمن `templates/includes/header.html`.

*   **`accept_educational_center.php`:**
    *   **PHP:** صفحة نجاح تعرض رسالة بعد تقديم طلب مركز تعليمي. تستقبل اسم المركز عبر URL (`$_GET['center']`).
    *   **Flask:**
        *   **Route:** دالة في `app.py` مرتبطة بالمسار `/center/request/accepted` (مثلاً).
        *   **Logic:** تستقبل اسم المركز (`request.args.get('center_name')`).
        *   **Template:** `templates/stories/story_accepted.html` (تمت إعادة تسميته ليكون أكثر عمومية، أو يمكن إنشاء `templates/center/request_accepted.html`). يعرض `{{ center_name }}`.

*   **`admin_page.php`:**
    *   **PHP:** صفحة خاصة بالمسؤولين لمراجعة القصص المعلقة. تتضمن تحقق من دور المستخدم في الجلسة، اتصال بقاعدة البيانات (عبر `db.php`)، استدعاء دالة لجلب القصص (`story_functions.php`)، وعرض القصص مع أزرار قبول/رفض. تحتوي على كود JavaScript للتعامل مع الأزرار عبر AJAX (يستدعي `update_story_status.php`).
    *   **Flask:**
        *   **Route:** دالة في `app.py` (أو في Blueprint خاص بالمسؤولين) مرتبطة بالمسار `/admin/pending-stories`.
        *   **Logic:** تتطلب تسجيل الدخول ودور المسؤول (باستخدام decorators مثل `@login_required` و `@admin_required`). تستعلم عن القصص المعلقة (`Story.query.filter_by(status='pending').all()`). تجلب بيانات المسؤول من الجلسة. ترسل البيانات للقالب.
        *   **Template:** `templates/admin/pending_stories.html`. تستخدم Jinja لعرض القصص (`{% for story in stories %}`). تحتوي على نفس كود JavaScript (أو يتم تحميله من `static/js/admin_script.js`) الذي سيستدعي نقطة نهاية API في Flask.

*   **`center_profile.php`:**
    *   **PHP:** هيكل HTML أساسي لصفحة ملف تعريف مركز تعليمي.
    *   **Flask:**
        *   **Route:** دالة مرتبطة بمسار مثل `/center/<center_id>/profile`.
        *   **Logic:** تجلب بيانات المركز من قاعدة البيانات.
        *   **Template:** `templates/center/profile.html`. يعرض بيانات المركز.

*   **`children.php` (وجميع ملفات التصنيفات الأخرى مثل `comedy.php`, `romance.php` إلخ):**
    *   **PHP:** تعرض صفحة خاصة بتصنيف معين (أو فئة عمرية في حالة `children.php`)، تتضمن الهيدر وقسم لعرض أحدث القصص ضمن هذا التصنيف (يفترض أن هناك منطق PHP غير مكتمل لجلب هذه القصص).
    *   **Flask:**
        *   **Route:** يمكن استخدام مسار ديناميكي واحد مثل `/category/<category_slug>` أو `/age-group/<age_range>`.
        *   **Logic:** تجلب التصنيف/الفئة العمرية من المسار. تستعلم عن القصص المنتمية لهذا التصنيف/الفئة من قاعدة البيانات.
        *   **Template:** `templates/stories/story_list_by_category.html` (قالب واحد يعاد استخدامه). يعرض اسم التصنيف والقصص المرتبطة به. يتضمن `header.html`.

*   **`confirmation_sent_email.php`:**
    *   **PHP:** صفحة تخبر المستخدم بأنه تم إرسال بريد إلكتروني للتأكيد.
    *   **Flask:**
        *   **Route:** دالة مرتبطة بمسار مثل `/auth/confirmation-sent`.
        *   **Template:** `templates/auth/registration_confirmation.html`. تعرض الرسالة المناسبة.

*   **`create_center_account.php` / `register_center.php`:**
    *   **PHP:** تبدو أنها صفحة تسجيل حساب لمركز تعليمي (الأولى تعرض التصنيفات، الثانية تستدعي مكتبات).
    *   **Flask:**
        *   **Route:** دالة مرتبطة بمسار `/register/center`، تتعامل مع طلبات GET (لعرض النموذج) و POST (لمعالجة التسجيل).
        *   **Form:** استخدام `Flask-WTF` لإنشاء نموذج `CenterRegistrationForm` في `forms.py` للتحقق من صحة المدخلات.
        *   **Logic:** (في POST) تتحقق من النموذج، تنشئ حساب المركز في قاعدة البيانات، قد ترسل بريد تأكيد، وتعيد التوجيه. (في GET) تعرض النموذج.
        *   **Template:** `templates/auth/register_center.html`. يستخدم الماكرو الخاص بـ Flask-WTF لعرض حقول النموذج (`{{ wtf.quick_form(form) }}`).

*   **`delete_account.php` / `delete_account.css` (اسم خاطئ):**
    *   **PHP/HTML:** تعرض نموذجًا للمستخدم لاختيار سبب حذف الحساب وتقديم طلب تجميد أو حذف نهائي. (منطق المعالجة PHP غير موجود). الملف `.css` هو في الحقيقة HTML.
    *   **Flask:**
        *   **Route:** دالة مرتبطة بـ `/user/delete-account` تتعامل مع GET و POST.
        *   **Form:** يمكن استخدام `Flask-WTF` لنموذج بسيط.
        *   **Logic:** (POST) تعالج الطلب (تجميد/حذف) بناءً على الزر المضغوط. تتفاعل مع قاعدة البيانات. تسجل خروج المستخدم. تعيد التوجيه لصفحة تأكيد الحذف.
        *   **Template:** `templates/user/delete_account.html`.

*   **`deleted_confirmation.php`:**
    *   **PHP:** صفحة تعرض رسالة تأكيد بعد حذف الحساب بنجاح.
    *   **Flask:**
        *   **Route:** دالة مرتبطة بـ `/auth/account-deleted`.
        *   **Template:** `templates/auth/deleted_confirmation.html`.

*   **`forgot_password.php`:**
    *   **PHP:** تعرض نموذجًا لإدخال البريد الإلكتروني لطلب استعادة كلمة المرور. تتضمن JavaScript لإخفاء النموذج وإظهار رسالة تأكيد. (منطق الإرسال الفعلي غير موجود).
    *   **Flask:**
        *   **Route:** دالة مرتبطة بـ `/auth/forgot-password` تتعامل مع GET و POST.
        *   **Form:** `ForgotPasswordForm` في `forms.py`.
        *   **Logic:** (POST) تتحقق من صحة البريد الإلكتروني، تنشئ رمز استعادة (token)، ترسله للمستخدم عبر البريد، تعيد التوجيه أو تعرض رسالة نجاح.
        *   **Template:** `templates/auth/forgot_password.html`.

*   **`login.php`:**
    *   **PHP:** تعالج تسجيل الدخول. تستقبل `username` و `password` عبر POST. تتحقق منهما (هنا مقابل قيم ثابتة، لكن يجب أن يكون مقابل قاعدة بيانات). تعرض رسالة خطأ أو تعيد التوجيه إلى `dashboard.php` (غير موجودة في القائمة).
    *   **Flask:**
        *   **Route:** دالة مرتبطة بـ `/login` تتعامل مع GET و POST.
        *   **Form:** `LoginForm` في `forms.py`.
        *   **Logic:** (POST) تتحقق من النموذج. تستعلم عن المستخدم في قاعدة البيانات. تقارن كلمة المرور (باستخدام hash). إذا نجح، تخزن بيانات المستخدم في الجلسة (`session['user_id'] = ...`). تعيد التوجيه للصفحة الرئيسية أو لوحة التحكم. إذا فشل، تعرض رسالة خطأ (flash message).
        *   **Template:** `templates/login.html`. تعرض النموذج ورسائل الخطأ (`{% with messages = get_flashed_messages(with_categories=true) %}`).

*   **`logout.php`:**
    *   **PHP:** تدمر الجلسة (`session_destroy()`) وتعيد التوجيه للصفحة الرئيسية.
    *   **Flask:**
        *   **Route:** دالة مرتبطة بـ `/logout`.
        *   **Logic:** تحذف بيانات المستخدم من الجلسة (`session.pop('user_id', None)`, `session.clear()`). تعيد التوجيه (`redirect(url_for('index'))`).

*   **`read_story.php`:**
    *   **PHP:** تحاول عرض ملف PDF باستخدام مكتبات JavaScript (pdf.js, turn.js). دور PHP هو فقط تحديد مسار ملف PDF.
    *   **Flask:**
        *   **Route:** دالة مرتبطة بـ `/story/<story_id>/read`.
        *   **Logic:** تجلب بيانات القصة ومسار ملف PDF الخاص بها من قاعدة البيانات. ترسل المسار إلى القالب.
        *   **Template:** `templates/stories/read_story.html`. يحتوي على نفس إعداد JavaScript، ولكن يحصل على مسار PDF من متغير Jinja (`{{ story_pdf_path }}`). **ملاحظة:** عرض PDF تفاعلي بهذا الشكل داخل المتصفح مباشرة قد يكون معقدًا ويتطلب تحميل الملف للـ JavaScript. قد يكون من الأبسط توفير رابط لتحميل الـ PDF أو استخدام عارض `<iframe>` أو ` <embed>`.

*   **`reset_password.php`:**
    *   **PHP:** تعرض نموذج إعادة تعيين كلمة المرور (يبدو مشابهًا لـ `forgot_password.php` أو جزء من العملية).
    *   **Flask:**
        *   **Route:** دالة مرتبطة بمسار مثل `/auth/reset-password/<token>` تتعامل مع GET و POST. تتطلب رمز (token) صالحًا تم إرساله للمستخدم.
        *   **Form:** `ResetPasswordForm` في `forms.py` (يتضمن حقول كلمة المرور الجديدة وتأكيدها).
        *   **Logic:** (GET) تتحقق من صلاحية الـ token. تعرض النموذج. (POST) تتحقق من النموذج والـ token. تحدث كلمة المرور في قاعدة البيانات. تسجل دخول المستخدم أو تعيد التوجيه لصفحة تسجيل الدخول.
        *   **Template:** `templates/auth/reset_password.html`.

*   **`sent_educational_center.php`:**
    *   **PHP:** صفحة تعرض رسالة تأكيد بأنه تم إرسال طلب المركز التعليمي.
    *   **Flask:**
        *   **Route:** دالة مرتبطة بـ `/center/request-sent`.
        *   **Template:** `templates/center/submission_sent.html`.

*   **`statistics.php`:**
    *   **PHP:** هيكل HTML لعرض جداول إحصائيات (أنواع قصص، حسابات، دول). يفترض وجود منطق (غير موجود) لجلب البيانات وتعبئة الجداول.
    *   **Flask:**
        *   **Route:** دالة مرتبطة بـ `/statistics` (قد تتطلب صلاحيات مدير).
        *   **Logic:** تجمع بيانات إحصائية متنوعة من قاعدة البيانات (باستخدام queries مجمعة `count`, `group by`). ترسل البيانات للقالب.
        *   **Template:** `templates/general/statistics.html`. تعرض البيانات في الجداول باستخدام Jinja.

*   **`subscriptions.php`:**
    *   **PHP:** تعرض بطاقات لأنواع الاشتراكات المتاحة (شهري، سنوي، مركز تعليمي).
    *   **Flask:**
        *   **Route:** دالة مرتبطة بـ `/subscriptions`.
        *   **Logic:** قد تجلب تفاصيل الاشتراكات من قاعدة بيانات أو ملف إعدادات.
        *   **Template:** `templates/general/subscriptions.html`.

*   **`teacher_accounts.php`:**
    *   **PHP:** تعرض نموذجًا لإدخال عناوين البريد الإلكتروني للمعلمين بناءً على عدد محدد مخزن في الجلسة. تتحقق من صحة الإدخالات وتخزنها في الجلسة عند الإرسال.
    *   **Flask:**
        *   **Route:** دالة مرتبطة بـ `/center/setup/teachers` (أو ما شابه) تتعامل مع GET و POST.
        *   **Logic:** (GET) تقرأ عدد الحسابات من الجلسة. ترسل العدد للقالب لعرض العدد الصحيح من الحقول. (POST) تستقبل البيانات (قد تستخدم `request.form.getlist('teacher_emails')`). تتحقق من صحة الإيميلات. تخزنها في الجلسة أو قاعدة البيانات. تعيد التوجيه للخطوة التالية أو صفحة نجاح.
        *   **Template:** `templates/center/teacher_accounts.html`. تستخدم حلقة Jinja (`{% for i in range(num_accounts) %}`) لإنشاء الحقول ديناميكيًا.

*   **`terms_conditions.php`:**
    *   **PHP:** تعرض صفحة الشروط والأحكام (محتوى ثابت).
    *   **Flask:**
        *   **Route:** دالة بسيطة مرتبطة بـ `/terms`.
        *   **Template:** `templates/general/terms_conditions.html` (محتوى ثابت).

*   **`write_story.php`:**
    *   **PHP:** صفحة مع نموذج لكتابة قصة جديدة. تتضمن حقول للعنوان، الوصف، المحتوى، اختيار التصنيفات، وحالة النشر (يفترض)، ورفع ملف PDF. تتصل بقاعدة البيانات للتحقق من تكرار العنوان، إدراج القصة، وربط التصنيفات. تعالج رفع الملف.
    *   **Flask:**
        *   **Route:** دالة مرتبطة بـ `/stories/write` (أو `/stories/new`) تتعامل مع GET و POST. تتطلب تسجيل الدخول (`@login_required`).
        *   **Form:** `StoryForm` في `forms.py` يتضمن جميع الحقول اللازمة (نص، textarea، checkboxes أو multiple select للتصنيفات، file upload) والتحقق من الصحة (`validators`).
        *   **Logic:** (POST) تتحقق من النموذج (`form.validate_on_submit()`). تعالج رفع الملف بأمان (`secure_filename`, حفظ في مجلد `uploads`). تنشئ كائن `Story` جديد و `StoryCategory`s، تحفظها في قاعدة البيانات (`db.session.add()`, `db.session.commit()`). تعيد التوجيه (`redirect(url_for(...))`). (GET) تعرض النموذج مع قائمة التصنيفات المتاحة.
        *   **Template:** `templates/stories/write_story.html`. تستخدم Flask-WTF لعرض النموذج.

*   **`writer_profile.php`:**
    *   **PHP:** صفحة تعرض ملف تعريف الكاتب (اسمه، تاريخ انضمامه، إلخ) وقائمة بقصصه مع تقييماتها وإجراءات (قراءة، تعديل). تتطلب تسجيل الدخول وتجلب البيانات من قاعدة البيانات. تتضمن `header.php`.
    *   **Flask:**
        *   **Route:** دالة مرتبطة بـ `/user/profile` (أو `/writer/<writer_id>`). تتطلب تسجيل الدخول (`@login_required`) إذا كانت تعرض ملف المستخدم الحالي.
        *   **Logic:** تجلب بيانات المستخدم من قاعدة البيانات (`User.query.get(session['user_id'])` أو `User.query.get(writer_id)`). تجلب قصص هذا المستخدم مع تقييماتها (قد تحتاج لاستعلام `JOIN` أو علاقة في SQLAlchemy). ترسل البيانات للقالب.
        *   **Template:** `templates/user/writer_profile.html`. تعرض معلومات المستخدم وقائمة القصص مع التقييمات والروابط.

## 2. ملفات الإعداد والمساعدة (Config, Models, Helpers)

*   **`databass.php`:**
    *   **PHP:** طريقة اتصال بسيطة باستخدام `mysqli`. تطبع رسالة نجاح وتغلق الاتصال فوراً (غير عملي للتطبيق).
    *   **Flask:** يتم تجاهل هذا الملف لصالح إعداد `Flask-SQLAlchemy` في `config.py` و `app.py`.

*   **`db.php`:**
    *   **PHP:** طريقة اتصال أفضل باستخدام `PDO` مع خيارات جيدة. تُرجع كائن PDO ليتم استخدامه في ملفات أخرى.
    *   **Flask:** تُستبدل وظيفتها بإعداد `SQLAlchemy`:
        *   `config.py`: يحتوي على `SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://user:password@host/db_name'`.
        *   `app.py`: `from flask_sqlalchemy import SQLAlchemy; db = SQLAlchemy(app)`
        *   `models.py`: يحتوي على تعريفات النماذج (`class User(db.Model): ...`).

*   **`header.php`:**
    *   **PHP:** جزء HTML يتضمن شعار الموقع، وروابط تسجيل الدخول/الخروج بناءً على الجلسة، وقائمة بالتصنيفات. يتم تضمينه في صفحات أخرى.
    *   **Flask:**
        *   **Template:** `templates/includes/header.html`. يستخدم `{{ url_for('...') }}` للروابط. يستخدم `{% if session.username %}` للجزء الديناميكي. يستخدم حلقة لعرض التصنيفات.
        *   **Layout:** يتم تضمين هذا الملف عادة في `templates/layout.html` الذي ترث منه الصفحات الأخرى.

*   **`IDs.php`:**
    *   **PHP:** يُرجع مصفوفة بمعرفات مثال.
    *   **Flask:** هذه الطريقة ليست شائعة في Flask. توليد المعرفات (IDs) يتم عادة بواسطة قاعدة البيانات (primary key auto-increment) أو باستخدام مكتبة مثل `uuid` عند الحاجة لمعرفات فريدة عالمياً. يمكن وضع منطق توليد ID مخصص في `helpers.py` أو ضمن نماذج `models.py` إذا لزم الأمر.

*   **`Packages.php`:**
    *   **PHP:** يبدو أنه يهدف لتحميل الاعتماديات (مثل `vendor/autoload.php` لـ Composer).
    *   **Flask:** تتم إدارة الاعتماديات باستخدام `pip` وملف `requirements.txt`. يتم استيراد المكتبات باستخدام `import` في ملفات Python (`.py`).

*   **`Sessionss.php`:**
    *   **PHP:** يبدأ الجلسة ويقوم بتهيئة بعض متغيرات الجلسة إذا لم تكن موجودة.
    *   **Flask:** Flask يتعامل مع الجلسات تلقائيًا عند استخدام `flask.session`. تحتاج فقط إلى تعيين `app.secret_key` في `config.py`. يمكنك تعيين قيم افتراضية في الجلسة عند الحاجة داخل الدوال (routes).

*   **`story_functions.php`:**
    *   **PHP:** يحتوي على دالة `getPendingStories` التي تأخذ كائن PDO وتستعلم عن القصص المعلقة. مكان جيد لفصل منطق الاستعلام.
    *   **Flask:**
        *   **Models:** يتم تعريف نموذج `Story` في `models.py` مع حقوله وعلاقاته.
        *   **Logic:** الاستعلامات تتم باستخدام SQLAlchemy ORM مباشرة في الدوال (routes) أو يمكن إنشاء دوال مساعدة في `helpers.py` أو كـ class methods في `models.py`. مثال: `pending_stories = Story.query.filter_by(status='pending').order_by(Story.submission_date).all()`

## 3. نقاط نهاية API (للطلبات من JavaScript)

*   **`update_story_status.php`:**
    *   **PHP:** نقطة نهاية API تستقبل طلب POST (يفترض JSON) لتغيير حالة القصة (قبول/رفض). تتحقق من صلاحيات المدير، تتصل بقاعدة البيانات، تنفذ التحديث، وتعيد استجابة JSON.
    *   **Flask:**
        *   **Route:** دالة في `app.py` (أو blueprint) مرتبطة بـ `/api/stories/<story_id>/status` (أو مسار مشابه)، محددة لاستقبال طلبات `POST` أو `PUT`.
        *   **Logic:** تستخدم `@login_required`, `@admin_required`. تقرأ `request.get_json()`. تتحقق من المدخلات. تستعلم عن القصة باستخدام `story_id`. تحدث حالتها (`story.status = new_status; db.session.commit()`). تعيد استجابة JSON باستخدام `jsonify({'success': True, 'message': '...'})` أو رسالة خطأ مناسبة مع رمز حالة HTTP صحيح (403, 404, 400, 500).

## 4. ملفات غير مكتملة أو أجزاء HTML

*   **`center_country.php`:**
    *   **PHP:** مجرد عنصر `<select>` بقائمة دول. ليس ملفًا كاملاً.
    *   **Flask:** يمكن أن يكون جزءًا من قالب أكبر (مثل نموذج تسجيل المركز)، أو يتم تضمينه كـ snippet باستخدام `{% include 'templates/center/_country_select.html' %}`. بيانات الدول قد تأتي من `helpers.py` أو ملف إعدادات.
*   **`register.php`:**
    *   **PHP:** الملف فارغ.
    *   **Flask:** يفترض أن يقابله مسار ونموذج لتسجيل المستخدم العادي (`/register`, `templates/auth/register_user.html`, `UserRegistrationForm`).# مشروع عوالمنا - Flask
