from flask import Blueprint

visor = Blueprint('visor', __name__, url_prefix="/visor")

from . import views