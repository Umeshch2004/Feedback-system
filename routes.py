from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, db
from models import User, Feedback
from datetime import datetime
from sqlalchemy import func

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if user.role == 'manager':
        return redirect(url_for('manager_dashboard'))
    else:
        return redirect(url_for('employee_dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            flash(f'Welcome, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/manager/dashboard')
def manager_dashboard():
    if 'user_id' not in session or session.get('role') != 'manager':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    manager = User.query.get(session['user_id'])
    team_members = User.query.filter_by(manager_id=manager.id).all()
    
    # Get feedback stats
    feedback_stats = []
    for employee in team_members:
        feedback_count = Feedback.query.filter_by(employee_id=employee.id).count()
        recent_feedback = Feedback.query.filter_by(employee_id=employee.id).order_by(Feedback.created_at.desc()).first()
        unacknowledged_count = Feedback.query.filter_by(employee_id=employee.id, acknowledged=False).count()
        
        feedback_stats.append({
            'employee': employee,
            'feedback_count': feedback_count,
            'recent_feedback': recent_feedback,
            'unacknowledged_count': unacknowledged_count
        })
    
    # Get sentiment distribution
    sentiment_data = db.session.query(
        Feedback.sentiment, func.count(Feedback.id)
    ).filter(
        Feedback.manager_id == manager.id
    ).group_by(Feedback.sentiment).all()
    
    return render_template('manager_dashboard.html', 
                         manager=manager, 
                         team_members=team_members,
                         feedback_stats=feedback_stats,
                         sentiment_data=sentiment_data)

@app.route('/employee/dashboard')
def employee_dashboard():
    if 'user_id' not in session or session.get('role') != 'employee':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    employee = User.query.get(session['user_id'])
    feedback_list = Feedback.query.filter_by(employee_id=employee.id).order_by(Feedback.created_at.desc()).all()
    
    # Get sentiment distribution for this employee
    sentiment_data = db.session.query(
        Feedback.sentiment, func.count(Feedback.id)
    ).filter(
        Feedback.employee_id == employee.id
    ).group_by(Feedback.sentiment).all()
    
    return render_template('employee_dashboard.html', 
                         employee=employee, 
                         feedback_list=feedback_list,
                         sentiment_data=sentiment_data)

@app.route('/feedback/submit/<int:employee_id>', methods=['GET', 'POST'])
def submit_feedback(employee_id):
    if 'user_id' not in session or session.get('role') != 'manager':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    manager = User.query.get(session['user_id'])
    employee = User.query.get(employee_id)
    
    # Check if employee belongs to this manager
    if not employee or employee.manager_id != manager.id:
        flash('Employee not found or not in your team', 'error')
        return redirect(url_for('manager_dashboard'))
    
    if request.method == 'POST':
        strengths = request.form['strengths']
        areas_to_improve = request.form['areas_to_improve']
        sentiment = request.form['sentiment']
        tags = request.form.get('tags', '')
        
        feedback = Feedback(
            manager_id=manager.id,
            employee_id=employee.id,
            strengths=strengths,
            areas_to_improve=areas_to_improve,
            sentiment=sentiment,
            tags=tags
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('manager_dashboard'))
    
    return render_template('submit_feedback.html', employee=employee)

@app.route('/feedback/history/<int:employee_id>')
def feedback_history(employee_id):
    if 'user_id' not in session:
        flash('Please log in', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    employee = User.query.get(employee_id)
    
    # Check access permissions
    if user.role == 'manager':
        if not employee or employee.manager_id != user.id:
            flash('Employee not found or not in your team', 'error')
            return redirect(url_for('manager_dashboard'))
    elif user.role == 'employee':
        if employee_id != user.id:
            flash('Access denied', 'error')
            return redirect(url_for('employee_dashboard'))
    
    feedback_list = Feedback.query.filter_by(employee_id=employee_id).order_by(Feedback.created_at.desc()).all()
    
    return render_template('feedback_history.html', 
                         employee=employee, 
                         feedback_list=feedback_list,
                         user_role=user.role)

@app.route('/feedback/edit/<int:feedback_id>', methods=['GET', 'POST'])
def edit_feedback(feedback_id):
    if 'user_id' not in session or session.get('role') != 'manager':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    manager = User.query.get(session['user_id'])
    feedback = Feedback.query.get(feedback_id)
    
    # Check if feedback belongs to this manager
    if not feedback or feedback.manager_id != manager.id:
        flash('Feedback not found or access denied', 'error')
        return redirect(url_for('manager_dashboard'))
    
    if request.method == 'POST':
        feedback.strengths = request.form['strengths']
        feedback.areas_to_improve = request.form['areas_to_improve']
        feedback.sentiment = request.form['sentiment']
        feedback.tags = request.form.get('tags', '')
        feedback.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Feedback updated successfully!', 'success')
        return redirect(url_for('feedback_history', employee_id=feedback.employee_id))
    
    return render_template('edit_feedback.html', feedback=feedback)

@app.route('/feedback/acknowledge/<int:feedback_id>', methods=['POST'])
def acknowledge_feedback(feedback_id):
    if 'user_id' not in session or session.get('role') != 'employee':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    employee = User.query.get(session['user_id'])
    feedback = Feedback.query.get(feedback_id)
    
    # Check if feedback belongs to this employee
    if not feedback or feedback.employee_id != employee.id:
        flash('Feedback not found or access denied', 'error')
        return redirect(url_for('employee_dashboard'))
    
    feedback.acknowledged = True
    feedback.acknowledged_at = datetime.utcnow()
    db.session.commit()
    
    flash('Feedback acknowledged!', 'success')
    return redirect(url_for('employee_dashboard'))

@app.route('/api/sentiment-data')
def sentiment_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401
    
    user = User.query.get(session['user_id'])
    
    if user.role == 'manager':
        # Get sentiment data for all team members
        sentiment_data = db.session.query(
            Feedback.sentiment, func.count(Feedback.id)
        ).filter(
            Feedback.manager_id == user.id
        ).group_by(Feedback.sentiment).all()
    else:
        # Get sentiment data for this employee
        sentiment_data = db.session.query(
            Feedback.sentiment, func.count(Feedback.id)
        ).filter(
            Feedback.employee_id == user.id
        ).group_by(Feedback.sentiment).all()
    
    result = {
        'labels': [item[0].title() for item in sentiment_data],
        'data': [item[1] for item in sentiment_data]
    }
    
    return jsonify(result)
