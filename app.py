from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import logging
from logging.handlers import RotatingFileHandler
import secrets
import subprocess
import shlex
from db_handler import db, log_action, get_user
from functools import wraps
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from werkzeug.middleware.proxy_fix import ProxyFix

# --- Define APPLICATION_ROOT at the top ---
APPLICATION_ROOT = os.environ.get('APPLICATION_ROOT', '/contentmaster')

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session or not session['authenticated']:
            return redirect(url_for('login', _external=True, _scheme='https'))
        return f(*args, **kwargs)
    return decorated_function

# Pattern mappings
PATTERN_MAPPINGS = {
    "executive_summary": "summarize",
    "key_points": "summarize_micro",
    "insight_extraction": "extract_wisdom",
    "core_concept": "extract_main_idea",
    "action_steps": "extract_instructions",
    "prompt_enhancement": "improve_prompt",
    "content_polish": "improve_writing",
    "custom_analysis": "other"
}

# Flask app init
app = Flask(__name__)
app.config['APPLICATION_ROOT'] = APPLICATION_ROOT
app.config['SERVER_NAME'] = None #'apps.peyman.io'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Fix for handling URLs with nginx reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Session cookie configuration
if APPLICATION_ROOT != '/':
    app.config['SESSION_COOKIE_PATH'] = APPLICATION_ROOT
    app.config['SESSION_COOKIE_NAME'] = 'contentmaster_session'
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Prefix middleware for subpath routing
if APPLICATION_ROOT != '/':
    class PrefixMiddleware:
        def __init__(self, app, prefix):
            self.app = app
            self.prefix = prefix

        def __call__(self, environ, start_response):
            if environ['PATH_INFO'].startswith(self.prefix):
                environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
                environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)



# SQLAlchemy config
DATABASE_DIR = '/app/data'
os.makedirs(DATABASE_DIR, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(DATABASE_DIR, 'fabric-ui.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Logging setup
if not app.debug:
    log_dir = os.path.join(DATABASE_DIR, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(os.path.join(log_dir, 'contentmaster.log'), maxBytes=10485760, backupCount=5)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('ContentMaster startup')

# DB init
with app.app_context():
    db.create_all()

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user(username)
        if user and user.verify_password(password):
            session['authenticated'] = True
            session['username'] = username
            log_action(username, "User logged in")
            flash('Login successful!', 'success')
            return redirect(url_for('index', _external=True, _scheme='https'))
        else:
            app.logger.warning(f"Failed login attempt for user: {username}")
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        log_action(session.get('username'), "User logged out")
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login', _external=True, _scheme='https'))

@app.route('/')
@login_required
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/process', methods=['POST'])
@login_required
def process():
    function_type = request.form.get('function_type')
    pattern = request.form.get('pattern')
    language = request.form.get('language', 'en')
    username = session.get('username')
    cmd = ""
    try:
        if function_type == 'youtube':
            url = request.form.get('youtube_url')
            if not url:
                return jsonify({'status': 'error', 'message': 'YouTube URL is required'}), 400
            quoted_url = shlex.quote(url)
            log_action(username, f"Processed YouTube URL: {url}")
            if pattern == "custom_analysis":
                custom_query = request.form.get('custom_query')
                cmd = f"fabric -y {quoted_url} {shlex.quote(custom_query)} -g {language}"
            else:
                mapped_pattern = PATTERN_MAPPINGS.get(pattern)
                cmd = f"fabric -y {quoted_url} -p {mapped_pattern} -g {language}"
        elif function_type == 'text':
            text = request.form.get('text_input')
            if not text:
                return jsonify({'status': 'error', 'message': 'Text input is required'}), 400
            quoted_text = shlex.quote(text)
            log_action(username, "Processed text input")
            if pattern == "custom_analysis":
                custom_query = request.form.get('custom_query')
                cmd = f'echo {quoted_text} | fabric -p "{shlex.quote(custom_query)}" -g {language}'
            else:
                mapped_pattern = PATTERN_MAPPINGS.get(pattern)
                cmd = f'echo {quoted_text} | fabric -p {mapped_pattern} -g {language}'
        else:
            return jsonify({'status': 'error', 'message': 'Invalid function type'}), 400
        app.logger.info(f"Executing command: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        app.logger.info(f"Command completed with return code: {result.returncode}")
        return jsonify({
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr
        })
    except subprocess.TimeoutExpired:
        app.logger.error("Command execution timed out")
        return jsonify({"status": "error", "message": "Command timed out after 60 seconds"})
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"})

# Dispatcher to expose at /contentmaster
application = DispatcherMiddleware(Flask('dummy'), {
    APPLICATION_ROOT: app
})

if __name__ == "__main__":
    run_simple('0.0.0.0', 8700, application)