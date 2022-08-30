from flask import Blueprint

event = Blueprint('eventos', __name__, url_prefix="/event")

from . import views