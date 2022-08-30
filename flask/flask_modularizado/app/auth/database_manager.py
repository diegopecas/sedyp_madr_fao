import random
import string
import base64
import json
import jwt
import datetime


from flask import request
from app.config import Config
from app.services.email_service import get_email_service
from app.helpers import searchUser, send_validate_email
from app.helpers import raise_exception, send_reset_token_email
from app.exceptions import CustomException
from app.services.database_service import DatabaseService


# This function looks for a user in the database with the given email and password, if one is found
# it returns its information encoded, if not it returns an error message
def login_user(email, password, connection):
    try:
        cursor = connection.cursor()
        encPass = base64.b64encode(password.encode())

        ip = request.remote_addr

        query = ("""
            SELECT
            a.id, a.usuario, a.email, a.password, a.activo, a.nombre,
            a.apellido, a.numero_documento, a.cod_tipo_documento,
            a.institucion, a.cargo, b.tipo_documento, a.rol, r.nombre AS nombre_rol
            FROM usuarios a JOIN tipo_documento2 b ON (b.cod_tipo_documento = a.cod_tipo_documento)
            JOIN Rol r ON (a.rol = r.id_rol)
            WHERE email = %s AND password = %s AND activo = 'S' AND validated = true
        """)
        cursor.execute(query, (email, encPass.decode()))
        records = cursor.fetchall()

        # if exists a token is given
        if cursor.rowcount > 0:

            row = records[0]

            sql = (""" SELECT * FROM Modulo""")

            cursor.execute(sql)
            columns = [column[0] for column in cursor.description]
            modules = []
            for _row in cursor.fetchall():
                modules.append(dict(zip(columns, _row)))

            sql = (""" SELECT * FROM Permisos""")

            cursor.execute(sql)
            columns = [column[0] for column in cursor.description]
            perms = []
            for _row in cursor.fetchall():
                perms.append(dict(zip(columns, _row)))

            sql = (""" SELECT * FROM Rol_modulo_permisos WHERE id_rol = %s """)
            val = ([row[12]])

            cursor.execute(sql, val)
            columns = [column[0] for column in cursor.description]
            results = []
            for _row in cursor.fetchall():
                results.append(dict(zip(columns, _row)))

            perms_user = join_perm_mod(modules, perms, results)
            if perms_user[1] != 200:
                raise_exception(perms_user[0].to_dict()['message'],  perms_user[0].to_dict()['error'])

            res = '' 

            notifications = get_notificacions(row[0], connection)
            if notifications[1] != 200:
                raise_exception(notifications[0].to_dict()['message'],  notifications[0].to_dict()['error'])

            if row[12] == 7:
                # if town validator, search for the amount of not validated events in their uer
                sql = ("""
                    SELECT COUNT(cod_evento) as eventos_sin_validar FROM Evento JOIN Validador_municipal 
                    ON cod_municipio_fk = cod_mun_fk WHERE usuario = %s AND validado = false;
                """)

                val = ([row[0]])

                cursor.execute(sql, val)
                events_to_validate = cursor.fetchone()[0]

                res = {
                    'id': row[0],
                    'usuario': row[1],
                    'email': row[2],
                    'activo': row[4],
                    'nombre': row[5],
                    'apellido': row[6],
                    'nuDocumento': row[7],
                    'idDocumento': row[8],
                    'institucion': row[9],
                    'cargo': row[10],
                    'id_rol': row[12],
                    'nombre_rol': row[13],
                    'permisos_usuario': perms_user,
                    'eventos_validar': events_to_validate,
                    'notificaciones': notifications[0]
                }
            else:    
                res = {
                    'id': row[0],
                    'usuario': row[1],
                    'email': row[2],
                    'activo': row[4],
                    'nombre': row[5],
                    'apellido': row[6],
                    'nuDocumento': row[7],
                    'idDocumento': row[8],
                    'institucion': row[9],
                    'cargo': row[10],
                    'id_rol': row[12],
                    'nombre_rol': row[13],
                    'permisos_usuario': perms_user,
                    'notificaciones': notifications[0]
                }
            
            token = jwt.encode({'userobj': res},
            #'exp': datetime.datetime.utcnow(
            #) + datetime.timedelta(minutes=60)}, 
            Config.SECRET_KEY)
            
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(res['id']), str(ip), 'Inicio de sesión', None, None, None
            )

            cursor.execute(sql, val)
            if not cursor.fetchone()[0]:
                raise_exception('Ocurrió un error, intente de nuevo', 'Error al auditar')

            return {'token': token.decode('UTF-8')}, 200

        
        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            None, str(ip), 'Inicio de sesión', None, None, None
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

        token = jwt.encode({'userobj': 'No se ha encontrado el usuario'},
        #'exp': datetime.datetime.utcnow(
        #) + datetime.timedelta(minutes=60)}, 
        Config.SECRET_KEY)

        return {'token': token.decode('UTF-8')}, 404
 
        #raise_exception('Error en autenticación', 'Error en autenticación')

    except CustomException as e:
        print("ERROR (auth/database_manager/login_user): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (auth/database_manager/login_user): ", e)
        return CustomException('Ha ocurrido un error en el login', str(e)), 500
    finally:
        if not cursor.closed:
            cursor.close()


