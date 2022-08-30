import jwt

from . import user
from flask import request, jsonify
from app.user.database_manager import verify_user_code, update_user_info, get_users, change_user_rol
from app.user.database_manager import review_notification, change_password
from app.decorators import token_required
from app.eventos.database_manager import search_document_type
from app.helpers import raise_exception
from app.exceptions import CustomException
from app.services.database_service import DatabaseService
from app.config import Config


# Validate user email route using the code inside the url
@user.route('/validate', methods=['POST'])
def validate():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()

        code = request.get_json()['code']
        res = verify_user_code(code, connection)

        if(res[1] != 200):
            raise_exception(res[0].to_dict()['message'], res[0].to_dict()['error'])

    except CustomException as e:
      connection.rollback()
      print("ERROR (user/views/validate): ",e.to_dict()['error'])
      return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
      connection.rollback()
      print("ERROR (user/views/validate): ",e)
      return jsonify({'message': 'Ha ocurrido un error inesperado'}), 500
    else:
      connection.commit()
      return jsonify(res[0]), 200
    finally:
      if connection:
        if not connection.closed:
          connection.close()


# This endpoint checks that the code sended is the one able to change the password and changes the password too
@user.route('/forgotPassword', methods=['POST'])
def reset_password():
  try:
    db_service = DatabaseService()
    connection = db_service.get_connection()

    code = request.get_json()['code']
    password = request.get_json()['password']
    changed = change_password(code, password, connection)
    if changed[1] != 200:
      raise_exception(changed[0].to_dict()['message'],  changed[0].to_dict()['error'])

  except CustomException as e:
    connection.rollback()
    print("ERROR (user/views/reset_password): ",e.to_dict()['error'])
    return jsonify({'message': e.to_dict()['message']}), 500
  except Exception as e:
    connection.rollback()
    print("ERROR (user/views/reset_password): ",e)
    return jsonify({'message': 'Ha ocurrido un error inesperado'}), 500
  else:
    connection.commit()
    return jsonify(changed[0]), 200
  finally:
    if not connection.closed:
          connection.close()
  

# Endpoint to updat the user information
@user.route('/updateUser', methods=['POST'])
@token_required
def update_user():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()

        obj = request.get_json()['obj']
        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        res = update_user_info(obj, connection, id_user)

        if res[1] == 401:
            raise_exception('No tiene permisos para realizar esta operacion', 'No tiene permisos para realizar esta operacion')
        elif(res[1] != 200):
            raise_exception(res[0].to_dict()['message'], res[0].to_dict()['error'])


    except CustomException as e:
      connection.rollback()
      print("ERROR (user/views/update_user): ", e.to_dict()['error'])
      return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
      connection.rollback()
      print("ERROR (user/views/update_user): ", e)
      return jsonify({'message': 'Ha ocurrido un error inesperado'}), 500
    else:
      connection.commit()
      return jsonify(res[0]), res[1]
    finally:
      if not connection.closed:
        connection.close()



# Search the documents types
@user.route('/getDataDocumentType', methods=['GET'])
def get_data_document_type():
  try:
    # consultar tipos de documento.
    db_service = DatabaseService()
    connection = db_service.get_connection()

    docType = search_document_type(connection)

    if(docType[1] != 200):
      raise_exception(docType[0].to_dict()['message'], docType[0].to_dict()['error'])

    resData = {'documentType':docType[0]}

  except CustomException as e:
    connection.rollback()
    print("ERROR (user/views/get_data_document_type): ", e.to_dict()['error'])
    return jsonify({'message': e.to_dict()['message']}), 500
  except Exception as e:
    connection.rollback()
    print("ERROR (user/views/get_data_document_type): ", e)
    return jsonify({'message': 'No se han podido obtener los datos de los tipos de documentos'}), 500
  else:
    return jsonify({
      'message': {
        **resData
      },
      'error': False
    }), 200
  finally:
      if not connection.closed:
          connection.close()


# Endpoint to get the users and their roles
@user.route('/getUsers', methods=['GET'])
@token_required
def rol_manage():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()

        cursor = connection.cursor()
        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 3)
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
            res = get_users(connection)
            if res[1] != 200:
                raise_exception(res[0].to_dict()['message'],  res[0].to_dict()['error'])
                
            break
        
        if not _perm:
          _perm = True
          res = get_users(connection, id_user=id_user)
          if res[1] != 200:
            raise_exception(res[0].to_dict()['message'],  res[0].to_dict()['error'])

    except CustomException as e:
        connection.rollback()
        print("ERROR (user/views/rol_manage: )", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (user/views/rol_manage: )", e)
        return jsonify({'message': 'No se ha podido obtener los usuarios'}), 500
    else:
        if _perm:
            return jsonify(res[0]), 200
        else:
            return jsonify({'message': 'No tiene permisos para realizar esta operacion'}), 401
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()
        if connection:
            if not connection.closed:
                connection.close()


# Endpoint to change de rol of a user
@user.route('/changeRol', methods=['POST'])
@token_required
def change_rol():
  try:
    db_service = DatabaseService()
    connection = db_service.get_connection()

    cursor = connection.cursor()
    id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
    sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
    ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
    val = (id_user, 3)
    cursor.execute(sql, val)
    results = []
    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))

    res = []
    _perm = False
    for perm in results:
        if perm['id_permiso'] == 4:
            _perm = True
            obj = request.get_json()['obj']
            res = change_user_rol(obj, id_user, connection)
            if res[1] != 200:
              raise_exception(res[0].to_dict()['message'],  res[0].to_dict()['error'])

            break
  except CustomException as e:
    connection.rollback()
    print("ERROR (user/views/change_rol: )", e.to_dict()['error'])
    return jsonify({'message': e.to_dict()['message']}), 500
  except Exception as e:
    connection.rollback()
    print("ERROR (user/views/change_rol: )", e)
    return jsonify({'message': 'No se han podido obtener los datos'}), 500
  else:
    if _perm:
      connection.commit()
      return jsonify({'message': 'OK'}), 200
    else:
      return jsonify({'message': 'No tiene permisos para realizar esta operacion'}), 401
  finally:
    if connection:
      if not connection.closed:
        connection.close()


# This endpoint reviews a notification
@user.route('/notifications', methods=['POST']) 
@token_required
def notifications():
  try:
    db_service = DatabaseService()
    connection = db_service.get_connection()
    id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']

    if 'notificacion' in request.json:
      notif = request.json['notificacion']
      reviwed = review_notification(notif, id_user, connection)
      if reviwed[1] != 200:
        raise_exception(reviwed[0].to_dict()['message'],  reviwed[0].to_dict()['error'])
    else:
      raise_exception('No se ha recibido la notificación a revisar', 'Objeto notificacion no recibido')

  except CustomException as e:
    connection.rollback()
    print("ERROR (user/views/notifications: )", e.to_dict()['error'])
    return jsonify({'message': e.to_dict()['message']}), 500
  except Exception as e:
    connection.rollback()
    print("ERROR (user/views/notifications: )", e)
    return jsonify({'message': 'No se han podido revisar la notificación'}), 500
  else:
    connection.commit()
    return jsonify({'message': 'OK'}), 200
  finally:
    if connection:
      if not connection.closed:
        connection.close() 