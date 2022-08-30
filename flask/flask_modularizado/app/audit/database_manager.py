
import jwt
import json

from app.exceptions import CustomException
from app.config import Config


# This function returns all the audits registers
def get_audits(connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT id_auditoria, email AS id_usuario,fecha_operacion::text, hora_operacion::text, 
            ip, accion, entidad, id_registro, valor::TEXT FROM Auditoria JOIN Usuarios ON id_usuario = id 

            UNION

            SELECT id_auditoria, CASE WHEN id_usuario ISNULL THEN NULL END AS id_usuario, fecha_operacion::text, hora_operacion::text, 
            ip, accion, entidad, id_registro, valor::TEXT FROM Auditoria WHERE id_usuario ISNULL 
            ORDER BY id_auditoria DESC;
        """)

        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        # Transform the dict into a json
        for result in results:
            result['valor'] = json.loads(result['valor']) if result['valor'] else None
        
        token = jwt.encode({'auditorias': results}, Config.SECRET_KEY)

    except CustomException as e:
        print("ERROR (audit/database_manager/get_audits): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (audit/database_manager/get_audits): ", e)
        return CustomException('Ocurrió un error al obtener los registros de auditoría', str(e)), 500
    else:
        return {'token': token.decode('UTF-8')}, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()
            