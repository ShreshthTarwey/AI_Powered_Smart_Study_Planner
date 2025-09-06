from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(120))
    password_hash = db.Column(db.String(200), nullable=False)
    interests = db.Column(db.String(300))
    
    # Gamification fields
    xp = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    last_login_date = db.Column(db.Date, default=None)  # NEW: Track last login
    total_days_logged = db.Column(db.Integer, default=0)  # NEW: Total login days
    
    tasks = db.relationship('Task', backref='user', lazy=True)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)
    
    # NEW: Gamification methods
    def update_daily_login(self):
        """
        Update user's login streak and XP when they log in
        """
        today = date.today()

        # Initialize None values to defaults
        if self.total_days_logged is None:
            self.total_days_logged = 0
        if self.streak is None:
            self.streak = 0
        if self.xp is None:
            self.xp = 0
        
        # If first login ever
        if self.last_login_date is None:
            self.streak = 1
            self.total_days_logged = 1
            self.xp += 10  # Award daily XP
            self.last_login_date = today
            db.session.commit()
            return True, {
                'daily_xp': 10,
                'streak_bonus': 0,
                'current_streak': self.streak,
                'total_xp': self.xp
            }

        # If user already logged in today, don't give XP again
        if self.last_login_date == today:
            return False, "Already logged in today"

        # Check if login is consecutive (yesterday or today)
        days_diff = (today - self.last_login_date).days
        
        if days_diff == 1:
            # Consecutive day - increase streak
            self.streak += 1
        elif days_diff > 1:
            # Missed days - reset streak
            self.streak = 1

        # Award daily XP
        daily_xp = 10
        self.xp += daily_xp

        # Award streak bonus (every 7 days)
        streak_bonus = 0
        if self.streak > 0 and self.streak % 7 == 0:
            streak_bonus = 70
            self.xp += streak_bonus

        # Update tracking fields
        self.last_login_date = today
        self.total_days_logged += 1

        # Commit changes
        db.session.commit()

        return True, {
            'daily_xp': daily_xp,
            'streak_bonus': streak_bonus,
            'current_streak': self.streak,
            'total_xp': self.xp
        }
    
    def get_level(self):
        """Calculate user level based on XP (100 XP per level)"""
        return self.xp // 100 + 1
    
    def get_xp_for_next_level(self):
        """Get XP needed for next level"""
        current_level = self.get_level()
        xp_for_next_level = current_level * 100
        return xp_for_next_level - self.xp
    
    def get_level_progress(self):
        """Get progress percentage for current level (0-100)"""
        current_level_base_xp = (self.get_level() - 1) * 100
        xp_in_current_level = self.xp - current_level_base_xp
        return (xp_in_current_level / 100) * 100


# Keep your existing Task model unchanged
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending/completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
