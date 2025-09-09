from app import create_app
from app.models import User, Task
from app import db
import os

def setup_database():
    """Initialize database tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Test database connection
        try:
            db.session.execute('SELECT 1')
            print("✅ Database connection successful!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
            
        # Create a test user (optional)
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            test_user = User(
                email='test@example.com',
                username='testuser',
                interests='Testing, Development'
            )
            test_user.set_password('testpass123')
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created!")
        
        return True

if __name__ == '__main__':
    setup_database()
