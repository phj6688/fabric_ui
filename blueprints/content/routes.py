from flask import request, jsonify, current_app, session
from . import content_bp
from utils import login_required
import db_handler
from config import Config

@content_bp.route('/process', methods=['POST'])
@login_required
def process():
    """Process content through the Fabric API."""
    function_type = request.form.get('function_type')
    pattern = request.form.get('pattern')
    language = request.form.get('language', 'en')
    username = session.get('username')
    custom_query = request.form.get('custom_query')
    
    # Get the pattern mapping from config
    pattern_mapping = Config.PATTERN_MAPPINGS
    
    # Get the Fabric API service
    fabric_service = current_app.fabric_service
    
    result = None
    
    try:
        if function_type == 'youtube':
            url = request.form.get('youtube_url')
            if not url:
                return jsonify({'status': 'error', 'message': 'YouTube URL is required'}), 400
            
            # Log the action
            db_handler.log_action(username, f"Processed YouTube URL: {url}")
            
            # Use the fabric service to process the content
            result = fabric_service.process_youtube_content(
                url=url, 
                pattern=pattern_mapping.get(pattern, pattern),
                language=language,
                custom_query=custom_query if pattern == "custom_analysis" else None
            )
            
        elif function_type == 'text':
            text = request.form.get('text_input')
            if not text:
                return jsonify({'status': 'error', 'message': 'Text input is required'}), 400
            
            # Log the action
            db_handler.log_action(username, "Processed text input")
            
            # Use the fabric service to process the content
            result = fabric_service.process_text_content(
                text=text,
                pattern=pattern_mapping.get(pattern, pattern),
                language=language,
                custom_query=custom_query if pattern == "custom_analysis" else None
            )
            
        else:
            return jsonify({'status': 'error', 'message': 'Invalid function type'}), 400
        
        if result:
            return jsonify({
                'status': 'success',
                'stdout': result.get('stdout', ''),
                'stderr': result.get('stderr', '')
            })
        else:
            return jsonify({'status': 'error', 'message': 'No result from API'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error processing content: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"An error occurred: {str(e)}"
        }), 500