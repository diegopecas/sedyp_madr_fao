from . import auth
from flask import request, jsonify
from app.auth.database_manager import login_user, register_user, send_reset_password_email
from app.helpers import raise_exception
from app.exceptions import CustomException
from app.services.database_service import DatabaseService


## Login user route
@auth.route('/login', methods=['POST'])
def login():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()

        email = ''
        password = ''
        if 'email' in request.get_json():
            if 'password' in request.get_json():
                email = request.get_json()['email']
                password = request.get_json()['password']
            else:
                raise_exception('No se ha enviado contraseña', 'No se ha enviado contraseña')
        else:
            raise_exception('No se ha enviado el correo', 'No se ha enviado el correo')
            
        res = login_user(email, password, connection)
        
        if res[1] == 404:
            connection.commit()
            return jsonify({'message': 'Usuario no encontrado'}), 500
        elif(res[1] != 200):
            raise_exception(res[0].to_dict()['message'], res[0].to_dict()['error'])

    except CustomException as e:
        connection.rollback()
        print("ERROR (auth/views/login): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (auth/views/login): ", e)
        return jsonify({'message': 'Ha ocurrido un error inesperado'}), 500
    else:
        connection.commit()
        return jsonify(res[0]), 200
    finally:
        if connection:
            if not connection.closed:
                connection.close()


# Register user route
@auth.route('/createUser', methods=['POST'])
def create_user():
    try: 
        db_service = DatabaseService()
        connection = db_service.get_connection()

        obj = request.get_json()['obj']
        res = register_user(obj, connection)

        if(res[1] != 200):
            raise_exception(res[0].to_dict()['message'], res[0].to_dict()['error'])

    except CustomException as e:
        connection.rollback()
        print("ERROR (auth/views/create_user): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500  
    except Exception as e:
        connection.rollback()
        print("ERROR (auth/views/create_user): ", e)
        return jsonify({'message': 'Ha ocurrido un error inesperado'}), 500
    else:
        connection.commit()
        return jsonify(res[0]), 200
    finally:
        if not connection.closed:
            connection.close()


# This endpoint is to reset the password when the user forgot their password
@auth.route('/forgotPassword', methods=['POST'])
def recover_account():
    try: 
        db_service = DatabaseService()
        connection = db_service.get_connection()

        email = request.get_json()['email']

        res = send_reset_password_email(email, connection)
        if res[1] != 200:
            raise_exception(res[0].to_dict()['message'],  res[0].to_dict()['error'])

    except CustomException as e:
        connection.rollback()
        print("ERROR (auth/views/recover_account): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500  
    except Exception as e:
        connection.rollback()
        print("ERROR (auth/views/recover_account): ", e)
        return jsonify({'message': 'Ha ocurrido un error inesperado'}), 500
    else:
        connection.commit()
        return jsonify(res[0]), 200
    finally:
        if not connection.closed:
            connection.close()
    


