import jwt

from . import permits
from app.decorators import token_required
from flask import request, jsonify
from app.services.database_service import DatabaseService
from app.exceptions import CustomException
from app.helpers import raise_exception
from app.permits.database_manager import get_roles, get_modules, get_permissions, get_perm_per_rol, full_perms
from app.permits.database_manager import change_p_status, add_rol, delete_rol
from app.config import Config


# Get the roles, modules and permits
@permits.route('/', methods=['GET', 'POST'])
@token_required
def index():        
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'),
                            Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 3)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        _perm_add_rol = False
        _perm_see_rol = False

        if request.method == 'POST':
            for perm in results:
                if perm['id_permiso'] == 3:
                    _perm_add_rol = True
                    rol = request.get_json()['rol']
                    res_rol = add_rol(connection, rol, id_user)
                    if res_rol[1] != 200:
                        raise_exception(res_rol[0].to_dict()['message'],  res_rol[0].to_dict()['error'])

                    break
            
            for perm in results:
                if perm['id_permiso'] == 1:
                    _perm_see_rol = True
                    res_roles = get_roles(connection)
                    if res_roles[1] != 200:
                        raise_exception(res_roles[0].to_dict()[
                                        'message'],  res_roles[0].to_dict()['error'])

                    res_modulos = get_modules(connection)
                    if res_modulos[1] != 200:
                        raise_exception(res_modulos[0].to_dict()[
                                        'message'],  res_modulos[0].to_dict()['error'])

                    res_perms = get_permissions(connection)
                    if res_perms[1] != 200:
                        raise_exception(res_perms[0].to_dict()[
                                        'message'],  res_perms[0].to_dict()['error'])

                    res_perm_per_role = get_perm_per_rol(connection)
                    if res_perm_per_role[1] != 200:
                        raise_exception(res_perm_per_role[0].to_dict()[
                                        'message'],  res_perm_per_role[0].to_dict()['error'])

                    res_full = full_perms(
                        res_roles[0], res_modulos[0], res_perms[0], res_perm_per_role[0])
                    if res_full[1] != 200:
                        raise_exception(res_full[0].to_dict()[
                                        'message'],  res_full[0].to_dict()['error'])

                    break
                
        elif request.method == 'GET':
            for perm in results:
                if perm['id_permiso'] == 1:
                    _perm_see_rol = True
                    res_roles = get_roles(connection)
                    if res_roles[1] != 200:
                        raise_exception(res_roles[0].to_dict()[
                                        'message'],  res_roles[0].to_dict()['error'])

                    res_modulos = get_modules(connection)
                    if res_modulos[1] != 200:
                        raise_exception(res_modulos[0].to_dict()[
                                        'message'],  res_modulos[0].to_dict()['error'])

                    res_perms = get_permissions(connection)
                    if res_perms[1] != 200:
                        raise_exception(res_perms[0].to_dict()[
                                        'message'],  res_perms[0].to_dict()['error'])

                    res_perm_per_role = get_perm_per_rol(connection)
                    if res_perm_per_role[1] != 200:
                        raise_exception(res_perm_per_role[0].to_dict()[
                                        'message'],  res_perm_per_role[0].to_dict()['error'])

                    res_full = full_perms(
                        res_roles[0], res_modulos[0], res_perms[0], res_perm_per_role[0])
                    if res_full[1] != 200:
                        raise_exception(res_full[0].to_dict()[
                                        'message'],  res_full[0].to_dict()['error'])

                    break            

    except CustomException as e:
        connection.rollback()
        print("ERROR (permits/views/index): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (permits/views/index): ", e)
        return jsonify({'message': 'Ocurrio un error al obtener los permisos'}), 500
    else:
        if request.method == 'GET':
            if _perm_see_rol:
                return jsonify({'message': res_full}), 200
            else:
                return jsonify({'message': 'No tiene permisos para ver los roles'}), 401
        if request.method == 'POST':
            if _perm_add_rol and _perm_see_rol:
                connection.commit()
                return jsonify({'message': res_full}), 200
            elif not _perm_add_rol:
                connection.rollback()
                return jsonify({'message': 'No tiene permisos para crear roles'}), 401
            elif not _perm_see_rol:
                connection.commit()
                return jsonify({'message': 'Rol creado. No tiene permisos para ver los roles'}), 401    
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()

        if connection:
            if not connection.closed:
                connection.close()


