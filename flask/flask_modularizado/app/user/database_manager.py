import base64
import jwt
import json

from app.config import Config
from app.helpers import searchUser, raise_exception
from app.exceptions import CustomException
from app.services.database_service import DatabaseService
from flask import request

##connection = Config.connection

# Looks for the user and the token that are hidden inside the url and checks if the token in the url is the same
# that is saved in the database
def verify_user_code(code, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr
        data = base64.b64decode(code).decode().split('-')

        _email = data[0]
        _code = data[1]

        sql = ("""
            SELECT id, token, validated FROM usuarios WHERE email = '{}'
        """.format(_email))

        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        if len(results) == 0:
            raise_exception('El usuario no existe','El usuario no existe')

        if results[0]['validated'] == True:
            raise_exception('El correo ya ha sido validado', 'El correo ya ha sido validado')

        if results[0]['token'] == _code:
            sql = ("""
                    UPDATE usuarios SET validated = true WHERE email = '{}'
                """.format(_email))
            cursor.execute(sql)

            
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                results[0]['id'], str(ip), 'Actualización de registro', 'Usuarios', int(results[0]['id']), json.dumps({'validated': True}),
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')
        else:
            raise_exception('El codigo no coincide', 'El codigo no coincide')

    except CustomException as e:
        print("ERROR (user/database_manager/verify_user_code):", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (user/database_manager/verify_user_code):", e)
        return CustomException('Ocurrio un error al validar el correo.', str(e)), 500
    else:
        return {'message': "Correo validado"}, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Changes the password if the code is valid
def change_password(code, password, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr


        payload = jwt.decode(code, Config.SECRET_KEY, algorithms=["HS256"])

        email = payload['token'].split('-')[1]

        sql = ("""
            SELECT * FROM Usuarios WHERE email = %s AND reset_token = %s
        """)

        val = (email, code)
        cursor.execute(sql, val)

        user = cursor.fetchone()
        if user:
            sql = ("""
                UPDATE Usuarios SET password = %s, reset_token = NULL WHERE email = %s
            """)

            passw = base64.b64encode(password.encode())
            val = (passw.decode(), email)

            cursor.execute(sql,val)

            audit = {
                "password": passw.decode(),
                "reset_token": None
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                None, str(ip), 'Actualización de registro', 'Usuarios', int(user[0]), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

        else:
            raise_exception('Token inválido','Token inválido')

    except CustomException as e:
        print("ERROR (user/database_manager/change_password):", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (user/database_manager/change_password):", e)
        return CustomException('Ocurrio un error al cambiar la contraseña', str(e)), 500
    else:
        return {'message': "Contraseña cambiada"}, 200
    finally:
        if not cursor.closed:
            cursor.close()



# This function updates the user information
def update_user_info(obj, connection, id_req):
    try:
        cursor = connection.cursor()
        _perm = False
        dataUserExisting = []

        # validaciones creación de un usuario nuevo
        if id_req != obj['idUser']:
            sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
                ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
            val = (id_req, 3)
            cursor.execute(sql, val)
            results = []
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            for perm in results:
                if perm['id_permiso'] == 4:
                    _perm = True
                    user_edited = edit_user(obj, connection, id_req)
                    if user_edited[1] != 200:
                        raise_exception(user_edited[0].to_dict()['message'],  user_edited[0].to_dict()['error'])
                    break
            dataUserExisting = searchUser(
                obj['numDocument'], obj['email'], idUser=obj['idUser'], perm_edit=True)
        else:
            dataUserExisting = searchUser(
                obj['numDocument'], obj['email'], idUser=obj['idUser'])
        if not dataUserExisting:
            raise_exception('El usuario a actualizar no existe','El usuario a actualizar no existe')

        results = []
        
        sql = ("""
            SELECT usuario,email,password,nombre,apellido,numero_documento,cod_tipo_documento,institucion,cargo
            FROM Usuarios WHERE id={}
        """.format(obj['idUser']))

        cursor.execute(sql)

        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
    
        token = ''
        if obj['idUser'] == id_req:
            user_edited = edit_user(obj, connection, id_req)
            if user_edited[1] != 200:
                raise_exception(user_edited[0].to_dict()['message'],  user_edited[0].to_dict()['error'])

            res = {
                'id': obj['idUser'],
                'usuario': obj['usuario'],
                'email': obj['email'],
                'nombre': obj['firstName'],
                'apellido': obj['lastName'],
                'nuDocumento': obj['numDocument'],
                'idDocumento': obj['typeDocument'],
                'institucion': obj['institution'],
                'cargo': obj['workCenter'], 
                'activo': obj['active']

            }

            _perm = True
            token = jwt.encode({'userobj': res}, Config.SECRET_KEY)
        else:
            sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
            ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
            val = (id_req, 3)
            cursor.execute(sql, val)
            results = []
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            for perm in results:
                if perm['id_permiso'] == 4:
                    _perm = True
                    user_edited = edit_user(obj, connection, id_req)
                    if user_edited[1] != 200:
                        raise_exception(user_edited[0].to_dict()['message'],  user_edited[0].to_dict()['error'])
                    break
            
            if not _perm:
                token = jwt.encode({'userobj': 'No tiene permisos para realizar esta operacion'}, Config.SECRET_KEY)
            else:
                res = {
                    'id': obj['idUser'],
                    'usuario': obj['usuario'],
                    'email': obj['email'],
                    'nombre': obj['firstName'],
                    'apellido': obj['lastName'],
                    'nuDocumento': obj['numDocument'],
                    'idDocumento': obj['typeDocument'],
                    'institucion': obj['institution'],
                    'cargo': obj['workCenter'],
                    'activo': obj['active']
                }

                token = jwt.encode({'userobj': res}, Config.SECRET_KEY)


    except CustomException as e:
        print("ERROR (user/database_manager/update_user_info): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (user/database_manager/update_user_info): ", e)
        return CustomException('Ocurrio un error al actualizar el usuario.', str(e)), 500
    else:
        if _perm:
            return {'token': token.decode('UTF-8')}, 200
        else:
            return {'token': token.decode('UTF-8')}, 401
    finally:
        if not cursor.closed:
            cursor.close()


# This function edits the user wheter it's the own user editing its profile or the admin
def edit_user(obj, connection, id_req):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        if 'password' in obj and obj['password'] != "" and 'pascheckPasswordsword' in obj and obj['pascheckPasswordsword'] != '':
            if obj['password'] != obj['pascheckPasswordsword']:
                raise_exception('Las contraseñas no coinciden', 'Las contraseñas no coinciden')
            hashed_password = base64.b64encode(obj['password'].encode())

            sqlUpdateUser = ("""
            UPDATE usuarios SET usuario=%s,email=%s,password=%s,nombre=%s,apellido=%s,numero_documento=%s,
            cod_tipo_documento=%s,institucion=%s,cargo=%s,activo=%s
            WHERE id=%s
            """)
            val = (obj['usuario'], obj['email'], hashed_password.decode(), obj['firstName'], obj['lastName'],
            obj['numDocument'], obj['typeDocument'], obj['institution'], obj['workCenter'], obj['active'], obj['idUser'])
            cursor.execute(sqlUpdateUser, val)

            audit = {
                'usuario': obj['usuario'],
                'email': obj['email'],
                'password': hashed_password.decode(),
                'nombre': obj['firstName'],
                'apellido': obj['lastName'],
                'numero_documento': obj['numDocument'],
                'cod_tipo_documento': obj['typeDocument'],
                'institucion': obj['institution'],
                'cargo': obj['workCenter']
            }

            
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(id_req), str(ip), 'Actualización de registro', 'Usuarios', int(obj['idUser']), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')
        else:
            sqlUpdateUser = ("""
            UPDATE usuarios SET usuario=%s,email=%s,nombre=%s,apellido=%s,numero_documento=%s,cod_tipo_documento=%s,
            institucion=%s,cargo=%s,activo=%s
            WHERE id=%s
            """)
            val = (obj['usuario'], obj['email'], obj['firstName'], obj['lastName'], obj['numDocument'],
            obj['typeDocument'], obj['institution'], obj['workCenter'], obj['active'], obj['idUser'])
            cursor.execute(sqlUpdateUser, val)

            #del results[0]['password']

            audit = {
                'usuario': obj['usuario'],
                'email': obj['email'],
                'nombre': obj['firstName'],
                'apellido': obj['lastName'],
                'numero_documento': obj['numDocument'],
                'cod_tipo_documento': obj['typeDocument'],
                'institucion': obj['institution'],
                'cargo': obj['workCenter']
            }

            
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)
            

            val = (
                int(id_req), str(ip), 'Actualización de registro', 'Usuarios', int(obj['idUser']), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')
    except CustomException as e:
        print("ERROR (user/database_manager/edit_user): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (user/database_manager/edit_user): ", e)
        return CustomException('Ocurrio un error al actualizar el usuario', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Function to get all the users
def get_users(connection, id_user=None):
    try:
        cursor = connection.cursor()
        results = []
        if id_user:
            sql = ("""
                SELECT u.id, u.usuario, u.email, u.activo, u.nombre, u.apellido, 
                u.numero_documento, u.cod_tipo_documento, u.institucion, u.cargo,
                u.validated AS validado, u.rol, r.nombre AS nombre_rol
                FROM usuarios u JOIN Rol r ON u.rol = r.id_rol WHERE u.id = %s;
            """)

            val = ([id_user])
            cursor.execute(sql,val)

            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
   
        else:
            sql = ("""
                SELECT u.id, u.usuario, u.email, u.activo, u.nombre, u.apellido, 
                u.numero_documento, u.cod_tipo_documento, u.institucion, u.cargo,
                u.validated AS validado, u.rol, r.nombre AS nombre_rol
                FROM usuarios u JOIN Rol r ON u.rol = r.id_rol;
            """)

            cursor.execute(sql)

            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

        
        sql = (""" SELECT * FROM Rol""")

        cursor.execute(sql)

        columns = [column[0] for column in cursor.description]
        roles = []
        for row in cursor.fetchall():
            roles.append(dict(zip(columns, row)))


        token = jwt.encode({'users': results, 'roles': roles}, Config.SECRET_KEY)
    except CustomException as e:
        print("ERROR (user/database_manager/get_users): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (user/database_manager/get_users): ", e)
        return CustomException('Ocurrio un error al obtener los usuarios', str(e)), 500
    else:
        return {'token': token.decode('UTF-8')}, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()
    

# Function to change a user rol
def change_user_rol(obj, id_user, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        sql = ("""
            UPDATE usuarios SET rol = %s WHERE id = %s
        """)

        val = (obj['id_rol'], obj['id'])
        cursor.execute(sql, val)

        audit = {
            'id_rol': obj['id_rol']
        }

        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(id_user), str(ip), 'Actualización de registro', 'Usuarios', int(obj['id']), json.dumps(audit)
        )

        cursor.execute(sql, val)
        if not cursor.fetchone()[0]:
            raise_exception(
                'Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (user/database_manager/change_user_rol): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (user/database_manager/change_user_rol): ", e)
        return CustomException('Ocurrio un error al cambiar el rol del usuario', str(e))
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# This function delete a notification from notifications table
def review_notification(notif, id_user, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        sql = ("""
            SELECT * FROM Notificaciones WHERE id_notificacion = %s
        """)

        val = ([notif])

        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        sql = ("""
            DELETE FROM Notificaciones WHERE id_notificacion = %s
        """)

        val = ([notif])

        cursor.execute(sql, val)

        audit = {
            'id_notificacion': results[0]['id_notificacion'],
            'titulo': results[0]['titulo'],
            'descripcion': results[0]['descripcion'],
            'id_usuario': results[0]['id_usuario'],
            'id_creador': results[0]['id_creador']
        }

        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(id_user), str(ip), 'Eliminación de registro', 'Notificaciones', int(notif), json.dumps(audit)
        )

        cursor.execute(sql, val)
        if not cursor.fetchone()[0]:
            raise_exception(
                'Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (user/database_manager/review_notification): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (user/database_manager/review_notification): ", e)
        return CustomException('Ocurrio un error al revisar la notificación', str(e))
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()