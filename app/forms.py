# -*- coding: utf-8 -*- # ضروري إذا كانت التعليقات أو التسميات بالعربية في بايثون 2، جيد وجوده دائماً
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, SelectMultipleField, HiddenField, RadioField, IntegerField # <-- أضف IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Optional, NumberRange # <-- أضف NumberRange
from app.models import User, Category, EducationalCenter
from wtforms.widgets import ListWidget, CheckboxInput
from flask_wtf.file import FileField, FileAllowed, FileRequired # <-- استيراد أنواع حقول الملفات

# --- Authentication Forms ---
class LoginForm(FlaskForm):
    """نموذج تسجيل الدخول."""
    username = StringField('اسم المستخدم', validators=[DataRequired(message="اسم المستخدم مطلوب.")])
    password = PasswordField('كلمة المرور', validators=[DataRequired(message="كلمة المرور مطلوبة.")])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

class RegistrationForm(FlaskForm):
    """نموذج إنشاء حساب مستخدم جديد (قارئ أو كاتب)."""
    username = StringField('اسم المستخدم', validators=[
        DataRequired(message="اسم المستخدم مطلوب."),
        Length(min=3, max=64, message="يجب أن يكون اسم المستخدم بين 3 و 64 حرفًا.")
    ])
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(message="البريد الإلكتروني مطلوب."),
        Email(message="يرجى إدخال بريد إلكتروني صالح.")
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message="كلمة المرور مطلوبة."),
        Length(min=6, message="يجب أن تكون كلمة المرور 6 أحرف على الأقل.")
    ])
    password2 = PasswordField(
        'تأكيد كلمة المرور', validators=[
            DataRequired(message="تأكيد كلمة المرور مطلوب."),
            EqualTo('password', message='كلمتا المرور غير متطابقتين.')
        ])
    # تحديد الدور عند التسجيل (يمكن تعديله أو فصله)
    role = SelectField('نوع الحساب', choices=[('reader', 'قارئ'), ('writer', 'كاتب')], default='reader', validators=[DataRequired()])
    accept_terms = BooleanField('أوافق على <a href="/terms">الشروط والأحكام</a>', validators=[DataRequired(message="يجب الموافقة على الشروط.")])
    submit = SubmitField('إنشاء حساب')

    # التحقق من أن اسم المستخدم غير موجود
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('اسم المستخدم هذا موجود بالفعل. يرجى اختيار اسم آخر.')

    # التحقق من أن البريد الإلكتروني غير موجود
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('هذا البريد الإلكتروني مسجل بالفعل. هل نسيت كلمة المرور؟')


class CenterRegistrationForm(FlaskForm):
    """نموذج تسجيل مركز تعليمي."""
    center_name = StringField('اسم المركز', validators=[DataRequired()])
    country = SelectField('البلد', choices=[], validators=[DataRequired()]) # سيتم ملء الخيارات من ملف أو helper
    contact_email = StringField('بريد التواصل الإلكتروني للمركز', validators=[DataRequired(), Email()])
    # قد تحتاج حقول أخرى مثل رقم الترخيص، عدد الموظفين المتوقع...
    # ... حقول لإنشاء حساب المدير للمركز ...
    admin_username = StringField('اسم مستخدم المسؤول', validators=[DataRequired(), Length(min=3, max=64)])
    admin_email = StringField('بريد المسؤول الإلكتروني', validators=[DataRequired(), Email()])
    admin_password = PasswordField('كلمة مرور المسؤول', validators=[DataRequired(), Length(min=6)])
    admin_password2 = PasswordField(
        'تأكيد كلمة مرور المسؤول', validators=[
            DataRequired(), EqualTo('admin_password', message='كلمتا مرور المسؤول غير متطابقتين.')
            ]
        )
    accept_terms = BooleanField('أوافق على <a href="/terms">الشروط والأحكام</a> الخاصة بالمراكز التعليمية', validators=[DataRequired()])
    submit = SubmitField('إرسال طلب تسجيل المركز')

    # التحقق المخصص
    def validate_center_name(self, center_name):
        center = EducationalCenter.query.filter_by(name=center_name.data).first()
        if center:
            raise ValidationError('اسم المركز التعليمي هذا مسجل بالفعل.')

    def validate_contact_email(self, contact_email):
        center = EducationalCenter.query.filter_by(contact_email=contact_email.data).first()
        if center:
            raise ValidationError('بريد التواصل هذا مستخدم بالفعل لمركز آخر.')

    def validate_admin_username(self, admin_username):
        user = User.query.filter_by(username=admin_username.data).first()
        if user:
            raise ValidationError('اسم مستخدم المسؤول هذا موجود بالفعل.')

    def validate_admin_email(self, admin_email):
        user = User.query.filter_by(email=admin_email.data).first()
        if user:
            raise ValidationError('بريد المسؤول الإلكتروني هذا موجود بالفعل.')