# Activate or deactivate a rol per module
@permits.route('/permStatus', methods=['POST', 'DELETE'])
@token_required
def change_perm_status():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        perm_to_change = request.get_json()['permiso']

        remove = True if request.method == 'DELETE' else False

        id_user = jwt.decode(request.args.get('token'),
                             Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 3)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        _perm = False
        for perm in results:
            if perm['id_permiso'] == 4:
                _perm = True

                res = change_p_status(
                    connection, perm_to_change, id_user, remove)
                if res[1] != 200:
                    raise_exception(res[0].to_dict()[
                                    'message'],  res[0].to_dict()['error'])
                break

    except CustomException as e:
        connection.rollback()
        print("ERROR (permits/views/change_perm_status): ",
              e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (permits/views/change_perm_status): ", e)
        return jsonify({'message': 'Ocurrio un error al actualizar el permiso'}), 500
    else:
        if _perm:
            connection.commit()
            return jsonify({'message': 'OK'}), 200
        else:
            return jsonify({'message': 'No tiene permisos para realizar esta operacion'}), 401
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()

        if connection:
            if not connection.closed:
                connection.close()


# This endpoint is specific to delete a rol using a post request
@permits.route('/deleteRol', methods=['POST'])
@token_required
def delete_rol_view():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'),
                            Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 3)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        _perm_see_rol = False
        _perm_delete_rol = False
        
        for perm in results:
            if perm['id_permiso'] == 6:
                _perm_delete_rol = True
                rol = request.get_json()['rolDelete']['rol']
                res_rol = delete_rol(connection, rol, id_user)
                if res_rol[1] != 200:
                    raise_exception(res_rol[0].to_dict()['message'],  res_rol[0].to_dict()['error'])

                break

        for perm in results:
            if perm['id_permiso'] == 1:
                _perm_see_rol = True
                res_roles = get_roles(connection)
                if res_roles[1] != 200:
                    raise_exception(res_roles[0].to_dict()[
                                    'message'],  res_roles[0].to_dict()['error'])

                res_modulos = get_modules(connection)
                if res_modulos[1] != 200:
                    raise_exception(res_modulos[0].to_dict()[
                                    'message'],  res_modulos[0].to_dict()['error'])

                res_perms = get_permissions(connection)
                if res_perms[1] != 200:
                    raise_exception(res_perms[0].to_dict()[
                                    'message'],  res_perms[0].to_dict()['error'])

                res_perm_per_role = get_perm_per_rol(connection)
                if res_perm_per_role[1] != 200:
                    raise_exception(res_perm_per_role[0].to_dict()[
                                    'message'],  res_perm_per_role[0].to_dict()['error'])

                res_full = full_perms(
                    res_roles[0], res_modulos[0], res_perms[0], res_perm_per_role[0])
                if res_full[1] != 200:
                    raise_exception(res_full[0].to_dict()[
                                    'message'],  res_full[0].to_dict()['error'])

                break

    except CustomException as e:
        connection.rollback()
        print("ERROR (permits/views/delete_rol_view): ",
              e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (permits/views/delete_rol_view): ", e)
        return jsonify({'message': 'Ocurrio un error al borrar el rol'}), 500
    else:
        if _perm_delete_rol and _perm_see_rol:
            connection.commit()
            return jsonify({'message': res_full}), 200
        elif not _perm_delete_rol:
            connection.rollback()
            return jsonify({'message': 'No tiene permisos para crear roles'}), 401
        elif not _perm_see_rol:
            connection.commit()
            return jsonify({'message': 'Rol creado. No tiene permisos para ver los roles'}), 401
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()
        
        if connection:
            if not connection.closed:
                connection.close()

