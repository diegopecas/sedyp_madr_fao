import jwt
import json

from app.exceptions import CustomException
from app.config import Config
from app.helpers import raise_exception
from flask import request


# Get all the roles
def get_roles(connection):
    try:
        cursor = connection.cursor()
        sql = ("""
        SELECT * FROM Rol
        """)

        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (permits/database_manager/get_roles): ",
              e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (permits/database_manager/get_roles): ", e)
        return CustomException('Ocurrio un error al obtener los roles', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Get all the modules
def get_modules(connection):
    try:
        cursor = connection.cursor()

        sql = ("""
        SELECT * FROM Modulo
        """)

        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (permits/database_manager/get_modules): ",
              e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (permits/database_manager/get_modules): ", e)
        return CustomException('Ocurrio un error al obtener los modulos')
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Get all the permissions
def get_permissions(connection):
    try:
        cursor = connection.cursor()

        sql = ("""
        SELECT * FROM Permisos
        """)

        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (permits/database_manager/get_permissions): ",
              e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (permits/database_manager/get_permissions): ", e)
        return CustomException('Ocurrio un error al obtener los permisos')
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Get all the permissions per rol
def get_perm_per_rol(connection):
    try:
        cursor = connection.cursor()
        sql = ("""
        SELECT * FROM Rol_Modulo_Permisos
        """)

        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (permits/database_manager/get_perm_per_rol): ",
              e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (permits/database_manager/get_permissions): ", e)
        return CustomException('Ocurrio un error al obtener los permisos por rol')
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Relations all the roles, modules and permissions
def full_perms(roles, modules, perms, perms_per_role):
    try:
        arr = []
        for rol in roles:
            obj = {
                'id_rol': rol['id_rol'],
                'nombre_rol': rol['nombre'],
                'modulos': [],
            }
            for modul in modules:
                status = False
                exist = [ppr for ppr in perms_per_role if ppr['id_rol'] ==
                         rol['id_rol'] and ppr['id_modulo'] == modul['id_modulo']]
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
                    _exist = [ppr for ppr in perms_per_role if ppr['id_rol'] == rol['id_rol']
                              and ppr['id_modulo'] == modul['id_modulo'] and ppr['id_permiso'] == perm['id_permiso']]
                    if _exist:
                        _status = True

                    obj_p = {
                        'id_permiso': perm['id_permiso'],
                        'nombre_permiso': perm['nombre'],
                        'estado': _status
                    }

                    obj_m['permisos'].append(obj_p)
                obj['modulos'].append(obj_m)
            arr.append(obj)

        token = jwt.encode({'permisos_por_rol': arr}, Config.SECRET_KEY)

    except Exception as e:
        print("ERROR (permits/database_manager/full_perms): ", e)
        return CustomException('Ocurrio un error al relaciones los roles con los permisos', str(e)), 500
    else:
        return {'token': token.decode('UTF-8')}, 200


# This function adds a perm on a mod to a rol or delete the perm on a mod for a rol
def change_p_status(connection, perm_to_change, id_user, remove):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        id_rol = perm_to_change['id_rol']
        id_modulo = perm_to_change['id_modulo']
        id_permiso = perm_to_change['id_permiso']

        if remove:
            sql = ("""
            SELECT id_rol_modulo_permisos FROM Rol_Modulo_Permisos WHERE id_rol=%s AND id_modulo=%s AND id_permiso=%s
            """)
            val = (id_rol, id_modulo, id_permiso)
            cursor.execute(sql, val)

            id_res = cursor.fetchone()[0]

            sql = ("""
            DELETE FROM Rol_Modulo_Permisos WHERE id_rol=%s AND id_modulo=%s AND id_permiso=%s
            """)

            val = (id_rol, id_modulo, id_permiso)
            cursor.execute(sql, val)

            audit = {
                'id_rol': id_rol,
                'id_modulo': id_modulo,
                'id_permiso': id_permiso
            }

            sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(id_user), str(ip), 'Eliminación de registro', 'Rol_Modulo_Permisos', int(
                    id_res), json.dumps(audit)
            )

            cursor.execute(sql, val)
            if not cursor.fetchone()[0]:
                raise_exception(
                    'Ocurrio un error, intente de nuevo', 'Error al auditar')
        else:
            sql = ("""
            INSERT INTO Rol_Modulo_Permisos(id_rol, id_modulo, id_permiso) VALUES(%s,%s,%s) RETURNING id_rol_modulo_permisos
            """)

            val = (id_rol, id_modulo, id_permiso)
            cursor.execute(sql, val)
            id_res = cursor.fetchone()[0]

            audit = {
                'id_rol': id_rol,
                'id_modulo': id_modulo,
                'id_permiso': id_permiso
            }

            
            sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(id_user), str(ip), 'Creación de registro', 'Rol_Modulo_Permisos', int(id_res), json.dumps(audit)
            )

            cursor.execute(sql, val)
            if not cursor.fetchone()[0]:
                raise_exception(
                    'Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (permits/database_manager/change_p_status): ",
              e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (permits/database_manager/change_p_status): ", e)
        return CustomException('Ocurrio un error al cambiar el estado del permiso'), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# This function creates a new rol
def add_rol(connection, rol, id_user):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        sqlInsert = ("""
            INSERT INTO Rol(Nombre) VALUES(%s) RETURNING id_rol
        """)

        val = ([rol])
        cursor.execute(sqlInsert, val)

        audit = {
            'Nombre': rol
        }

        id_res = cursor.fetchone()[0]
        
        sql = ("""
        SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(id_user), str(ip), 'Creación de registro', 'Rol', id_res, json.dumps(audit)
        )

        cursor.execute(sql, val)
        if not cursor.fetchone()[0]:
            raise_exception(
                'Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (permits/database_manager/add_rol): ",
              e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (permits/database_manager/add_rol): ", e)
        return CustomException('Ocurrio un error al agregar el rol'), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()
    

# This is a function to delete a rol and its permits
def delete_rol(connection, rol, id_user):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        # Deleting permits
        sql = ("""
            SELECT * FROM Rol_Modulo_Permisos WHERE id_rol = %s 
        """)

        val = ([rol])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        # If the rol has a permit then they are deleted and audited
        if len(results) > 0:
            

            sql = ("""
                DELETE FROM Rol_Modulo_Permisos WHERE id_rol = %s
            """)

            val = ([rol])
            cursor.execute(sql, val)

            for audit in results:
                sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
                """)

                val = (
                    int(id_user), str(ip), 'Eliminación de registro', 'Rol_Modulo_Permisos', int(audit['id_rol_modulo_permisos']), json.dumps(audit)
                )

                cursor.execute(sql, val)
                if not cursor.fetchone()[0]:
                    raise_exception(
                        'Ocurrio un error, intente de nuevo', 'Error al auditar')


        # Deleting rol
        sql = ("""
            SELECT * FROM Rol WHERE id_rol = %s 
        """)

        val = ([rol])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        audit = results[0]

        sql = ("""
            DELETE FROM Rol WHERE id_rol = %s
        """)

        val = ([rol])
        cursor.execute(sql, val)

        sql = ("""
        SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(id_user), str(ip), 'Eliminación de registro', 'Rol', int(rol), json.dumps(audit)
        )

        cursor.execute(sql, val)
        if not cursor.fetchone()[0]:
            raise_exception(
                'Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (permits/database_manager/delete_rol): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (permits/database_manager/delete_rol): ", e)
        return CustomException('Ocurrio un al eliminar el rol'), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()
                