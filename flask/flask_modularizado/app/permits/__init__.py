from flask import Blueprint

permits = Blueprint('permits', __name__, url_prefix="/permits")

from . import views