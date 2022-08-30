import jwt

from . import audit
from app.decorators import token_required
from app.services.database_service import DatabaseService
from app.exceptions import CustomException
from flask import request, jsonify
from app.config import Config
from app.helpers import raise_exception
from app.audit.database_manager import get_audits


@audit.route('/', methods=['GET'])
@token_required
def index():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 4)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        res = []
        _perm = False
        for perm in results:
            if perm['id_permiso'] == 1:
                _perm = True
                res = get_audits(connection)
                if res[1] != 200:
                    raise_exception(res[0].to_dict()['message'],  res[0].to_dict()['error'])
                break
    except CustomException as e:
        connection.rollback()
        print("ERROR (audit/views/index): ", e.to_dict['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (audit/views/index): ", e)
        return jsonify({'message': 'Ocurrió un error al obtener los datos de auditoría'}), 500
    else:
        if _perm:
            return jsonify(res[0]), 200
        else:
            return jsonify({'message': 'No tienes permiso para ver los registros de auditoría'}), 401
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()
        if connection:
            if not connection.closed:
                connection.close()
