from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'manager' or 'employee'
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    manager = db.relationship('User', remote_side=[id], backref='team_members')
    feedback_given = db.relationship('Feedback', foreign_keys='Feedback.manager_id', backref='manager')
    feedback_received = db.relationship('Feedback', foreign_keys='Feedback.employee_id', backref='employee')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    strengths = db.Column(db.Text, nullable=False)
    areas_to_improve = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)  # 'positive', 'neutral', 'negative'
    tags = db.Column(db.String(200), nullable=True)  # Comma-separated tags
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Feedback {self.id}>'

def create_default_users():
    """Create default users for testing"""
    # Check if users already exist
    if User.query.count() > 0:
        return
    
    # Create managers
    manager1 = User(
        username='john_manager',
        email='john@company.com',
        role='manager'
    )
    manager1.set_password('password123')
    
    manager2 = User(
        username='sarah_manager',
        email='sarah@company.com',
        role='manager'
    )
    manager2.set_password('password123')
    
    # Create employees
    employee1 = User(
        username='alice_employee',
        email='alice@company.com',
        role='employee'
    )
    employee1.set_password('password123')
    
    employee2 = User(
        username='bob_employee',
        email='bob@company.com',
        role='employee'
    )
    employee2.set_password('password123')
    
    employee3 = User(
        username='charlie_employee',
        email='charlie@company.com',
        role='employee'
    )
    employee3.set_password('password123')
    
    # Add to database
    db.session.add_all([manager1, manager2, employee1, employee2, employee3])
    db.session.commit()
    
    # Assign employees to managers
    employee1.manager_id = manager1.id
    employee2.manager_id = manager1.id
    employee3.manager_id = manager2.id
    
    db.session.commit()
