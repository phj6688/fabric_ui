from flask import Blueprint

content_bp = Blueprint('content', __name__, url_prefix='/content')

from . import routes