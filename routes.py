from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, db
from models import User, Feedback, FeedbackRequest
from datetime import datetime
from sqlalchemy import func
from ai_utils import analyze_feedback_sentiment, generate_feedback_suggestions, extract_smart_tags, generate_performance_insights, improve_feedback_writing

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
    sentiment_query = db.session.query(
        Feedback.sentiment, func.count(Feedback.id)
    ).filter(
        Feedback.manager_id == manager.id
    ).group_by(Feedback.sentiment).all()
    
    # Convert to serializable format
    sentiment_data = [(row[0], row[1]) for row in sentiment_query]
    
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
    sentiment_query = db.session.query(
        Feedback.sentiment, func.count(Feedback.id)
    ).filter(
        Feedback.employee_id == employee.id
    ).group_by(Feedback.sentiment).all()
    
    # Convert to serializable format
    sentiment_data = [(row[0], row[1]) for row in sentiment_query]
    
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
        sentiment_query = db.session.query(
            Feedback.sentiment, func.count(Feedback.id)
        ).filter(
            Feedback.manager_id == user.id
        ).group_by(Feedback.sentiment).all()
    else:
        # Get sentiment data for this employee
        sentiment_query = db.session.query(
            Feedback.sentiment, func.count(Feedback.id)
        ).filter(
            Feedback.employee_id == user.id
        ).group_by(Feedback.sentiment).all()
    
    # Convert to serializable format
    sentiment_data = [(row[0], row[1]) for row in sentiment_query]
    
    result = {
        'labels': [item[0].title() for item in sentiment_data],
        'data': [item[1] for item in sentiment_data]
    }
    
    return jsonify(result)

# AI-powered routes
@app.route('/ai/suggestions')
def ai_suggestions():
    if 'user_id' not in session or session.get('role') != 'manager':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    return render_template('ai_suggestions.html')

@app.route('/ai/analyzer')
def feedback_analyzer():
    if 'user_id' not in session or session.get('role') != 'manager':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    return render_template('feedback_analyzer.html')

@app.route('/ai/insights')
def performance_insights():
    if 'user_id' not in session:
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    team_members = []
    if session.get('role') == 'manager':
        manager = User.query.get(session['user_id'])
        team_members = User.query.filter_by(manager_id=manager.id).all()
    
    return render_template('performance_insights.html', team_members=team_members)

@app.route('/ai/improver')
def feedback_improver():
    if 'user_id' not in session or session.get('role') != 'manager':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    return render_template('feedback_improver.html')

# AI API endpoints
@app.route('/api/ai-suggestions', methods=['POST'])
def api_ai_suggestions():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authorized'}), 401
    
    try:
        employee_role = request.form.get('employee_role')
        performance_area = request.form.get('performance_area')
        
        suggestions = generate_feedback_suggestions(employee_role, performance_area)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze-feedback', methods=['POST'])
