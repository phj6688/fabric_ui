from flask import render_template, request, redirect, url_for, flash, session
from flask import current_app as app
from . import auth_bp
import db_handler

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db_handler.get_user(username)
        if user and user.verify_password(password):
            session['authenticated'] = True
            session['username'] = username
            db_handler.log_action(username, "User logged in")
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        else:
            app.logger.warning(f"Failed login attempt for user: {username}")
            flash('Invalid credentials', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """Handle user logout."""
    if 'username' in session:
        username = session.get('username')
        db_handler.log_action(username, "User logged out")
        
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))