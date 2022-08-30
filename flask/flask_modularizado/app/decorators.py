import jwt

from functools import wraps
from flask import request, jsonify
from app.config import Config


## Decorator that looks for a token in the request to validate the user authentication
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'No se encontro token!'}), 403
        try:
            data = jwt.decode(token, Config.SECRET_KEY)
            if 'userobj' in data:
                return f(*args, **kwargs)
            else:
                return jsonify({'message': 'Token inválido'}), 403
        except Exception as e:
            print("ERROR (decorators/token_required): ", e)
            return jsonify({'message': 'Token error'}), 403
    return decorated