class ForgotPasswordForm(FlaskForm):
    """نموذج طلب استعادة كلمة المرور."""
    email = StringField('البريد الإلكتروني المسجل', validators=[DataRequired(), Email()])
    submit = SubmitField('إرسال رابط استعادة كلمة المرور')

class ResetPasswordForm(FlaskForm):
    """نموذج تعيين كلمة مرور جديدة."""
    password = PasswordField('كلمة المرور الجديدة', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        'تأكيد كلمة المرور الجديدة', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('تعيين كلمة المرور الجديدة')


# --- Story Forms ---
class StoryForm(FlaskForm):
    """نموذج إضافة أو تعديل قصة."""
    title = StringField('عنوان القصة', validators=[DataRequired(), Length(max=150)])
    short_description = TextAreaField('وصف موجز', validators=[Optional(), Length(max=500)]) # جعله اختياري
    content = TextAreaField('محتوى القصة (اختياري إذا وجد PDF)') # النص نفسه اختياري إذا كان سيرفع PDF
    # categories = SelectMultipleField('التصنيفات', coerce=int, widget=ListWidget(prefix_label=False), option_widget=CheckboxInput())
    categories = SelectMultipleField('التصنيفات', coerce=int) # استخدام SelectMultipleField القياسي أسهل
    pdf_file = FileField('ملف PDF للقصة (اختياري إذا تم إدخال المحتوى)', validators=[
        Optional(), # جعله اختياري
        FileAllowed(['pdf'], 'يُسمح بملفات PDF فقط!')
        ])
    status = SelectField('حالة النشر', choices=[('pending', 'إرسال للمراجعة'), ('draft', 'مسودة (حفظ دون إرسال)')], default='pending')
    submit = SubmitField('حفظ القصة')

    # تحميل قائمة التصنيفات بشكل ديناميكي
    def __init__(self, *args, **kwargs):
        super(StoryForm, self).__init__(*args, **kwargs)
        self.categories.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]

class RatingForm(FlaskForm):
    """نموذج لإضافة تقييم وتعليق على قصة."""
    rating = SelectField('التقييم (من 1 إلى 5 نجوم)',
                       choices=[(1, '★☆☆☆☆'), (2, '★★☆☆☆'), (3, '★★★☆☆'), (4, '★★★★☆'), (5, '★★★★★')],
                       coerce=int, # تحويل القيمة إلى رقم صحيح
                       validators=[DataRequired(message="التقييم مطلوب.")])

    # يمكنك إضافة تحقق لضمان وجود إما محتوى أو ملف PDF


# --- User Forms ---
class DeleteAccountForm(FlaskForm):
    """نموذج حذف الحساب."""
    reason = RadioField('سبب الحذف', choices=[
        ('no_longer_needed', 'لا أحتاجه بعد'),
        ('privacy_concern', 'قلق بشأن الخصوصية'),
        ('moving_to_another_service', 'الانتقال إلى خدمة أخرى'),
        ('other', 'أخرى (يرجى التوضيح)')
        ], validators=[DataRequired(message="يرجى تحديد سبب الحذف.")])
    additional_info = TextAreaField('معلومات إضافية (اختياري)')
    action = HiddenField() # لتحديد freeze أو delete عبر JavaScript
    confirm_password = PasswordField('تأكيد كلمة المرور الحالية', validators=[DataRequired()])
    submit_freeze = SubmitField('تجميد الحساب')
    submit_delete = SubmitField('حذف الحساب نهائياً')

# --- Center Forms ---
class TeacherEmailForm(FlaskForm):
    """نموذج لإدخال ايميلات المدرسين (سيتم إنشاؤه ديناميكيا في ال route)"""
    # سيتم إضافة الحقول بشكل ديناميكي في الدالة (route)
    submit = SubmitField('إرسال بيانات المعلمين')