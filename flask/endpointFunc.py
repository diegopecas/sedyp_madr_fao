from datetime import datetime, timedelta
import datetime
import re
from flask import jsonify
from psycopg2 import connect

#########################################################################################################
############################################ Funciones ##################################################
#########################################################################################################

######################################
# validación de campos
######################################


def validarCampos(campos):

    correcto = 1
    for campo in campos:
        if campo['obligatorio'] and campo['valor'] == None:
            correcto = 0

    return correcto

######################################
# esta funció busca un usuario con
# base en el número de documento y
# email.
######################################


def searchUser(noDocumento, email, connection, idUser=None):
    where = "AND a.id != " + str(idUser) if idUser else ''
    val = (noDocumento, email)

    try:
        cursor = connection.cursor()
        sql = ("""
            SELECT * FROM usuarios WHERE numero_documento = '{}' AND validated = false
        """.format(noDocumento))
        cursor.execute(sql)

        if len(cursor.fetchall()) == 1:
            sql = ("""
            DELETE FROM usuarios WHERE numero_documento = '{}' AND validated = false
            """.format(noDocumento))
            cursor.execute(sql)

            return False

        # consultar usuario
        sqlUsuario = ("""
            SELECT a.*
            FROM usuarios a
            WHERE
            (a.numero_documento = %s OR a.email = %s) AND validated = true """ + where)
        cursor.execute(sqlUsuario, val)

        recordsUser = cursor.fetchall()

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al crear el usuario.'}), 400

    finally:
        cursor.close()

    return recordsUser


######################################
# Crear diccionario evento
######################################
def diccionarioEvento(records, connection):
    eventos = []

    for record in records:
        record['evento_productor'] = searchProductorEvento(
            record['cod_evento'], connection)
        record['sistemas_afectados'] = searchSistemasAfectadosEvento(
            record['cod_evento'], connection)
        record['especie_forestal'] = searchEspecieForestalEvento(
            record['cod_evento'], connection)

        eventos.append(record)
        # record['sistemas_afectados'] =
        # record['eventos_sistemas'] =

        # consultar relación lote propagación con  evento

    return eventos

######################################
# Consultar productores asociados a un
# evento.
######################################


def searchProductorEvento(codEvento, connection):


    try:
        cursor = connection.cursor()
        # consultar eventos
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
        cursor.execute(sql, [val])
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al crear el usuario.'}), 400

    finally:
        cursor.close()


######################################
# Consultar sistemas afectados en el
# evento.
######################################
def searchSistemasAfectadosEvento(codEvento, connection):

    try:
        cursor = connection.cursor()
        # consultar eventos
        sql = ("""
            SELECT
              a.*
            FROM evento_sist_prod_afectado a
            JOIN sistema_productivo_afectado b ON (b.cod_sis_prod_afec = a.cod_sist_prod_afect_fk)
            WHERE a.cod_evento_FK = '%s'""")
        val = (codEvento)
        cursor.execute(sql, [val])
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        cursor.close()
        return results

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al crear el usuario.'}), 400
    finally:
        cursor.close()


######################################
# Consultar sistemas afectados en el
# evento.
######################################
def searchEspecieForestalEvento(codEvento, connection):

    try:
        cursor = connection.cursor()
        # consultar eventos
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
        cursor.execute(sql, [val])
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
                cursor.execute(sqlLote, [val])
                columns = [column[0] for column in cursor.description]
                recordsLote = []
                for row in cursor.fetchall():
                    recordsLote.append(dict(zip(columns, row)))

                item['lote_propagacion'] = recordsLote

        return results

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al crear el usuario.'}), 400

    finally:
        cursor.close()


######################################
# Buscar los tipos de documento.
######################################
def searchTipoDocumento(connection):


    try:
        cursor = connection.cursor()
        # consultar
        sqlTipoDocumento = ("""
      SELECT
      a.cod_tipo_documento,
      a.tipo_documento,
      CASE WHEN cod_tipo_documento = 6 THEN 'juridica'
            ELSE 'natural'
      END persona
      FROM tipo_documento2 a
      """)
        cursor.execute(sqlTipoDocumento)
        records = cursor.fetchall()

        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los tipos de documento.'}), 400

    finally:
        cursor.close()


######################################
# Buscar condiciones juridicas
######################################
def searchCondicionJuridica(connection):

    try:
        cursor = connection.cursor()
        # consultar
        sqlCondicionJuridica = ("""
      SELECT
      a.*
      FROM condicion_juridica a
      """)
        cursor.execute(sqlCondicionJuridica)
        records = cursor.fetchall()
        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los tipos de documento.'}), 400

    finally:
        cursor.close()


######################################
# Buscar sexo
######################################
def searchSexo(connection):


    try:
        cursor = connection.cursor()
        # consultar
        sqlSexo = ("""
            SELECT
            a.*
            FROM sexo a
        """)
        cursor.execute(sqlSexo)
        records = cursor.fetchall()
        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los tipos de documento.'}), 400

    finally:
        cursor.close()

######################################
# Buscar grupos etnicos
######################################
def searchGruposEtnicos(connection):


    try:
        cursor = connection.cursor()
        # consultar
        sqlGrupoEtnico = ("""
            SELECT
            a.*
            FROM grupo_etnico a
        """)
        cursor.execute(sqlGrupoEtnico)
        records = cursor.fetchall()
        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los tipos de documento.'}), 400

    finally:
        cursor.close()


######################################
# Buscar tipo productor
######################################
def searchTipoProductor(connection):


    try:
        cursor = connection.cursor()
        # consultar
        sqlTipoProductor = ("""
            SELECT
            a.*
            FROM tipo_productor a
        """)
        cursor.execute(sqlTipoProductor)
        records = cursor.fetchall()
        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los tipos de documento.'}), 400

    finally:
        cursor.close()

######################################
# Buscar tipo productor
######################################
def searchtTipoRelacionPredio(connection):

    try:
        cursor = connection.cursor()
        # consultar
        sqlTipoRelacion = ("""
            SELECT
            a.*
            FROM tipo_relacion_predio a
        """)
        cursor.execute(sqlTipoRelacion)
        records = cursor.fetchall()
        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los tipos de documento.'}), 400

    finally:
        cursor.close()

######################################
# Consultar departamentos
######################################
def searchDepartamentos(connection):
    records = []

    try:
        cursor = connection.cursor()
        sql = ("""
        SELECT *
        FROM departamentos """)
        cursor.execute(sql)
        records = cursor.fetchall()

        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio al consultar los datos del departamento.'}), 400

    finally:
        cursor.close()


