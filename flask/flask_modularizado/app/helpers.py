import os
import base64
import datetime
import json


from flask import jsonify
from flask_mail import Message 
from app.exceptions import CustomException
from app.services.database_service import DatabaseService


# Validate that the mandatory fields are filled with non None values
def validate_fields(campos):
    correcto = 1
    for campo in campos:
        if campo['obligatorio'] and campo['valor'] == None:
            correcto = 0

    return correcto


# Returns if a file has an allowed extension or not
def allowed_file(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Raises an exception
def raise_exception(msg, error):
    raise CustomException(message=msg, error=error)


# This function looks for a user with the given document id and email
def searchUser(noDocumento, email, connection=None, idUser=None, perm_edit=False):
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection() 
        
        # If user is validated, then it's neded to search that exists a user with the same doc or email but with different id
        # In order to not get the same user 
        where = "AND a.id != " + str(idUser) if idUser else ''
        val = (noDocumento, email)

        cursor = connection.cursor()

        sql = ("""
            SELECT * FROM usuarios WHERE numero_documento = '{}' AND validated = false
        """.format(noDocumento))
        cursor.execute(sql)

        rows = cursor.fetchall()

        if len(rows) == 1 and not perm_edit:
            results = []
            columns = [column[0] for column in cursor.description]
            for row in rows:
                # Por favor, indique el tipo de construcción afectada
                results.append(dict(zip(columns, row)))
            sql = ("""
            DELETE FROM usuarios WHERE numero_documento = '{}' AND validated = false
            """.format(noDocumento))
            cursor.execute(sql)
            
            
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                None, '192.168.0.0', 'Eliminación de registro', 'Usuarios', int(results[0]['id']), json.dumps(results[0])
            )

            cursor.execute(sql, val)
            
            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

            connection.commit()

            return False

        # Search user
        sqlUsuario = ("""
            SELECT a.*
            FROM usuarios a
            WHERE
            a.numero_documento = %s OR a.email = %s AND validated = true """ + where)
        cursor.execute(sqlUsuario, val)


        recordsUser = cursor.fetchall()

        return recordsUser

    except Exception as e:
        connection.rollback()
        print(e)
        return False

    finally:
        if not cursor.closed:
            cursor.close()

        if not connection.closed:
            connection.close()


## This function sends the validate email to finish the user register
def send_validate_email(EMAIL_SENDER, email, token_email, request, mail):
    try:
        msg = Message("Confirmación de correo",
                        sender=EMAIL_SENDER,
                        recipients=[email])
        
        to_hash = email +'-'+ token_email
        hashed = base64.b64encode(to_hash.encode())

        url = ''
        if os.environ['FLASK_ENV'] == 'development':
            url = 'http://localhost:8080'
        else:
            url = 'https://blue-ocean-0a3453310.1.azurestaticapps.net/'

        link = '{}/validate/{}'.format(url, hashed.decode())
        msg.html = '''
                    <h4>Para completar tu registro en la aplicación por favor accede a esta página</h4>
                    <h3>{}</h3>
            '''.format(link)
        
        mail.send(msg)
    except Exception as e:
        print("ERROR (helpers/send_validate_email): ", str(e))
        return CustomException('No se ha podido enviar el correo de validación', str(e)), 500
    else:
        return True, 200


# This function sends the email to recover the password
def send_reset_token_email(email_sender, email_send, token, mail):
    try:
        msg = Message("Recuperar contraseña",
                        sender=email_sender,
                        recipients=[email_send])
        url = ''
        if os.environ['FLASK_ENV'] == 'development':
            url = 'http://localhost:8080'
        else:
            url = 'https://blue-ocean-0a3453310.1.azurestaticapps.net/'

        link = '{}/forgotPassword/{}'.format(url, token.decode('UTF-8'))
        body = 'Para recuperar su contraseña por favor acceda a este link {}'.format(link)
        msg.html = '''
                    <h4>{}</h4>
            '''.format(body)
        
        mail.send(msg)
    except Exception as e:
        print("ERROR (helpers/send_reset_token_email): ", str(e))
        return CustomException('No se ha podido enviar el correo de recuperación de la contraseña', str(e)), 500
    else:
        return True, 200


# This function send a notification email in order to notify the validators or another user about a change in something they have created.
def send_notification_email(EMAIL_SENDER, email, title, body, mail):
    try:
        msg = Message(title,
                    sender=EMAIL_SENDER,
                    recipients=[email])
        msg.html = """
                    <h3>{}</h3>
            """.format(body)
        
        mail.send(msg)
    except Exception as e:
        print("ERROR (helpers/send_notification_email): ", str(e))
        return CustomException('No se ha podido enviar el correo de notificación', str(e)), 500
    else:
        return True, 200
        
    