# Join the pems and the modules per role
def join_perm_mod(modules, perms, perms_per_role):
    try:
        arr = []
        for modul in modules:
            status = False
            exist = [ppr for ppr in perms_per_role if ppr['id_modulo'] == modul['id_modulo']]
            if exist:
                status = True
            obj_m = {
                'id_modulo': modul['id_modulo'],
                'nombre_modulo': modul['nombre'],
                'estado': status,
                'permisos': []
            }

            for perm in perms:
                _status = False
                _exist = [ppr for ppr in perms_per_role if ppr['id_modulo'] == modul['id_modulo'] and ppr['id_permiso'] == perm['id_permiso']]
                if _exist:
                    _status = True

                obj_p = {
                    'id_permiso': perm['id_permiso'],
                    'nombre_permiso': perm['nombre'],
                    'estado': _status
                }

                obj_m['permisos'].append(obj_p)
            arr.append(obj_m)
        
    except CustomException as e:
        print("ERROR (auth/database_manager/join_perm_mod): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (auth/database_manager/join_perm_mod): ", e)
        return CustomException('Ocurrio un error al obtener los permisos del usuario', str(e)), 500
    else:
        return arr, 200


# Get the notifications of a given user
def get_notificacions(id, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT id_notificacion, titulo, descripcion, id_usuario, id_creador, 
            (SELECT usuario FROM usuarios WHERE id = id_creador) AS usuario_creador 
            FROM Notificaciones WHERE id_usuario = %s ORDER BY id_notificacion DESC
        """)

        val = ([id])

        cursor.execute(sql, val)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (auth/database_manager/get_notificacions): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (auth/database_manager/get_notificacions): ", e)
        return CustomException('Ocurrio un error al obtener las notificaciones', str(e)), 500
    else:
        return results, 200


# This function validates the existence of a user, register them if not exist and sends the validate email
# If the user already exists it sends an alert with that message
def register_user(obj, connection):
    try:
        cursor = connection.cursor()
        mail = get_email_service()
        ip = request.remote_addr

        # validaciones creación de un usuario nuevo
        dataUserExisting = searchUser(
            obj['numDocument'], obj['email'])
        if dataUserExisting:
            raise_exception('Ya existe un usuario con el mismo número de documento o email', 'Ya existe un usuario con el mismo número de documento o email')

        hashed_password = base64.b64encode(obj['password'].encode())
        token_email = '{}{}{}'.format(random.choice(string.ascii_letters), random.randint(
            1000, 9999), random.choice(string.ascii_letters))

        sqlInsertUser = ('''
            INSERT INTO usuarios (usuario,email,password,activo,nombre,apellido,numero_documento,
            cod_tipo_documento,institucion,cargo,token,validated,rol)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, false, 12) RETURNING id
        ''')
        val = (obj['usuario'], obj['email'], hashed_password.decode(), obj['active'], obj['firstName'], obj['lastName'], obj['numDocument'],
               obj['typeDocument'], obj['institution'], obj['workCenter'], token_email)


        cursor.execute(sqlInsertUser, val)
        id_new_user = cursor.fetchone()[0]

        audit = {
            'usuario': obj['usuario'],
            'email': obj['email'],
            'password': hashed_password.decode(),
            'activo': obj['active'],
            'nombre': obj['firstName'],
            'apellido': obj['lastName'],
            'numero_documento': obj['numDocument'],
            'cod_tipo_documento': obj['typeDocument'],
            'institucion': obj['institution'],
            'cargo': obj['workCenter'],
            'token': token_email,
            'validated': False, 
            'rol': 12
        }   

        id_user = None

        if request.args.get('token'):
            id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        
        
        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            id_user, str(ip), 'Creación de registro', 'Usuarios', int(id_new_user), json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

        sended = send_validate_email(Config.EMAIL_SENDER,
                            obj['email'], token_email, request, mail)
        if sended[1] != 200:
            raise_exception(sended[0].to_dict()['message'],  sended[0].to_dict()['error'])

        res = {
            'id': id_new_user,
            'usuario': obj['usuario'],
            'email': obj['email'],
            'activo': obj['active'],
            'nombre': obj['firstName'],
            'apellido': obj['lastName'],
            'nuDocumento': obj['numDocument'],
            'idDocumento': obj['typeDocument'],
            'institucion': obj['institution'],
            'cargo': obj['workCenter']
        }

        token = jwt.encode({'userobj': res}, 
        #'exp': datetime.datetime.utcnow(
        #) + datetime.timedelta(minutes=60)}, 
        Config.SECRET_KEY)

    except CustomException as e:
        print("ERROR (auth/database_manager/register_user): ",e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (auth/database_manager/register_user): ",e)
        return CustomException('Ocurrio un error al crear el usuario.', str(e)), 500
    else:
        return {'token': token.decode('UTF-8')}, 200
    finally:
        if not cursor.closed:
            cursor.close()


# This function create the token to be sended and calls the one that sends the email to reset the password.
# The token sended only has a last of 60 minutes in order to get more security
def send_reset_password_email(email, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        sql = ("""
            SELECT * FROM Usuarios WHERE email = %s
        """)

        val = ([email])

        cursor.execute(sql, val)
        exists = cursor.fetchone()
        if exists:
            reset_token = '{}{}{}'.format(random.choice(string.ascii_letters), random.randint(
            1000, 9999), random.choice(string.ascii_letters))

            token = jwt.encode({'token': reset_token+'-'+email, 
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, 
            Config.SECRET_KEY)

            sql = ("""
                UPDATE Usuarios SET reset_token = %s WHERE email = %s
            """)

            val = (token.decode('UTF-8'), email)
            cursor.execute(sql, val)

            audit = {
                "reset_token": token.decode('UTF-8')
            }


            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                None, str(ip), 'Actualización de registro', 'Usuarios', int(exists[0]), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

            
            mail = get_email_service()
            sended = send_reset_token_email(Config.EMAIL_SENDER, email, token, mail)
            if sended[1] != 200:
                raise_exception(sended[0].to_dict()['message'],  sended[0].to_dict()['error'])

        else:
            raise_exception('El usuario no se ha encontrado', 'El usuario no se ha encontrado')
    except CustomException as e:
        print("ERROR (auth/database_manager/send_reset_password_email): ",e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (auth/database_manager/send_reset_password_email): ",e)
        return CustomException('Ocurrio un error al reestablecer la contraseña.', str(e)), 500
    else:
        return {"message": "OK"}, 200
    finally:
        if not cursor.closed:
            cursor.close()