def api_analyze_feedback():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authorized'}), 401
    
    try:
        strengths_text = request.form.get('strengths_text')
        areas_text = request.form.get('areas_text')
        
        sentiment, confidence, reasoning = analyze_feedback_sentiment(strengths_text, areas_text)
        
        # Extract smart tags
        combined_text = f"{strengths_text} {areas_text}"
        tags = extract_smart_tags(combined_text)
        
        return jsonify({
            'success': True,
            'sentiment': sentiment,
            'confidence': confidence,
            'reasoning': reasoning,
            'tags': tags
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/performance-insights', methods=['POST'])
def api_performance_insights():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authorized'}), 401
    
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')
        
        user = User.query.get(session['user_id'])
        employee = User.query.get(employee_id)
        
        # Check permissions
        if user.role == 'manager' and employee.manager_id != user.id:
            return jsonify({'success': False, 'error': 'Access denied'})
        elif user.role == 'employee' and employee_id != user.id:
            return jsonify({'success': False, 'error': 'Access denied'})
        
        # Get feedback history
        feedback_list = Feedback.query.filter_by(employee_id=employee_id).order_by(Feedback.created_at.desc()).all()
        
        # Prepare data for AI analysis
        feedback_history = []
        timeline_data = {'dates': [], 'scores': []}
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for feedback in feedback_list:
            feedback_history.append({
                'date': feedback.created_at.strftime('%Y-%m-%d'),
                'sentiment': feedback.sentiment,
                'strengths': feedback.strengths,
                'areas': feedback.areas_to_improve
            })
            
            timeline_data['dates'].append(feedback.created_at.strftime('%m/%d'))
            # Convert sentiment to score (positive=5, neutral=3, negative=1)
            score = 5 if feedback.sentiment == 'positive' else 3 if feedback.sentiment == 'neutral' else 1
            timeline_data['scores'].append(score)
            
            sentiment_counts[feedback.sentiment] += 1
        
        # Generate AI insights
        insights = generate_performance_insights(feedback_history)
        
        # Calculate metrics
        total_feedback = len(feedback_list)
        avg_sentiment = max(sentiment_counts, key=sentiment_counts.get) if total_feedback > 0 else 'neutral'
        
        # Determine trend
        if len(timeline_data['scores']) >= 2:
            recent_avg = sum(timeline_data['scores'][-3:]) / min(3, len(timeline_data['scores']))
            older_avg = sum(timeline_data['scores'][:-3]) / max(1, len(timeline_data['scores']) - 3) if len(timeline_data['scores']) > 3 else recent_avg
            improvement_trend = 'Improving' if recent_avg > older_avg else 'Declining' if recent_avg < older_avg else 'Stable'
        else:
            improvement_trend = 'Insufficient Data'
        
        # Extract growth areas from recent feedback
        growth_areas = []
        for feedback in feedback_list[:5]:  # Last 5 feedback items
            if feedback.tags:
                growth_areas.extend([tag.strip() for tag in feedback.tags.split(',')])
        growth_areas = list(set(growth_areas))[:6]  # Unique tags, max 6
        
        return jsonify({
            'success': True,
            'insights': insights,
            'metrics': {
                'total_feedback': total_feedback,
                'avg_sentiment': avg_sentiment,
                'improvement_trend': improvement_trend
            },
            'timeline_data': timeline_data,
            'growth_areas': growth_areas
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/improve-feedback', methods=['POST'])
def api_improve_feedback():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authorized'}), 401
    
    try:
        original_feedback = request.form.get('original_feedback')
        improved_feedback = improve_feedback_writing(original_feedback)
        
        return jsonify({
            'success': True,
            'improved_feedback': improved_feedback
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/request-feedback', methods=['GET', 'POST'])
def request_feedback():
    if 'user_id' not in session or session.get('role') != 'employee':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    employee = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        if not employee.manager:
            flash('No manager assigned to send request to', 'error')
            return redirect(url_for('employee_dashboard'))
        
        feedback_request = FeedbackRequest(
            employee_id=employee.id,
            manager_id=employee.manager_id,
            focus_area=request.form.get('focus_area') or None,
            specific_request=request.form.get('specific_request') or None,
            priority=request.form.get('priority', 'normal')
        )
        
        db.session.add(feedback_request)
        db.session.commit()
        
        flash('Feedback request sent to your manager!', 'success')
        return redirect(url_for('employee_dashboard'))
    
    # Get previous requests
    feedback_requests = FeedbackRequest.query.filter_by(employee_id=employee.id).order_by(FeedbackRequest.created_at.desc()).all()
    
    return render_template('request_feedback.html', employee=employee, feedback_requests=feedback_requests)

@app.route('/manage-employees')
def manage_employees():
    if 'user_id' not in session or session.get('role') != 'manager':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    manager = User.query.get(session['user_id'])
    team_members = User.query.filter_by(manager_id=manager.id).all()
    all_managers = User.query.filter_by(role='manager').all()
    
    return render_template('manage_employees.html', 
                         team_members=team_members, 
                         all_managers=all_managers)

@app.route('/add-employee', methods=['POST'])
def add_employee():
    if 'user_id' not in session or session.get('role') != 'manager':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    try:
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        assign_to_me = request.form.get('assign_to_me') == 'on'
        
        # Validation
        if len(username) < 3:
            flash('Username must be at least 3 characters long', 'error')
            return redirect(url_for('manage_employees'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return redirect(url_for('manage_employees'))
        
        # Check for existing username/email
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            flash('Username or email already exists', 'error')
            return redirect(url_for('manage_employees'))
        
        # Create new employee
        new_employee = User(
            username=username,
            email=email,
            role='employee',
            manager_id=session['user_id'] if assign_to_me else None
        )
        new_employee.set_password(password)
        
        db.session.add(new_employee)
        db.session.commit()
        
        flash(f'Employee {username} added successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding employee: {str(e)}', 'error')
    
    return redirect(url_for('manage_employees'))

@app.route('/reassign-employee', methods=['POST'])
def reassign_employee():
    if 'user_id' not in session or session.get('role') != 'manager':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    try:
        employee_id = request.form.get('employee_id')
        new_manager_id = request.form.get('new_manager_id')
        
        employee = User.query.get(employee_id)
        
        # Check if current manager owns this employee
        if employee.manager_id != session['user_id']:
            flash('You can only reassign your own team members', 'error')
            return redirect(url_for('manage_employees'))
        
        # Reassign employee
        employee.manager_id = int(new_manager_id) if new_manager_id else None
        db.session.commit()
        
        if new_manager_id:
            new_manager = User.query.get(new_manager_id)
            flash(f'{employee.username} reassigned to {new_manager.username}', 'success')
        else:
            flash(f'{employee.username} removed from all teams', 'info')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error reassigning employee: {str(e)}', 'error')
    
    return redirect(url_for('manage_employees'))

@app.route('/delete-employee', methods=['POST'])
def delete_employee():
    if 'user_id' not in session or session.get('role') != 'manager':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    try:
        employee_id = request.form.get('employee_id')
        employee = User.query.get(employee_id)
        
        # Check if current manager owns this employee
        if employee.manager_id != session['user_id']:
            flash('You can only delete your own team members', 'error')
            return redirect(url_for('manage_employees'))
        
        # Delete associated feedback and requests first
        Feedback.query.filter(
            (Feedback.employee_id == employee_id) | (Feedback.manager_id == employee_id)
        ).delete()
        
        FeedbackRequest.query.filter(
            (FeedbackRequest.employee_id == employee_id) | (FeedbackRequest.manager_id == employee_id)
        ).delete()
        
        # Delete the employee
        username = employee.username
        db.session.delete(employee)
        db.session.commit()
        
        flash(f'Employee {username} and all associated data deleted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting employee: {str(e)}', 'error')
    
    return redirect(url_for('manage_employees'))