# It creates the event dictionary
def diccionarioEvento(records, connection):
    eventos = []

    for record in records:
        record['evento_productor'] = searchProductorEvento(record['cod_evento'], connection)
        record['sistemas_afectados'] = searchSistemasAfectadosEvento(record['cod_evento'], connection)
        record['especie_forestal'] = searchEspecieForestalEvento(record['cod_evento'], connection)

        eventos.append(record)
        # record['sistemas_afectados'] =
        # record['eventos_sistemas'] =

        # consultar relación lote propagación con  evento

    return eventos


# Looks for producers associated to an event
def searchProductorEvento(codEvento, connection):

    cursor = connection.cursor()

    try:

      # Search event
      sql = ("""
            SELECT
              a.*,
              cod_productor_agropecuario,
              cod_condicion_juridica_FK,
              cod_tipo_productor_FK,
              nombre_apellido_productor,
              cod_tipo_documento_FK,
              nro_documento,
              direccion_residencia,
              numero_contacto,
              cod_sexo_FK,
              TO_CHAR(b.fch_nacimiento, 'YYYY-MM-DD') AS fech_nacimiento,
              cod_grupo_etnico_FK
            FROM evento_productos_agropecuario a
            JOIN productor_agropecuario b ON (b.cod_productor_agropecuario = a.cod_producto_agro)
            WHERE a.cod_evento_FK = '%s'""")
      val = (codEvento)
      cursor.execute(sql, [val]);
      columns = [column[0] for column in cursor.description]
      results = []
      for row in cursor.fetchall():
          results.append(dict(zip(columns, row)))

      return results

    except Exception as e:
      print(e)
      return jsonify({'message': 'Ocurrio un error al crear el usuario.'}), 400

    finally:
      cursor.close()


# Looks for the associated affected systems in the event
def searchSistemasAfectadosEvento(codEvento, connection):
    cursor = connection.cursor()

    try:

        # Search events
        sql = ("""
            SELECT
              a.*
            FROM evento_sist_prod_afectado a
            JOIN sistema_productivo_afectado b ON (b.cod_sis_prod_afec = a.cod_sist_prod_afect_fk)
            WHERE a.cod_evento_FK = '%s'""")
        val = (codEvento)
        cursor.execute(sql, [val]);
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        cursor.close()
        return results

    except Exception as e:
        print(e)
        cursor.close()
        return jsonify({'message': 'Ocurrio un error al crear el usuario.'}), 400


