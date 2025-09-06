from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from .models import Task
from . import db
from datetime import datetime

main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def home():
    return "<h1>Welcome to Smart Study Planner</h1><p><a href='/auth/login'>Login</a> | <a href='/auth/register'>Register</a></p>"

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# API endpoints for tasks
@main_bp.route('/api/tasks', methods=['GET','POST'])
@login_required
def tasks_api():
    if request.method == 'GET':
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        out = []
        for t in tasks:
            out.append({
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'due_date': t.due_date.isoformat(),
                'status': t.status
            })
        return jsonify(out)

    # POST - Create new task
    data = request.get_json()
    due = datetime.fromisoformat(data['due_date']).date()
    t = Task(
        user_id=current_user.id,
        title=data['title'],
        description=data.get('description',''),
        due_date=due
    )
    db.session.add(t)
    db.session.commit()
    
    # Return complete task object (FIXED)
    return jsonify({
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'due_date': t.due_date.isoformat(),
        'status': t.status
    })
# Add these new routes to your main.py file

@main_bp.route('/api/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
@login_required
def task_detail_api(task_id):
    # Get task and verify ownership
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    if request.method == 'DELETE':
        # Delete task
        db.session.delete(task)
        db.session.commit()
        return jsonify({'success': True})
    
    if request.method == 'PUT':
        # Update task status
        data = request.get_json()
        if 'status' in data:
            task.status = data['status']
            db.session.commit()
            
            return jsonify({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'due_date': task.due_date.isoformat(),
                'status': task.status
            })
        
        return jsonify({'error': 'No status provided'}), 400
