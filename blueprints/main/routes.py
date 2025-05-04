from flask import render_template, session
from . import main_bp
from utils import login_required

@main_bp.route('/')
@login_required
def index():
    """Render the main index page."""
    return render_template('index.html', username=session.get('username'))