# Looks for the associated affected systems in the event
def searchEspecieForestalEvento(codEvento, connection):

    try:
        cursor = connection.cursor()

        # Search events
        sql = ("""
            SELECT
              a.*,
              b.*,
              c.cod_especie_forestal_sembrada,
              c.cod_fase_productiva_FK,
              c.cod_especie_forestal_afec_FK,
              c.cod_especie_extractiva_FK,
              c.nom_comun_especie,
              TO_CHAR(c.fch_establecimiento, 'YYYY-MM-DD') AS fch_establecimiento,
              TO_CHAR(c.densidad_siembra_Ha, 'l99999D99999999') AS densidad_siembra_Ha,
              TO_CHAR(c.area_total_sembrada_Ha, 'l99999D99999999') AS area_total_sembrada_Ha,
              c.cod_objetivo_plantacion_FK,
              TO_CHAR(c.num_arbol_ha, 'l99999D99999999') AS num_arbol_ha,
              c.num_estresacas,
              TO_CHAR(c.diam_prom_altura_pecho, 'l99999D99999999') AS diam_prom_altura_pecho,
              TO_CHAR(c.altura_comercial, 'l99999D99999999') AS altura_comercial,
              TO_CHAR(c.altura_total, 'l99999D99999999') AS altura_total,
              c.producto_final_esperado,
              TO_CHAR(c.turno_plantacion, 'l99999D99999999') AS turno_plantacion,
              TO_CHAR(c.porc_arboles_turno, 'l99999D99999999') AS porc_arboles_turno,
              TO_CHAR(c.valor_recibir_prod_afectada, 'l99999D99999999') AS valor_recibir_prod_afectada,
              TO_CHAR(c.area_afectada_ha, 'l99999D99999999') AS area_afectada_ha,
              TO_CHAR(c.fcha_afectacion_sist_forestal, 'YYYY-MM-DD') AS fcha_afectacion_sist_forestal,
              TO_CHAR(c.duracion_dias_afectacion, 'l99999D99999999') AS duracion_dias_afectacion,
              c.num_arboles_afectados,
              TO_CHAR(c.volumen_madera_afectados, 'l99999D99999999') AS volumen_madera_afectados ,
              c.afectacion_infraestructura,
              d.cod_infraestructura_forestal,
              d.cod_tipo_infraestrucrtura_FK,
              d.nom_especie_semilla,
              d.cod_tip_semilla_FK,
              TO_CHAR(d.cant_semilla_almacenada, 'l99999D99999999') AS cant_semilla_almacenada,
              d.cod_unidad_FK,
              TO_CHAR(d.vlr_pesos_afectacion, 'l99999D99999999') AS vlr_pesos_afectacion,
              d.cod_tipo_fertilizante_FK,
              d.nombre_fertilizante,
              TO_CHAR(d.cantidad, 'l99999D99999999') AS cantidad,
              TO_CHAR(d.valor_pesos_afectacion, 'l99999D99999999') AS valor_pesos_afectacion,
              d.nom_plaguicida,
              d.cod_tipo_plaguicida_FK,
              d.cant_plaguicidas,
              TO_CHAR(d.vlr_pesos_afectacion_pla, 'l99999D99999999') AS vlr_pesos_afectacion_pla,
              d.cod_tipo_maquinaria_FK,
              d.nom_comercial,
              TO_CHAR(d.vlr_pesos_afectacion_maq, 'l99999D99999999') AS vlr_pesos_afectacion_maq,
              d.cod_especie_forestal_sembrada_FK,
              '' AS lote_propagacion
            FROM evento_sist_prod_afectado a
            JOIN sistema_productivo_afectado b ON (b.cod_sis_prod_afec = a.cod_sist_prod_afect_fk)
            JOIN especie_forestal_sembrada c ON (c.cod_especie_forestal_sembrada = a.cod_especie_forestal_fk)
            LEFT JOIN infraestructura_forestal d ON (d.cod_especie_forestal_sembrada_fk = c.cod_especie_forestal_sembrada)
            WHERE a.cod_evento_FK = '%s'""")
        val = (codEvento)
        cursor.execute(sql, [val]);
        columns = [column[0] for column in cursor.description]
        results = []

        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        for item in results:

            if item['cod_infraestructura_forestal']:
                sqlLote = ("""
            SELECT a.* 
            FROM infraestructura_lote_propagacion a 
            JOIN lote_propagacion b ON (b.cod_lote_propagacion = a.cod_lote_propagacion_FK)
            WHERE a.cod_infraestructura_FK = '%s'""")
                val = (item['cod_infraestructura_forestal'])
                cursor.execute(sqlLote, [val]);
                columns = [column[0] for column in cursor.description]
                recordsLote = []
                for row in cursor.fetchall():
                    recordsLote.append(dict(zip(columns, row)))

                item['lote_propagacion'] = recordsLote

        cursor.close()
        return results

    except Exception as e:
        print(e)
        cursor.close()
        return jsonify({'message': 'Ocurrio un error al crear el usuario.'}), 400
    

# Save the relation productor event
def save_relation_productor_event(idEvento, idProductor, idU, connection):
    try:
        cursor = connection.cursor()
        validacion = [
            {'campo': 'idEvento', 'valor': idEvento['id'], 'obligatorio': 1},
            {'campo': 'idProductor', 'valor': idProductor, 'obligatorio': 1}
        ]

        estadoValidate = validate_fields(validacion)

        if estadoValidate == 0:
            raise_exception('Error en validación de datos.', 'Error en validación de datos.')

        sqlInsert = ("""
        INSERT INTO evento_productos_agropecuario (cod_evento_FK, cod_producto_agro)
        VALUES (%s,%s) RETURNING cod_evento_productos_agropecuario
        """)
        val = (idEvento['id'], idProductor)
        cursor.execute(sqlInsert, val)

        idR = cursor.fetchone()[0]

        audit = {
            'cod_evento_FK': idEvento['id'],
            'cod_producto_agro': idProductor
        }

        
        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(idU), '192.168.0.0', 'Creación de registro', 'Evento_productos_agropecuario', int(idR), json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

        return True, 200

    except CustomException as e:
        print("ERROR (helpers/save_relation_productor_event): ", e.to_dict()['error'])
        return e.to_dict(), 500
    except Exception as e:
        print("ERROR (helpers/save_relation_productor_event): ", e)
        return CustomException('Ocurrio un error al guardar la relacion entre el productor y el evento', str(e)), 500

    finally:
        if not cursor.closed:
            cursor.close()