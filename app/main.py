from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from .models import Task
from . import db
from datetime import datetime
from .motivation_service import get_motivation_service



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
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    if request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return jsonify({'success': True})

    if request.method == 'PUT':
        data = request.get_json()
        if 'status' in data:
            old_status = task.status
            task.status = data['status']
            db.session.commit()

            # Award XP only if task just got completed (status changed from pending to completed)
            if old_status != 'completed' and task.status == 'completed':
                user = task.user
                xp_award = 5  # XP per completed task
                user.xp = (user.xp or 0) + xp_award
                db.session.commit()
            return jsonify({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'due_date': task.due_date.isoformat(),
                'status': task.status
            })
        return jsonify({'error': 'No status provided'}), 400

# Add this new route to your main.py
@main_bp.route('/api/gamification')
@login_required
def gamification_api():
    """Return user's gamification data"""
    return jsonify({
        'xp': current_user.xp,
        'level': current_user.get_level(),
        'streak': current_user.streak,
        'total_days_logged': current_user.total_days_logged,
        'xp_for_next_level': current_user.get_xp_for_next_level(),
        'level_progress': current_user.get_level_progress(),
        'last_login_date': current_user.last_login_date.isoformat() if current_user.last_login_date else None
    })

# Add this import at the top


# Update the import
from .motivation_service import get_motivation_service

# Update the route
@main_bp.route('/api/motivation')
@login_required
def motivation_api():
    """Generate personalized motivational message"""
    try:
        api_key = current_app.config.get('GEMINI_API_KEY')
        motivation_service = get_motivation_service(api_key)
        message = motivation_service.generate_personalized_motivation(current_user)
        
        return jsonify({
            'message': message,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'message': "Keep pushing forward! Every step counts! 💪",
            'generated_at': datetime.now().isoformat(),
            'error': str(e)
        }), 200

# Add this TEMPORARY debug route to main.py
@main_bp.route('/api/debug-config')
@login_required
def debug_config():
    """Debug configuration - REMOVE IN PRODUCTION"""
    api_key = current_app.config.get('GEMINI_API_KEY', 'NOT_SET')
    return jsonify({
        'api_key_configured': len(api_key) > 0,
        'api_key_length': len(api_key),
        'api_key_preview': api_key[:10] + "..." if len(api_key) > 10 else api_key
    })