######################################
# Consultar municipios
######################################
def searchMunicipios(connection):
    records = []

    try:
        cursor = connection.cursor()
        sql = ("""
            SELECT *
            FROM municipios 
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

        return records
    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un erro al consultar los datos del municipio.'}), 400

    finally:
        cursor.close()

######################################
# Consultar veredas
######################################
def searchVeredas(connection):
    records = []

    try:
        cursor = connection.cursor()
        sql = ("""
            SELECT *
            FROM vereda 
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un erro al consultar los datos de las veredas.'}), 400

    finally:
        cursor.close()

######################################
# Buscar tipo evento
######################################
def searchTipoEvento(connection):
    try:
        cursor = connection.cursor()
        # consultarroot
        sqlTipoEvento = ("SELECT * FROM tipo_evento")
        cursor.execute(sqlTipoEvento)
        records = cursor.fetchall()
        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los tipos de eventos.'}), 400

    finally:
        cursor.close()

######################################
# Buscar sub evento
######################################
def searchSubEvento(connection):
    try:
        cursor = connection.cursor()
        # consultar
        sqlSubEventos = ("""
            SELECT
            a.*
            FROM subeventos a
        """)
        cursor.execute(sqlSubEventos)
        records = cursor.fetchall()
        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los sub eventos.'}), 400

    finally:
        cursor.close()


######################################
# Buscar sistemas productivos
######################################
def searchSistemaProductivoAfectado(connection):
    try:
        cursor = connection.cursor()
        # consultar
        sqlSistema = ("""
            SELECT
            a.*
            FROM sistema_productivo_afectado a
        """)
        cursor.execute(sqlSistema)
        records = cursor.fetchall()

        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los sistemas productivos afectados.'}), 400

    finally:
        cursor.close()


######################################
# Buscar fase productiva
######################################
def searchFaseProductiva(connection):
    try:
        cursor = connection.cursor()
        # consultar
        sqlFase = ("""
            SELECT
            a.*
            FROM fase_productiva a
        """)
        cursor.execute(sqlFase)
        records = cursor.fetchall()

        return records
    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar las fases productivas.'}), 400

    finally:
        cursor.close()


######################################
# Buscar especie forestal
######################################
def searchEspecieForestal(connection):

    try:
        cursor = connection.cursor()
        # consultar
        sqlEspecie = ("""
            SELECT
            a.*
            FROM especie_forestal_afectada a
        """)
        cursor.execute(sqlEspecie)
        records = cursor.fetchall()

        return records
    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar las especies forestales.'}), 400

    finally:
        cursor.close()


######################################
# Buscar especie extractiva
######################################
def searchEspecieExtractiva(connection):

    try:
        cursor = connection.cursor()
        # consultar
        sqlEspecieEx = ("""
            SELECT
            a.*
            FROM especie_extractiva a
        """)
        cursor.execute(sqlEspecieEx)
        records = cursor.fetchall()

        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar las especies extractivas.'}), 400

    finally:
        cursor.close()

######################################
# Buscar objetivo plantación
######################################
def searchObjePlantacion(connection):


    try:
        cursor = connection.cursor()

        # consultar
        sql = ("""
            SELECT
            a.*
            FROM objetivo_plantacion a
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

        return records
    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los objetivos de la plantación.'}), 400

    finally:
        cursor.close()


######################################
# Buscar tipo infraestructura
######################################
def searchTipoInfraestructura(connection):

    try:
        cursor = connection.cursor()
        # consultar
        sql = ("""
            SELECT
            a.*
            FROM tipo_infraestructura a
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

        return records
    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los tipos de infraestructura.'}), 400

    finally:
        cursor.close()


######################################
# Buscar tipo semilla
######################################
def searchTipoSemilla(connection):

    try:
        cursor = connection.cursor()
        # consultar
        sql = ("""
            SELECT
            a.*
            FROM tipos_semilla a
        """)
        cursor.execute(sql)
        records = cursor.fetchall()
        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los tipos de semillas.'}), 400

    finally:
        cursor.close()


######################################
# Buscar tlote propagación
######################################
def searchLotePropaga(connection):

    try:
        cursor = connection.cursor()
        # consultar
        sql = ("""
            SELECT
            a.*
            FROM lote_propagacion a
        """)
        cursor.execute(sql)
        records = cursor.fetchall()
        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los lotes de propagación.'}), 400

    finally:
        cursor.close()


######################################
# Buscar unidad
######################################
def searchUnidad(connection):

    try:
        cursor = connection.cursor()
        # consultar
        sql = ("""
            SELECT
            a.*
            FROM unidad a
        """)
        cursor.execute(sql)
        records = cursor.fetchall()
        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar las unidades.'}), 400

    finally:
        cursor.close()


######################################
# Buscar tipo fertilizante
######################################
def searchTipoFertilizante(connection):

    try:
        cursor = connection.cursor()
        # consultar
        sql = ("""
            SELECT
            a.*
            FROM tipo_fertilizante a
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

        return records
    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los tipos de fertilizantes.'}), 400

    finally:
        cursor.close()


######################################
# Buscar tipo maquinaria
######################################
def searchTipoMaquinaria(connection):

    try:
        cursor = connection.cursor()
        # consultar
        sql = ("""
            SELECT
            a.*
            FROM tipo_maquinaria a
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los tipos de maquinarias.'}), 400

    finally:
        cursor.close()

######################################
# Buscar tipo plaguicida
######################################
def searchTipoPlaguicida(connection):

    try:
        cursor = connection.cursor()
        # consultar
        sql = ("""
            SELECT
            a.*
            FROM tipo_plaguicida a
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

        return records

    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los tipos de plaguicidas.'}), 400

    finally:
        cursor.close()


######################################
# Buscar rubros
######################################
def searchRubros(connection):

    try:
        cursor = connection.cursor()
        # consultar
        sql = ("""
            SELECT
            a.*
            FROM rubros a
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

        return records
    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar los rubros.'}), 400

    finally:
        cursor.close()

######################################
# Buscar actividades
######################################
def searchActividad(connection):

    try:
        cursor = connection.cursor()
        # consultar
        sql = ("""
            SELECT
            a.*
            FROM actividad a
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

        return records
    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al consultar las actividades.'}), 400

    finally:
        cursor.close()


######################################
# Guardar encabezado de evento
######################################
def guardarEncabezadoEvento(dataEncabezadoEvento, connection):
    # Fecha actual
    fechaActual = datetime.datetime.utcnow()

    try:
        cursor = connection.cursor()
        obj = {
            'tipoEv': dataEncabezadoEvento['tipoEv'] if 'tipoEv' in dataEncabezadoEvento else None,
            'latitud': dataEncabezadoEvento['latitud'] if 'latitud' in dataEncabezadoEvento else None,
            'longitud': dataEncabezadoEvento['longitud'] if 'longitud' in dataEncabezadoEvento else None,
            'altitud': float(dataEncabezadoEvento['altitud']) if 'altitud' in dataEncabezadoEvento and dataEncabezadoEvento['altitud'] else None,
            'precision': float(dataEncabezadoEvento['precision']) if 'precision' in dataEncabezadoEvento and dataEncabezadoEvento['precision'] else None,
            'fechaActual': fechaActual,
            'cod_municipio_FK': dataEncabezadoEvento['municipio'] if 'municipio' in dataEncabezadoEvento else None,
            'ubicacion_vereda': dataEncabezadoEvento['ubicacion_vereda'] if 'ubicacion_vereda' in dataEncabezadoEvento and dataEncabezadoEvento['ubicacion_vereda'] else None,
            'cod_vereda_FK': dataEncabezadoEvento['codVereda'] if 'codVereda' in dataEncabezadoEvento and dataEncabezadoEvento['codVereda'] else None,
            'nom_puerto_desembarquee': dataEncabezadoEvento['nombrePuerto'] if 'nombrePuerto' in dataEncabezadoEvento and dataEncabezadoEvento['nombrePuerto'] else None,
            'idUsuario': dataEncabezadoEvento['idUsuario'] if 'idUsuario' in dataEncabezadoEvento else None,
            'observacion': dataEncabezadoEvento['observacion'] if 'observacion' in dataEncabezadoEvento else None,
        }

        validacion = [
            {'campo': 'tipoEv', 'valor': obj['tipoEv'], 'obligatorio': 1},
            {'campo': 'latitud', 'valor': obj['latitud'], 'obligatorio': 1},
            {'campo': 'longitud', 'valor': obj['longitud'], 'obligatorio': 1},
            {'campo': 'fechaActual',
                'valor': obj['fechaActual'], 'obligatorio': 1},
            {'campo': 'idUsuario', 'valor': obj['idUsuario'], 'obligatorio': 1},
            {'campo': 'observacion',
                'valor': obj['observacion'], 'obligatorio': 1},
        ]

        estadoValidate = validarCampos(validacion)

        if estadoValidate == 0:
            return jsonify({'message': 'Error en validación de datos.'}), 400

        sqlInsert = ("""
        INSERT INTO evento (cod_tipo_evento_FK, coord_x, coord_y, altitud, precision,
                            fecha_registro_evento, cod_municipio_FK, ubicacion_vereda,
                            cod_vereda_FK, nom_puerto_desembarquee,
                            cod_encuestador_FK, descrip_llegada_casco_urbano)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_evento
        """)
        val = (obj['tipoEv'], obj['latitud'], obj['longitud'], obj['altitud'],
            obj['precision'], fechaActual, obj['cod_municipio_FK'],
            obj['ubicacion_vereda'], obj['cod_vereda_FK'],
            obj['nom_puerto_desembarquee'], obj['idUsuario'], obj['observacion'])

        cursor.execute(sqlInsert, val)


        res = {
            'id': cursor.fetchone()[0],
        }
        connection.commit()


        return res

    except Exception as e:
        connection.rollback()
        print(e)
        return jsonify({'message': 'Error al insertar los datos.'}), 400

    finally:
        cursor.close()

######################################
# Guardar productor asociado al evento
######################################
def guardarDataProductor(idEvento, dataProductor, connection):

    try:
        cursor = connection.cursor()
        for data in dataProductor:
            obj = camposDataProductor(data)

            sqlInsert = ("""
            INSERT INTO productor_agropecuario (cod_condicion_juridica_FK, cod_tipo_productor_FK,nombre_apellido_productor,
                                                cod_tipo_documento_FK, nro_documento, direccion_residencia, numero_contacto,
                                                cod_sexo_FK, fch_nacimiento, cod_grupo_etnico_FK)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_productor_agropecuario;
        """)
            val = (obj['condJuridica'], obj['tipoProd'], obj['nombre'],
                obj['tipoDcto'], obj['dcto'], obj['dirRes'], obj['tel'],
                obj['sexo'], obj['fechaNac'], obj['gEtnico'])
            cursor.execute(sqlInsert, val)

            idProductor = cursor.fetchone()[0]

            guardarRelProductorEvento(idEvento, idProductor, connection)
    
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()

######################################
# Datos del productor a guardar.
######################################
def camposDataProductor(data):

    obj = {
        'condJuridica': data['condJuridica'] if 'condJuridica' in data else None,
        'tipoProd': data['tipoProd'] if 'tipoProd' in data else None,
        'nombre': data['nombre'] if 'nombre' in data else None,
        'tipoDcto': data['tipoDcto'] if 'tipoDcto' in data else None,
        'dcto': data['dcto'] if 'dcto' in data else None,
        'dirRes': data['dirRes'] if 'dirRes' in data else None,
        'tel': data['tel'] if 'tel' in data else None,
        'sexo': data['sexo'] if 'sexo' in data else None,
        'fechaNac': data['fechaNac'] if 'fechaNac' in data else None,
        'gEtnico': data['gEtnico'] if 'gEtnico' in data else None,
    }

    validacion = [
        {'campo': 'condJuridica',
            'valor': obj['condJuridica'], 'obligatorio': 1},
        {'campo': 'tipoProd', 'valor': obj['tipoProd'], 'obligatorio': 0},
        {'campo': 'nombre', 'valor': obj['nombre'], 'obligatorio': 1},
        {'campo': 'tipoDcto', 'valor': obj['tipoDcto'], 'obligatorio': 1},
        {'campo': 'dcto', 'valor': obj['dcto'], 'obligatorio': 1},
        {'campo': 'dirRes', 'valor': obj['dirRes'], 'obligatorio': 0},
        {'campo': 'tel', 'valor': obj['tel'], 'obligatorio': 0},
        {'campo': 'sexo', 'valor': obj['sexo'], 'obligatorio': 0},
        {'campo': 'fechaNac', 'valor': obj['fechaNac'], 'obligatorio': 0},
        {'campo': 'gEtnico', 'valor': obj['gEtnico'], 'obligatorio': 0},
    ]

    estadoValidate = validarCampos(validacion)

    if estadoValidate == 0:
        return jsonify({'message': 'Error en validación de datos.'}), 400

    return obj

######################################
# Guardar relación entre el evento y
# el productor.
######################################
def guardarRelProductorEvento(idEvento, idProductor, connection):

    try:
        cursor = connection.cursor()
        validacion = [
            {'campo': 'idEvento', 'valor': idEvento['id'], 'obligatorio': 1},
            {'campo': 'idProductor', 'valor': idProductor, 'obligatorio': 1}
        ]
        estadoValidate = validarCampos(validacion)

        if estadoValidate == 0:
            return jsonify({'message': 'Error en validación de datos.'}), 400

        sqlInsert = ("""
        INSERT INTO evento_productos_agropecuario (cod_evento_FK, cod_producto_agro)
        VALUES (%s,%s)
        """)
        val = (idEvento['id'], idProductor)
        cursor.execute(sqlInsert, val)

    except Exception as e:
        connection.rollback()
        print(e)

    finally:
        cursor.close()

######################################
# Guardar relación entre el evento y
# el sistema forestal.
######################################
def guardarEventoSistema(idEvento, dataEspecie, sisProds, connection):
    for sistema in sisProds:
        if sistema == 3 and len(dataEspecie) != 0:  # Forestal
            guardarSistemaForestal(
                idEvento, dataEspecie['forestal'], sistema, connection)
        elif sistema == 1 and len(dataEspecie) != 0:  # Agricola
            guardarSistemaAgro(
                idEvento, dataEspecie['agropecuario'], sistema, connection)
        elif sistema == 2 and len(dataEspecie) != 0: # Pecuario
            guardarSistemaPecuario(
                idEvento, dataEspecie['infoPecuario'], sistema, connection
            )

######################################
# Datos del sistema forestal
######################################
def guardarSistemaForestal(idEvento, dataEspecie, sistema, connection):
    try:
        cursor = connection.cursor()
        for especie in dataEspecie:

            obj = camposDataForestal(especie)

            sqlInsert = ("""
            INSERT INTO especie_forestal_sembrada (cod_fase_productiva_FK, cod_especie_forestal_afec_FK,
                                                cod_especie_extractiva_FK,nom_comun_especie,fch_establecimiento,
                                                densidad_siembra_Ha,area_total_sembrada_Ha,cod_objetivo_plantacion_FK,
                                                num_arbol_ha,num_estresacas,diam_prom_altura_pecho,altura_comercial,
                                                altura_total,turno_plantacion,porc_arboles_turno,
                                                valor_recibir_prod_afectada,area_afectada_ha,fcha_afectacion_sist_forestal,
                                                duracion_dias_afectacion,num_arboles_afectados,volumen_madera_afectados,
                                                valor_entresacas,porcentaje_entresacas)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_especie_forestal_sembrada
            """)
            val = (obj['faseProd'], obj['espAfectada'], obj['espExtractiva'],
                obj['nombre'], obj['fecha'], obj['densHectarea'],
                obj['areaSembrada'], obj['objetivo'], obj['noArbolesAntesAfectacion'],
                obj['noEntresacas'], obj['diametroPromedio'], obj['alturaComercial'],
                obj['alturaTotal'], obj['plantacionAnos'], obj['porceArbolesTurnoFinal'],
                obj['valorVenderProduccionAfectada'], obj['areaAfectadaHectareas'],
                obj['fechaAfactaForestal'], obj['diasAfectoSistemaForestal'],
                obj['noArbolesAfectados'], obj['vlMaderaAfectado'],
                obj['valEntreSacas'], obj['porceEntreSacas'])
            cursor.execute(sqlInsert, val)

            idEspecieForestal = cursor.fetchone()[0]


            guardarRelEventoSistema(
                idEvento, sistema, idEspecieForestal, connection)
            gaurdarRelSistemaInfraestructura(
                especie, idEspecieForestal, connection)
            costos = gaurdarRelSistemaCostos(
                idEvento, idEspecieForestal, especie, connection)

            variables = {
                # Valor venta de entresacas
                'VTENT': float(obj['valEntreSacas']) if obj['valEntreSacas'] != None else 0,
                # costo total
                'CT': float(costos['costoTotalDirecto']) + float(costos['costoTotalInDirecto']) if costos['costoTotalDirecto'] != None and costos['costoTotalInDirecto'] != None else 0,
                # Número de arboles afectados
                'NAF': float(obj['noArbolesAfectados']) if obj['noArbolesAfectados'] != None else 0,
                # Número total arboles sembrados
                'NTAS': float(obj['densHectarea']) * float(obj['areaSembrada']) if obj['densHectarea'] != None and obj['areaSembrada'] != None else 0,
                # Porcentaje de arboles talados entresaca
                'PATE': float(obj['porceEntreSacas']) if obj['porceEntreSacas'] != None else 0
            }

            guardarFormulas(idEvento, variables, connection)
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Datos del sistema forestal
######################################
def camposDataForestal(dataEspecie):

    obj = {
        'faseProd': dataEspecie['faseProd'] if 'faseProd' in dataEspecie else None,
        'espAfectada': dataEspecie['espAfectada'] if 'espAfectada' in dataEspecie else None,
        'espExtractiva': dataEspecie['espExtractiva'] if 'espExtractiva' in dataEspecie else None,
        'nombre': dataEspecie['nombre'] if 'nombre' in dataEspecie else None,
        'fecha': dataEspecie['fecha'] if 'fecha' in dataEspecie else None,
        'densHectarea': float(dataEspecie['densHectarea']) if 'densHectarea' in dataEspecie else None,
        'areaSembrada': float(dataEspecie['areaSembrada']) if 'areaSembrada' in dataEspecie else None,
        'objetivo': dataEspecie['objetivo'] if 'objetivo' in dataEspecie else None,
        'noArbolesAntesAfectacion': float(dataEspecie['noArbolesAntesAfectacion']) if 'noArbolesAntesAfectacion' in dataEspecie else None,
        'noEntresacas': dataEspecie['noEntresacas'] if 'noEntresacas' in dataEspecie else None,
        'diametroPromedio': float(dataEspecie['diametroPromedio']) if 'diametroPromedio' in dataEspecie else None,
        'alturaComercial': float(dataEspecie['alturaComercial']) if 'alturaComercial' in dataEspecie else None,
        'alturaTotal': float(dataEspecie['alturaTotal']) if 'alturaTotal' in dataEspecie else None,
        'plantacionAnos': float(dataEspecie['plantacionAnos']) if 'plantacionAnos' in dataEspecie else None,
        'porceArbolesTurnoFinal': float(dataEspecie['porceArbolesTurnoFinal']) if 'porceArbolesTurnoFinal' in dataEspecie else None,
        'valorVenderProduccionAfectada': float(dataEspecie['valorVenderProduccionAfectada']) if 'valorVenderProduccionAfectada' in dataEspecie else None,
        'areaAfectadaHectareas': float(dataEspecie['areaAfectadaHectareas']) if 'areaAfectadaHectareas' in dataEspecie else None,
        'fechaAfactaForestal': dataEspecie['fechaAfactaForestal'] if 'fechaAfactaForestal' in dataEspecie else None,
        'diasAfectoSistemaForestal': float(dataEspecie['diasAfectoSistemaForestal']) if 'diasAfectoSistemaForestal' in dataEspecie else None,
        'noArbolesAfectados': dataEspecie['noArbolesAfectados'] if 'noArbolesAfectados' in dataEspecie else None,
        'vlMaderaAfectado': float(dataEspecie['vlMaderaAfectado']) if 'vlMaderaAfectado' in dataEspecie else None,
        'valEntreSacas': float(dataEspecie['valEntreSacas']) if 'valEntreSacas' in dataEspecie else None,
        'porceEntreSacas': float(dataEspecie['porceEntreSacas']) if 'porceEntreSacas' in dataEspecie else None,
    }

    return obj

# Guarda los datos del sistema de agro
def guardarSistemaAgro(idEvento, dataEspecie, sistema, connection):
    try:
        cursor = connection.cursor()
        for cultivo in dataEspecie:
            validated = validateFieldsAgro(cultivo)

            sql = ("""
            INSERT INTO Cultivos_afectados(
                cod_nombre_FK, 
                area_total_cultivo_sembrado, 
                cod_unidad_area_FK, 
                area_total_cultivo_Ha, 
                cod_tipo_material_siembra_FK, 
                cantidad_semilla_utilizo_siembra_ha, 
                cod_unidad_cantidad_semilla_FK, 
                equivalencia_kg_carga, 
                cod_semilla_equiv_Kg_FK, 
                cod_fuente_semilla_FK, 
                fch_inicio_afectacion, 
                duracion_dias_afectacion, 
                fcha_siembra, 
                mes_cosecha_cultivo, 
                mes_esperado_cosecha, 
                cant_cosechada, 
                cod_unidad_consecha_FK, 
                cod_equiva_kg_FK, 
                equivalencia_Kg_carga_zona, 
                cant_dinero_venta_cosecha, 
                proyectada_cant_produc_estim_producir, 
                proyectada_cod_unidad_reporte_FK, 
                proyectada_precio_por_cada_unidad, 
                proyectada_cod_equiva_kg_FK, 
                proyectada_equivalencia_kg, 
                proyectada_vlr_total_recibir_venta_total_produccion, 
                costo_promedio_jornal_zona, 
                porc_resiembra, 
                perdida_estimada_inversion, 
                rendimiento_esperado_productor, 
                rendimiento_real_productor, 
                perdida_estimado_rend_cultivo, 
                afectacion_infraestructura)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING cod_cultivo
                    """)

            params = (
                validated["nombreCultivo"],  # 1
                validated["areaCultivo"],  # 2
                validated["unidadArea"],  # 3
                validated["areaTotCultHa"],  # 4
                validated["materiralSiembra"],  # 5
                validated["cantSemillas"],  # 6
                validated["medidaSemilla"],  # 7
                validated["equivCargaKg"],  # 8
                validated["equivaleKilos"],  # 9
                validated["fuenteSemilla"],  # 10
                validated["fechaAfectacion"],  # 11
                validated["diasCultivoExpuesto"],  # 12
                validated["fechaSiembra"],  # 13
                validated["fechaPrimeCosecha"],  # 14
                validated["fechaEsperaCosecha"],  # 15
                validated["cantCosechada"],  # 16
                validated["medidaCantCosechada"],  # 17
                validated["equivaleKilosCosecha"],  # 18
                validated["equivKgCargZon"],  # 19
                validated["totalReciCosechado"],  # 20
                validated["cantProduProducir"],  # 21
                validated["medidaReportar"],  # 22
                validated["totalReportado"],  # 23
                validated["equivaleKilosReportar"],  # 24
                validated["proyEqvKg"],  # 25
                validated["totalProyectaVenta"],  # 26
                validated["costoPromeJornal"],  # 27
                validated["porceResiembra"],  # 28
                validated["perdEstInv"],  # 29
                validated["renEspProd"],  # 30
                validated["rendRealProd"],  # 31
                validated["perdEstimRendCult"],  # 32
                validated["afectInfr"]  # 33
            )

            cursor.execute(sql, params)

            idCultivoAfectado = cursor.fetchone()[0]
            connection.commit()

            saveCostosDirectos(idCultivoAfectado,
                               cultivo['costosDirectos'], connection)
            saveCostosIndirectos(
                idCultivoAfectado, cultivo['costosInDirectos'], connection)
            saveInfraestructura(idCultivoAfectado, cultivo, connection)

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


def validateFieldsAgro(cultivo):
    obj = {
        # 1 YA
        'nombreCultivo': cultivo['nombreCultivo'] if 'nombreCultivo' in cultivo else None,
        # 2 YA
        'areaCultivo':  cultivo['areaCultivo'] if 'areaCultivo' in cultivo else None,
        # 3 YA
        'unidadArea': cultivo['unidadArea'] if 'unidadArea' in cultivo else None,
        # 4
        'areaTotCultHa': cultivo['areaTotCultHa'] if 'areaTotCultHa' in cultivo else None,
        # 5 YA
        'materiralSiembra': cultivo['materiralSiembra'] if 'materiralSiembra' in cultivo else None,
        # 6 YA
        'cantSemillas': cultivo['cantSemillas'] if 'cantSemillas' in cultivo else None,
        # 7 YA
        'medidaSemilla': cultivo['medidaSemilla'] if 'medidaSemilla' in cultivo else None,
        # 8
        'equivCargaKg': cultivo['equivCargaKg'] if 'equivCargaKg' in cultivo else None,
        # 9  YA
        'equivaleKilos': cultivo['equivaleKilos'] if 'equivaleKilos' in cultivo else None,
        # 10  YA
        'fuenteSemilla': cultivo['fuenteSemilla'] if 'fuenteSemilla' in cultivo else None,
        # 11 YA
        'fechaAfectacion': cultivo['fechaAfectacion'] if 'fechaAfectacion' in cultivo else None,
        # 12 YA
        'diasCultivoExpuesto': cultivo['diasCultivoExpuesto'] if 'diasCultivoExpuesto' in cultivo else None,
        # 13 YA
        'fechaSiembra': cultivo['fechaSiembra'] if 'fechaSiembra' in cultivo else None,
        # 14 YA
        'fechaPrimeCosecha': cultivo['fechaPrimeCosecha']+'-01' if 'fechaPrimeCosecha' in cultivo else None,
        # 15 YA
        'fechaEsperaCosecha': cultivo['fechaEsperaCosecha']+'-01' if 'fechaEsperaCosecha' in cultivo else None,
        # 16 YA
        'cantCosechada': cultivo['cantCosechada'] if 'cantCosechada' in cultivo else None,
        # 17 YA
        'medidaCantCosechada': cultivo['medidaCantCosechada'] if 'medidaCantCosechada' in cultivo else None,
        # 18 YA
        'equivaleKilosCosecha': cultivo['equivaleKilosCosecha'] if 'equivaleKilosCosecha' in cultivo else None,
        # 19
        'equivKgCargZon': cultivo['codEquivKg'] if 'codEquivKg' in cultivo else None,
        # 20 YA
        'totalReciCosechado': cultivo['totalReciCosechado'] if 'totalReciCosechado' in cultivo else None,
        # 21 YA
        'cantProduProducir': cultivo['cantProduProducir'] if 'cantProduProducir' in cultivo else None,
        # 22 YA
        'medidaReportar': cultivo['medidaReportar'] if 'medidaReportar' in cultivo else None,
        # 23 YA
        'totalReportado': cultivo['totalReportado'] if 'totalReportado' in cultivo else None,
        # 24 YA
        'equivaleKilosReportar': cultivo['equivaleKilosReportar'] if 'equivaleKilosReportar' in cultivo else None,
        # 25
        'proyEqvKg': cultivo['proyEqvKg'] if 'proyEqvKg' in cultivo else None,
        # 26 YA
        'totalProyectaVenta': cultivo['totalProyectaVenta'] if 'totalProyectaVenta' in cultivo else None,
        # 27 YA
        'costoPromeJornal': cultivo['costoPromeJornal'] if 'costoPromeJornal' in cultivo else None,
        # 28 YA
        'porceResiembra': cultivo['porceResiembra'] if 'porceResiembra' in cultivo else None,
        # 29
        'perdEstInv': cultivo['perdEstInv'] if 'perdEstInv' in cultivo else None,
        # 30
        'renEspProd': cultivo['renEspProd'] if 'renEspProd' in cultivo else None,
        # 31
        'rendRealProd': cultivo['rendRealProd'] if 'rendRealProd' in cultivo else None,
        # 32
        'perdEstimRendCult': cultivo['perdEstimRendCult'] if 'perdEstimRendCult' in cultivo else None,
        # 33
        'afectInfr': cultivo['afectInfr'] if 'afectInfr' in cultivo else None
    }

    return obj

## Guardar datos del sistema pecuario
def guardarSistemaPecuario(idEvento, dataEspecie, sistema, connection):
    try:
        cursor = connection.cursor()
        #for produccionAnimal in dataEspecie:
        #validated = validateFieldsPecuario(dataEspecie)
        validated_apicola = validateFieldsApicola(dataEspecie)
        validated_pecuario = validateFieldsPecuario(dataEspecie)


        if len(validated_apicola) > 0:
            save_apicola(validated_apicola, connection)

        if len(validated_pecuario) > 0:
            save_pecuario(validated_pecuario, connection)
        
        

        '''
        idProduccionAnimal = cursor.fetchone()[0]


        
        
        '''
    except Exception as e: 
        connection.rollback()
        print(e)
    finally:
        cursor.close()


## Guarda los datos que vienen en el array de apicola
def save_apicola(apicolas, connection):
    try:
        for apicola in apicolas:
            cursor = connection.cursor()

            sql = ("""
                INSERT INTO Novedad_pecuaria(num_colmenas_afectadas, valor_comercial_prom_colmena,
                prod_mensual_propoleo_kg_antes_afectacion, prod_mensual_miel_litros_antes_afectacion,
                prod_mensual_jalea_litros_antes_afectacion, vlr_ingreso_prom_mensual_antes_afectacion,
                ingreso_mensual_actualmente, cod_sistema_afectado_FK) values(
                    %s,%s,%s,%s,%s,%s,%s,%s
                ) RETURNING cod_novedad_peq
            """)

            params = (
                apicola['numColmenas'],
                apicola['valorColmena'],
                apicola['propoleoMensual'],
                apicola['mielMensual'],
                apicola['jaleaMensual'],
                apicola['valorMensual'],
                apicola['ingresoMensual'],
                apicola['sistema']['sistema']
            )

            cursor.execute(sql, params)
            idProduccionAnimal = cursor.fetchone()[0]
            connection.commit()

            
            saveAfectacionPecuaria(idProduccionAnimal, 
            apicola['dataMaquinaria'], connection)
            saveMaquinariaBBA(idProduccionAnimal, 
            apicola['dataMaquinaria'], connection)
            saveMaquinariaPEM(idProduccionAnimal, 
            apicola['dataMaquinaria'], connection)
            saveInfraestructuraPecuario(idProduccionAnimal, 
            apicola['dataInfraestructura'], connection)
            
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()

## Guarda los datos que vienen en el array de pecuario
def save_pecuario(pecuarios, connection):
    try:
        cursor = connection.cursor()
        for pecuario in pecuarios:

            sql = ("""
                INSERT INTO Novedad_pecuaria(cod_sistema_afectado_fk, nombre_raza, num_total_anim_explotacion,
                peso_prom_animal_explotacion, cod_unidad_reporte_FK, precio_prom_x_animal,
                area_usada_animales, cod_unidad_area_FK, fch_inicio_actividad_productiva,
                fch_inicio_evento, num_animales_enfermos_afectados, num_animales_hembra_muertos,
                num_animales_macho_muertos, edad_promedio_meses_anim_muerto, cod_tipo_producto_FK,
                prod_mensual_antes_afectacion, prod_mensual_actual_potencial_afectacion, cod_unidad_reporte1_FK,
                """+
                #cod_equiva1_kg_FK, 
                """
                precio_venta_und_producto, huevos_producto_diferentes_avicola, sistema_afectado_nom_otro, peso_prom_animal_explotacion_nom_otro,
                eqv_kg_unidad_reportar_otro, eqv_kg_carga_report_cant_otro, unidad_area_reporte_otro, nombre_producto_obtenido_otro, eqv_kg_carga_prod_en_zona_otro) 
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_novedad_peq
            """)

            params = (
                pecuario['sistema']['sistema'],
                pecuario['nombreRaza'],
                pecuario['numAnimal'],
                pecuario['pesoAnimal'],
                pecuario['uniMedidaAnimal'],
                pecuario['valorAnimal'],
                pecuario['areaAnimal'],
                pecuario['unidadArea'],
                pecuario['fechaProduccion'],
                pecuario['fechaIniEvento'],
                pecuario['numAnimalEnfermos'],
                pecuario['numAnimalHembMuerto'],
                pecuario['numAnimalMachMuerto'],
                pecuario['edadAnimal'],
                pecuario['tipoProducto'],
                pecuario['produMensualAfectacion'],
                pecuario['produPotencial'],
                pecuario['unidadProdccion'],
                #pecuario['pesoProduccion'],
                pecuario['valorVentaProducto'],
                pecuario['huevosAvicola'], 
                pecuario['sistema']['dataCamposNuevos']['sistemaNuevo'],
                pecuario['dataCamposNuevos']['unidadMedidaNuevo']['nombre'],
                pecuario['dataCamposNuevos']['unidadMedidaNuevo']['unidad'],
                pecuario['dataCamposNuevos']['pesoNuevo'],
                pecuario['dataCamposNuevos']['unidadArea'],
                pecuario['dataCamposNuevos']['tipoProductoNuevo'],
                pecuario['dataCamposNuevos']['pesoProduccionNuevo']
                #FALTAN LOS NUEVOS CAMPOS
            )
            
            cursor.execute(sql, params)
            idProduccionAnimal = cursor.fetchone()[0]
            connection.commit()


            saveAfectacionPecuaria(idProduccionAnimal, 
            pecuario['dataMaquinaria'], connection)
            saveMaquinariaBBA(idProduccionAnimal, 
            pecuario['dataMaquinaria'], connection)
            saveMaquinariaPEM(idProduccionAnimal, 
            pecuario['dataMaquinaria'], connection)
            saveInfraestructuraPecuario(idProduccionAnimal, 
            pecuario['dataInfraestructura'], connection)

            saveCostosVariablesPecuario(idProduccionAnimal, 
            pecuario['costosVariables'], connection)
            saveCostosFijosPecuario(idProduccionAnimal, 
            pecuario['costosFijos'], connection)

            '''
            # FALTA CORREGIR
            
            '''
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


# Validated that the information sended in the request has the needed info, otherwise, the needed info is filled with none
def validateFieldsApicola(dataEspecie):
    array_apicola = []
    if len(dataEspecie) > 0:
        for _sistema in dataEspecie:
            dataApicola = _sistema['dataApicola']
            for sistema in dataApicola:
                cod_sistema = None
                if 'sistema' in sistema and 'sistema' in sistema['sistema']:
                    cod_sistema = sistema['sistema']['sistema']

                array_apicola.append(
                    {
                        'numColmenas': sistema['numColmenas'] if 'numColmenas' in sistema else None,
                        'valorColmena': sistema['valorColmena'] if 'valorColmena' in sistema else None,
                        'propoleoMensual': sistema['propoleoMensual'] if 'propoleoMensual' in sistema else None,
                        'mielMensual': sistema['mielMensual'] if 'mielMensual' in sistema else None,
                        'jaleaMensual': sistema['jaleaMensual'] if 'jaleaMensual' in sistema else None,
                        'valorMensual': sistema['valorMensual'] if 'valorMensual' in sistema else None,
                        'ingresoMensual': sistema['ingresoMensual'] if 'ingresoMensual' in sistema else None,
                        'sistema': sistema['sistema'] if 'sistema' in sistema else None,
                        'codSistema': cod_sistema,
                        'dataMaquinaria': sistema['dataMaquinaria'] if 'dataMaquinaria' in sistema else None,
                        'dataInfraestructura': sistema['dataInfraestructura'] if 'dataInfraestructura' in sistema else None,
                    }
                )
        
    return array_apicola


# Validated that the information sended in the request has the needed info, otherwise, the needed info is filled with none
def validateFieldsPecuario(dataEspecie):
    array_pecuario = []
    if len(dataEspecie) > 0:
        for _sistema in dataEspecie:
            dataPecuario = _sistema['dataPecuario']
            for sistema in dataPecuario:
                array_pecuario.append(
                    {
                        'dataCamposNuevos': sistema['dataCamposNuevos'] if 'dataCamposNuevos' in sistema else None,
                        'nombreRaza': sistema['nombreRaza'] if 'nombreRaza' in sistema else None,
                        'pesoAnimal': sistema['pesoAnimal'] if 'pesoAnimal' in sistema else None,
                        'numAnimal': sistema['numAnimal'] if 'numAnimal' in sistema else None,
                        'uniMedidaAnimal': sistema['uniMedidaAnimal'] if 'uniMedidaAnimal' in sistema else None,
                        'peso': sistema['peso'] if 'peso' in sistema else None,
                        'valorAnimal': sistema['valorAnimal'] if 'valorAnimal' in sistema else None,
                        'areaAnimal': sistema['areaAnimal'] if 'areaAnimal' in sistema else None,
                        'unidadArea': sistema['unidadArea'] if 'unidadArea' in sistema else None,
                        'menuFechaProduccion': sistema['menuFechaProduccion'] if 'menuFechaProduccion' in sistema else None,
                        'fechaProduccion': sistema['fechaProduccion'] if 'fechaProduccion' in sistema else None,
                        'menuFechaIniEvento': sistema['menuFechaIniEvento'] if 'menuFechaIniEvento' in sistema else None,
                        'fechaIniEvento': sistema['fechaIniEvento'] if 'fechaIniEvento' in sistema else None,
                        'numAnimalEnfermos': sistema['numAnimalEnfermos'] if 'numAnimalEnfermos' in sistema else None,
                        'numAnimalHembMuerto': sistema['numAnimalHembMuerto'] if 'numAnimalHembMuerto' in sistema else None,
                        'numAnimalMachMuerto': sistema['numAnimalMachMuerto'] if 'numAnimalMachMuerto' in sistema else None,
                        'edadAnimal': sistema['edadAnimal'] if 'edadAnimal' in sistema else None,
                        'tipoProducto': sistema['tipoProducto'] if 'tipoProducto' in sistema else None,
                        'produMensualAfectacion': sistema['produMensualAfectacion'] if 'produMensualAfectacion' in sistema else None,
                        'produPotencial': sistema['produPotencial'] if 'produPotencial' in sistema else None,
                        'unidadProdccion': sistema['unidadProdccion'] if 'unidadProdccion' in sistema else None,
                        'pesoProduccion': sistema['pesoProduccion'] if 'pesoProduccion' in sistema else None,
                        'valorVentaProducto': sistema['valorVentaProducto'] if 'valorVentaProducto' in sistema else None,
                        'huevosAvicola': sistema['huevosAvicola'] if 'huevosAvicola' in sistema else None,
                        'costosVariables': validatedCostosVariablesPecuario(sistema) if 'costosVariables' in sistema else None,
                        'costosFijos': validatedCostosFijosPecuario(sistema) if 'costosFijos' in sistema else None,
                        'sistema': sistema['sistema'] if 'sistema' in sistema else None,
                        'dataMaquinaria': sistema['dataMaquinaria'] if 'dataMaquinaria' in sistema else None,
                        'dataInfraestructura': sistema['dataInfraestructura'] if 'dataInfraestructura' in sistema else None,
                        'dataMaquinaria': sistema['dataMaquinaria'] if 'dataMaquinaria' in sistema else None
                    }
                )
        #print(array_pecuario) # VERIFICAR QUE LOS COSTOS NO SE ESTAN GUARDANDO BIEN
    
    return array_pecuario


def validatedCostosVariablesPecuario(_sistema):
    sistema = _sistema['costosVariables'][0]
    array_costo = []
    for costo in sistema:
        array_costo.append(
            {
                'tipoCosto': costo['tipoCosto'] if 'tipoCosto' in costo else None,
                'valor': costo['valor'] if 'valor' in costo else None
            }
        )
    
    return array_costo

def validatedCostosFijosPecuario(_sistema):
    sistema = _sistema['costosFijos'][0]
    array_costo = []
    for costo in sistema:
        array_costo.append(
            {
                'tipoCosto': costo['tipoCosto'] if 'tipoCosto' in costo else None,
                'valor': costo['valor'] if 'valor' in costo else None
            }
        )
    
    return array_costo


# Guardar costos directos
def saveCostosDirectos(idCultivoAfectado, costosDirectos, connection):
    try:
        cursor = connection.cursor()
        for costo in costosDirectos:
            validated = validateCostosDirectos(costo)

            sql = ("""
                INSERT INTO costos_de_produccion(cod_actividad_FK, num_jornales, cod_cultivo_afectado_FK, gastos)
                VALUES(%s, %s, %s, %s)
            """)

            params = (
                validated['id'], validated['noJornales'], idCultivoAfectado, validated['costo']
            )

            cursor.execute(sql, params)
            connection.commit()

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


# Validar costos directos
def validateCostosDirectos(costo):
    noJornales = costo['noJornales']
    _costo = costo['costo']

    if costo['costo'] == '' or not 'costo' in costo:
        _costo = None

    if costo['noJornales'] == '' or not 'noJornales' in costo:
        noJornales = None

    obj = {
        'actividad': costo['actividad'] if 'actividad' in costo else None,
        'costo': _costo,
        'id': costo['id'] if 'id' in costo else None,
        'noJornales': noJornales,
    }

    return obj


# Guardar costos indirectos
def saveCostosIndirectos(idCultivoAfectado, costosIndirectos, connection):
    try:
        cursor = connection.cursor()
        for costo in costosIndirectos:
            validated = validateCostosIndirectos(costo)

            sql = ("""
                INSERT INTO costos_indirectos_produccion(cod_rubro_FK, gastos_incurridos, cod_cultivo_afectado_FK)
                VALUES(%s, %s, %s)
            """)

            params = (
                validated['id'], validated['costo'], idCultivoAfectado
            )

            cursor.execute(sql, params)
            connection.commit()

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


# Validar costos indirectos
def validateCostosIndirectos(costo):
    obj = {
        'actividad': costo['actividad'] if 'actividad' in costo else None,
        'costo': costo['costo'] if 'costo' in costo else None,
        'id': costo['id'] if 'id' in costo else None,
    }

    return obj


# Guardar infraestructuras
def saveInfraestructura(idCultivoAfectado, dataEspecie, connection):
    if 'tipoInfraFertilizante' in dataEspecie:
        validatedFertilizante = validateTipoInfraFertilizante(
            dataEspecie['tipoInfraFertilizante'])
        saveFertilizante(validatedFertilizante, idCultivoAfectado, connection)

    if 'tipoInfraMaquinaria' in dataEspecie:
        validatedMaquinaria = validateTipoInfraMaquinaria(
            dataEspecie['tipoInfraMaquinaria'])
        saveMaquinaria(validatedMaquinaria, idCultivoAfectado, connection)

    if 'tipoInfraPlaguicidas' in dataEspecie:
        validatedPlaguicida = validateTipoInfraPlaguicidas(
            dataEspecie['tipoInfraPlaguicidas'])
        savePlaguicida(validatedPlaguicida, idCultivoAfectado, connection)

    if 'tipoInfraSemilla' in dataEspecie:
        validatedSemilla = validatedTipoInfraSemilla(
            dataEspecie['tipoInfraSemilla'])
        saveSemilla(validatedSemilla, idCultivoAfectado, connection)


# Valida que todos los campos del fertilizante necesarios tengan un valor
def validateTipoInfraFertilizante(infraestructura):
    validatedInfraestructura = []
    for fertilizante in infraestructura:
        obj = {
            'canFertilizante': fertilizante['canFertilizante'] if 'canFertilizante' in fertilizante else None,
            'fechaAdquisicion': fertilizante['fechaAdquisicion'] if 'fechaAdquisicion' in fertilizante else None,
            'idTipoFertilizante': fertilizante['idTipoFertilizante'] if 'idTipoFertilizante' in fertilizante else None,
            'menuFechaAdquisicion': fertilizante['menuFechaAdquisicion'] if 'menuFechaAdquisicion' in fertilizante else None,
            'nombre': fertilizante['nombre'] if 'nombre' in fertilizante else None,
            'nombreTipoFerti': fertilizante['nombreTipoFerti'] if 'nombreTipoFerti' in fertilizante else None,
            'valPesos': fertilizante['valPesos'] if 'valPesos' in fertilizante else None,
        }

        validatedInfraestructura.append(obj)

    return validatedInfraestructura


# Guarda todos los fertilizantes en la tabla infraestructura
def saveFertilizante(fertilizantes, idCultivoAfectado, connection):
    try:
        cursor = connection.cursor()
        for fertilizante in fertilizantes:
            sql = ("""
                INSERT INTO infraestructura(cod_tipo_infraestructura_FK, cod_especie_FK, cod_tipo_fertilizante_FK, nom_fertilizante,
                fch_adquisicion, cant_fert_almac_afect, vlr_fertilizante_almacenado) VALUES(%s,%s,%s,%s,%s,%s,%s)
            """)

            params = (
                2, idCultivoAfectado, fertilizante['idTipoFertilizante'], fertilizante[
                    'nombre'], fertilizante['fechaAdquisicion'],
                fertilizante['canFertilizante'], fertilizante['valPesos']
            )

            cursor.execute(sql, params)
            connection.commit()

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()



# Valida que tofos los campos de maquinaria tengan un valor
def validateTipoInfraMaquinaria(infraestructura):
    validatedInfraestructura = []
    for maquinaria in infraestructura:
        obj = {
            'anoAdquisicion': maquinaria['anoAdquisicion'] if 'anoAdquisicion' in maquinaria else None,
            'idTipoMaquinariaAgricola': maquinaria['idTipoMaquinariaAgricola'] if 'idTipoMaquinariaAgricola' in maquinaria else None,
            'nombreTipoMaquinaria': maquinaria['nombreTipoMaquinaria'] if 'nombreTipoMaquinaria' in maquinaria else None,
            'porceDisminucion': maquinaria['porceDisminucion'] if 'porceDisminucion' in maquinaria else None,
            'valorPesos': maquinaria['valorPesos'] if 'valorPesos' in maquinaria else None,
        }

        validatedInfraestructura.append(obj)

    return validatedInfraestructura


# Guarda la maquinaria en la tabla infraestructura
def saveMaquinaria(maquinarias, idCultivoAfectado, connection):
    try:
        cursor = connection.cursor()
        for maquinaria in maquinarias:
            sql = ("""
                INSERT INTO infraestructura(cod_tipo_infraestructura_FK, cod_especie_FK, cod_tipo_maq_agr_afec_FK, fch_adquisicion_equipo, 
                edad_equipo, vlr_pesos_afectacion_maq, porc_disminuyo_prod_afect_maq) VALUES(%s,%s,%s,%s,%s,%s,%s)
            """)

            actual_year = datetime.date.today().year
            maquinaria_edad = actual_year - int(maquinaria['anoAdquisicion'])
            params = (
                4, idCultivoAfectado, maquinaria['idTipoMaquinariaAgricola'], maquinaria['anoAdquisicion'] +
                '-01-01',  maquinaria_edad,
                maquinaria['valorPesos'], maquinaria['porceDisminucion']
            )

            cursor.execute(sql, params)
            connection.commit()

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


# Valida que tofos los campos de plaguicidas tengan un valor
def validateTipoInfraPlaguicidas(infraestructura):
    validatedPlaguicidas = []
    for plaguicida in infraestructura:
        obj = {
            'cantPlaguicidaKg': plaguicida['cantPlaguicidaKg'] if 'cantPlaguicidaKg' in plaguicida else None,
            'cantPlaguicidaLt': plaguicida['cantPlaguicidaLt'] if 'cantPlaguicidaLt' in plaguicida else None,
            'idTipoPlaguicida': plaguicida['idTipoPlaguicida'] if 'idTipoPlaguicida' in plaguicida else None,
            'idTipoPresentacion': plaguicida['idTipoPresentacion'] if 'idTipoPresentacion' in plaguicida else None,
            'nombreTipoPlaguicida': plaguicida['nombreTipoPlaguicida'] if 'nombreTipoPlaguicida' in plaguicida else None,
            'valPesos': plaguicida['valPesos'] if 'valPesos' in plaguicida else None,
        }

        validatedPlaguicidas.append(obj)

    return validatedPlaguicidas


# Guarda el plaguicida en la tabla infraestructura
def savePlaguicida(plaguicidas, idCultivoAfectado, connection):
    try:
        cursor = connection.cursor()
        for plaguicida in plaguicidas:
            sql = ("""
                INSERT INTO infraestructura(cod_tipo_infraestructura_FK, cod_especie_FK, cod_tipo_plaguicida_FK, cod_presentacion_FK, 
                cantidad_plaguicidas_almac_afec_litros, cantidad_plaguicidas_almac_afec_kg, vlr_pesos_plaguicidas) 
                VALUES(%s,%s,%s,%s,%s,%s,%s)
            """)

            params = (
                3, idCultivoAfectado, plaguicida['idTipoPlaguicida'], plaguicida[
                    'idTipoPresentacion'], plaguicida['cantPlaguicidaLt'],
                plaguicida['cantPlaguicidaKg'], plaguicida['valPesos']
            )

            cursor.execute(sql, params)
            connection.commit()

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


# Valida que todos los campos de semillas tengan un valor
def validatedTipoInfraSemilla(infraestructura):
    validatedSemilla = []
    for semilla in infraestructura:
        obj = {
            'canSemillas': semilla['canSemillas'] if 'canSemillas' in semilla else None,
            'especie': semilla['especie'] if 'especie' in semilla else None,
            'valPesos': semilla['valPesos'] if 'valPesos' in semilla else None,
        }

        validatedSemilla.append(obj)
    return validatedSemilla


# Guarda la semilla en la tabla infraestructura
def saveSemilla(semillas, idCultivoAfectado, connection):
    try:
        cursor = connection.cursor()
        for semilla in semillas:
            sql = ("""
                INSERT INTO infraestructura(cod_tipo_infraestructura_FK, cod_especie_FK, cant_semilla_almacenada_kg, vlr_semilla_pesos)
                VALUES(%s,%s,%s,%s)
            """)

            params = (
                1, idCultivoAfectado, semilla['canSemillas'], semilla['valPesos']
            )

            cursor.execute(sql, params)
            connection.commit()

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


# Guardar los costos variables del modulo pecuario
def saveCostosVariablesPecuario(idProduccionAnimal, costosVariables, connection):
    ## FUNCIONA
    try:
        cursor = connection.cursor()
        for costo in costosVariables:
            #validated = validateCostoVariablPecuario(costo)
            sql = ("""
                INSERT INTO Costos_variables_pecuario(cod_actividad_FK,
                valor, cod_novedad_peq_FK) 
                VALUES(%s, %s, %s)
            """)

            params = (
                costo["tipoCosto"],
                costo["valor"],
                idProduccionAnimal
            )
            cursor.execute(sql, params)
            connection.commit()

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


# Guardar los costos fijos del modulo pecuario
def saveCostosFijosPecuario(idProduccionAnimal, costosFijos, connection):
    ## FUNCIONA
    try:
        cursor = connection.cursor()
        for costo in costosFijos:
            #validated = validateCostoFijo(costo)
            sql = ("""
                INSERT INTO Costos_fijos_pecuarios(cod_rubro_FK, 
                gasto_incurrido, cod_novedad_peq_FK)
                VALUES(%s,%s,%s)
            """)

            params = (
                costo["tipoCosto"],
                costo["valor"],
                idProduccionAnimal
            )

            cursor.execute(sql, params)
            connection.commit()
            
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()



# Guardar la afectacion del modulo pecuario
def saveAfectacionPecuaria(idProduccionAnimal, afectacionesPeq, connection):
    ## FALTA LO DE CODUNIDAD Y PROBAR
    try:
        cursor = connection.cursor()
        for afectacion in afectacionesPeq:
            validated = validateAfectacionPeq(afectacion)
            sql = ("""
                INSERT INTO Afectacion_peq(cod_tipo_insumo_FK, nombre_comercial,
                cantidad_insumos, cod_novedad_pecuaria_FK, 
                """+
                #cod_unidad_FK FALTA ESTO
                """
                vlr_pesos_afectacion, tipo_insumo_nom_otro) 
                VALUES(%s, %s, %s, %s, %s, %s)
            """)

            params = (
                validated['tipoInsumo'],
                validated['nombreComercial'],
                validated['cantInsumo'],
                idProduccionAnimal,
                #validated['codUnidad'], # NO HAY COD UNIDAD EN EL EJEMPLO ENVIADO
                validated['valorBienes'],
                validated['dataCamposNuevos']['nuevoInsumo']
            )

            cursor.execute(sql, params)
            connection.commit()

    except Exception as e:
        connection.rollback()
        print(e)
    finally: 
        cursor.close()


# Validar la afectacion del modulo pecuario
def validateAfectacionPeq(afectacion):
    obj = {
        'tipoInsumo': afectacion['tipoInsumo'] if 'tipoInsumo' in afectacion else None,
        'nombreComercial': afectacion['nombreComercial'] if 'nombreComercial' in afectacion else None,
        'cantInsumo': afectacion['cantInsumo'] if 'cantInsumo' in afectacion else None,
        'codUnidad': afectacion['codUnidad'] if 'codUnidad' in afectacion else None, ## ESTO AUN FALTA, PORQUE NO LO ENCUENTRO EN EL EJEMPLO
        'valorBienes': afectacion['valorBienes'] if 'valorBienes' in afectacion else None,
        'dataCamposNuevos': afectacion['dataCamposNuevos'] if 'dataCamposNuevos' in afectacion else None
    }

    return obj


# Guardar la maquinaria bba del modulo pecuario
def saveMaquinariaBBA(idProduccionAnimal, maquinarias, connection):
    ## LISTO, FALTA PROBAR QUE FUNCIONE
    try:
        cursor = connection.cursor()
        for maquinaria in maquinarias:
            validated = validateMaquinariaBBA(maquinaria)
            sql = ("""
                INSERT INTO Maquinaria_bba(cod_tipo_maquinaria_FK,
                nombre_maquinaria, vlr_pesos_afectacion, cod_novedad_pecuaria_FK)
                VALUES(%s,%s,%s,%s)
            """)

            params = (
                validated['tipoMaquinariaBba'],
                validated ['nombreMaquinariaBba'],
                validated['valorReparacionBba'],
                idProduccionAnimal
            )

            cursor.execute(sql, params)
            connection.commit()

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


# Valida la maquinaria bba del modulo pecuario
def validateMaquinariaBBA(maquinaria):
    obj = {
        'tipoMaquinariaBba': maquinaria['tipoMaquinariaBba'] if 'tipoMaquinariaBba' in maquinaria else None,
        'nombreMaquinariaBba': maquinaria['nombreMaquinariaBba'] if 'nombreMaquinariaBba' in maquinaria else None,
        'valorReparacionBba': maquinaria['valorReparacionBba'] if 'valorReparacionBba' in maquinaria else None,
    }

    return obj


def saveMaquinariaPEM(idProduccionAnimal, maquinarias, connection):
    ## LISTO, SOLO FALTA PROBAR QUE FUNCIONE
    try:
        cursor = connection.cursor()
        for maquinaria in maquinarias:
            validated = validateMaquinariaPEM(maquinaria)

            sql = ("""
                INSERT INTO Maquinaria_pem(cod_tipo_maquinaria_FK,
                nombre_marca_bien, vlr_pesos_afectacion, cod_novedad_pecuaria_FK)
                VALUES(%s,%s,%s,%s)
            """)

            params = (
                validated['tipoMaquinariaPem'],
                validated['nombreMarcaPem'],
                validated['valorReparacionPem'],
                idProduccionAnimal
            )
            cursor.execute(sql, params)
            connection.commit()

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


# Validar maquinaria PEM del modulo pecuario
def validateMaquinariaPEM(maquinaria):
    obj = {
        'tipoMaquinariaPem': maquinaria['tipoMaquinariaPem'] if 'tipoMaquinariaPem' in maquinaria else None,
        'nombreMarcaPem': maquinaria['nombreMarcaPem'] if 'nombreMarcaPem' in maquinaria else None,
        'valorReparacionPem': maquinaria['valorReparacionPem'] if 'valorReparacionPem' in maquinaria else None
    }

    return obj


# Guardar infraestructura pecuario
def saveInfraestructuraPecuario(idProduccionAnimal, infraestructuras, connection):
    ## LISTO, FALTA VERIFICAR QUE FUNCIONE!!
    try:
        cursor = connection.cursor()
        for infraestructura in infraestructuras:
            validated = validateInfraestructuraPecuario(infraestructura)

            sql = ("""
                INSERT INTO Infraestructura_pecuario(cod_tipo_activo_FK,
                nombre_equipo, fecha_adquisicion_bien, precio_pagado,
                vlr_invertido_reparacion, cod_novedad_pecuario_FK,
                cod_tipo_construccion_FK, area_m2_construccion_afectada,
                vlr_invertido_re_construccion, tiempo_realizar_reparacion_meses)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """)

            params = (
                validated['tipActivo'],
                validated['nombreEquipo'],
                validated['fechaAdquisicion'],
                validated['valorPagado'],
                validated['valorReponer'],
                idProduccionAnimal,
                validated['tipAfecta'],
                validated['areaAfectada'],
                validated['valorReparacion'],
                validated['mesesReparacion']
            )

            cursor.execute(sql, params)
            connection.commit()

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


def validateInfraestructuraPecuario(infraestructura):
    obj = {
        'tipActivo': infraestructura['tipActivo'] if 'tipActivo' in infraestructura else None,
        'nombreEquipo': infraestructura['nombreEquipo'] if 'nombreEquipo' in infraestructura else infraestructura['nombreEquipoConstruc']  if 'nombreEquipoConstruc' in infraestructura else None,
        # menuFechaAdquisicion y menuFechaConstruc ??
        'fechaAdquisicion': infraestructura['fechaAdquisicion'] if 'fechaAdquisicion' in infraestructura else infraestructura['fechaConstruc'] if 'fechaConstruc' in infraestructura else None,
        'valorPagado': infraestructura['valorPagado'] if 'valorPagado' in infraestructura else infraestructura['valorPagadoConstruc'] if 'valorPagadoConstruc' in infraestructura else None,
        'valorReponer': infraestructura['valorReponer'] if 'valorReponer' in infraestructura else infraestructura['valorReponerConstruc'] if 'valorReponerConstruc' in infraestructura else None,
        # nombreActivo ??
        'tipAfecta': infraestructura['tipAfecta'] if 'tipAfecta' in infraestructura else None,
        'areaAfectada': infraestructura['areaAfectada'] if 'areaAfectada' in infraestructura else None,
        'valorReparacion': infraestructura['valorReparacion'] if 'valorReparacion' in infraestructura else None,
        'mesesReparacion': infraestructura['mesesReparacion'] if 'mesesReparacion' in infraestructura else None
    }

    return obj


######################################
# Guardar relación entre el sistema y
# su infraestructura.
######################################
def gaurdarRelSistemaInfraestructura(dataEspecie, idSistema, connection):
    if ('tipoInfraestructura' in dataEspecie) != 1:
        return

    try:
        cursor = connection.cursor()
        for tipoInfraestructura in dataEspecie['tipoInfraestructura']:
            obj = {
                'cod_tipo_infraestrucrtura_FK': None,
                'nom_especie_semilla': None,
                'cod_tip_semilla_FK': None,
                'cant_semilla_almacenada': None,
                'cod_unidad_FK': None,
                'vlr_pesos_afectacion': None,
                'cod_tipo_fertilizante_FK': None,
                'nombre_fertilizante': None,
                'cantidad': None,
                'valor_pesos_afectacion': None,
                'nom_plaguicida': None,
                'cod_tipo_plaguicida_FK': None,
                'cant_plaguicidas': None,
                'vlr_pesos_afectacion_pla': None,
                'cod_tipo_maquinaria_FK': None,
                'nom_comercial': None,
                'vlr_pesos_afectacion_maq': None,
                'cod_especie_forestal_sembrada_FK': None,
            }

            validacion = [
                {'campo': 'tipoInfraestructura',
                    'valor': tipoInfraestructura, 'obligatorio': 1},
            ]
            estadoValidate = validarCampos(validacion)

            obj['cod_tipo_infraestrucrtura_FK'] = tipoInfraestructura

            if estadoValidate == 0:
                return jsonify({'message': 'Error en validación de datos.'}), 400

            if tipoInfraestructura == 1:
                obj['nom_especie_semilla'] = dataEspecie['semilla']['especieSemilla']
                obj['cod_tip_semilla_FK'] = dataEspecie['semilla']['tipo']
                obj['cant_semilla_almacenada'] = dataEspecie['semilla']['cantidadAlmacenada']
                obj['cod_unidad_FK'] = dataEspecie['semilla']['unidad']
                obj['vlr_pesos_afectacion'] = dataEspecie['semilla']['valorPesoAfectado']

            if tipoInfraestructura == 2:
                obj['cod_tipo_fertilizante_FK'] = dataEspecie['fertilizante']['tipoFertilizante']
                obj['nombre_fertilizante'] = dataEspecie['fertilizante']['nombreFertilizante']
                obj['cantidad'] = dataEspecie['fertilizante']['cantidadKgLt']
                obj['valor_pesos_afectacion'] = dataEspecie['fertilizante']['valorPeso']

            if tipoInfraestructura == 3:
                obj['nom_plaguicida'] = dataEspecie['plaguicida']['nombreFertilizante']
                obj['cod_tipo_plaguicida_FK'] = dataEspecie['plaguicida']['listaPresentacion']
                obj['cant_plaguicidas'] = dataEspecie['plaguicida']['cantidad']
                obj['vlr_pesos_afectacion_pla'] = dataEspecie['plaguicida']['valorPeso']

            if tipoInfraestructura == 4:
                obj['cod_tipo_maquinaria_FK'] = dataEspecie['maquinariaAgricola']['tipoMaquinariaAgricola']
                obj['nom_comercial'] = dataEspecie['maquinariaAgricola']['nombreMarca']
                obj['vlr_pesos_afectacion_maq'] = dataEspecie['maquinariaAgricola']['valorPeso']

            obj['cod_especie_forestal_sembrada_FK'] = idSistema

            sqlInsert = ("""
            INSERT INTO infraestructura_forestal (cod_tipo_infraestrucrtura_FK,nom_especie_semilla,
                                                cod_tip_semilla_FK,cant_semilla_almacenada,cod_unidad_FK,
                                                vlr_pesos_afectacion,cod_tipo_fertilizante_FK,nombre_fertilizante,
                                                cantidad,valor_pesos_afectacion,
                                                nom_plaguicida,cod_tipo_plaguicida_FK,cant_plaguicidas,
                                                vlr_pesos_afectacion_pla,cod_tipo_maquinaria_FK,nom_comercial,
                                                vlr_pesos_afectacion_maq,cod_especie_forestal_sembrada_FK)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)  RETURNING cod_infraestructura_forestal
            """)
            val = (obj['cod_tipo_infraestrucrtura_FK'], obj['nom_especie_semilla'],
                obj['cod_tip_semilla_FK'], obj['cant_semilla_almacenada'],
                obj['cod_unidad_FK'], obj['vlr_pesos_afectacion'], obj['cod_tipo_fertilizante_FK'],
                obj['nombre_fertilizante'], obj['cantidad'], obj['valor_pesos_afectacion'],
                obj['nom_plaguicida'], obj['cod_tipo_plaguicida_FK'], obj['cant_plaguicidas'],
                obj['vlr_pesos_afectacion_pla'], obj['cod_tipo_maquinaria_FK'], obj['nom_comercial'],
                obj['vlr_pesos_afectacion_maq'], obj['cod_especie_forestal_sembrada_FK'],)

            cursor.execute(sqlInsert, val)
            idInfraestructuraForestal = cursor.fetchone()[0]


            if tipoInfraestructura == 1:
                guardarRelLotePropagacion(dataEspecie['semilla']['lotePropagacionSemilla'], idInfraestructuraForestal,
                                        connection)
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()



######################################
# Guardar relación entre la semilla y
# el lote de propagación.
######################################
def guardarRelLotePropagacion(lotePropagacionSemilla, idInfraestructuraForestal, connection):
    
    try:
        cursor = connection.cursor()
        for lote in lotePropagacionSemilla:


            validacion = [
                {'campo': 'lote', 'valor': lote, 'obligatorio': 1}
            ]
            estadoValidate = validarCampos(validacion)

            if estadoValidate == 0:
                return jsonify({'message': 'Error en validación de datos.'}), 400

            sqlInsert = ("""
            INSERT INTO infraestructura_lote_propagacion (cod_infraestructura_FK, cod_lote_propagacion_FK)
            VALUES (%s,%s)
            """)
            val = (idInfraestructuraForestal, lote)
            cursor.execute(sqlInsert, val)

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Guardar relación entre el evento y
# el sistema.
######################################
def guardarRelEventoSistema(idEvento, sistema, idSistema, connection):
    try:
        cursor = connection.cursor()
        obj = {
            'idEvento': idEvento['id'],
            'cod_sist_prod_afect_FK': sistema,
            'cod_cultivo_afectado_FK': idSistema if sistema == 1 else None,
            'cod_especie_forestal_FK': idSistema if sistema == 3 else None,
            'cod_novedad_pesquera_FK': idSistema if sistema == 4 else None,
            'cod_novedad_pecuaria_FK': idSistema if sistema == 2 else None,
        }

        validacion = [
            {'campo': 'idEvento', 'valor': idEvento['id'], 'obligatorio': 1},
            {'campo': 'sistema', 'valor': sistema, 'obligatorio': 1},
            {'campo': 'idSistema', 'valor': idSistema, 'obligatorio': 1},
        ]
        estadoValidate = validarCampos(validacion)

        if estadoValidate == 0:
            return jsonify({'message': 'Error en validación de datos.'}), 400

        sqlInsert = ("""
        INSERT INTO evento_sist_prod_afectado (cod_evento_FK, cod_sist_prod_afect_FK,cod_especie_forestal_FK)
        VALUES (%s,%s,%s)
        """)
        val = (obj['idEvento'], obj['cod_sist_prod_afect_FK'],
            obj['cod_especie_forestal_FK'])

        cursor.execute(sqlInsert, val)

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Guardar relación entre el sistema y
# los costos directos e indiretos
######################################
def gaurdarRelSistemaCostos(idEvento, idSistema, dataEspecie, connection):
    costoTotalDirecto = guardarCostosDirectos(
        idEvento, idSistema, dataEspecie['costosDirectos'], connection)
    costoTotalInDirecto = guardarCostosInDirectos(
        idEvento, idSistema, dataEspecie['costosInDirectos'], connection)
    return {
        'costoTotalDirecto': costoTotalDirecto,
        'costoTotalInDirecto': costoTotalInDirecto,
    }


######################################
# Guardar costos directos
######################################
def guardarCostosDirectos(idEvento, idSistema, costosDirectos, connection):
    costoTotalDirecto = 0
    try:
        cursor = connection.cursor()
        for costo in costosDirectos:

            costoTotalDirecto += float(costo['costo'])

            obj = {
                'costo': costo['costo'] if costo['costo'] else None,
                'idActividad': costo['id'] if costo['id'] else None,
                'idSistema': idSistema if idSistema else None,
            }

            validacion = [
                {'campo': 'costo', 'valor': costo['costo'], 'obligatorio': 1},
                {'campo': 'idActividad', 'valor': costo['id'], 'obligatorio': 1},
                {'campo': 'idSistema', 'valor': idSistema, 'obligatorio': 1},
            ]
            estadoValidate = validarCampos(validacion)

            if estadoValidate == 0:
                return jsonify({'message': 'Error en validación de datos.'}), 400

            sqlInsert = ("""
            INSERT INTO costos_directos (gasto_incurrido, cod_actividad_fk, cod_especie_forestal_fk)
            VALUES (%s,%s,%s)
            """)
            val = (obj['costo'], obj['idActividad'], obj['idSistema'])

            cursor.execute(sqlInsert, val)

        return costoTotalDirecto
    
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Guardar costos indirectos
######################################
def guardarCostosInDirectos(idEvento, idSistema, costosInDirectos, connection):
    costoTotalInDirecto = 0

    try:
        cursor = connection.cursor()
        for costo in costosInDirectos:

            costoTotalInDirecto += float(costo['costo'])

            obj = {
                'costo': costo['costo'] if costo['costo'] else None,
                'idRubro': costo['id'] if costo['id'] else None,
                'idSistema': idSistema if idSistema else None,
            }

            validacion = [
                {'campo': 'costo', 'valor': costo['costo'], 'obligatorio': 1},
                {'campo': 'idRubro', 'valor': costo['id'], 'obligatorio': 1},
                {'campo': 'idSistema', 'valor': idSistema, 'obligatorio': 1},
            ]
            estadoValidate = validarCampos(validacion)

            if estadoValidate == 0:
                return jsonify({'message': 'Error en validación de datos.'}), 400

            sqlInsert = ("""
            INSERT INTO costos_fijos_indirectos (gasto_incurrido, cod_rubro_fk, cod_especie_forestal_fk)
            VALUES (%s,%s,%s)
            """)
            val = (obj['costo'], obj['idRubro'], obj['idSistema'])

            cursor.execute(sqlInsert, val)

        return costoTotalInDirecto

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Guardar formulas por evento
######################################
def guardarFormulas(idEvento, variables, connection):
    # formulas
    siglas = ['PE', 'VPE', 'PPR']

    for sigla in siglas:
        calcularYGuardarFormula(idEvento, variables, sigla, connection)


######################################
# Guardar formulas por evento
######################################
def calcularYGuardarFormula(idEvento, variables, sigla, connection):
    formula = ''

    if (sigla == 'PE'):
        if variables['CT'] != 0:
            formula = round(
                (variables['CT'] - variables['VTENT']) / (variables['CT'] * 100), 2)
        else:
            formula = 0
    if (sigla == 'VPE'):
        formula = round((variables['CT'] - variables['VTENT']), 2)
    if (sigla == 'PPR'):
        if variables['NTAS'] != 0:
            formula = round((variables['NAF'] / variables['NTAS']) -
                            ((variables['NTAS'] * variables['PATE']) * 100), 2)
        else:
            formula = 0

    # Fecha actual
    fechaActual = datetime.datetime.utcnow()

    idIndicador = consultarIdFormulaPorSigla(sigla, connection)
    variablesIndicador = consultarVariablesPorIndicador(
        idIndicador['cod_indicador'], connection)

    try:
        cursor = connection.cursor()

        sqlInsertIndicador = ("""
        INSERT INTO indicador_valor (valor, cod_indicador_FK, cod_evento_FK)
        VALUES (%s,%s,%s) RETURNING cod_indicador_valor
        """)
        valIndicador = (formula, idIndicador['cod_indicador'], idEvento['id'])
        cursor.execute(sqlInsertIndicador, valIndicador)

        codIndicador = cursor.fetchone()[0]

        for variable in variablesIndicador:
            costo = variables[str(variable['siglas'])]

            idVariable = consultarIdVariablePorSigla(
                variable['siglas'], connection)


            sqlInsertVariable = ("""
            INSERT INTO variable_valor (fch_actualizacion, valor, cod_variable_FK)
            VALUES (%s,%s,%s) RETURNING cod_variable_valor
            """)

            valVariable = (fechaActual, costo, idVariable['cod_variable'])
            cursor.execute(sqlInsertVariable, valVariable)
            codVariable = cursor.fetchone()[0]

            sqlInsertRelVariableIndicador = ("""
            INSERT INTO indicador_valor_variable_valor (indicador_valor_FK, variable_valor_FK)
            VALUES (%s,%s)
            """)

            valRel = (codIndicador, codVariable)
            cursor.execute(sqlInsertRelVariableIndicador, valRel)

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Consultar formula por sigla
######################################
def consultarIdFormulaPorSigla(sigla, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
            SELECT * FROM indicador WHERE siglas = %s
        """)
        val = ([sigla])

        cursor.execute(sql, val)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results[0]

    except Exception as e:
        connection.rollback()
        print(e)

    finally:
        cursor.close()


######################################
# Consultar variables por indicador
######################################
def consultarVariablesPorIndicador(idIndicador, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
        SELECT a.*
        FROM variable a
        JOIN indicador_variable b ON (b.cod_variable_FK = a.cod_variable)
        WHERE
        b.cod_indicador_FK = %s
        """)
        val = ([idIndicador])

        cursor.execute(sql, val)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Consultar variables por sigla
######################################
def consultarIdVariablePorSigla(sigla, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
        SELECT * FROM variable WHERE siglas = %s
        """)
        val = ([sigla])

        cursor.execute(sql, val)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results[0]

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()



######################################
# validar adjunto
######################################
def allowed_file(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


######################################
# Guardar seguimiento
######################################
def guardarSeguimientoEvento(idEvento, observacion, idUsuario, connection):

    try:
        cursor = connection.cursor()
        # Fecha actual
        fechaActual = datetime.datetime.utcnow()

        obj = {
            'idEvento': idEvento if idEvento else None,
            'observacion': observacion if observacion else None,
        }

        validacion = [
            {'campo': 'idEvento', 'valor': obj['idEvento'], 'obligatorio': 1},
            {'campo': 'observacion',
                'valor': obj['observacion'], 'obligatorio': 1},
        ]

        estadoValidate = validarCampos(validacion)

        if estadoValidate == 0:
            return jsonify({'message': 'Error en validación de datos.'}), 400

        sqlInsert = ("""
        INSERT INTO evento_seguimiento (observacion, cod_evento_FK, fecha_registro, cod_usuario_FK)
        VALUES (%s,%s,%s,%s) RETURNING cod_evento_seguimiento
        """)
        val = (obj['observacion'], obj['idEvento'], fechaActual, idUsuario)

        cursor.execute(sqlInsert, val)

        res = {
            'id': cursor.fetchone()[0],
        }

        return res
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Guardar adjunto seguimiento
######################################
def guardarAdjuntoSeguimiento(idSeguimiento, ruta, filename, connection):

    # Fecha actual
    fechaActual = datetime.datetime.utcnow()
    try:
        cursor = connection.cursor()
        obj = {
            'idSeguimiento': idSeguimiento if idSeguimiento else None,
            'ruta': ruta if ruta else None,
            'filename': filename if filename else None,
        }

        validacion = [
            {'campo': 'idSeguimiento',
                'valor': obj['idSeguimiento'], 'obligatorio': 1},
            {'campo': 'ruta', 'valor': obj['ruta'], 'obligatorio': 1},
            {'campo': 'filename', 'valor': obj['filename'], 'obligatorio': 1},
        ]

        estadoValidate = validarCampos(validacion)

        if estadoValidate == 0:
            return jsonify({'message': 'Error en validación de datos.'}), 400

        sqlInsert = ("""
        INSERT INTO evento_seguimiento_adju (ruta, nombre_archivo, cod_evento_seguimiento_FK)
        VALUES (%s,%s,%s)
        """)
        val = (obj['ruta'], obj['filename'], obj['idSeguimiento']['id'])

        cursor.execute(sqlInsert, val)

    except Exception as e:
        connection.rollback()
        print(e)

    finally:
        cursor.close()

######################################
# Consultar seguimientos por evento
######################################
def consultarSeguimientos(idEvento, connection):

    try:
        cursor = connection.cursor()
        sqlInsert = ("""
        SELECT
        a.cod_evento_seguimiento,
        a.observacion,
        a.cod_evento_FK,
        TO_CHAR(a.fecha_registro, 'YYYY-MM-DD') AS fecha_registro,
        b.id AS id_usuario,
        CONCAT(b.nombre, b.apellido) AS nombre_usuario
        FROM evento_seguimiento a
        JOIN usuarios b ON (b.id = a.cod_usuario_FK)
        WHERE a.cod_evento_FK = '%s'
        ORDER BY cod_evento_seguimiento DESC
        """)
        val = ([idEvento])

        cursor.execute(sqlInsert, val)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))


        return adjuntosSeguimiento(results, connection)

    except Exception as e:
        connection.rollback()
        print(e)

    finally:
        cursor.close()


######################################
# Consultar adjuntos de seguimientos
######################################
def adjuntosSeguimiento(records, connection):
    seguimientos = []

    try:
        cursor = connection.cursor()
        for record in records:
            sql = ("""
            SELECT
            a.cod_evento_seguimiento_adju,
            a.ruta,
            a.nombre_archivo,
            a.cod_evento_seguimiento_FK
            FROM evento_seguimiento_adju a
            WHERE a.cod_evento_seguimiento_FK = %s """)
            val = (sql)
            cursor.execute(sql, [record['cod_evento_seguimiento']])

            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            record['adjuntos'] = results
            seguimientos.append(record)

        return seguimientos
    
    except Exception as e:
        connection.rollback()
        print(e)

    finally:
        cursor.close()


######################################
# Consultar costos directos por actividad
######################################
def costosDirectosActividad(idEvento, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
        SELECT
        d.cod_evento_FK,
        b.actividad,
        TO_CHAR(SUM(COALESCE(a.gasto_incurrido, 0)), 'l99999999999999D99') AS gasto_incurrido
        FROM costos_directos a
        JOIN actividad b ON (b.cod_actividad = a.cod_actividad_fk)
        JOIN especie_forestal_sembrada c ON (c.cod_especie_forestal_sembrada = a.cod_especie_forestal_FK)
        JOIN evento_sist_prod_afectado d ON (d.cod_especie_forestal_fk = c.cod_especie_forestal_sembrada)
        WHERE d.cod_evento_FK = %s
        GROUP BY cod_actividad, d.cod_evento_FK """)
        val = (sql)
        cursor.execute(sql, [idEvento])

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))


        return results

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Consultar costos indirectos por rubro
######################################
def costosInDirectosRubro(idEvento, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
        SELECT
        d.cod_evento_FK,
        b.rubros,
        TO_CHAR(SUM(COALESCE(a.gasto_incurrido, 0)), 'l99999999999999D99') AS gasto_incurrido
        FROM costos_fijos_indirectos a
        JOIN rubros b ON (b.cod_rubros = a.cod_rubro_fk)
        JOIN especie_forestal_sembrada c ON (c.cod_especie_forestal_sembrada = a.cod_especie_forestal_FK)
        JOIN evento_sist_prod_afectado d ON (d.cod_especie_forestal_fk = c.cod_especie_forestal_sembrada)
        WHERE d.cod_evento_FK = %s
        GROUP BY b.cod_rubros, d.cod_evento_FK """)
        val = (sql)
        cursor.execute(sql, [idEvento])

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))


        return results

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Consultar costos por tipo
# infraestructura.
######################################
def valorTipoInfraestructura(idEvento, connection):

    try:
        cursor = connection.cursor()
        sql = ("""
        SELECT
        d.cod_evento_FK,
        TO_CHAR(SUM(COALESCE(a.vlr_pesos_afectacion,0)), 'l99999999999999D99') AS vlr_semilla,
        TO_CHAR(SUM(COALESCE(a.valor_pesos_afectacion,0)), 'l99999999999999D99') AS vlr_fertilizante,
        TO_CHAR(SUM(COALESCE(a.vlr_pesos_afectacion_pla,0)), 'l99999999999999D99') AS vlr_plaguicida,
        TO_CHAR(SUM(COALESCE(a.vlr_pesos_afectacion_maq,0)), 'l99999999999999D99') AS vlr_maquinaria
        FROM infraestructura_forestal a
        JOIN especie_forestal_sembrada c ON (c.cod_especie_forestal_sembrada = a.cod_especie_forestal_sembrada_FK)
        JOIN evento_sist_prod_afectado d ON (d.cod_especie_forestal_fk = c.cod_especie_forestal_sembrada)
        WHERE d.cod_evento_FK = %s
        GROUP BY d.cod_evento_FK """)
        cursor.execute(sql, [idEvento])

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Consultar % pérdida económica
# forestal
######################################
def perdidaEconomicaForestal(idEvento, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
        SELECT
        a.cod_evento_FK,
        TO_CHAR(COALESCE(a.valor,0), 'l99999999999999D99') AS valor
        FROM indicador_valor a
        JOIN indicador b ON (b.cod_indicador = a.cod_indicador_fk)
        WHERE a.cod_evento_FK = %s AND b.siglas = 'PE' """)
        cursor.execute(sql, [idEvento])

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    except Exception as e:
        connection.rollback()
        print(e)
    finally:    
        cursor.close()
    

######################################
# Consultar varlor pérdida económica
# forestal
######################################
def valorPerdidaEconomicaForestal(idEvento, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
        SELECT
        a.cod_evento_FK,
        TO_CHAR(COALESCE(a.valor,0), 'l99999999999999D99') AS valor
        FROM indicador_valor a
        JOIN indicador b ON (b.cod_indicador = a.cod_indicador_fk)
        WHERE a.cod_evento_FK = %s AND b.siglas = 'VPE' """)
        val = (sql)
        cursor.execute(sql, [idEvento])

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Consultar %  pérdida estimada
# producción
######################################
def perdidaEstimadaProduccion(idEvento, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
        SELECT
        a.cod_evento_FK,
        TO_CHAR(COALESCE(a.valor,0), 'l99999999999999D99') AS valor
        FROM indicador_valor a
        JOIN indicador b ON (b.cod_indicador = a.cod_indicador_fk)
        WHERE a.cod_evento_FK = %s AND b.siglas = 'PPR' """)
        val = (sql)
        cursor.execute(sql, [idEvento])

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Consultar sexo de productores
######################################
def getSexoProductores(ubicacion, val, connection):
    try:
        cursor = connection.cursor()
        sql = (f"""
        SELECT
        TO_CHAR( SUM(COALESCE(a.hombre, 0)), 'l99999D') AS hombres, 
        TO_CHAR( SUM(COALESCE(a.mujer, 0)), 'l99999D') AS mujeres
        FROM(
            SELECT
            CASE
            WHEN b.cod_sexo = 1 THEN COUNT(cod_sexo)
            END hombre,
            0 AS  mujer
            FROM productor_agropecuario a
            JOIN sexo b ON (b.cod_sexo = a.cod_sexo_FK)
        JOIN evento_productos_agropecuario c ON (c.cod_producto_agro = a.cod_productor_agropecuario)
        JOIN evento d ON (d.cod_evento = c.cod_evento_FK)
            WHERE cod_sexo = 1 AND { val }
            GROUP BY b.cod_sexo
            UNION ALL
            SELECT
            0 AS hombre,
            CASE
            WHEN b.cod_sexo = 2 THEN COUNT(cod_sexo)
            END mujer
            FROM productor_agropecuario a
            JOIN sexo b ON (b.cod_sexo = a.cod_sexo_FK)
        JOIN evento_productos_agropecuario c ON (c.cod_producto_agro = a.cod_productor_agropecuario)
        JOIN evento d ON (d.cod_evento = c.cod_evento_FK)
            WHERE cod_sexo = 2  AND { val }
            GROUP BY b.cod_sexo
        ) a """)

        cursor.execute(sql)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))


        return results
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()

######################################
# Consultar  promedio de edades de los
# productores.
######################################
def getPromedioEdad(ubicacion, val, connection):
    try:
        cursor = connection.cursor()
        sql = (f"""
        SELECT
        TO_CHAR(avg(date_part('year',Age(fch_nacimiento))), 'l99999D99') AS edad
        FROM productor_agropecuario a
        JOIN evento_productos_agropecuario b ON (b.cod_producto_agro = a.cod_productor_agropecuario)
        JOIN evento d ON (d.cod_evento = b.cod_evento_FK)
        WHERE fch_nacimiento IS NOT NULL AND { val } """)

        cursor.execute(sql)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))


        return results
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()

######################################
# Consultar  grupos étnicos
######################################
def getGrupoEtnico(ubicacion, val, connection):
    try:
        cursor = connection.cursor()
        sql = (f"""
        SELECT
        b.grupo_etnico,
        COUNT(b.cod_grupo_etnico) AS cantidad
        FROM productor_agropecuario a
        JOIN grupo_etnico b ON (b.cod_grupo_etnico = a.cod_grupo_etnico_FK)
        JOIN evento_productos_agropecuario c ON (c.cod_producto_agro = a.cod_productor_agropecuario)
        JOIN evento d ON (d.cod_evento = c.cod_evento_FK)
        WHERE  { val }
        GROUP BY b.cod_grupo_etnico """)

        cursor.execute(sql)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))


        return results
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Consultar tipos de productor
# por todos los productores registrados
######################################
def getTipoProductorProductores(ubicacion, val, connection):
    try:
        cursor = connection.cursor()
        sql = (f"""
        SELECT
        b.tipo_productor,
        COUNT(b.cod_tipo_productor) AS cantidad
        FROM productor_agropecuario a
        JOIN tipo_productor b ON (b.cod_tipo_productor = a.cod_tipo_productor_FK)
        JOIN evento_productos_agropecuario c ON (c.cod_producto_agro = a.cod_productor_agropecuario)
        JOIN evento d ON (d.cod_evento = c.cod_evento_FK)
        WHERE  { val }
        GROUP BY b.cod_tipo_productor """)

        cursor.execute(sql)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Consultar hectareas afectadas por
# especie.
######################################
def getHectareasEspecie(ubicacion, val, connection):
    try:
        cursor = connection.cursor()
        sql = (f"""
        SELECT
        b.especie_forestal_afectada,
        TO_CHAR(SUM(COALESCE(a.area_afectada_ha, 0)), 'l99999D99') cantidad
        FROM especie_forestal_sembrada a
        JOIN especie_forestal_afectada b ON (b.cod_esp_forestal_afectada = a.cod_especie_forestal_afec_FK)
        JOIN evento_sist_prod_afectado c ON (c.cod_especie_forestal_FK = a.cod_especie_forestal_sembrada)
        JOIN evento d ON (d.cod_evento = c.cod_evento_FK)
        WHERE  { val }
        GROUP BY b.cod_esp_forestal_afectada """)

        cursor.execute(sql)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Consultar ubicación eventos
######################################
def getUbicacionEventos(ubicacion, val, connection):
    try:
        cursor = connection.cursor()
        sql = (f"""
        SELECT
        TO_CHAR(d.coord_x, 'l99999D99999999') AS coord_x,
        TO_CHAR(d.coord_y, 'l99999D99999999') AS coord_y
        FROM evento d
        WHERE  { val }
        AND d.coord_x IS NOT NULL
        AND d.coord_y IS NOT NULL """)
        val = (sql)
        cursor.execute(sql)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))


        return results

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Consultar volumen madera afectado
######################################
def getVolumenMadera(ubicacion, val, connection):
    try:
        cursor = connection.cursor()
        sql = (f"""
        SELECT
        e.cod_tip_evento,
        e.tipo_evento,
        TO_CHAR(SUM(COALESCE(a.volumen_madera_afectados,0)), 'l99999D99') as volumen
        FROM especie_forestal_sembrada a
        JOIN evento_sist_prod_afectado b ON (b.cod_especie_forestal_FK = a.cod_especie_forestal_sembrada)
        JOIN evento d ON (d.cod_evento = b.cod_evento_FK)
        JOIN tipo_evento e ON (e.cod_tip_evento = d.cod_tipo_evento_FK)
        WHERE  { val }
        GROUP BY e.cod_tip_evento  """)
        val = (sql)
        cursor.execute(sql)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))


        return results
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Consultar daños por tipo
# infraestructura
######################################
def getDanosInfraestructura(ubicacion, val, connection):
    try:
        cursor = connection.cursor()
        sql = (f"""
        SELECT
        TO_CHAR(SUM(COALESCE(a.vlr_pesos_afectacion,0)), 'l99999999999999D99') AS vlr_semilla,
        TO_CHAR(SUM(COALESCE(a.valor_pesos_afectacion,0)), 'l99999999999999D99') AS vlr_fertilizante,
        TO_CHAR(SUM(COALESCE(a.vlr_pesos_afectacion_pla,0)), 'l99999999999999D99') AS vlr_plaguicida,
        TO_CHAR(SUM(COALESCE(a.vlr_pesos_afectacion_maq,0)), 'l99999999999999D99') AS vlr_maquinaria
        FROM infraestructura_forestal a
        JOIN especie_forestal_sembrada c ON (c.cod_especie_forestal_sembrada = a.cod_especie_forestal_sembrada_FK)
        JOIN evento_sist_prod_afectado e ON (e.cod_especie_forestal_fk = c.cod_especie_forestal_sembrada)
        JOIN evento d ON (d.cod_evento = e.cod_evento_FK) 
        WHERE  { val } """)
        val = (sql)
        cursor.execute(sql)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


######################################
# Consultar valor perdidas
######################################
def getValorPedidas(ubicacion, val, connection):
    try:
        cursor = connection.cursor()
        sql = (f"""
        SELECT
        e.cod_indicador,
        e.siglas,
        TO_CHAR(SUM(COALESCE(c.valor,0)), 'l99999999999999D99') as valor
        FROM tipo_evento a
        JOIN evento d ON (d.cod_tipo_evento_FK = a.cod_tip_evento)
        JOIN indicador_valor c ON (c.cod_evento_FK = d.cod_evento)
        JOIN indicador e ON (e.cod_indicador = c.cod_indicador_FK)
        WHERE e.siglas = 'VPE'
        AND  { val }
        GROUP BY e.cod_indicador """)
        val = (sql)
        cursor.execute(sql)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))


        return results
    except Exception as e:
        connection.rollback()
        print(e)
    finally:
        cursor.close()


# Datos de la especie
def getSpeciesData(connection):
    results = {'cropType': [], 'areaUnity': [],
               'error': False, 'errorMessage': ''}
    try:
        cursor = connection.cursor()
        # Select nombre del cultivo
        sql = (
            "SELECT cod_tipo_cultivo AS codCultivo, tipo_cultivo AS tipoCultivo FROM Tipo_cultivo;")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['cropType'].append(dict(zip(columns, row)))

        sql = ("SELECT cod_unidad_area AS codUndArea, unidad_area As undArea " +
               "FROM Unidad_area")  # Select unidad de area se realiza el reporte
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['areaUnity'].append(dict(zip(columns, row)))

    except Exception as e:
        connection.rollback()
        print(e)
        results['error'] = True
        results['message'] = 'Ha ocurrido un error, intente de nuevo'

    finally:
        cursor.close()

    return results


# Material de siembra
def getPlantingMaterial(connection):
    results = {'plantingMaterial': [], 'harvestUnity': [], 'equivCharge': [], 'seedSource': [],
               'error': False, 'errorMessage': ''}
    try:
        cursor = connection.cursor()
        sql = ("SELECT cod_material AS codMaterial, material " +
               "FROM Material_siembra")  # Select que tipo de material utilizo para la siembre
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['plantingMaterial'].append(dict(zip(columns, row)))

        sql = ("SELECT cod_und_cosecha AS codUndCosecha, und_cosecha AS undCosecha " +
               "FROM Unidad_cosecha WHERE und_cosecha NOT IN('Unidades', 'Litros')")  # Select Unidad para reportar la cantidad de semilla
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['harvestUnity'].append(dict(zip(columns, row)))        

        sql = ("SELECT cod_equiv_carga AS codEquivCarga, equiv_carga_kg AS eqvCargaKg " +
               "FROM Equivalencia_carga")  # Select equivalencia en kilos de carga
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['equivCharge'].append(dict(zip(columns, row)))
        
        sql = ("SELECT cod_fuente_semilla AS codFuenSemilla, fuente_semilla AS fuenSemilla " +
               "FROM Fuente_semilla")  # Select fuente de la semilla
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['seedSource'].append(dict(zip(columns, row)))

    except Exception as e:
        connection.rollback()
        print(e)
        results['error'] = True
        results['errorMessage'] = 'Ha ocurrido un error, intente de nuevo'

    finally:
        cursor.close()
    return results


# Costos directos e indirectos
def getCosts(connection):
    results = {'indirectCosts': [], 'directCosts': [],
               'error': False, 'errorMessage': ''}
    try:
        cursor = connection.cursor()
        # Select la unidad de medida para reportar la medida de costos indirectos
        sql = ("SELECT cod_rubros AS codRubro, rubros FROM Rubros")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['indirectCosts'].append(dict(zip(columns, row)))

        sql = ("SELECT cod_tipo_actividad AS codTipActividad, tipo_actividad AS tipActividad"+ 
               " FROM Tipo_actividad WHERE tipo_actividad NOT IN ('ADECUACIÓN Y PREPARACIÓN DEL SUELO', 'EMPAQUES');")  # Select la unidad de medida para reportar la medida de costos directos
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['directCosts'].append(dict(zip(columns, row)))

    except Exception as e:
        connection.rollback()
        print(e)
        results['error'] = True
        results['errorMessage'] = 'Ha ocurrido un error, intente de nuevo'
    finally:
        cursor.close()
    return results


# Datos de credito y datos de aseguramiento
def creditData_AssuranceData(connection):
    results = {'assruanceType': [], 'bankingEntity': [],
               'error': False, 'errorMessage': ''}

    try:
        cursor = connection.cursor()
        sql = ("SELECT cod_entidad_credito AS codEntCredito, entidad_credito AS entCredito " +
               "FROM Entidad_credito")  # Select de que entidad bancaria le dio el credito
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['bankingEntity'].append(dict(zip(columns, row)))

        # Select de tipo de seguro
        sql = (
            "SELECT cod_tipo_seguro AS codTipSeguro, tipo_seguro AS tipSeguro FROM Tipo_seguro")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['assruanceType'].append(dict(zip(columns, row)))

    except Exception as e:
        connection.rollback()
        print(e)
        results['error'] = True
        results['errorMessage'] = 'Ha ocurrido un error, intente de nuevo'
    finally:
        cursor.close()

    return results


# Datos de infraestructura
def getDataInfraestructura(connection):
    results = {'fertilizerType': [], 'pesticideType': [],
               'presentation': [], 'error': False, 'errorMessage': ''}
    try:
        cursor = connection.cursor()
        sql = ("SELECT cod_tipo_fertilizante AS codFertilizante, tipo_fertilizante AS tipoFertilizante " +
               "FROM Tipo_fertilizante")  # Select de tipo fertilizante
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['fertilizerType'].append(dict(zip(columns, row)))

        sql = ("SELECT cod_tip_plaguicida AS codPlaguicida, tipo_plaguicida AS tipoPlaguicida " +
               "FROM Tipo_plaguicida")  # Select de tipo plaguicida
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['pesticideType'].append(dict(zip(columns, row)))

        sql = ("SELECT cod_presentacion AS codPresentacion, presentacion " +
               "FROM Presentacion")  # Select presentacion
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['presentation'].append(dict(zip(columns, row)))

    except Exception as e:
        connection.rollback()
        print(e)
        results['error'] = True
        results['errorMessage'] = 'Ha ocurrido un error, intente de nuevo'
    finally:
        cursor.close()

    return results


# Datos del sistema pecuario afectado
def getSistemaPecuarioAfectado(connection):
    results = {'affectedSistem': [], 'harvestUnity': [], 'equivCharge': [], 'areaUnity': [],
               'typeProduct': [], 'unity': [], 'activity': [], 'rubro': [], 'inputType': [], 'machineryTypeBBA': [],
               'machineryTypePEM': [], 'activeType': [], 'constructionType': [], 'error': False, 'errorMessage': ''}
    try:
        cursor = connection.cursor()
        sql = ('''
        SELECT cod_sistem_afectado AS codSistemaAfectado, sistema_afectado AS sistemaAfectado FROM Sistema_afectado
        ''')
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # ¿Cuál fue el sistema afectado?
            results['affectedSistem'].append(dict(zip(columns, row)))

        sql = ("SELECT cod_und_cosecha AS codUndCosecha, und_cosecha AS undCosecha " +
               "FROM Unidad_cosecha WHERE und_cosecha NOT IN('Unidades', 'Litros')")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # La unidad de medida para reportar la cantidad es?
            results['harvestUnity'].append(dict(zip(columns, row)))

        sql = ("SELECT cod_equiv_carga AS codEquivCarga, equiv_carga_kg AS eqvCargaKg " +
               "FROM Equivalencia_carga")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Si selecciona carga en alguna unidad despliega esta lista
            results['equivCharge'].append(dict(zip(columns, row)))

        sql = ("SELECT cod_unidad_area AS codUndArea, unidad_area As undArea " +
               "FROM Unidad_area")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Por favor indique en que unidad de área se realiza el reporte
            results['areaUnity'].append(dict(zip(columns, row)))

        sql = ("SELECT cod_tipo_producto AS codTipProd, tipo_producto As tipProd " +
               "FROM Tipo_producto")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Por favor indique el tipo de producto obtenido de los animales
            results['typeProduct'].append(dict(zip(columns, row)))

        sql = ("SELECT cod_und_cosecha AS codUndCosecha, und_cosecha AS undCosecha " +
               "FROM Unidad_cosecha WHERE und_cosecha NOT IN('Gramos', 'Libras')")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # ¿En qué unidades desea reportar la producción?
            results['unity'].append(dict(zip(columns, row)))

        sql = ("SELECT cod_actividad AS codActividad, actividad " +
               "FROM Actividad")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Costos variables pecuarios
            results['activity'].append(dict(zip(columns, row)))

        sql = ("SELECT cod_rubros AS codRubro, rubros FROM Rubros")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Costos fijos pecuarios
            results['rubro'].append(dict(zip(columns, row)))

        sql = (
            "SELECT cod_tipo_insumo AS codInsumo, tipo_insumo AS tipInsumo FROM Tipo_insumo")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Tipo de insumo, forraje, alimento para los animales y piensos
            results['inputType'].append(dict(zip(columns, row)))

        sql = (
            '''
            SELECT cod_tipo_maquinaria AS codTipMaquinaria, tipo_maquinaria AS tipMaquinaria FROM Tipo_maquinaria
            WHERE tipo_maquinaria NOT IN ('Arados e implementos de labranza', 'Cosechadoras', 'Sistema de iluminación',
            'Sistemas de potabilización');
            ''')
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Instalaciones y maquinaria manejo de bovinos, bufalinos y afines
            results['machineryTypeBBA'].append(dict(zip(columns, row)))

        sql = (
            '''
        SELECT cod_tipo_maquinaria AS codTipMaquinaria, tipo_maquinaria AS tipMaquinaria FROM Tipo_maquinaria
        WHERE tipo_maquinaria NOT IN ('Arados e implementos de labranza', 'Cosechadoras', 'Sistema de iluminación',
            'Sistemas de potabilización');
        ''')
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Instalaciones y maquinaria para la producción de especies menores
            results['machineryTypePEM'].append(dict(zip(columns, row)))

        sql = (
            "SELECT cod_tipo_activo AS codTipActivo, tipo_activo tipActivo FROM Tipo_activo;")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Por favor seleccione un activo productivo afectado.
            results['activeType'].append(dict(zip(columns, row)))

        sql = ("SELECT cod_tipo_construccion AS codTipConstruccion, tipo_construccion tipConstruccion FROM Tipo_construccion;")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Por favor, indique el tipo de construcción afectada
            results['constructionType'].append(dict(zip(columns, row)))

    except Exception as e:
        connection.rollback()
        print(e)
        results['error'] = True
        results['errorMessage'] = 'No se han podido obtener los datos'
    finally:
        cursor.close()

    return results
