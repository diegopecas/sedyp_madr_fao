from flask import Blueprint

report = Blueprint('reports', __name__, url_prefix="/dataStudio")

from . import views