# app/models.py
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

# --- Association Table for Story Categories ---
story_category_association = db.Table('story_category',
    db.Column('story_id', db.Integer, db.ForeignKey('story.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

# --- User Model ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256)) # زيادة الطول لاستيعاب التجزئات الأقوى
    role = db.Column(db.String(20), index=True, default='reader') # Roles: reader, writer, center_admin, admin, super_admin
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # User can be an author of stories
    stories_authored = db.relationship('Story', backref='author', lazy='dynamic', foreign_keys='Story.author_id')
    # User can give ratings
    ratings_given = db.relationship('Rating', backref='rater', lazy='dynamic', foreign_keys='Rating.user_id')
    # Additional profile fields can be added here (e.g., profile_picture, bio)
    # Relationships for educational centers (if user represents a center admin)
    educational_center_id = db.Column(db.Integer, db.ForeignKey('educational_center.id'), nullable=True)

    # Password handling
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Roles check methods (example)
    def is_admin(self):
        return self.role in ['admin', 'super_admin']

    def is_writer(self):
        return self.role == 'writer'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

# --- Educational Center Model ---
class EducationalCenter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), index=True, unique=True, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120), unique=True, nullable=False)
    submission_date = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    # Relationship to users who manage this center
    admins = db.relationship('User', backref='educational_center', lazy='dynamic')
    # Relationship to teachers/students associated with the center (could be more complex)
    teachers = db.relationship('Teacher', backref='center', lazy='dynamic')
    students = db.relationship('Student', backref='center', lazy='dynamic')

    def __repr__(self):
        return f'<EducationalCenter {self.name} ({self.status})>'

# --- Story Model ---
class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), index=True, nullable=False)
    short_description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True) # Maybe markdown or plain text
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # The user who wrote the story
    author_name = db.Column(db.String(64), nullable=True) # Denormalized author name (set during creation)
    submission_date = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    publish_date = db.Column(db.DateTime, index=True, nullable=True) # Set when approved
    status = db.Column(db.String(20), index=True, default='pending') # pending, approved, rejected
    pdf_path = db.Column(db.String(300), nullable=True) # Path to the uploaded PDF file relative to UPLOAD_FOLDER
    view_count = db.Column(db.Integer, default=0)
    # Many-to-Many relationship with Category
    categories = db.relationship('Category', secondary=story_category_association,
                                 backref=db.backref('stories', lazy='dynamic'), lazy='dynamic')
    # One-to-Many relationship with Ratings
    ratings_received = db.relationship('Rating', backref='story', lazy='dynamic', foreign_keys='Rating.story_id')

    # Helper to get average rating (consider performance for many ratings)
    def average_rating(self):
        ratings = [r.rating for r in self.ratings_received]
        if not ratings:
            return 0
        return sum(ratings) / len(ratings)

    def __repr__(self):
        return f'<Story {self.title} by {self.author_name}>'


# --- Category Model ---
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False) # For URL generation (e.g., "khayal-elmi")

    def __repr__(self):
        return f'<Category {self.name}>'


# --- Rating Model ---
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False) # e.g., 1 to 5 stars
    comment = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Who gave the rating
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False) # Which story was rated

    __table_args__ = (db.UniqueConstraint('user_id', 'story_id', name='_user_story_uc'),) # User can rate a story only once

    def __repr__(self):
        return f'<Rating {self.rating} stars for Story {self.story_id} by User {self.user_id}>'


# --- Subscription Model (Example) ---
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan = db.Column(db.String(50)) # e.g., 'monthly', 'yearly'
    start_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active') # active, cancelled, expired

    user = db.relationship('User', backref=db.backref('subscriptions', lazy='dynamic'))

    def __repr__(self):
        return f'<Subscription {self.plan} for User {self.user_id}>'


# --- Teacher/Student Models (Simple Examples, link to Center) ---
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    center_id = db.Column(db.Integer, db.ForeignKey('educational_center.id'), nullable=False)
    # Add other teacher details if needed

    def __repr__(self):
        return f'<Teacher {self.email}>'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False) # Or maybe student ID
    name = db.Column(db.String(100), nullable=True)
    center_id = db.Column(db.Integer, db.ForeignKey('educational_center.id'), nullable=False)
    # Add other student details if needed

    def __repr__(self):
        return f'<Student {self.username}>'


# --- Flask-Login user loader callback ---
@login_manager.user_loader
def load_user(id):
    """Loads user object from the database based on the ID stored in the session."""
    return User.query.get(int(id))