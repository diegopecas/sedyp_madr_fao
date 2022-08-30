import jwt
import datetime
import json
import os
import shutil

from app.config import Config
from app.helpers import save_relation_productor_event, raise_exception, send_notification_email
from app.services.email_service import get_email_service
from app.eventos.validations import *
from app.exceptions import CustomException
from app.services.database_service import DatabaseService
from flask import request
from werkzeug.utils import secure_filename
from app.helpers import allowed_file



#connection = Config.connection

# Searches all the events and returns its code, type, ubication, observation and created date
def get_event(connection, perm, id_user, rol):
    try:
        cursor = connection.cursor()

        where = ''
        
        if rol == 8:
            select = ("""
                SELECT cod_dpto_fk FROM validador_departamental WHERE usuario = %s
            """)

            val1 = ([id_user])

            cursor.execute(select, val1)
            
            dpt=''
            possible_dpt = cursor.fetchone()
            if possible_dpt != None:
                dpt=possible_dpt[0]

            if dpt != '':
                where = 'WHERE d.cod_dpto = {} OR a.cod_encuestador_FK = {}'.format(dpt, id_user)
        elif rol == 7:
            select = ("""
                SELECT cod_mun_fk FROM validador_municipal WHERE usuario = %s
            """)

            val1 = ([id_user])

            cursor.execute(select, val1)
            
            mun=''
            possible_mun = cursor.fetchone()
            if possible_mun != None:
                mun=possible_mun[0]
            
            if mun != '':
                where = 'WHERE m.cod_municipios = {} OR a.cod_encuestador_FK = {}'.format(mun, id_user)
                

        see_ind = ''
        if perm == 2:
            see_ind = 'AND a.cod_encuestador_fk = {}'.format(id_user)

        # Search events
        sql = ('''
            SELECT json_build_object(
	'cod_evento', a.cod_evento,
	'tipo_evento', b.tipo_evento,
	'fecha_registro_evento', TO_CHAR(a.fecha_registro_evento, 'YYYY-MM-DD'),
    'ubicacion', CONCAT(d.nombre_dpto,' - ',m.nom_municipio, ' / ', a.descrip_llegada_casco_urbano),
	'ubicacion_vereda', a.ubicacion_vereda,
	'nom_vereda', v.nom_vereda,
	'nom_puerto_desembarquee', a.nom_puerto_desembarquee,
	'descrip_llegada_casco_urbano', a.descrip_llegada_casco_urbano,
	'validado', a.validado,
	'usuario', u.usuario,
	'adjuntos', array_remove(array_agg(ea.*), NULL)
)
FROM evento a
            JOIN tipo_evento b ON (b.cod_tip_evento = a.cod_tipo_evento_FK {})
            JOIN Municipios m ON (a.cod_municipio_FK = m.cod_municipios)
			JOIN Departamentos d ON(m.cod_dpto_FK = d.cod_dpto)
			JOIN Evento_sist_prod_afectado espa ON espa.cod_evento_FK =  a.cod_evento
            LEFT JOIN Vereda v ON a.cod_vereda_fk = v.cod_vereda
            JOIN Usuarios u ON a.cod_encuestador_FK = u.id
			LEFT JOIN evento_adjunto ea ON ea.cod_evento_fk = a.cod_evento
            {}
			GROUP BY a.cod_evento, b.tipo_evento, d.nombre_dpto, m.nom_municipio, v.nom_vereda,
			u.usuario
			ORDER BY a.cod_evento DESC
            --LIMIT 100 OFFSET 0;
        '''.format(see_ind, where))

        """
        sql = ('''
            SELECT row_to_json(row) FROM (
            SELECT
            a.cod_evento,
            b.tipo_evento,
            TO_CHAR(a.fecha_registro_evento, 'YYYY-MM-DD') AS fecha_registro_evento,
            CONCAT(d.nombre_dpto,' - ',m.nom_municipio, ' / ', a.descrip_llegada_casco_urbano) ubicacion,
            a.ubicacion_vereda,
            v.nom_vereda,
            a.nom_puerto_desembarquee,
            a.descrip_llegada_casco_urbano,
            a.validado,
            spa.sistema_productivo_afectado,
            u.usuario
            FROM evento a
            JOIN tipo_evento b ON (b.cod_tip_evento = a.cod_tipo_evento_FK {})
            JOIN Municipios m ON (a.cod_municipio_FK = m.cod_municipios)
            JOIN Departamentos d ON(m.cod_dpto_FK = d.cod_dpto)
            JOIN Evento_sist_prod_afectado espa ON espa.cod_evento_FK =  a.cod_evento
            JOIN sistema_productivo_afectado spa ON spa.cod_sis_prod_afec = espa.cod_sist_prod_afect_fk
            LEFT JOIN Vereda v ON a.cod_vereda_fk = v.cod_vereda
            JOIN Usuarios u ON a.cod_encuestador_FK = u.id
            {}
            
            ORDER BY a.cod_evento DESC LIMIT 50) AS row;
        '''.format(see_ind, where))
        """

        cursor.execute(sql)

        results = []
        for r in cursor.fetchall():
            results.append(r[0])

        """
        att_event = attached_event(results, connection)
        if att_event[1] != 200:
            raise_exception(att_event[0].to_dict()['message'],  att_event[0].to_dict()['error'])
        """



        resDataEvento = {
            'eventos': results,
        }

        token = jwt.encode({'eventos': resDataEvento}, Config.SECRET_KEY)

    except Exception as e:
        print("ERROR (eventos/database_manager/get_event): ",e)
        return CustomException('Ocurrio un error al obtener los datos.', str(e)), 500
    else:
        
        return {'token': token.decode('UTF-8')}, 200
        #return resDataEvento, 200

    finally:
        if not cursor.closed:
            cursor.close()


# Search document types
def search_document_type(connection):
    try:
        cursor = connection.cursor()

        # Search
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

        return records, 200

    except Exception as e:
        print("ERROR (eventos/database_manager/search_document_type): ", e)
        return CustomException('Ocurrio un error al consultar los tipos de documento.', str(e)), 500
    finally:
        if not cursor.closed:
            cursor.close()


# Search legal conditions
def search_legal_condition(connection):
    try:
        cursor = connection.cursor()

        # Search
        sqlCondicionJuridica = ("""
            SELECT
            a.*
            FROM condicion_juridica a
        """)
        cursor.execute(sqlCondicionJuridica)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_legal_condition): ", e)
        return CustomException('Ocurrio un error al consultar las condiciones juridicas', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search sex
def search_sex(connection):
    try:
        cursor = connection.cursor()

        # Search
        sqlSexo = ("""
            SELECT
            a.*
            FROM sexo a
        """)
        cursor.execute(sqlSexo)
        records = cursor.fetchall()


    except Exception as e:
        print("ERROR (eventos/database_manager/search_sex): ", e)
        return CustomException('Ocurrio un error al consultar los tipos de sexo', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search ethnic groups
def search_ethnic_groups(connection):
    try:
        cursor = connection.cursor()

        # Search
        sqlGrupoEtnico = ("""
            SELECT
            a.*
            FROM grupo_etnico a
        """)
        cursor.execute(sqlGrupoEtnico)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_ethnic_groups): ", e)
        return CustomException('Ocurrio un error al consultar los tipos de etnias', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search producer type
def search_producer_type(connection):
    try:
        cursor = connection.cursor()

        # Search
        sqlTipoProductor = ("""
            SELECT
            a.*
            FROM tipo_productor a
        """)
        cursor.execute(sqlTipoProductor)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_producer_type): ", e)
        return CustomException('Ocurrio un error al consultar los tipos de productores', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search estate relation type
def search_estate_relation_type(connection):
    try:
        cursor = connection.cursor()

        # Search
        sqlTipoRelacion = ("""
            SELECT
            a.*
            FROM tipo_relacion_predio a
        """)
        cursor.execute(sqlTipoRelacion)
        records = cursor.fetchall()

        return records, 200

    except Exception as e:
        print("ERROR (eventos/database_manager/search_estate_relation_type): ", e)
        return CustomException('Ocurrio un error al consultar los datos del tipo de relacion del predio', str(e)), 500
    finally:
        if not cursor.closed:
            cursor.close()


# Search departaments
def search_departaments(connection):
    try:
        cursor = connection.cursor()
        records = []

        sql = ("""
            SELECT cod_dpto, nombre_dpto, cod_dane
            FROM departamentos ORDER BY nombre_dpto
        """)
        cursor.execute(sql)
        records = cursor.fetchall()


    except Exception as e:
        print("ERROR (eventos/database_manager/search_departaments): ", e)
        return CustomException('Ocurrio un error al consultar los datos de los departamentos', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search township
def search_township(connection):
    try:
        cursor = connection.cursor()
        records = []

        sql = ("""
            SELECT cod_municipios, cod_dane, nom_municipio, cod_dpto_fk
            FROM municipios ORDER BY nom_municipio
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_township): ", e)
        return CustomException('Ocurrio un error al consultar los datos de los municipios', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search rural town
def search_rural_town(connection):
    try:
        cursor = connection.cursor()
        records = []

        sql = ("""
            SELECT cod_vereda, nom_vereda, cod_mun_fk::INT
            FROM vereda ORDER BY nom_vereda
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_rural_town): ", e)
        return CustomException('Ocurrio un error al consultar los datos de las veredas', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search event type
def search_event_type(connection):
    try:
        cursor = connection.cursor()
        # consultarroot
        sqlTipoEvento = ("SELECT * FROM tipo_evento")
        cursor.execute(sqlTipoEvento)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_event_type): ", e)
        return CustomException('Ocurrio un error al consultar los tipos de eventos', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search sub event
def search_sub_event(connection):
    try:
        cursor = connection.cursor()
        sqlSubEventos = ("""
            SELECT
            a.*
            FROM subeventos a
        """)
        cursor.execute(sqlSubEventos)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_sub_event): ", e)
        return CustomException('Ocurrio un error al consultar los sub eventos', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search productive system
def search_productive_affected_system(connection):
    try:
        cursor = connection.cursor()
        sqlSistema = ("""
            SELECT
            a.*
            FROM sistema_productivo_afectado a
        """)
        cursor.execute(sqlSistema)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_productive_affected_system): ", e)
        return CustomException('Ocurrio un error al consultar los tipos de sistemas productivo afectados', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search pests
def search_pests(connection):
    try:
        cursor = connection.cursor()
        sqlSistema = ("""
            SELECT
            *
            FROM Plaga
        """)
        cursor.execute(sqlSistema)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_pests): ", e)
        return CustomException('Ocurrio un error al consultar los tipos de plagas', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search diseases
def search_diseases(connection):
    try:
        cursor = connection.cursor()
        sqlSistema = ("""
            SELECT
            *
            FROM Enfermedad
        """)
        cursor.execute(sqlSistema)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_diseases): ", e)
        return CustomException('Ocurrio un error al consultar los tipos de enfermedades', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search the productive phase
def search_productive_phase(connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/search_productive_phase): ", e)
        return CustomException('Ocurrio un error al consultar las fases productivas', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search forestal specie
def search_forestal_specie(connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/search_forestal_specie): ", e)
        return CustomException('Ocurrio un error al consultar las especies forestales', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search extractive specie
def search_extractive_specie(connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/search_extractive_specie): ", e)
        return CustomException('Ocurrio un error al consultar las especies extractivas', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search plantatio objective
def search_plantation_objective(connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/search_plantation_objective): ", e)
        return CustomException('Ocurrio un error al consultar los objetivos de plantación', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search the infrastrcuture type
def search_infrastructure_type(connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/search_infrastructure_type): ", e)
        return CustomException('Ocurrio un error al consultar los tipos de infraestructura', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search the seed type
def search_seed_type(connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/search_seed_type): ", e)
        return CustomException('Ocurrio un error al consultar los tipos de semillas', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search the load equivalence for the seed infrastucture
def search_eqv_load(connection):
    try:
        cursor = connection.cursor()
        # consultar
        sql = ("""
            SELECT * FROM Equivalencia_carga;
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_eqv_load): ", e)
        return CustomException('Ocurrio un error al consultar las equivalencias de las cargas', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search the batch spread
def search_batch_spread(connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/search_batch_spread): ", e)
        return CustomException('Ocurrio un error al consultar los lotes de propagación', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search unity
def search_unity(connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/search_unity): ", e)
        return CustomException('Ocurrio un error al consultar las unidades', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search seed unity for the infrastructure
def search_seed_unity(connection):
    try:
        cursor = connection.cursor()
        # consultar
        sql = ("""
            SELECT * FROM Unidad_cosecha WHERE cod_und_cosecha IN(1,2,3,4,5,8);
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_seed_unity): ", e)
        return CustomException('Ocurrio un error al consultar las unidades de las semilla', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search fertilizer type
def search_fertilizer_type(connection):
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

    except Exception as e:
        connection.rollback()
        print("ERROR (eventos/database_manager/search_fertilizer_type): ", e)
        return CustomException('Ocurrio un error al consultar los tipos de fertilizantes', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search pesticide type
def search_pesticide_type(connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/search_pesticide_type): ", e)
        return CustomException('Ocurrio un error al consultar los tipos de plaguicidas', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search machinery type
def search_machinery_type(connection, type):
    try:
        cursor = connection.cursor()
        where = ''

        # The information changes when the productive system changes, 1. Forestal, 2. Agro
        if type == 1 or type == 2:
            where = ' WHERE cod_tipo_maquinaria IN(1,2,3,4,32,33,34,35,36,37,38,8,11,31)'
        

        # consultar
        sql = ("""
            SELECT
            a.*
            FROM tipo_maquinaria a
        """+where)
        cursor.execute(sql)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_machinery_type): ", e)
        return CustomException('Ocurrio un error al consultar los tipos de maquinarias', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search headings
def search_headings(connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/search_headings): ", e)
        return CustomException('Ocurrio un error al consultar los rubros', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search activity
def search_activity(connection):
    try:
        cursor = connection.cursor()
        # consultar
        sql = ("""
            SELECT
            a.*
            FROM actividad a WHERE cod_actividad NOT IN(9,10,11,13)
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_activity): ", e)
        return CustomException('Ocurrio un error al consultar las actividades', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Get the info of the seed source
def search_seed_source(connection):
    try:
        cursor = connection.cursor()
        # consultar
        sql = ("""
            SELECT
            a.*
            FROM Fuente_semilla a
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_seed_source): ", e)
        return CustomException('Ocurrio un error al consultar las fuentes de la semilla', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search the plaguicide presentations
def search_pesticide_presentation(connection):
    try:
        cursor = connection.cursor()
        # consultar
        sql = ("""
            SELECT
            a.*
            FROM Presentacion a
        """)
        cursor.execute(sql)
        records = cursor.fetchall()

    except Exception as e:
        print("ERROR (eventos/database_manager/search_pesticide_presentation): ", e)
        return CustomException('Ocurrio un error al consultar las presentaciones del plaguicida', str(e)), 500
    else:
        return records, 200
    finally:
        if not cursor.closed:
            cursor.close()


# This function saves the event in the database, no matter if it is an online or an offline event
def save_event(count, req, files, id_user, connection, i=None, old_date=None):
    try:
        ip = request.remote_addr
        mail = get_email_service()
        dataEncabezadoEvento = req['dataEncabezadoEvento'] ## Saves in the event table, mostly the location information
        dataProductor = req['dataProductor'] ## Saves in productor_agropecuario, the information about the producer
        dataEspecie = req['dataEspecies'] ## Saves the information about de event detail
        cursor = connection.cursor()

        if len(dataEncabezadoEvento) == 0:
            raise_exception('No hay datos para guardar el evento.', 'No hay datos para guardar el evento.')

        idEvento = save_event_header(dataEncabezadoEvento, connection, old_date) ## Event table
        if idEvento[1] != 200:
            raise_exception(idEvento[0].to_dict()['message'],  idEvento[0].to_dict()['error'])
        
        idStrEvento = str(idEvento[0]['id'])
        j = 0
        ruta = Config.UPLOAD_FOLDER+Config.UPLOAD_EVENTO

        if int(count) > 0:
            os.makedirs(ruta+'/'+idStrEvento, exist_ok=True)
            ruta = ruta+'/'+idStrEvento
            while j < int(count):
                name = ''
                # The i is cause when the event has been saved offline there could come more than one event, so the i helps to know which event they belong
                if i != None:
                    name = 'files'+str(i)+str(j)
                else:
                    name = 'files'+str(j)
                file = files[name]


                # check if the post request has the file part
                if name not in files:
                    raise_exception('Se recibió información de los adjuntos pero no se ha recibido alguno de los adjuntos', 
                    'El archivo contenido en el objeto: '+name+' no se encuentra entre los archivos recibidos')
                
                if file.name == '':
                    raise_exception('Uno de los archivos enviados no tiene nombre', 
                    'El archivo contenido en el objeto: '+name+' no tiene nombre')
                
                
                if file and allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(ruta, filename))

                at = save_attached(idEvento[0]['id'], ruta, file.filename, id_user, connection)
                if at[1] != 200:
                    raise_exception(at[0].to_dict()['message'],  at[0].to_dict()['error'])
                
                j += 1

        productor = save_data_productor(idEvento[0], dataProductor, dataEncabezadoEvento, connection) ## Producer table
        if productor[1] != 200:
            raise_exception(productor[0].to_dict()['message'], productor[0].to_dict()['error'])
        
        idU = dataEncabezadoEvento['idUsuario'] if 'idUsuario' in dataEncabezadoEvento else None
        event = save_event_system(idEvento[0], dataEspecie, dataEncabezadoEvento['sisProds'], idU, connection)
        if event[1] != 200:
            raise_exception(event[0].to_dict()['message'],event[0].to_dict()['error'])

        # Add the notification of new event created to town validator
        
        fechaActual = datetime.datetime.utcnow() - datetime.timedelta(minutes=300)
        sql = ("""
            INSERT INTO Notificaciones(titulo, descripcion, id_usuario, id_creador) VALUES(%s,
                CONCAT('Evento creado por el usuario: ', (SELECT usuario FROM Usuarios WHERE id = %s), ', fecha: {}, tipo de evento: ', 
                (SELECT tipo_evento FROM Tipo_evento WHERE cod_tip_evento = %s)),
                (SELECT vm.usuario FROM validador_municipal vm JOIN usuarios u ON u.id = vm.usuario WHERE vm.cod_mun_fk = %s), %s) 
                RETURNING id_notificacion, titulo, descripcion, id_usuario
        """.format(str(fechaActual.date())))

        val = ("Creación de evento", idU, dataEncabezadoEvento['tipoEv'], dataEncabezadoEvento['municipio'], int(idU))
        cursor.execute(sql, val)
        values = cursor.fetchall()[0]

        audit = {
            'titulo': values[1],
            'descripcion': values[2],
            'id_usuario': values[3],
            'id_creador': idU
        }

        sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

        val = (
            idU, str(ip), 'Creación de registro', 'Notificaciones', values[0], json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')
        
        # Sending the email to the town validator
        sql = ("""
           SELECT email FROM Usuarios u JOIN Validador_municipal vm ON vm.usuario =u.id WHERE cod_mun_fk = %s
        """)
        
        val = ([dataEncabezadoEvento['municipio']])
        cursor.execute(sql,val)

        mail_first = cursor.fetchone()

        if mail_first:
            email = mail_first[0]
            
            sended = send_notification_email(Config.EMAIL_SENDER, email, values[1], values[2], mail)
            if sended[1] != 200:
                raise_exception(sended[0].to_dict()['message'],  sended[0].to_dict()['error'])

            # Add the notification of new event created to department validator
            
            fechaActual = datetime.datetime.utcnow() - datetime.timedelta(minutes=300)

            sql = ("""
                INSERT INTO Notificaciones(titulo, descripcion, id_usuario, id_creador) VALUES(%s,
                    CONCAT('Evento creado por el usuario: ', (SELECT usuario FROM Usuarios WHERE id = %s), ', fecha: {}, tipo de evento: ', 
                    (SELECT tipo_evento FROM Tipo_evento WHERE cod_tip_evento = %s)),
                    (SELECT vm.usuario FROM validador_departamental vm JOIN usuarios u ON u.id = vm.usuario WHERE vm.cod_dpto_fk = %s), %s) 
                    RETURNING id_notificacion, titulo, descripcion, id_usuario
            """.format(str(fechaActual.date())))

            val = ("Creación de evento", idU, dataEncabezadoEvento['tipoEv'], dataEncabezadoEvento['departamento'], int(idU))
            cursor.execute(sql, val)

            values = cursor.fetchall()[0]

            audit = {
                'titulo': values[1],
                'descripcion': values[2],
                'id_usuario': values[3],
                'id_creador': idU
            }

            sql = ("""
                    SELECT log_audit(%s,%s,%s,%s,%s,%s)
                """)

            val = (
                idU, str(ip), 'Creación de registro', 'Notificaciones', values[0], json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

        # Sending the email to the department validator
        sql = ("""
        SELECT email FROM Usuarios u JOIN Validador_departamental vm ON vm.usuario =u.id WHERE cod_dpto_fk = %s
        """)
        
        val = ([dataEncabezadoEvento['departamento']])
        cursor.execute(sql,val)

        mail_first = cursor.fetchone()
        if mail_first:
            email = mail_first[0]
            
            sended = send_notification_email(Config.EMAIL_SENDER, email, values[1], values[2], mail)
            if sended[1] != 200:
                raise_exception(sended[0].to_dict()['message'],  sended[0].to_dict()['error'])

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_event): ", str(e))
        return CustomException('Ocurrio un error al guardar la información del evento', str(e)), 500
    else:
        return idEvento[0], 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Save the event header, ubication, event type, observation, user
def save_event_header(dataEncabezadoEvento, connection, old_date):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        # Fecha actual
        if old_date:
            fechaActual = old_date 
        else:
            fechaActual = datetime.datetime.utcnow() - datetime.timedelta(minutes=300)
            fechaActual = fechaActual.date()
            
        
        obj, estadoValidate = validate_event_header(dataEncabezadoEvento, fechaActual)

        if estadoValidate == 0:
            raise_exception('Error en validación de datos.', 'Error en validación de datos.')

        # Check that the event coords are in the selected town
        sql = ("""
            SELECT ST_CONTAINS( 
			(SELECT geom FROM municipios where cod_municipios = %s), ST_SetSrid(ST_MakePoint(%s, %s),4326));
        """)

        val = (obj['cod_municipio_FK'], obj['longitud'], obj['latitud'])

        cursor.execute(sql, val)
        if not cursor.fetchone()[0]:
            raise_exception('Las coordenadas ingresadas no se encuentran en el municipio seleccionado',
            'Las coordenadas ingresadas no se encuentran en el municipio seleccionado')

        sqlInsert = ("""
        INSERT INTO evento (cod_tipo_evento_FK, cod_tipo_subevento_FK, coord_x, coord_y, altitud, precision,
                            fecha_registro_evento, cod_municipio_FK, ubicacion_vereda,
                            cod_vereda_FK, nom_puerto_desembarquee,
                            cod_encuestador_FK, descrip_llegada_casco_urbano,cuarentenaria, cod_plaga_fk, cod_enfermedad_fk,
                            nom_enfermedad, nom_plaga, nombre_subevento_otro)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_evento
        """)


        cuarent = False
        vereda = False
        if obj['cuarentenario'] == 1:
            cuarent = True
        if obj['ubicacion_vereda'] == 1:
            vereda = True

        val = (obj['tipoEv'], obj['subEv'],obj['latitud'], obj['longitud'], obj['altitud'],
            obj['precision'], str(fechaActual) if not old_date else str(old_date), obj['cod_municipio_FK'],
            vereda, obj['cod_vereda_FK'],
            obj['nom_puerto_desembarquee'], obj['idUsuario'], obj['observacion'], 
            cuarent, obj['plagaCuarente'], obj['enfermedadCuarente'], obj['nombreEnfermedad'], 
            obj['nombrePlaga'], obj['otroSubEvento'])

        cursor.execute(sqlInsert, val)

        audit = {
            'cod_tipo_evento_FK': obj['tipoEv'],
            'cod_tipo_subevento_FK': obj['subEv'],
            'coord_x': obj['latitud'],
            'coord_y': obj['longitud'],
            'altitud': obj['altitud'],
            'precision': obj['precision'],
            'fecha_registro_evento': str(fechaActual),
            'cod_municipio_FK': obj['cod_municipio_FK'],
            'ubicacion_vereda': obj['ubicacion_vereda'],
            'cod_vereda_FK': obj['cod_vereda_FK'],
            'nom_puerto_desembarquee': obj['nom_puerto_desembarquee'],
            'cod_encuestador_FK': obj['idUsuario'],
            'descrip_llegada_casco_urbano': obj['observacion'],
            'cuarentenaria': cuarent,
            'cod_plaga_fk': obj['plagaCuarente'],
            'cod_enfermedad_fk': obj['enfermedadCuarente'],
            'nom_enfermedad': obj['nombreEnfermedad'], 
            'nom_plaga': obj['nombrePlaga'],
            'nombre_subevento_otro': obj['otroSubEvento']
        }

        idE = cursor.fetchone()[0]

        #db_service2 = DatabaseService()
        #with db_service2.get_connection() as conn:
        #    with conn.cursor() as cur:
        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            obj['idUsuario'], str(ip), 'Creación de registro', 'Evento', idE, json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

        res = {
            'id': idE,
        }

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_event_header): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_event_header): ", e)
        return CustomException('Ocurrio un error al guardar los datos del evento', str(e)), 500
    else:
        return res, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Save the productor data
def save_data_productor(idEvento, dataProductor, dataEncabezadoEvento, connection):
    try:
        idProductores = []
        cursor = connection.cursor()
        ip = request.remote_addr

        for data in dataProductor:
            obj, estadoValidate = fields_data_productor(data)

            if estadoValidate == 0:
                raise_exception('Error en validación de datos.','Error en validación de datos.')

            sqlInsert = ("""
            INSERT INTO productor_agropecuario (cod_condicion_juridica_FK, cod_tipo_productor_FK,nombre_apellido_productor,
                                                cod_tipo_documento_FK, nro_documento, direccion_residencia, numero_contacto,
                                                cod_sexo_FK, fch_nacimiento, cod_grupo_etnico_FK, correo)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_productor_agropecuario;
            """)
            val = (obj['condJuridica'], obj['tipoProd'], obj['nombre'],
                obj['tipoDcto'], obj['dcto'], obj['dirRes'], obj['tel'],
                obj['sexo'], obj['fechaNac'], obj['gEtnico'], obj['email'])
            cursor.execute(sqlInsert, val)

            idProductor = cursor.fetchone()[0]
            idU = dataEncabezadoEvento['idUsuario'] if 'idUsuario' in dataEncabezadoEvento else None

            audit = {
                'cod_condicion_juridica_FK': obj['condJuridica'],
                'cod_tipo_productor_FK': obj['tipoProd'],
                'nombre_apellido_productor': obj['nombre'],
                'cod_tipo_documento_FK': obj['tipoDcto'],
                'nro_documento': obj['dcto'],
                'direccion_residencia': obj['dirRes'],
                'numero_contacto': obj['tel'],
                'cod_sexo_FK': obj['sexo'],
                'fch_nacimiento': obj['fechaNac'],
                'cod_grupo_etnico_FK': obj['gEtnico']
            }

            #db_service2 = DatabaseService()
            #with db_service2.get_connection() as conn:
            #    with conn.cursor() as cur:
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                idU, str(ip), 'Creación de registro', 'Productor_agropecuario', idProductor, json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')


            idProductores.append(idProductor)


            res_rel_prod_event = save_relation_productor_event(idEvento, idProductor, idU, connection)
            if res_rel_prod_event[1] != 200:
                raise_exception(res_rel_prod_event[0].to_dict()['message'],  res_rel_prod_event[0].to_dict()['error'])

            res_rel_pred_prod = save_relation_predio_productor(idProductor, obj['relPre'], idU, connection)
            if res_rel_pred_prod[1] != 200:
                raise_exception(res_rel_pred_prod[0].to_dict()['message'],  res_rel_pred_prod[0].to_dict()['error'])
        
        if 'caladeros' in dataEncabezadoEvento:
            res_fishing_grounds = save_fishing_grounds(idProductores, dataEncabezadoEvento, idU, connection)
            if res_fishing_grounds[1] != 200:
                raise_exception(res_fishing_grounds[0].to_dict()['message'],  res_fishing_grounds[0].to_dict()['error'])

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_data_productor): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_data_productor): ", e)
        return CustomException('Ocurrio un error al guardar la informacion del productor', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the relation between the producer and the prey
def save_relation_predio_productor(idProductor, relPre, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        sql = ("""
            INSERT INTO Predio_productor(cod_productor_FK,cod_tipo_relacion_predio_FK) VALUES(%s,%s) RETURNING id_predio_productor
        """)

        val = (idProductor, relPre)
        cursor.execute(sql, val)

        id_pp = cursor.fetchone()[0]

        audit = {
            'cod_productor_FK': idProductor,
            'cod_tipo_relacion_predio_FK': relPre
        }

        sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            idU, str(ip), 'Creación de registro', 'Predio_productor', id_pp, json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')


    except CustomException as e:
        print("ERROR (eventos/database_manager/save_relation_predio_productor): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_relation_predio_productor): ", e)
        return CustomException('Ocurrio un error al guardar la relación entre el productor y el predio', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()

# Save the fishing grounds
def save_fishing_grounds(idProductores, encabezado, idU, connection):
    idCaladeros = []
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        caladeros = encabezado['caladeros']
        for caladero in caladeros:
            obj, estadoValidate = validate_fishing_grounds(caladero, encabezado)

            if estadoValidate == 0:
                raise_exception('Error en validación de datos.','Error en validación de datos.')

            sqlInsert = ("""
                INSERT INTO Caladeros(descripcion_zona,coord_x,coord_y,altitud,precision)
                VALUES(%s,%s,%s,%s,%s) RETURNING cod_caladero
            """)
            val = (obj['nombrePuerto'], obj['latitud'], obj['longitud'], obj['altitud'], obj['precision'])

            cursor.execute(sqlInsert,val)

            idCaladero = cursor.fetchone()[0]

            audit = {
                'descripcion_zona': obj['nombrePuerto'],
                'coord_x': obj['latitud'],
                'coord_y': obj['longitud'],
                'altitud': obj['altitud'],
                'precision': obj['precision']
            }

            #db_service2 = DatabaseService()
            #with db_service2.get_connection() as conn:
            #    with conn.cursor() as cur:
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Caladeros', int(idCaladero), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

            idCaladeros.append(idCaladero)

        res = save_producer_fishing_ground(idProductores,idCaladeros, idU, connection)
        if res[1] != 200:
            raise_exception(res[0].to_dict()['message'],  res[0].to_dict()['error'])

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_fishing_grounds): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_fishing_grounds): ", e)
        return CustomException('Ocurrio un error al guardar los caladeros', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the relation between the producer and the fishing grounds
def save_producer_fishing_ground(idProductores, idCaladeros, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        if len(idCaladeros) > 0:
            for idProductor in idProductores:
                for idCaladero in idCaladeros:

                    sqlInsert = ("""
                        INSERT INTO Productor_agro_caladero(cod_productor_agro_FK,cod_caladero_FK) VALUES(%s,%s) RETURNING cod_produc_agro_caladero
                    """)

                    val = (idProductor, idCaladero)

                    cursor.execute(sqlInsert, val)

                    idR = cursor.fetchone()[0]

                    audit = {
                        'cod_productor_agro_FK': idProductor,
                        'cod_caladero_FK': idCaladero
                    }

                    #db_service2 = DatabaseService()
                    #with db_service2.get_connection() as conn:
                    #    with conn.cursor() as cur:
                    sql = ("""
                        SELECT log_audit(%s,%s,%s,%s,%s,%s)
                    """)

                    val = (
                        int(idU), str(ip), 'Creación de registro', 'Productor_agro_caladero', int(idR), json.dumps(audit)
                    )

                    cursor.execute(sql, val)

                    if not cursor.fetchone()[0]:
                        raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')
        
    except Exception as e:
        print("ERROR (eventos/database_manager/save_producer_fishing_ground):", e)
        return CustomException('Ocurrio un error al guardar la relacion entre el productor y los caladeros', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the relation between the event and the systems
def save_event_system(idEvento, dataEspecie, sisProds, idU, connection):
    try:
        for sistema in sisProds:
            if sistema == 3 and len(dataEspecie) != 0:  # Forestal
                forestal = save_forestal_system(
                            idEvento, dataEspecie['forestal'], sistema, idU, connection)
                if forestal[1] != 200:
                    raise_exception(forestal[0].to_dict()['message'], forestal[0].to_dict()['error'])

            elif sistema == 1 and len(dataEspecie) != 0:  # Agricola
                agro = save_agro_system(
                        idEvento, dataEspecie['agropecuario'], sistema, idU, connection)
                if agro[1] != 200:
                    raise_exception(agro[0].to_dict()['message'],  agro[0].to_dict()['error'])

            elif sistema == 2 and len(dataEspecie) != 0: # Pecuario
                peq = save_peq_system(
                        idEvento, dataEspecie['infoPecuario'], sistema, idU, connection)
                if peq[1] != 200:
                    raise_exception(peq[0].to_dict()['message'],  peq[0].to_dict()['error'])
            
            elif sistema == 4 and len(dataEspecie) != 0: # Pesquero
                pesq = save_fishing_system(
                    idEvento, dataEspecie['infoPesquero'], sistema, idU, connection)
                if pesq[1] != 200:
                    raise_exception(pesq[0].to_dict()['message'],pesq[0].to_dict()['error'])
            
            elif sistema == 5 and len(dataEspecie) != 0: # Apicola
                api = save_apiarian(
                        idEvento, sistema, dataEspecie['infoApicola'], idU, connection)
                if api[1] != 200:
                    raise_exception(api[0].to_dict()['message'],  api[0].to_dict()['error'])

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_event_system):", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_event_system):", e)
        return CustomException('Ocurrio un error al guardar uno de los eventos', str(e)), 500

    else:
        return True, 200


# Save forestal system
def save_forestal_system(idEvento, dataEspecie, sistema, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr
        for especie in dataEspecie:

            obj = validate_forestal_fields(especie)

            sqlInsert = ("""
            INSERT INTO especie_forestal_sembrada (cod_fase_productiva_FK, cod_especie_forestal_afec_FK,
                                                nom_comun_especie,fch_establecimiento,
                                                densidad_siembra_Ha,area_total_sembrada_Ha,cod_objetivo_plantacion_FK,
                                                num_arbol_ha,num_estresacas,diam_prom_altura_pecho,altura_comercial,
                                                altura_total,turno_plantacion,porc_arboles_turno,
                                                valor_recibir_prod_afectada,area_afectada_ha,fcha_afectacion_sist_forestal,
                                                duracion_dias_afectacion,num_arboles_afectados,volumen_madera_afectados,
                                                valor_entresacas,porcentaje_entresacas,
                                                afectacion_infraestructura)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_especie_forestal_sembrada
            """)
            val = (obj['faseProd'], obj['espAfectada'],
                obj['nombre'], obj['fecha'], obj['densHectarea'],
                obj['areaSembrada'], obj['objetivo'], obj['noArbolesAntesAfectacion'],
                obj['noEntresacas'], obj['diametroPromedio'], obj['alturaComercial'],
                obj['alturaTotal'], obj['plantacionAnos'], obj['porceArbolesTurnoFinal'],
                obj['valorVenderProduccionAfectada'], 
                obj['areaAfectadaHectareas'],
                obj['fechaAfactaForestal'], obj['diasAfectoSistemaForestal'],
                obj['noArbolesAfectados'], 
                obj['vlMaderaAfectado'],
                obj['valEntreSacas'], 
                obj['porceEntreSacas'],
                obj['afectacionesEnMaquinaria'])
            cursor.execute(sqlInsert, val)

            idEspecieForestal = cursor.fetchone()[0]

            audit = {
                'cod_fase_productiva_FK': obj['faseProd'],
                'cod_especie_forestal_afec_FK': obj['espAfectada'],
                'nom_comun_especie': obj['nombre'],
                'fch_establecimiento': obj['fecha'],
                'densidad_siembra_Ha': obj['densHectarea'],
                'area_total_sembrada_Ha': obj['areaSembrada'],
                'cod_objetivo_plantacion_FK': obj['objetivo'],
                'num_arbol_ha': obj['noArbolesAntesAfectacion'],
                'num_estresacas': obj['noEntresacas'],
                'diam_prom_altura_pecho': obj['diametroPromedio'],
                'altura_comercial': obj['alturaComercial'],
                'altura_total': obj['alturaTotal'],
                'turno_plantacion': obj['plantacionAnos'],
                'porc_arboles_turno': obj['porceArbolesTurnoFinal'],
                'valor_recibir_prod_afectada': obj['valorVenderProduccionAfectada'],
                'area_afectada_ha': obj['areaAfectadaHectareas'],
                'fcha_afectacion_sist_forestal': obj['fechaAfactaForestal'],
                'duracion_dias_afectacion': obj['diasAfectoSistemaForestal'],
                'num_arboles_afectados': obj['noArbolesAfectados'],
                'volumen_madera_afectados': obj['vlMaderaAfectado'],
                'valor_entresacas': obj['valEntreSacas'],
                'porcentaje_entresacas': obj['porceEntreSacas']
            }

            #db_service2 = DatabaseService()
            #with db_service2.get_connection() as conn:
            #    with conn.cursor() as cur:
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Especie_forestal_sembrada', int(idEspecieForestal), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

            rel = save_relation_event_system(
                    idEvento, sistema, idEspecieForestal, 'cod_especie_forestal_FK', idU, connection)
            if rel[1] != 200:
                raise_exception(rel[0].to_dict()['message'],  rel[0].to_dict()['error'])

            afect_maq = save_relation_system_infrastructure(especie, idEspecieForestal, idU, connection)
            if afect_maq[1] != 200:
                raise_exception(afect_maq[0].to_dict()['message'],  afect_maq[0].to_dict()['error'])

            costos = save_relation_costs_system(idEvento, idEspecieForestal, especie, idU, connection)
            if costos[1] != 200:
                raise_exception(costos[0].to_dict()['message'],  costos[0].to_dict()['error'])

            variables = {
                # Valor venta de entresacas
                'VTENT': float(obj['valEntreSacas']) if obj['valEntreSacas'] != None else 0,
                # costo total
                'CT': float(costos[0]['costoTotalDirecto']) + float(costos[0]['costoTotalInDirecto']) if costos[0]['costoTotalDirecto'] != None and costos[0]['costoTotalInDirecto'] != None else 0,
                # Número de arboles afectados
                'NAF': float(obj['noArbolesAfectados']) if obj['noArbolesAfectados'] != None else 0,
                # Número total arboles sembrados
                'NTAS': float(obj['densHectarea']) * float(obj['areaSembrada']) if obj['densHectarea'] != None and obj['areaSembrada'] != None else 0,
                # Porcentaje de arboles talados entresaca
                'PATE': float(obj['porceEntreSacas']) if obj['porceEntreSacas'] != None else 0,
                # Costos totales directos
                'CD': float(costos[0]['costoTotalDirecto']) if costos[0]['costoTotalDirecto'] != None else 0,
                # Costos totales indirectos
                'CI': float(costos[0]['costoTotalInDirecto']) if costos[0]['costoTotalInDirecto'] != None else 0,
                # Cantidad hectareas afectadas
                'CHA': float(obj['areaAfectadaHectareas']) if obj['areaAfectadaHectareas'] != None else 0,
                # Valor afectacion maquinaria
                'VAM': float(afect_maq[0])
            }

            form = save_formulas(idEvento, variables, 1, idU, connection)
            if form[1] != 200:
                raise_exception(form[0].to_dict()['message'],  form[0].to_dict()['error'])
        
        
    except CustomException as e:
        print("ERROR (eventos/database_manager/save_forestal_system): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_forestal_system): ", e)
        return CustomException('Ocurrio un error al guardar los eventos forestales', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()
    

# Save relation between the event and the system
def save_relation_event_system(idEvento, sistema, idSistema, field, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        obj, estadoValidate = validate_relation_event_system_fields(idEvento, sistema, idSistema)
        
        if estadoValidate == 0:
            raise_exception('Error en validación de datos.', 'Error en validación de datos.')

        sqlInsert = ("INSERT INTO evento_sist_prod_afectado (cod_evento_FK, cod_sist_prod_afect_FK,"+field+")VALUES (%s,%s,%s) RETURNING cod_evento_sist_prod_afectado")
        val = (obj['idEvento'], obj['cod_sist_prod_afect_FK'], obj[field])

        cursor.execute(sqlInsert, val)

        idR = cursor.fetchone()[0]
        
        audit = {
            'cod_evento_FK': obj['idEvento'],
            'cod_sist_prod_afect_FK': obj['cod_sist_prod_afect_FK'],
            field: obj[field]
        }

        #db_service2 = DatabaseService()
        #with db_service2.get_connection() as conn:
        #    with conn.cursor() as cur:
        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(idU), str(ip), 'Creación de registro', 'Evento_sist_prod_afectado', int(idR), json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_relation_event_system): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_relation_event_system): ", e)
        return CustomException('Ocurrio un error al guardar los datos de la relacion entr el sistema y el evento', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the relation between system and infrastructure
def save_relation_system_infrastructure(dataEspecie, idSistema, idU, connection):
    try:
        cursor = connection.cursor()
        valor_afect_maq = 0

        if 'semilla' in dataEspecie:
            validatedSeed = validate_seed_type_forestal(dataEspecie['semilla'])
            seed = save_seed_forestal(validatedSeed, idSistema, idU, connection)
            if seed[1] != 200:
                raise_exception(seed[0].to_dict()['message'],  seed[0].to_dict()['error'])

        if 'fertilizante' in dataEspecie:
            validatedFert = validate_fert_type_forestal(dataEspecie['fertilizante'])
            fert = save_fert_forestal(validatedFert, idSistema, idU, connection)
            if fert[1] != 200:
                raise_exception(fert[0].to_dict()['message'],  fert[0].to_dict()['error'])

        if 'plaguicida' in dataEspecie:
            validatedPla = validate_pla_type_forestal(dataEspecie['plaguicida'])
            plag = save_plag_forestal(validatedPla, idSistema, idU, connection)
            if plag[1] != 200:
                raise_exception(plag[0].to_dict()['message'], plag[0].to_dict()['error'])

        if 'maquinariaAgricola' in dataEspecie:
            validatedMaq = validate_maq_type_forestal(dataEspecie['maquinariaAgricola'])
            maq = save_maq_forestal(validatedMaq, idSistema, idU, connection)
            if maq[1] != 200:
                raise_exception(maq[0].to_dict()['message'], maq[0].to_dict()['error'])
            
            valor_afect_maq = maq[0]

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_relation_system_infrastructure): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_relation_system_infrastructure): ", e)
        return CustomException('Ocurrio un error al guardar la infraestructura', str(e)), 500
    else:
        return valor_afect_maq, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the relation between the batch and propagation
def save_relation_batch_propagation(lotePropagacionSemilla, idInfraestructuraForestal, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        print(lotePropagacionSemilla, idInfraestructuraForestal, idU)

        sqlInsert = ("""
        INSERT INTO infraestructura_lote_propagacion (cod_infraestructura_FK, cod_lote_propagacion_FK)
        VALUES (%s,%s) RETURNING cod_infraestructura_lote_propagacion
        """)

        if type(lotePropagacionSemilla) == dict:
            lotePropagacionSemilla = lotePropagacionSemilla['codLotePropagacion']

        val = (idInfraestructuraForestal, lotePropagacionSemilla)
        cursor.execute(sqlInsert, val)

        idR = cursor.fetchone()[0]

        audit = {
            'cod_infraestructura_FK': idInfraestructuraForestal,
            'cod_lote_propagacion_FK': lotePropagacionSemilla
        }

        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(idU), str(ip), 'Creación de registro', 'Infraestructura_lote_propagacion', int(idR), json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')
            
    except CustomException as e:
        print("ERROR (eventos/database_manager/save_relation_batch_propagation): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_relation_batch_propagation): ", e)
        return CustomException('Ocurrio un error al guardar la relacion entre el lote y la propagacion', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the relation between the costs and the forestal system
def save_relation_costs_system(idEvento, idSistema, dataEspecie, idU, connection):
    try:
        costoTotalDirecto = save_direct_costs_forestal(
            idEvento, idSistema, dataEspecie['costosDirectos'], idU, connection)
        if costoTotalDirecto[1] != 200:
            raise_exception(costoTotalDirecto[0].to_dict()['message'],  costoTotalDirecto[0].to_dict()['error'])
        
        costoTotalInDirecto = save_indirect_costs_forestal(
            idEvento, idSistema, dataEspecie['costosInDirectos'], idU, connection)
        if costoTotalDirecto[1] != 200:
            raise_exception(costoTotalInDirecto[0].to_dict()['message'],  costoTotalInDirecto[0].to_dict()['error'])

        return {
            'costoTotalDirecto': costoTotalDirecto[0],
            'costoTotalInDirecto': costoTotalInDirecto[0],
        }, 200
    except CustomException as e:
        print("ERROR (eventos/database_manager/save_relation_costs_system): ", e.to_dict()['error'])
        return e, 500


# Save direct costs forestal system
def save_direct_costs_forestal(idEvento, idSistema, costosDirectos, idU, connection):
    costoTotalDirecto = 0
    try:
        cursor = connection.cursor()
        ip = request.remote_addr
            
        for costo in costosDirectos:

            costoTotalDirecto += float(str(costo['costo']).replace(',','')) if costo['costo'] else 0

            obj, estadoValidate = validate_direct_costs_fields_forestal(costo, idSistema)

            if estadoValidate == 0:
                raise_exception('Error en validación de datos.', 'Error en validación de datos.')

            sqlInsert = ("""
            INSERT INTO costos_directos (gasto_incurrido, cod_actividad_fk, cod_especie_forestal_fk)
            VALUES (%s,%s,%s) RETURNING cod_costo_directo
            """)
            val = (obj['costo'], 
            obj['idActividad'], obj['idSistema'])

            cursor.execute(sqlInsert, val)
            idR = cursor.fetchone()[0]

            audit = {
                'gasto_incurrido': obj['costo'],
                'cod_actividad_fk': obj['idActividad'],
                'cod_especie_forestal_fk': obj['idSistema']
            }

            #db_service2 = DatabaseService()
            #with db_service2.get_connection() as conn:
            #    with conn.cursor() as cur:
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Costos_directos', int(idR), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')


    except CustomException as e:
        print("ERROR (eventos/database_manager/save_direct_costs_forestal): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_direct_costs_forestal): ", e)
        return CustomException('Ocurrio un error al guardar los costos directos de forestal', str(e)), 500
    else:
        return costoTotalDirecto, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the indirect costs from forestal system
def save_indirect_costs_forestal(idEvento, idSistema, costosInDirectos, idU, connection):
    costoTotalInDirecto = 0
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        for costo in costosInDirectos:

            costoTotalInDirecto += float(str(costo['costo']).replace(',','')) if costo['costo'] else 0

            obj, estadoValidate = validate_indirect_costs_fields_forestal(costo, idSistema)

            if estadoValidate == 0:
                raise_exception('Error en validación de datos.', 'Error en validación de datos.')

            sqlInsert = ("""
            INSERT INTO costos_fijos_indirectos (gasto_incurrido, cod_rubro_fk, cod_especie_forestal_fk)
            VALUES (%s,%s,%s) RETURNING cod_costo_fijo_prod
            """)
            val = (obj['costo'], 
            obj['idRubro'], obj['idSistema'])

            cursor.execute(sqlInsert, val)
            idR = cursor.fetchone()[0]

            audit = {
                'gasto_incurrido': obj['costo'],
                'cod_rubro_fk': obj['idRubro'],
                'cod_especie_forestal_fk': obj['idSistema']
            }

            #db_service2 = DatabaseService()
            #with db_service2.get_connection() as conn:
            #    with conn.cursor() as cur:
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Costos_fijos_indirectos', int(idR), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')
            
    except CustomException as e:
        print("ERROR (eventos/database_manager/save_indirect_costs_forestal): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_indirect_costs_forestal): ", e)
        return CustomException('Ocurrio un error al guardar los costos indirectos de forestal', str(e)), 500
    else:
        return costoTotalInDirecto, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save forestal system formulas
def save_formulas(idEvento, variables, modulo, idU, connection):
    # formulas
    try:
        # Forestal
        if modulo == 1:
            siglas = ['PEmf', 'PPRmf', 'CTDmf', 'CTImf', 'CPmf', 'CPAmf', 'VPEPmf', 'VEDmf']

            for sigla in siglas:
                calc = calc_and_save_formula(idEvento, variables, sigla, modulo, idU, connection)
                if calc[1] != 200:
                    raise_exception(calc[0].to_dict()['message'],  calc[0].to_dict()['error'])
            return True, 200
        # Agro
        elif modulo == 2:
            siglas = ['CTDma', 'CTIma', 'CTma', 'PEma', 'VPECma', 'PPRDCma', 'VEDma']
            for sigla in siglas:
                calc = calc_and_save_formula(idEvento, variables, sigla, modulo, idU, connection)
                if calc[1] != 200:
                    raise_exception(calc[0].to_dict()['message'],  calc[0].to_dict()['error'])
            return True, 200

        # Pecuario
        elif modulo == 3:
            siglas = ['AMmpeq', 'PEKGAMmpeq', 'VAMmpeq', 'PPmpeq', 'CVPmpeq', 'CFPmpeq', 'CTmpeq', 'PPImpeq']
            for sigla in siglas:
                calc = calc_and_save_formula(idEvento, variables, sigla, modulo, idU, connection)
                if calc[1] != 200:
                    raise_exception(calc[0].to_dict()['message'],  calc[0].to_dict()['error'])
            return True, 200

        # Pesuqero
        elif modulo == 4:
            siglas = ['IPFmpesq', 'IAPmpesq', 'DImpesq']
            for sigla in siglas:
                calc = calc_and_save_formula(idEvento, variables, sigla, modulo, idU, connection)
                if calc[1] != 200:
                    raise_exception(calc[0].to_dict()['message'],  calc[0].to_dict()['error'])
            return True, 200
    
    except CustomException as e:
        print("ERROR (eventos/database_manager/save_formulas): ", e.to_dict()['error'])
        return e, 500


# Save formulas by event
def calc_and_save_formula(idEvento, variables, sigla, modulo, idU, connection):
    formula = ''

    if modulo == 1:
        if (sigla == 'PEmf'):
            if variables['CT'] != 0:
                formula = round(
                    ((variables['CT'] - variables['VTENT']) / variables['CT']) * 100, 2)
            else:
                formula = 0
        '''
        if (sigla == 'VPEmf'):
            formula = round((variables['CT'] - variables['VTENT']), 2)
        '''
        if (sigla == 'PPRmf'):
            if variables['NTAS'] != 0:
                formula = round((variables['NAF'] / variables['NTAS'])  * variables['PATE'] * 100, 2)
            else:
                formula = 0
        if(sigla == 'CTDmf'):
            formula = round(variables['CD'], 2)
        if(sigla == 'CTImf'):
            formula = round(variables['CI'], 2)
        if(sigla == 'CPmf'):
            formula = round(variables['CT'], 2)
        if(sigla == 'CPAmf'):
            if variables['CHA'] != 0:
                formula = round(variables['CT'] / variables['CHA'], 2)
            else:
                formula = 0
        if(sigla == 'VPEPmf'):
            if variables['CT'] != 0 and variables['CHA'] != 0:
                formula = round((((variables['CT'] - variables['VTENT']) / variables['CT']) * 100)/variables['CHA'], 2)
            else:
                formula = 0
        if(sigla == 'VEDmf'):
            formula = round(variables['VAM'],2)
    elif modulo == 2:
        if sigla == 'CTDma':
            formula = round(variables['CPJZ'] * variables['NJ'] + variables['GDP'], 2)
        elif sigla == 'CTIma':
            formula = round(variables['GI'], 2)
        elif sigla == 'CTma':
            formula = round(variables['CPJZ'] * variables['NJ'] + variables['GDP'] + variables['GI'], 2)
        elif sigla == 'PEma':
            CT = variables['CPJZ'] * variables['NJ'] + variables['GDP'] + variables['GI']
            if CT != 0:
                formula = round(((CT - variables['CDVC'])/CT)* 100, 2)
            else:
                formula = 0
        elif sigla == 'VPECma':
            CT = variables['CPJZ'] * variables['NJ'] + variables['GDP'] + variables['GI']
            formula = round(CT - variables['CDVC'], 2)
        elif sigla == 'PPRDCma':
            if variables['CPEP'] != 0:
                formula = round(((variables['CPEP'] - variables['CC'])/variables['CPEP'])*100,2)
            else:
                formula = 0
        elif sigla == 'VEDma':
            formula = round(variables['VSP']+variables['VFA']+variables['VPP']+variables['VPAM'],2)
    elif modulo == 3:
        if sigla == 'AMmpeq':
            formula = round(variables['NAHM'] + variables['NAMM'], 2)
        elif sigla == 'PEKGAMmpeq':
            formula = round(variables['PPAE'] * (variables['NAHM'] + variables['NAMM']), 2)
        elif sigla == 'VAMmpeq':
            formula = round(variables['PPPA'] * (variables['NAHM'] + variables['NAMM']),2)
        elif sigla == 'PPmpeq':
            if variables['PMAF'] != 0:
                formula = round(((variables['PMAF'] - variables['PMAPA'])/variables['PMAF'])*100,2)
            else:
                formula = 0
        elif sigla == 'CVPmpeq':
            formula = round((variables['PPPA'] * (variables['NAHM'] + variables['NAMM'])) + variables['VCVP'], 2)
        elif sigla == 'CFPmpeq':
            formula = round(variables['GICF'],2)
        elif sigla == 'CTmpeq':
            formula = round((variables['PPPA'] * (variables['NAHM'] + variables['NAMM'])) + variables['VCVP'] + variables['GICF'], 2)
        elif sigla == 'PPImpeq':
            form = (variables['PPPA'] * (variables['NAHM'] + variables['NAMM'])) + variables['VCVP']
            if form != 0:
                formula = round(((form - variables['PVUP'])/form) * 100, 2)
            else:
                formula = 0
    elif modulo == 4:
        if sigla == 'IPFmpesq':
            formula = round(variables['NFP'] * variables['VPRVPF'], 2)
        if sigla == 'IAPmpesq':
            formula = round(variables['FP'] * variables['VPRVPF'], 2)
        elif sigla == 'DImpesq':
            form = variables['NFP'] * variables['VPRVPF']
            if form != 0:
                formula = round(100-((variables['FP'] * variables['VPRVPF'] * 100)/form), 2)
            else:
                formula = 0

    # Fecha actual
    fechaActual = datetime.datetime.utcnow() - datetime.timedelta(minutes=300)
    cursor = None
    try:
        ip = request.remote_addr
        idIndicador = search_id_formula_by_initials(sigla, connection)
        if idIndicador[1] != 200:
            raise_exception(idIndicador[0].to_dict()['message'],  idIndicador[0].to_dict()['error'])

        variablesIndicador = search_variable_by_indicator(idIndicador[0]['cod_indicador'], connection) 
        if variablesIndicador[1] != 200:
            raise_exception(variablesIndicador[0].to_dict()['message'],  variablesIndicador[0].to_dict()['error'])

    
        cursor = connection.cursor()

        sqlInsertIndicador = ("""
        INSERT INTO indicador_valor (valor, cod_indicador_FK, cod_evento_FK)
        VALUES (%s,%s,%s) RETURNING cod_indicador_valor
        """)
        valIndicador = (formula, idIndicador[0]['cod_indicador'], idEvento['id'])
        cursor.execute(sqlInsertIndicador, valIndicador)

        codIndicador = cursor.fetchone()[0]

        audit = {
            'valor': formula,
            'cod_indicador_FK': idIndicador[0]['cod_indicador'],
            'cod_evento_FK': idEvento['id']  
        }

        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(idU), str(ip), 'Creación de registro', 'Indicador_valor', int(codIndicador), json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')
        

        for variable in variablesIndicador[0]:
            costo = variables[str(variable['siglas'])]

            idVariable = search_id_variable_by_initials(variable['siglas'], connection)
            if idVariable[1] != 200:
                raise_exception(idVariable[0].to_dict()['message'],  idVariable[0].to_dict()['error'])


            sqlInsertVariable = ("""
            INSERT INTO variable_valor (fch_actualizacion, valor, cod_variable_FK)
            VALUES (%s,%s,%s) RETURNING cod_variable_valor
            """)

            valVariable = (str(fechaActual.date()), costo, idVariable[0]['cod_variable'])
            cursor.execute(sqlInsertVariable, valVariable)
            codVariable = cursor.fetchone()[0]

            audit = {
                'fch_actualizacion': str(fechaActual.date()),
                'valor': costo,
                'cod_variable_FK': idVariable[0]['cod_variable']
            }

            #db_service2 = DatabaseService()
            #with db_service2.get_connection() as conn:
            #    with conn.cursor() as cur:
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Variable_valor', int(codVariable), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')


            sqlInsertRelVariableIndicador = ("""
            INSERT INTO indicador_valor_variable_valor (indicador_valor_FK, variable_valor_FK)
            VALUES (%s,%s) RETURNING cod_indicador_valor_variable_valor
            """)

            valRel = (codIndicador, codVariable)
            cursor.execute(sqlInsertRelVariableIndicador, valRel)
            idR = cursor.fetchone()[0]

            audit = {
                'indicador_valor_FK': codIndicador,
                'variable_valor_FK': codVariable
            }

            #db_service2 = DatabaseService()
            #with db_service2.get_connection() as conn:
            #    with conn.cursor() as cur:
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Indicador_valor_variable_valor', int(idR), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')


    except CustomException as e:
        print("ERROR (eventos/database_manager/calc_and_save_formula): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/calc_and_save_formula): ", e)
        return CustomException('Ocurrio un error al calcular y guardar las formulas', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search formula by initials
def search_id_formula_by_initials(sigla, connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/search_id_formula_by_initials): ", e)
        return CustomException('Ocurrio un error buscando las formulas', str(e)), 500
    else:
        return results[0], 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search variable by indicator
def search_variable_by_indicator(idIndicador, connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/search_variable_by_indicator): ", e)
        return CustomException('Ocurrio un error al buscar las variables por indicador', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search variable by initials
def search_id_variable_by_initials(sigla, connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/search_id_variable_by_initials): ", e)
        return CustomException('Ocurrio un error al buscar las variables por iniciales', str(e)), 500
    else:
        return results[0], 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the agro system
def save_agro_system(idEvento, dataEspecie, sistema, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        for cultivo in dataEspecie:

            validated = validate_fields_agro(cultivo)
            
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
                afectacion_infraestructura,
                eqv_carga_otro_material_siembra,
                nombre_nueva_unidad_reporte_area_cultivo,
                eqv_mt_nueva_unidad_reporte_area_cultivo)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING cod_cultivo
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
                str(validated["totalReciCosechado"]).replace(',','') if validated["totalReciCosechado"] else None,  # 20
                validated["cantProduProducir"],  # 21
                validated["medidaReportar"],  # 22
                str(validated["totalReportado"]).replace(',','') if validated["totalReportado"] else None,  # 23
                validated["equivaleKilosReportar"],  # 24
                validated["proyEqvKg"],  # 25
                str(validated["totalProyectaVenta"]).replace(',','') if validated["totalProyectaVenta"] else None,  # 26
                str(validated["costoPromeJornal"]).replace(',','') if validated["costoPromeJornal"] else None,  # 27
                validated["porceResiembra"],  # 28
                str(validated["perdEstInv"]).replace(',','') if validated["perdEstInv"] else None,  # 29
                str(validated["renEspProd"]).replace(',','') if validated["renEspProd"] else None,  # 30
                str(validated["rendRealProd"]).replace(',','') if validated["rendRealProd"] else None,  # 31
                str(validated["perdEstimRendCult"]).replace(',','') if validated["perdEstimRendCult"] else None,  # 32
                validated["afectaMaquinaria"] if validated["afectaMaquinaria"] else None,  # 33
                validated['nuevaEquivalencia'],
                validated['nombrenuvaunidad'], 
                validated['nuevaunidadmetros']
            )
            
            cursor.execute(sql, params)

            idCultivoAfectado = cursor.fetchone()[0]

            audit = {
                'cod_nombre_FK': validated["nombreCultivo"], 
                'area_total_cultivo_sembrado': validated["areaCultivo"], 
                'cod_unidad_area_FK': validated["unidadArea"], 
                'area_total_cultivo_Ha': validated["areaTotCultHa"], 
                'cod_tipo_material_siembra_FK': validated["materiralSiembra"], 
                'cantidad_semilla_utilizo_siembra_ha': validated["cantSemillas"], 
                'cod_unidad_cantidad_semilla_FK': validated["medidaSemilla"], 
                'equivalencia_kg_carga': validated["equivCargaKg"], 
                'cod_semilla_equiv_Kg_FK': validated["equivaleKilos"], 
                'cod_fuente_semilla_FK': validated["fuenteSemilla"], 
                'fch_inicio_afectacion': validated["fechaAfectacion"], 
                'duracion_dias_afectacion': validated["diasCultivoExpuesto"], 
                'fcha_siembra': validated["fechaSiembra"], 
                'mes_cosecha_cultivo': validated["fechaPrimeCosecha"], 
                'mes_esperado_cosecha': validated["fechaEsperaCosecha"], 
                'cant_cosechada': validated["cantCosechada"], 
                'cod_unidad_consecha_FK': validated["medidaCantCosechada"], 
                'cod_equiva_kg_FK': validated["equivaleKilosCosecha"], 
                'equivalencia_Kg_carga_zona': validated["equivKgCargZon"], 
                'cant_dinero_venta_cosecha': str(validated["totalReciCosechado"]).replace(',','') if validated["totalReciCosechado"] else None, 
                'proyectada_cant_produc_estim_producir': validated["cantProduProducir"],
                'proyectada_cod_unidad_reporte_FK': validated["medidaReportar"], 
                'proyectada_precio_por_cada_unidad': str(validated["totalReportado"]).replace(',','') if validated["totalReportado"] else None, 
                'proyectada_cod_equiva_kg_FK': validated["equivaleKilosReportar"], 
                'proyectada_equivalencia_kg': validated["proyEqvKg"], 
                'proyectada_vlr_total_recibir_venta_total_produccion': str(validated["totalProyectaVenta"]).replace(',','') if validated["totalProyectaVenta"] else None, 
                'costo_promedio_jornal_zona': str(validated["costoPromeJornal"]).replace(',','') if validated["costoPromeJornal"] else None, 
                'porc_resiembra': validated["porceResiembra"], 
                'perdida_estimada_inversion': str(validated["perdEstInv"]).replace(',','') if validated["perdEstInv"] else None, 
                'rendimiento_esperado_productor': str(validated["renEspProd"]).replace(',','') if validated["renEspProd"] else None, 
                'rendimiento_real_productor': str(validated["rendRealProd"]).replace(',','') if validated["rendRealProd"] else None, 
                'perdida_estimado_rend_cultivo': str(validated["perdEstimRendCult"]).replace(',','') if validated["perdEstimRendCult"] else None, 
                'afectacion_infraestructura': validated["afectaMaquinaria"] if validated["afectaMaquinaria"] else None,
                'eqv_carga_otro_material_siembra': validated['nuevaEquivalencia'],
                'nombre_nueva_unidad_reporte_area_cultivo': validated['nombrenuvaunidad'],
                'eqv_mt_nueva_unidad_reporte_area_cultivo': validated['nuevaunidadmetros']
            }

            #db_service2 = DatabaseService()
            #with db_service2.get_connection() as conn:
            #    with conn.cursor() as cur:
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Cultivos_afectados', int(idCultivoAfectado), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')
            
            rel = save_relation_event_system(idEvento, sistema, idCultivoAfectado, 'cod_cultivo_afectado_FK', idU, connection)
            if rel[1] != 200:
                raise_exception(rel[0].to_dict()['message'],  rel[0].to_dict()['error'])
           
            direct = save_direct_costs(idCultivoAfectado, cultivo['costosDirectos'], cultivo['costoPromeJornal'], idU, connection)
            if direct[1] != 200:
                raise_exception(direct[0].to_dict()['message'], direct[0].to_dict()['error'])
           
            indirect = save_indirect_costs_agro(idCultivoAfectado, cultivo['costosInDirectos'], idU, connection)
            if indirect[1] != 200:
                raise_exception(indirect[0].to_dict()['message'],  indirect[0].to_dict()['error'])
          
            assurance_credit = save_assurance_credit_agro(idCultivoAfectado, cultivo, idU, connection)
            if assurance_credit[1] != 200:
                raise_exception(assurance_credit[0].to_dict()['message'],  assurance_credit[0].to_dict()['error'])
      
            infra = save_infrastructure_agro(idCultivoAfectado, cultivo, validated["nombreCultivo"], idU, connection)
            if infra[1] != 200:
                raise_exception(infra[0].to_dict()['message'],  infra[0].to_dict()['error'])
          
            variables = {
                # Costo promedio jornal zona
                'CPJZ': float(str(validated['costoPromeJornal']).replace(',','')) if validated['costoPromeJornal'] != None else 0,
                # Numero de jornales 
                'NJ': float(direct[0]['numJornales']) if direct[0]['numJornales'] != None else 0,
                # Gastos de produccion 
                'GDP': float(direct[0]['gastosDeProduccion']) if direct[0]['gastosDeProduccion'] != None else 0,
                # Gastos incurridos
                'GI': float(indirect[0]['gastosIncurridos']) if indirect[0]['gastosIncurridos'] != None else 0,
                # Cantidad dinero venta cosecha
                'CDVC': float(str(validated['totalReciCosechado']).replace(',','')) if validated['totalReciCosechado'] != None else 0,
                # Cantidad producto que estimaba producir
                'CPEP': float(validated['cantProduProducir']) if validated['cantProduProducir'] != None else 0,
                # Cantidad cosechada
                'CC': float(validated['cantCosechada']) if validated['cantCosechada'] != None else 0,
                # Valor semilla en pesos
                'VSP': float(infra[0]['valorSemilla']) if infra[0]['valorSemilla'] != None else 0,
                # Valor fertilizantes almacenados
                'VFA': float(infra[0]['valorFertilizante']) if infra[0]['valorFertilizante'] != None else 0,
                # Valor pesos plaguicidas
                'VPP': float(infra[0]['valorPlaguicida']) if infra[0]['valorPlaguicida'] != None else 0,
                # Valor pesos afectacion maquinaria
                'VPAM': float(infra[0]['valorMaquinaria']) if infra[0]['valorMaquinaria'] != None else 0
            }

            form = save_formulas(idEvento, variables, 2, idU, connection)
            if form[1] != 200:
                raise_exception(form[0].to_dict()['message'],  form[0].to_dict()['error'])

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_agro_system): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_agro_system): ", e)
        return CustomException('Ocurrio un error al guardar el evento agropecuario', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save direct costs in agro system
def save_direct_costs(idCultivoAfectado, costosDirectos, costoPromeJornal, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        jornales = 0
        costos = 0

        for costo in costosDirectos:
            validated = validate_direct_costs_agro(costo)
            sql = ("""
                INSERT INTO costos_de_produccion(cod_actividad_FK, num_jornales, cod_cultivo_afectado_FK, gastos, 
                costo_promedio_jornal)
                VALUES(%s, %s, %s, %s, %s) RETURNING cod_costo_produccion
            """)

            params = (
                validated['id'], float(validated['noJornales']), idCultivoAfectado, 
                float(str(validated['gastos']).replace(',','')) if validated['gastos'] else None, 
                float(str(costoPromeJornal).replace(',','')) if costoPromeJornal else None
            )

            jornales += float(validated['noJornales'])
            costos += float(str(validated['gastos']).replace(',','')) if validated['gastos'] else 0

            cursor.execute(sql, params)
            idR = cursor.fetchone()[0]

            audit = {
                'cod_actividad_FK': validated['id'],
                'num_jornales': validated['noJornales'],
                'cod_cultivo_afectado_FK': idCultivoAfectado,
                'gastos': str(validated['gastos']).replace(',','') if validated['gastos'] else None,
                'costo_promedio_jornal': float(str(costoPromeJornal).replace(',','')) if costoPromeJornal else None
            }

            #db_service2 = DatabaseService()
            #with db_service2.get_connection() as conn:
            #    with conn.cursor() as cur:
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Costos_de_produccion', int(idR), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except Exception as e:
        print("ERROR (eventos/database_manager/save_direct_costs): ", e)
        return CustomException('Ocurrio un error al guardar los costos directos de agropecuario', str(e)), 500
    else:
        return {'numJornales': jornales, 'gastosDeProduccion': costos}, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the indirect costs in agro system
def save_indirect_costs_agro(idCultivoAfectado, costosIndirectos, idU, connection):
    costos = 0
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        for costo in costosIndirectos:
            validated = valdate_indirect_costs_agro(costo)

            sql = ("""
                INSERT INTO costos_indirectos_produccion(cod_rubro_FK, gastos_incurridos, cod_cultivo_afectado_FK)
                VALUES(%s, %s, %s) RETURNING cod_costo_indirecto
            """)

            params = (
                validated['tipoCostoInDirecto'], 
                str(validated['costo']).replace(',','') if validated['costo'] else None, 
                idCultivoAfectado
            )

            costos += float(str(validated['costo']).replace(',','')) if validated['costo'] else 0

            cursor.execute(sql, params)
            idR = cursor.fetchone()[0]

            audit = {
                'cod_rubro_FK': validated['tipoCostoInDirecto'],
                'gastos_incurridos': str(validated['costo']).replace(',','') if validated['costo'] else None,
                'cod_cultivo_afectado_FK': idCultivoAfectado
            }

            #db_service2 = DatabaseService()
            #with db_service2.get_connection() as conn:
            #    with conn.cursor() as cur:
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Costos_indirectos_produccion', int(idR), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except Exception as e:
        print("ERROR (eventos/database_manager/save_indirect_costs_agro): ", e)
        return CustomException('Ocurrio un error al guardar los costos indirectos de agropecuario', str(e)), 500
    else:
        return {'gastosIncurridos': costos}, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Saves the assurance and credit information of agro system
def save_assurance_credit_agro(idCult, cult, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr
        
        if('tipoSeguro' in cult):
            sql = ("""
                INSERT INTO Aseguramiento(valor_cultivo_asegurado, cod_tipo_seguro_FK, cod_cultivo_afectado_FK)
                VALUES(%s,%s,%s) RETURNING cod_aseguramiento
            """)

            val = (str(cult['valCultiAsegurado']).replace(',',''), cult['tipoSeguro'], idCult)
            cursor.execute(sql, val)

            cod_ass = cursor.fetchone()[0]

            audit = {
                'valor_cultivo_asegurado': str(cult['valCultiAsegurado']).replace(',',''),
                'cod_tipo_seguro_FK': cult['tipoSeguro'],
                'cod_cultivo_afectado_FK': idCult
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Aseguramiento', int(cod_ass), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

        if('idEntidadesBancarias' in cult):
            sql = ("""
                INSERT INTO Credito(cod_entidad_credito_FK, porc_costos_cultivo, cod_cultivo_FK)
                values(%s,%s,%s) RETURNING cod_credito
            """)
            
            val = (cult['idEntidadesBancarias'], cult['porceCostoCredito'], idCult)
            cursor.execute(sql, val)

            id_cred = cursor.fetchone()[0]

            audit = {
                'cod_entidad_credito_FK': cult['idEntidadesBancarias'],
                'porc_costos_cultivo': cult['porceCostoCredito'],
                'cod_cultivo_FK': idCult
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Credito', int(id_cred), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_assurance_credit_agro): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_assurance_credit_agro): ", e)
        return CustomException('Ocurrio un error al guardar los datos del aseguramiento y crédito del evento agro', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the infrastructure in agro system, whatever it be
def save_infrastructure_agro(idCultivoAfectado, dataEspecie, nombreCultivo, idU, connection):
    try:
        if 'tipoInfraFertilizante' in dataEspecie:
            validatedFertilizante = validate_fertilizer_type_agro(dataEspecie['tipoInfraFertilizante'])
            fert = save_fertilizer_agro(validatedFertilizante, idCultivoAfectado, nombreCultivo, idU, connection)
            if fert[1] != 200:
                raise_exception(fert[0].to_dict()['message'],  fert[0].to_dict()['error'])

        if 'tipoInfraMaquinaria' in dataEspecie:
            validatedMaquinaria = validate_machinery_type_agro(dataEspecie['tipoInfraMaquinaria'])
            mach = save_machinery_agro(validatedMaquinaria, idCultivoAfectado, nombreCultivo, idU, connection)
            if mach[1] != 200:
                raise_exception(mach[0].to_dict()['message'],  mach[0].to_dict()['error'])

        if 'tipoInfraPlaguicidas' in dataEspecie:
            validatedPlaguicida = validate_plaguicide_type_agro(dataEspecie['tipoInfraPlaguicidas'])
            plag = save_plaguicide_agro(validatedPlaguicida, idCultivoAfectado, nombreCultivo, idU, connection)
            if plag[1] != 200:
                raise_exception(plag[0].to_dict()['message'],  plag[0].to_dict()['error'])

        if 'tipoInfraSemilla' in dataEspecie:
            validatedSemilla = validate_seed_type_agro(dataEspecie['tipoInfraSemilla'])
            seed = save_seed_agro(validatedSemilla, idCultivoAfectado, nombreCultivo, idU, connection)
            if seed[1] != 200:
                raise_exception(seed[0].to_dict()['message'],  seed[0].to_dict()['error'])
            
    except CustomException as e:
        print("ERROR (eventos/database_manager/save_infrastructure_agro):", e.to_dict()['error'])
        return e, 500
    else:
        return {'valorFertilizante': fert[0], 'valorMaquinaria': mach[0], 'valorPlaguicida': plag[0], 'valorSemilla': seed[0]}, 200


# Save the fertilizer from agro system
def save_fertilizer_agro(fertilizantes, idCultivoAfectado, nombreCultivo, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr
        fert_val = 0
        for fertilizante in fertilizantes:
            sql = ("""
                INSERT INTO infraestructura(cod_tipo_infraestructura_FK, cod_tipo_fertilizante_FK, nom_fertilizante,
                fch_adquisicion, cant_fert_almac_afect, vlr_fertilizante_almacenado) VALUES(%s,%s,%s,%s,%s,%s) RETURNING cod_infraestructura
            """) 

            params = (
                2, fertilizante['idTipoFertilizante'], fertilizante['nombre'], 
                fertilizante['fechaAdquisicion'], fertilizante['canFertilizante'], 
                str(fertilizante['valPesos']).replace(',','') if fertilizante['valPesos'] else None
            )

            fert_val += float(str(fertilizante['valPesos']).replace(',','')) if fertilizante['valPesos'] else 0
            cursor.execute(sql, params)
            idFertilizer =  cursor.fetchone()[0]

            audit = {
                'cod_tipo_infraestructura_FK': 2,
                'cod_tipo_fertilizante_FK': fertilizante['idTipoFertilizante'],
                'nom_fertilizante': fertilizante['nombre'],
                'fch_adquisicion': fertilizante['fechaAdquisicion'],
                'cant_fert_almac_afect': fertilizante['canFertilizante'],
                'vlr_fertilizante_almacenado': str(fertilizante['valPesos']).replace(',','') if fertilizante['valPesos'] else None
            }

            #db_service2 = DatabaseService()
            #with db_service2.get_connection() as conn:
            #    with conn.cursor() as cur:
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Infraestructura', int(idFertilizer), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

            crop_inf = save_crop_infrastructure(idCultivoAfectado, idFertilizer, idU, connection)
            if crop_inf[1] != 200:
                raise_exception(crop_inf[0].to_dict()['message'],  crop_inf[0].to_dict()['error'])

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_fertilizer_agro): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_fertilizer_agro): ", e)
        return CustomException('Ocurrio un error al guardar los fertilizantes de agropecuario', str(e)), 500
    else:
        return fert_val, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the machinery in agro system
def save_machinery_agro(maquinarias, idCultivoAfectado, nombreCultivo, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr
        maq_val = 0
        for maquinaria in maquinarias:
            sql = ("""
                INSERT INTO infraestructura(cod_tipo_infraestructura_FK, cod_tipo_maq_agr_afec_FK, fch_adquisicion_equipo, 
                edad_equipo, vlr_pesos_afectacion_maq, porc_disminuyo_prod_afect_maq) VALUES(%s,%s,%s,%s,%s,%s) RETURNING cod_infraestructura
            """)

            actual_year = datetime.date.today().year
            maquinaria_edad = actual_year - int(maquinaria['anoAdquisicion'])
            params = (
                4, maquinaria['idTipoMaquinariaAgricola'], str(maquinaria['anoAdquisicion']) +'-01-01',  
                maquinaria_edad, str(maquinaria['valorPesos']).replace(',','') if maquinaria['valorPesos'] else None, 
                maquinaria['porceDisminucion']
            )

            maq_val += float(str(maquinaria['valorPesos']).replace(',','')) if maquinaria['valorPesos'] else 0

            cursor.execute(sql, params)
            idMachinery =  cursor.fetchone()[0]

            audit = {
                'cod_tipo_infraestructura_FK': 4,
                'cod_tipo_maq_agr_afec_FK': maquinaria['idTipoMaquinariaAgricola'],
                'fch_adquisicion_equipo': str(maquinaria['anoAdquisicion']) +'-01-01',
                'edad_equipo': maquinaria_edad,
                'vlr_pesos_afectacion_maq': str(maquinaria['valorPesos']).replace(',','') if maquinaria['valorPesos'] else None,
                'porc_disminuyo_prod_afect_maq': maquinaria['porceDisminucion']
            }

            #db_service2 = DatabaseService()
            #with db_service2.get_connection() as conn:
            #    with conn.cursor() as cur:
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Infraestructura', int(idMachinery), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

            crop_inf = save_crop_infrastructure(idCultivoAfectado, idMachinery, idU, connection)
            if crop_inf[1] != 200:
                raise_exception(crop_inf[0].to_dict()['message'],  crop_inf[0].to_dict()['error'])

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_machinery_agro): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_machinery_agro): ", e)
        return CustomException('Ocurrio un error al guardar la maquinaria de agropecuario', str(e)), 500
    else:
        return maq_val, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the plaguicide in agro system
def save_plaguicide_agro(plaguicidas, idCultivoAfectado, nombreCultivo, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr
        plag_val = 0
        for plaguicida in plaguicidas:
            sql = ("""
                INSERT INTO infraestructura(cod_tipo_infraestructura_FK, cod_tipo_plaguicida_FK, cod_presentacion_FK, 
                cantidad_plaguicidas_almac_afec_litros, cantidad_plaguicidas_almac_afec_kg, vlr_pesos_plaguicidas)
                VALUES(%s,%s,%s,%s,%s,%s) RETURNING cod_infraestructura
            """)

            params = (
                3, plaguicida['idTipoPlaguicida'], plaguicida['idTipoPresentacion'], 
                plaguicida['cantPlaguicidaLt'], plaguicida['cantPlaguicidaKg'], 
                str(plaguicida['valPesos']).replace(',','') if plaguicida['valPesos'] else None
            )

            plag_val += float(str(plaguicida['valPesos']).replace(',','')) if plaguicida['valPesos'] else 0
            cursor.execute(sql, params)
            idPlaguicide =  cursor.fetchone()[0]

            audit = {
                'cod_tipo_infraestructura_FK': 3,
                'cod_tipo_plaguicida_FK': plaguicida['idTipoPlaguicida'],
                'cod_presentacion_FK': plaguicida['idTipoPresentacion'],
                'cantidad_plaguicidas_almac_afec_litros': plaguicida['cantPlaguicidaLt'],
                'cantidad_plaguicidas_almac_afec_kg': plaguicida['cantPlaguicidaKg'],
                'vlr_pesos_plaguicidas': str(plaguicida['valPesos']).replace(',','') if plaguicida['valPesos'] else None
            }

            #db_service2 = DatabaseService()
            #with db_service2.get_connection() as conn:
            #    with conn.cursor() as cur:
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Infraestructura', int(idPlaguicide), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

            crop_inf = save_crop_infrastructure(idCultivoAfectado, idPlaguicide, idU, connection)
            if crop_inf[1] != 200:
                raise_exception(crop_inf[0].to_dict()['message'],  crop_inf[0].to_dict()['error'])

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_plaguicide_agro): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_plaguicide_agro): ", e)
        return CustomException('Ocurrio un error al guardar los plaguicidas de agropecuario', str(e)), 500
    else:
        return plag_val, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save seed in agro system
def save_seed_agro(semillas, idCultivoAfectado, nombreCultivo, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr
        seed_val = 0
        for semilla in semillas:
            sql = ("""
                INSERT INTO infraestructura(cod_tipo_infraestructura_FK, cod_especie_fk, cant_semilla_almacenada_kg, vlr_semilla_pesos, material_siembra_fk,
                cant_semilla_siembra, unidad_reporte_cant_semilla_fk, fuente_semilla_fk, eqv_carga_kg_semilla, eqv_carga_kg_semilla_otro)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_infraestructura
            """)

            params = (
                1, semilla['tipoCultivo'], semilla['canSemillas'], 
                str(semilla['valPesos']).replace(',','') if semilla['valPesos'] else None, 
                semilla['materiralSiembra'], semilla['cantSemillas'], semilla['medidaSemilla'],
                semilla['fuenteSemilla'], semilla['equivaleKilos'], semilla['nuevaEquivalencia']
            )

            seed_val += float(str(semilla['valPesos']).replace(',','')) if semilla['valPesos'] else 0

            cursor.execute(sql, params)
            idSeed =  cursor.fetchone()[0]

            audit = {
                'cod_tipo_infraestructura_FK': 1,
                'cod_especie_fk': semilla['tipoCultivo'],
                'nom_especie': nombreCultivo,
                'cant_semilla_almacenada_kg': semilla['canSemillas'],
                'vlr_semilla_pesos': str(semilla['valPesos']).replace(',','') if semilla['valPesos'] else None,
                'material_siembra_fk': semilla['materiralSiembra'],
                'cant_semilla_siembra': semilla['cantSemillas'],
                'unidad_reporte_cant_semilla_fk': semilla['medidaSemilla'],
                'fuente_semilla_fk': semilla['fuenteSemilla'],
                'eqv_carga_kg_semilla': semilla['equivaleKilos'],
                'eqv_carga_kg_semilla_otro': semilla['nuevaEquivalencia']
            }

            #db_service2 = DatabaseService()
            #with db_service2.get_connection() as conn:
            #    with conn.cursor() as cur:
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Infraestructura', int(idSeed), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')
            
            crop_inf = save_crop_infrastructure(idCultivoAfectado, idSeed, idU, connection)
            if crop_inf[1] != 200:
                raise_exception(crop_inf[0].to_dict()['message'],  crop_inf[0].to_dict()['error'])

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_seed_agro): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_seed_agro): ", e)
        return CustomException('Ocurrio un error al guardar las semillas de agropecuario', str(e)), 500
    else:
        return seed_val, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save seed of forestal system
def save_seed_forestal(semillas, idSistema, idU, connection):
    try:

        cursor = connection.cursor()
        ip = request.remote_addr
        
        for semilla in semillas:
            insert = """
                INSERT INTO Infraestructura_forestal(cod_tipo_infraestrucrtura_FK,cod_especie_semilla_fk,cant_semilla_almacenada,
                vlr_pesos_afectacion,cant_semilla_siembra,cod_unidad_cantidad_semilla_fk,cod_tip_semilla_FK,cod_fuente_semilla_fk,
                eqv_kg_carga_semilla_fk,eqv_kg_carga_otro_semilla_fk,cod_especie_forestal_sembrada_FK) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
                RETURNING cod_infraestructura_forestal
            """

            val = (1,semilla['espAfectada'],semilla['canSemillas'],
            str(semilla['valPesos']).replace(',','') if semilla['valPesos'] else None,
            semilla['cantSemillas'],semilla['medidaSemilla'],
            semilla['idTipoSemilla'],semilla['fuenteSemilla'],semilla['equivaleKilos'],semilla['nuevaEquivalencia'],idSistema)

            cursor.execute(insert, val)
            idSeed =  cursor.fetchone()[0]

            audit = {
                'cod_tipo_infraestrucrtura_FK': 1,
                'cod_especie_semilla_fk': semilla['espAfectada'],
                'cant_semilla_almacenada': semilla['canSemillas'],
                'vlr_pesos_afectacion': str(semilla['valPesos']).replace(',','') if semilla['valPesos'] else None,
                'cant_semilla_siembra': semilla['cantSemillas'],
                'cod_unidad_cantidad_semilla_fk': semilla['medidaSemilla'],
                'cod_tip_semilla_FK': semilla['idTipoSemilla'],
                'cod_fuente_semilla_fk': semilla['fuenteSemilla'],
                'eqv_kg_carga_semilla_fk': semilla['equivaleKilos'],
                'eqv_kg_carga_otro_semilla_fk': semilla['nuevaEquivalencia'],
                'cod_especie_forestal_sembrada_FK': idSistema
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Infraestructura_forestal', int(idSeed), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

            if semilla['idLotePropagacion']:
                batch = save_relation_batch_propagation(semilla['idLotePropagacion'], idSeed, idU, connection)
                if batch[1] != 200:
                    raise_exception(batch[0].to_dict()['message'],  batch[0].to_dict()['error'])
        
    except CustomException as e:
        print("ERROR (eventos/database_manager/save_seed_forestal): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_seed_forestal): ", e)
        return CustomException('Ocurrio un error al guardar las semillas de forestal', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save seed of forestal system
def save_fert_forestal(fertilizantes, idSistema, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        for fertilzante in fertilizantes:
            insert = """
                INSERT INTO Infraestructura_forestal(cod_tipo_infraestrucrtura_FK,cod_tipo_fertilizante_FK,nombre_fertilizante,
                fecha_adquisicion_fert,cantidad,valor_pesos_afectacion,cod_especie_forestal_sembrada_FK) VALUES(%s,%s,%s,%s,%s,%s,%s) 
                RETURNING cod_infraestructura_forestal
            """

            val = (2, fertilzante['idTipoFertilizante'], fertilzante['nombre'], fertilzante['fechaAdquisicion'], fertilzante['canFertilizante'],
            str(fertilzante['valPesos']).replace(',','') if fertilzante['valPesos'] else None, 
            idSistema)

            cursor.execute(insert, val)
            idSeed =  cursor.fetchone()[0]

            audit = {
                'cod_tipo_infraestrucrtura_FK': 2,
                'cod_tipo_fertilizante_FK': fertilzante['idTipoFertilizante'],
                'nombre_fertilizante': fertilzante['nombre'],
                'fecha_adquisicion_fert': fertilzante['fechaAdquisicion'],
                'cantidad': fertilzante['canFertilizante'],
                'valor_pesos_afectacion': str(fertilzante['valPesos']).replace(',','') if fertilzante['valPesos'] else None,
                'cod_especie_forestal_sembrada_FK': idSistema
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Infraestructura_forestal', int(idSeed), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_fert_forestal): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_fert_forestal): ", e)
        return CustomException('Ocurrio un error al guardar los fertilizantes de forestal', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save plaguicides of forestal system
def save_plag_forestal(plaguicidas, idSistema, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        for plaguicida in plaguicidas:
            insert = """
                INSERT INTO Infraestructura_forestal(cod_tipo_infraestrucrtura_FK,cod_tipo_plaguicida_FK,presentacion_plaguicida,
                cant_plaguicidas_kg,cant_plaguicidas_lt,vlr_pesos_afectacion_pla,cod_especie_forestal_sembrada_FK) VALUES(%s,%s,%s,%s,%s,%s,%s) 
                RETURNING cod_infraestructura_forestal
            """

            val = (3, plaguicida['idTipoPlaguicida'], plaguicida['idTipoPresentacion'], plaguicida['cantPlaguicidaKg'], plaguicida['cantPlaguicidaLt'],
            str(plaguicida['valPesos']).replace(',','') if plaguicida['valPesos'] else None, 
            idSistema)

            cursor.execute(insert, val)
            idSeed = cursor.fetchone()[0]

            audit = {
                'cod_tipo_infraestrucrtura_FK': 2,
                'cod_tipo_plaguicida_FK': plaguicida['idTipoPlaguicida'],
                'presentacion_plaguicida': plaguicida['idTipoPresentacion'],
                'cant_plaguicidas_kg': plaguicida['cantPlaguicidaKg'],
                'cant_plaguicidas_lt': plaguicida['cantPlaguicidaLt'],
                'vlr_pesos_afectacion_pla': str(plaguicida['valPesos']).replace(',','') if plaguicida['valPesos'] else None,
                'cod_especie_forestal_sembrada_FK': idSistema
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Infraestructura_forestal', int(idSeed), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_plag_forestal): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_plag_forestal): ", e)
        return CustomException('Ocurrio un error al guardar los plaguicidas de forestal', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save machinery of forestal system
def save_maq_forestal(maquinarias, idSistema, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr
        valor_afect_maq = 0

        for maquinaria in maquinarias:
        
            edadMaq = None
            if maquinaria['anoAdquisicion']:
                edadMaq = datetime.date.today().year - int(maquinaria['anoAdquisicion'])

            insert = """
                INSERT INTO Infraestructura_forestal(cod_tipo_infraestrucrtura_FK,cod_tipo_maquinaria_FK,edad_equipo_maq,
                vlr_pesos_afectacion_maq,porc_dism_prod_maq,cod_especie_forestal_sembrada_FK) VALUES(%s,%s,%s,%s,%s,%s) 
                RETURNING cod_infraestructura_forestal
            """

            val = (4,maquinaria['idTipoMaquinariaAgricola'],edadMaq,
            str(maquinaria['valorPesos']).replace(',','') if maquinaria['valorPesos'] else None,
            maquinaria['porceDisminucion'],idSistema)

            if maquinaria['valorPesos']:
                valor_afect_maq += float(str(maquinaria['valorPesos']).replace(',','')) if maquinaria['valorPesos'] else 0

            cursor.execute(insert, val)
            idSeed = cursor.fetchone()[0]

            audit = {
                'cod_tipo_infraestrucrtura_FK': 4,
                'cod_tipo_maquinaria_FK': maquinaria['idTipoMaquinariaAgricola'],
                'edad_equipo_maq': edadMaq,
                'vlr_pesos_afectacion_maq': str(maquinaria['valorPesos']).replace(',','') if maquinaria['valorPesos'] else None,
                'porc_dism_prod_maq': maquinaria['porceDisminucion'],
                'cod_especie_forestal_sembrada_FK': idSistema
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Infraestructura_forestal', int(idSeed), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_maq_forestal): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_maq_forestal): ", e)
        return CustomException('Ocurrio un error al guardar la maquinaria de forestal', str(e)), 500
    else:
        return valor_afect_maq, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the relation between crop and its infrastructure
def save_crop_infrastructure(idCultivo, idInfraestructura, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        sql = ("""
            INSERT INTO Cultivo_Infraestructura(cod_cultivo_FK, cod_infraestructura_FK) VALUES(%s,%s) RETURNING cod_cultivo_infraestructura
        """)

        params = (
            idCultivo,
            idInfraestructura
        )

        cursor.execute(sql, params)
        idR = cursor.fetchone()[0]

        audit = {
            'cod_cultivo_FK': idCultivo,
            'cod_infraestructura_FK': idInfraestructura
        }

        #db_service2 = DatabaseService()
        #with db_service2.get_connection() as conn:
        #    with conn.cursor() as cur:
        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(idU), str(ip), 'Creación de registro', 'Cultivo_Infraestructura', int(idR), json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')
    
    except Exception as e:
        print("ERROR (eventos/database_manager/save_crop_infrastructure): ", e)
        return CustomException('Ocurrio un error al guardar la relacion entre el cultivo y la infraestructura', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save peq system
def save_peq_system(idEvento, dataEspecie, sistema, idU, connection):
    try:
        validated_pecuario, estadoValidate = validate_fields_peq(dataEspecie)
        if estadoValidate == 0:
            raise_exception('Error en validación de datos.', 'Error en validación de datos.')

        if len(validated_pecuario) > 0:
            peq = save_peq(idEvento, sistema, validated_pecuario, idU, connection)
            if peq[1] != 200:
                raise_exception(peq[0].to_dict()['message'],  peq[0].to_dict()['error'])
                
    except CustomException as e:
        print("ERROR (eventos/database_manager/save_peq_system): ", e.to_dict()['error'])
        return e, 500
    except Exception as e: 
        print("ERROR (eventos/database_manager/save_peq_system): ", e)
        return CustomException('Ocurrio un error al guardar uno de los sistemas pecuarios', str(e)), 500
    else:
        return True, 200


# Save the apiarian system
def save_apiarian(idEvento, sistema, dataEspecie, idU, connection):
    try:
        apicolas, estadoValidate = validate_fields_apiarian(dataEspecie)
        if estadoValidate == 0:
            raise_exception('Error en validación de datos.', 'Error en validación de datos.')

        cursor = connection.cursor()
        ip = request.remote_addr

        for apicola in apicolas:

            sql = ("""
                INSERT INTO Novedad_pecuaria(num_colmenas_afectadas, valor_comercial_prom_colmena,
                prod_mensual_propoleo_kg_antes_afectacion, prod_mensual_miel_litros_antes_afectacion,
                prod_mensual_jalea_litros_antes_afectacion, vlr_ingreso_prom_mensual_antes_afectacion,

                valor_pie_cria_anual, 

                ingreso_mensual_actualmente, cod_sistema_afectado_FK, afectacion_infraestructura) values(
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                ) RETURNING cod_novedad_peq
            """)

            params = (
                apicola['numColmenas'],
                str(apicola['valorColmena']).replace(',','') if apicola['valorColmena'] else None,
                apicola['propoleoMensual'],
                apicola['mielMensual'],
                apicola['jaleaMensual'],
                str(apicola['valorMensual']).replace(',', '') if apicola['valorMensual'] else None,

                apicola['valorCriaAnual'],

                str(apicola['ingresoMensual']).replace(',', '') if apicola['ingresoMensual'] else None,
                2, # Cause the apiarian system is the number 2
                apicola['afectacion']
            )

            cursor.execute(sql, params)
            idProduccionAnimal = cursor.fetchone()[0]

            audit = {
                'num_colmenas_afectadas': apicola['numColmenas'],
                'valor_comercial_prom_colmena': apicola['valorColmena'],
                'prod_mensual_propoleo_kg_antes_afectacion': apicola['propoleoMensual'],
                'prod_mensual_miel_litros_antes_afectacion': apicola['mielMensual'],
                'prod_mensual_jalea_litros_antes_afectacion': apicola['jaleaMensual'],
                'vlr_ingreso_prom_mensual_antes_afectacion': apicola['valorMensual'],
                'ingreso_mensual_actualmente': apicola['ingresoMensual'],

                'valor_pie_cria_anual': apicola['valorCriaAnual'],

                'cod_sistema_afectado_FK': 2,
                'afectacion_infraestructura': apicola['afectacion']
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Novedad_pecuaria', int(idProduccionAnimal), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

            rel = save_relation_event_system(idEvento, sistema, idProduccionAnimal, 'cod_novedad_pecuaria_apicola_FK', idU, connection)
            if rel[1] != 200:
                raise_exception(rel[0].to_dict()['message'],  rel[0].to_dict()['error'])

            pec_afec = save_peq_affectation(idProduccionAnimal, apicola['insumos'], idU, connection)
            if pec_afec[1] != 200:
                raise_exception(pec_afec[0].to_dict()['message'],  pec_afec[0].to_dict()['error'])


            macPEM = save_machineryPEM_peq(idProduccionAnimal, apicola['maquinarias'], idU, connection)
            if macPEM[1] != 200:
                raise_exception(macPEM[0].to_dict()['message'],  macPEM[0].to_dict()['error'])
            

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_apiarian): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_apiarian): ", e)
        return CustomException('Ocurrio un error al guardar el sistema apicola', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Save the peq affectation 
def save_peq_affectation(idProduccionAnimal, afectacionesPeq, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        for afectacion in afectacionesPeq:
            validated, estadoValidate = validate_peq_affectation(afectacion)
            if estadoValidate == 0:
                raise_exception('Error en validación de datos.', 'Error en validación de datos.')

            sql = ("""
                INSERT INTO Afectacion_peq(cod_tipo_insumo_FK, nombre_comercial,
                cantidad_insumos, cod_novedad_pecuaria_FK, cod_unidad_FK,
                vlr_pesos_afectacion, tipo_insumo_nom_otro) 
                VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING cod_infraestructura
            """)

            params = (
                validated['tipoInsumo'],
                validated['nombreComercial'],
                validated['cantInsumo'],
                idProduccionAnimal,
                validated['unidadMedida'] if validated['unidadMedida'] in [1,2,3,4] else 4,
                validated['valorBienes'] if validated['valorBienes'] else None,
                validated['nuevoInsumo']
            )

            cursor.execute(sql, params)

            idR = cursor.fetchone()[0]

            audit = {
                'cod_tipo_insumo_FK': validated['tipoInsumo'],
                'nombre_comercial': validated['nombreComercial'],
                'cantidad_insumos': validated['cantInsumo'],
                'cod_novedad_pecuaria_FK': idProduccionAnimal,
                'cod_unidad_FK': validated['unidadMedida'],
                'vlr_pesos_afectacion': validated['valorBienes'] if validated['valorBienes'] else None,
                'tipo_insumo_nom_otro': validated['nuevoInsumo']
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Afectacion_peq', int(idR), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_peq_affectation): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_peq_affectation): ", e)
        return CustomException('Ocurrio un error al guardar la afectacion pecuaria', str(e)), 500
    else:
        return True, 200
    finally: 
        if not cursor.closed:
            cursor.close()


# Save the machinery for BBA species in peq system
def save_machineryBBA_peq(idProduccionAnimal, maquinarias, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        for maquinaria in maquinarias:
            validated, estadoValidate = validate_machineryBBA_peq(maquinaria)
            if estadoValidate == 0:
                raise_exception('Error en validación de datos.', 'Error en validación de datos.')

            sql = ("""
                INSERT INTO Maquinaria_bba(cod_tipo_maquinaria_FK,
                nombre_maquinaria, vlr_pesos_afectacion, cod_novedad_pecuaria_FK)
                VALUES(%s,%s,%s,%s) RETURNING cod_maquinaria_bba
            """)
            
            # VERIFICAR SI ESTO SIGUE FALLANDO
            params = (
                validated['tipoMaquinariaBba'] if validated['tipoMaquinariaBba'] != '' else None,
                validated ['nombreMaquinariaBba'],
                validated['valorReparacionBba'] if validated['valorReparacionBba'] and validated['valorReparacionBba'] != '' else None,
                idProduccionAnimal
            )

            cursor.execute(sql, params)
            idR = cursor.fetchone()[0]

            audit = {
                'cod_tipo_maquinaria_FK': validated['tipoMaquinariaBba'],
                'nombre_maquinaria': validated ['nombreMaquinariaBba'],
                'vlr_pesos_afectacion': validated['valorReparacionBba'] if validated['valorReparacionBba'] else None,
                'cod_novedad_pecuaria_FK': idProduccionAnimal
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Maquinaria_bba', int(idR), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except Exception as e:
        print("ERROR (eventos/database_manager/save_machineryBBA_peq): ", e)
        return CustomException('Ocurrio un error al guardar la maquinaria de especies mayores', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the machinery for PEM species in peq system
def save_machineryPEM_peq(idProduccionAnimal, maquinarias, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        for maquinaria in maquinarias:
            validated, estadoValidate= validate_machineryPEM_peq(maquinaria)
            if estadoValidate == 0:
                raise_exception('Error en validación de datos.', 'Error en validación de datos.')

            sql = ("""
                INSERT INTO Maquinaria_pem(cod_tipo_maquinaria_FK,
                nombre_marca_bien, vlr_pesos_afectacion, 

                fch_adquisicion_bien,

                cod_novedad_pecuaria_FK)
                VALUES(%s,%s,%s,%s,%s) RETURNING cod_maquinaria_pem
            """)

            params = (
                validated['tipoMaquinariaPem'],
                validated['nombreMarcaPem'],
                validated['valorReparacionPem'] if validated['valorReparacionPem'] else None,

                validated['fechaAdquisicion'],

                idProduccionAnimal
            )
            cursor.execute(sql, params)
            idR = cursor.fetchone()[0]

            audit = {
                'cod_tipo_maquinaria_FK': validated['tipoMaquinariaPem'],
                'nombre_marca_bien': validated['nombreMarcaPem'],
                'vlr_pesos_afectacion': validated['valorReparacionPem'] if validated['valorReparacionPem'] else None,
                'fch_adquisicion_bien': validated['fechaAdquisicion'],
                'cod_novedad_pecuaria_FK': idProduccionAnimal
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Maquinaria_pem', int(idR), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except Exception as e:
        print("ERROR (eventos/database_manager/save_machineryPEM_peq): ", e)
        return CustomException('Ocurrio un error al guardar la maquinaria de especies menores', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the infrastructure for peq system
def save_infrastructure_peq(idProduccionAnimal, infraestructuras, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        for infraestructura in infraestructuras:
            validated, estadoValidate = validate_infrastructure_peq(infraestructura)
            if estadoValidate == 0:
                raise_exception('Error en validación de datos.', 'Error en validación de datos.')

            sql = ("""
                INSERT INTO Infraestructura_pecuario(cod_tipo_activo_FK,
                nombre_equipo, fecha_adquisicion_bien, precio_pagado,
                vlr_invertido_reparacion, cod_novedad_pecuario_FK,
                cod_tipo_construccion_FK, area_m2_construccion_afectada,
                vlr_invertido_re_construccion, tiempo_realizar_reparacion_meses)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_infraestructura_pecuario
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
            idR = cursor.fetchone()[0]

            audit = {
                'cod_tipo_activo_FK': validated['tipActivo'],
                'nombre_equipo': validated['nombreEquipo'],
                'fecha_adquisicion_bien': validated['fechaAdquisicion'],
                'precio_pagado': validated['valorPagado'],
                'vlr_invertido_reparacion': validated['valorReponer'],
                'cod_novedad_pecuario_FK': idProduccionAnimal,
                'cod_tipo_construccion_FK': validated['tipAfecta'],
                'area_m2_construccion_afectada': validated['areaAfectada'],
                'vlr_invertido_re_construccion': validated['valorReparacion'],
                'tiempo_realizar_reparacion_meses': validated['mesesReparacion']
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Infraestructura_pecuario', int(idR), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except Exception as e:
        print("ERROR (eventos/database_manager/save_infrastructure_peq): ", e)
        return CustomException('Ocurrio un error al guardar la infraestructura de pecuario', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the peq system
def save_peq(idEvento, sistema, pecuarios, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr


        for pecuario in pecuarios:

            sql = ("""
                INSERT INTO Novedad_pecuaria(cod_sistema_afectado_fk, nombre_raza, num_total_anim_explotacion,
                peso_prom_animal_explotacion, cod_unidad_reporte_FK, cod_equiva_kg_FK, precio_prom_x_animal,
                area_usada_animales, cod_unidad_area_FK, fch_inicio_actividad_productiva,
                fch_inicio_evento, num_animales_enfermos_afectados, num_animales_hembra_muertos,
                num_animales_macho_muertos, edad_promedio_meses_anim_muerto, cod_tipo_producto_FK,
                prod_mensual_antes_afectacion, prod_mensual_actual_potencial_afectacion, cod_unidad_reporte1_FK, cod_equiva1_kg_carga,
                precio_venta_und_producto, 

                peso_kg_und_producto, 

                huevos_producto_diferentes_avicola, cant_meses_recuperar_capac_perdida, afectacion_infraestructura, sistema_afectado_nom_otro, peso_prom_animal_explotacion_nom_otro,
                eqv_kg_unidad_reportar_otro, equivalencia_kg_carga, unidad_area_reporte_otro, nombre_producto_obtenido_otro, equivalencia1_kg_carga, kilos_x_unidad_datos_produccion,
                nombre_otra_unidad_datos_produccion, eqv_kilos_otra_unidad_datos_produccion) 
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_novedad_peq
            """)

            afectac_exist = False
            if len(pecuario['dataMaquinaria']) > 0 or len(pecuario['dataInfraestructura']) > 0:
                afectac_exist = True

            params = (
                pecuario['sistema'],
                pecuario['nombreRaza'],
                pecuario['numAnimal'],
                pecuario['pesoAnimal'],
                pecuario['uniMedidaAnimal'],
                pecuario['peso'],

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
                pecuario['pesoProduccion'],
                pecuario['valorVentaProducto'],

                pecuario['pesoPromedioUnidad'],

                pecuario['huevosAvicola'], 
                pecuario['mesesRecuperarPecuaria'],
                afectac_exist,
                pecuario['sistemaNuevo'] ,
                pecuario['nombreUnidadMedidaNuevo'],
                pecuario['unidadMedidaNuevo'],
                pecuario['pesoNuevo'],
                pecuario['unidadAreaNuevo'],
                pecuario['tipoProductoNuevo'],
                pecuario['pesoProduccionNuevo'],
                pecuario['kilosUnidad'],
                pecuario['nombreUnidadProduccionNueva'],
                pecuario['unidadProduccionNueva']
            )

            cursor.execute(sql, params)
            idProduccionAnimal = cursor.fetchone()[0]

            audit = {
                'cod_sistema_afectado_fk': pecuario['sistema'], 
                'nombre_raza': pecuario['nombreRaza'], 
                'num_total_anim_explotacion': pecuario['numAnimal'], 
                'peso_prom_animal_explotacion': pecuario['pesoAnimal'], 
                'cod_unidad_reporte_FK': pecuario['uniMedidaAnimal'], 
                'cod_equiva_kg_FK': pecuario['peso'], 
                'precio_prom_x_animal': pecuario['valorAnimal'], 
                'area_usada_animales': pecuario['areaAnimal'], 
                'cod_unidad_area_FK': pecuario['unidadArea'], 
                'fch_inicio_actividad_productiva': pecuario['fechaProduccion'], 
                'fch_inicio_evento': pecuario['fechaIniEvento'], 
                'num_animales_enfermos_afectados': pecuario['numAnimalEnfermos'], 
                'num_animales_hembra_muertos': pecuario['numAnimalHembMuerto'], 
                'num_animales_macho_muertos': pecuario['numAnimalMachMuerto'], 
                'edad_promedio_meses_anim_muerto': pecuario['edadAnimal'], 
                'cod_tipo_producto_FK': pecuario['tipoProducto'], 
                'prod_mensual_antes_afectacion': pecuario['produMensualAfectacion'], 
                'prod_mensual_actual_potencial_afectacion': pecuario['produPotencial'], 
                'cod_unidad_reporte1_FK': pecuario['unidadProdccion'], 
                'cod_equiva1_kg_carga': pecuario['pesoProduccion'], 
                'precio_venta_und_producto': pecuario['valorVentaProducto'], 

                'peso_kg_und_producto': pecuario['pesoPromedioUnidad'],

                'huevos_producto_diferentes_avicola': pecuario['huevosAvicola'], 
                'cant_meses_recuperar_capac_perdida':  pecuario['mesesRecuperarPecuaria'], 
                'afectacion_infraestructura': afectac_exist, 
                'sistema_afectado_nom_otro': pecuario['sistemaNuevo'], 
                'peso_prom_animal_explotacion_nom_otro': pecuario['nombreUnidadMedidaNuevo'], 
                'eqv_kg_unidad_reportar_otro': pecuario['unidadMedidaNuevo'], 
                'equivalencia_kg_carga': pecuario['pesoNuevo'], 
                'unidad_area_reporte_otro': pecuario['unidadAreaNuevo'], 
                'nombre_producto_obtenido_otro': pecuario['tipoProductoNuevo'], 
                'equivalencia1_kg_carga': pecuario['pesoProduccionNuevo'] ,
                'kilos_x_unidad_datos_produccion': pecuario['kilosUnidad'],
                'nombre_otra_unidad_datos_produccion': pecuario['nombreUnidadProduccionNueva'],
                'eqv_kilos_otra_unidad_datos_produccion': pecuario['unidadProduccionNueva']
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Novedad_pecuaria', int(idProduccionAnimal), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')


            rel = save_relation_event_system(idEvento, sistema, idProduccionAnimal, 'cod_novedad_pecuaria_FK', idU, connection)
            if rel[1] != 200:
                raise_exception(rel[0].to_dict()['message'],  rel[0].to_dict()['error'])

            peq_afec = save_peq_affectation(idProduccionAnimal, pecuario['dataInsumos'], idU, connection)
            if peq_afec[1] != 200:
                raise_exception(peq_afec[0].to_dict()['message'],  peq_afec[0].to_dict()['error'])

            macBBA = save_machineryBBA_peq(idProduccionAnimal, pecuario['dataMaquinaria'], idU, connection)
            if macBBA[1] != 200:
                raise_exception(macBBA[0].to_dict()['message'],  macBBA[0].to_dict()['error'])

            macPEM = save_machineryPEM_peq(idProduccionAnimal, pecuario['dataMaquinaria'], idU, connection)
            if macPEM[1] != 200:
                raise_exception(macPEM[0].to_dict()['message'],  macPEM[0].to_dict()['error'])

            infra = save_infrastructure_peq(idProduccionAnimal, pecuario['dataInfraestructura'], idU, connection)
            if infra[1] != 200:
                raise_exception(infra[0].to_dict()['message'],  infra[0].to_dict()['error'])

            var_costs = save_variable_costs_peq(idProduccionAnimal, pecuario['costosVariables'], idU, connection)
            if var_costs[1] != 200:
                raise_exception(var_costs[0].to_dict()['message'],  var_costs[0].to_dict()['error'])

            nonvar_costs = save_nonvariable_costs_peq(idProduccionAnimal, pecuario['costosFijos'], idU, connection)
            if nonvar_costs[1] != 200:
                raise_exception(nonvar_costs[0].to_dict()['message'],  nonvar_costs[0].to_dict()['error'])

            PPAE = 0
            if pecuario['uniMedidaAnimal'] == 1:
                PPAE = float(pecuario['pesoAnimal']) * 1000
            elif pecuario['uniMedidaAnimal'] == 2:
                PPAE = float(pecuario['pesoAnimal'])
            elif pecuario['uniMedidaAnimal'] == 3:
                PPAE = float(pecuario['pesoAnimal']) * 11.34
            elif pecuario['uniMedidaAnimal'] == 4:
                if pecuario['peso'] != 6:
                    sql = ("SELECT cod_equiv_carga AS codEquivCarga, equiv_carga_kg AS eqvCargaKg " +
                    "FROM Equivalencia_carga")
                
                    cursor.execute(sql)
                    for row in cursor.fetchall():
                        if int(row[0]) == int(pecuario['peso']):
                            PPAE = float(row[1])
                            break  
                else:
                    PPAE = float(pecuario['pesoNuevo'])
            elif pecuario['uniMedidaAnimal'] == 5:
                PPAE = float(pecuario['pesoAnimal']) * 0.453
            elif pecuario['uniMedidaAnimal'] == 8:
                PPAE = float(pecuario['unidadMedidaNuevo'])

            variables = {
                # Numero de animales hembra muertos
                'NAHM': int(pecuario['numAnimalHembMuerto']) if pecuario['numAnimalHembMuerto'] != None else 0,
                # Numero de animales macho muertos
                'NAMM': int(pecuario['numAnimalMachMuerto']) if pecuario['numAnimalMachMuerto'] != None else 0,
                # Peso promedio animales explotacion
                'PPAE': PPAE,
                # Precio promedio por animal
                'PPPA': float(pecuario['valorAnimal']) if pecuario['valorAnimal'] != None else 0,
                # Produccion mensual antes afectacion
                'PMAF': float(pecuario['produMensualAfectacion']) if pecuario['produMensualAfectacion'] != None else 0,
                # Produccion mensual actual potencial afectacion
                'PMAPA': float(pecuario['produPotencial']) if pecuario['produPotencial'] != None else 0,
                # Valor costos variables 
                'VCVP': var_costs[0],
                # Gasto incurrido costos fijos
                'GICF': nonvar_costs[0],
                # Precio venta unidad producto
                'PVUP': float(pecuario['valorVentaProducto']) if pecuario['valorVentaProducto'] != None else 0,
            }

            form = save_formulas(idEvento, variables, 3, idU, connection)
            if form[1] != 200:
                raise_exception(form[0].to_dict()['message'],  form[0].to_dict()['error'])

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_peq): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_peq): ", e)
        return CustomException('Ocurrio un error al guardar el sistema pecuario', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the variable costs from peq system
def save_variable_costs_peq(idProduccionAnimal, costosVariables, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        costos = 0
        for costo in costosVariables:
            #validated = validateCostoVariablPecuario(costo)
            sql = ("""
                INSERT INTO Costos_variables_pecuario(cod_actividad_FK,
                valor, cod_novedad_peq_FK) 
                VALUES(%s, %s, %s) RETURNING cod_costo_variable
            """)

            params = (
                costo["tipoCosto"],
                costo["valor"],
                idProduccionAnimal
            )

            costos += float(costo["valor"]) if costo["valor"] else 0
            cursor.execute(sql, params)

            idR = cursor.fetchone()[0]

            audit = {
                'cod_actividad_FK': costo["tipoCosto"],
                'valor': costo["valor"],
                'cod_novedad_peq_FK': idProduccionAnimal
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Costos_variables_pecuario', int(idR), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except Exception as e:
        print("ERROR (eventos/database_manager/save_variable_costs_peq): ", e)
        return CustomException('Ocurrio un error al guardar los costos variables de pecuario', str(e)), 500
    else:
        return costos, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save non variable costs from peq system
def save_nonvariable_costs_peq(idProduccionAnimal, costosFijos, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        costos = 0
        for costo in costosFijos:
            #validated = validateCostoFijo(costo)
            sql = ("""
                INSERT INTO Costos_fijos_pecuarios(cod_rubro_FK, 
                gasto_incurrido, cod_novedad_peq_FK)
                VALUES(%s,%s,%s) RETURNING cod_costo_fijo_prod
            """)

            params = (
                costo["tipoCosto"],
                costo["valor"],
                idProduccionAnimal
            )
            costos += float(costo["valor"]) if costo["valor"] else 0
            cursor.execute(sql, params)

            idR = cursor.fetchone()[0]

            audit = {
                'cod_rubro_FK': costo["tipoCosto"],
                'gasto_incurrido': costo["valor"],
                'cod_novedad_peq_FK': idProduccionAnimal
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Costos_fijos_pecuarios', int(idR), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')
            
    except Exception as e:
        print("ERROR (eventos/database_manager/save_nonvariable_costs_peq): ", e)
        return CustomException('Ocurrio un error al guardar los costos fijos de pecuario', str(e)), 500
    else:
        return costos, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save fishing event
def save_fishing_system(idEvento, dataEspecie, sistema, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        for fishing in dataEspecie:
            validated = validate_fields_fishing(fishing)
            
            sql = ("""
                INSERT INTO Novedad_pesquera(
                    principales_especies_explotadas, embarcaciones_afectadas, instalaciones_afectadas,
                    redes_afectadas, num_redes, vlr_pesos_redes_afectadas, num_faenas_pesca, faenas_pesca,
                    vlr_prom_recibido_venta_peces_faena, instalacion_maquinaria_afectada, puerto_desembarque_pesca
                ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_novedad_pesq
            """)

            val = (
                validated['especieExplotada'], validated['embarcacionAfectada'], validated['instalacionAfectada'],
                validated['redesAfectadas'], validated['numeroRedes'], 
                validated['valorRedes'], 
                validated['numeroFaenas'],
                validated['cantidadFaenasMes'], 
                validated['valorVentaPeces'], 
                validated['maquinariaAfectada'], validated['puertoDesembarque']
            )

            cursor.execute(sql, val)

            idFish = cursor.fetchone()[0]

            audit = {
               'principales_especies_explotadas': validated['especieExplotada'],
               'embarcaciones_afectadas': validated['embarcacionAfectada'],
               'instalaciones_afectadas': validated['instalacionAfectada'],
               'redes_afectadas': validated['redesAfectadas'],
               'num_redes': validated['numeroRedes'],
               'vlr_pesos_redes_afectadas': validated['valorRedes'],
               'num_faenas_pesca': validated['numeroFaenas'],
               'faenas_pesca': validated['cantidadFaenasMes'],
               'vlr_prom_recibido_venta_peces_faena': validated['valorVentaPeces'],
               'instalacion_maquinaria_afectada': validated['maquinariaAfectada'],
               'puerto_desembarque_pesca': validated['puertoDesembarque']
            }
            
            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Novedad_pesquera', int(idFish), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')


            rel_event = save_relation_event_system(idEvento, sistema, idFish, 'cod_novedad_pesquera_FK', idU, connection)
            if rel_event[1] != 200:
                raise_exception(rel_event[0].to_dict()['message'],  rel_event[0].to_dict()['error'])

            rel = save_relation_fishing_typefishing(idFish,validated['tipoPesqueria'], idU, connection)
            if rel[1] != 200:
                raise_exception(rel[0].to_dict()['message'],  rel[0].to_dict()['error'])
            
            emb = save_emb(idFish, validated['embarcaciones'], idU, connection)
            if emb[1] != 200:
                raise_exception(emb[0].to_dict()['message'],  emb[0].to_dict()['error'])

            net = save_networks_affected(idFish, validated, idU, connection)
            if net[1] != 200:
                raise_exception(net[0].to_dict()['message'],  net[0].to_dict()['error'])

            inf = save_infrastructure_fishing(idFish, validated['maquinarias'], idU, connection)
            if inf[1] != 200:
                raise_exception(inf[0].to_dict()['message'],  inf[0].to_dict()['error'])

            variables = {
                # Numero faenas pesca
                'NFP': int(validated['numeroFaenas']) if validated['numeroFaenas'] != None else 0,
                # Valor promedio recibido venta de peces faena
                'VPRVPF': int(validated['valorVentaPeces']) if validated['valorVentaPeces'] != None else 0,
                # Faenas pesca
                'FP': int(validated['cantidadFaenasMes']) if validated['cantidadFaenasMes'] != None else 0,
            }

            form = save_formulas(idEvento, variables, 4, idU, connection)
            if form[1] != 200:
                raise_exception(form[0].to_dict()['message'],  form[0].to_dict()['error'])

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_fishing_system): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_fishing_system): ", e)
        return CustomException('Ocurrio un error al guardar el evento pesquero', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the relation between the fishing system affected and the fishing type
def save_relation_fishing_typefishing(idFish,fishing_type, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        for id_fishing in fishing_type:
            sql = ( """
                INSERT INTO Novedad_pesquera_tipo_pes(cod_novedad_pesquera_FK, cod_tipo_pesquera_FK)
                VALUES(%s,%s) RETURNING cod_nov_pesq_tip_pes
            """)

            val = (idFish, id_fishing)

            cursor.execute(sql, val)

            idR = cursor.fetchone()[0]

            audit = {
                'cod_novedad_pesquera_FK': idFish,
                'cod_tipo_pesquera_FK': id_fishing
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Novedad_pesquera', int(idR), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')


    except Exception as e:
        print("ERROR (eventos/database_manager/save_relation_fishing_typefishing): ", e)
        return CustomException('Ocurrio un error al guardar la relacion entre el sistema pesquero y los tipos de pesqueria', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save the embarkations
def save_emb(idFish, embarcaciones, idU, connection):
    cursor = None
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        for embarcacion in embarcaciones:
            validated = validate_embarkations(embarcacion)
            sql = ("""
                INSERT INTO Tipo_embarcacion(tipo_embarcacion) VALUES('{}') RETURNING cod_tipo_embarcacion
            """.format(validated['tipoEmbarcacion']))

            cursor.execute(sql)

            idEmb = cursor.fetchone()[0]

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Tipo_embarcacion', int(idEmb), json.dumps({'tipo_embarcacion': validated['tipoEmbarcacion']})
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')


            sql = ("""
                INSERT INTO Embarcacion(cod_tipo_embarcacion_FK, patente_embarcacion, eslora_mts, valor_afectacion_pesos,
                observaciones, 
                cod_material_embarcacion_fk,
                cod_tipo_propulsion_fk,
                edad,
                cod_novedad_pesquera_FK) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_embarcacion
            """)

            val = (idEmb, 
                validated['patenteEmbarcacion'], 
                validated['esloraEmbarcacion'], 
                validated['valorEmbarcacion'],
                validated['observacionEmbarcacion'], 
                validated['material'],
                validated['propulsion'],
                validated['edad'],
                idFish)

            cursor.execute(sql, val)

            idR = cursor.fetchone()[0]

            audit = {
                'cod_tipo_embarcacion_FK': idEmb,
                'patente_embarcacion': validated['patenteEmbarcacion'],
                'eslora_mts': validated['esloraEmbarcacion'],
                'valor_afectacion_pesos': validated['valorEmbarcacion'],
                'observaciones': validated['observacionEmbarcacion'],
                'cod_material_embarcacion_fk': validated['material'],
                'cod_tipo_propulsion_fk': validated['propulsion'],
                'edad': validated['edad'],
                'cod_novedad_pesquera_FK': idFish
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Embarcacion', int(idR), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_emb): ", e.to_dict()['error'])
        return e, 500  
    except Exception as e:
        print("ERROR (eventos/database_manager/save_emb): ", e)
        return CustomException('Ocurrio un error al guardar las embarcaciones', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Save the affected networks of pesq system
def save_networks_affected(idF, pesq, idU, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        sql = ("""
            INSERT INTO Infraestructura_pesquera(cod_tipo_red_fk, nombre_equipo, fecha_adquisicion_bien, precio_pagado, cod_tipo_perdida_fk, cod_novedad_pesquera_FK)
            VALUES(%s,%s,%s,%s,%s,%s) RETURNING cod_infraestructura_pesquera
        """)

        val = (pesq['tipoRedes'], pesq['marcaRed'], pesq['fechaAdquisicion'], pesq['valorRedes'], pesq['tipoPerdida'], idF)

        cursor.execute(sql, val)

        id_infra = cursor.fetchone()[0]

        audit = {
            'cod_tipo_red_fk': pesq['tipoRedes'],
            'nombre_equipo': pesq['marcaRed'],
            'fecha_adquisicion_bien': pesq['fechaAdquisicion'],
            'precio_pagado': pesq['valorRedes'],
            'cod_tipo_perdida_fk': pesq['tipoPerdida']
        }

        sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(idU), str(ip), 'Creación de registro', 'Infraestructura_pesquera', int(id_infra), json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_networks_affected): ", e.to_dict()['error'])
        return e, 500  
    except Exception as e:
        print("ERROR (eventos/database_manager/save_networks_affected): ", e)
        return CustomException('Ocurrio un error al guardar las redes afectadas', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()
    

# Save the infrastructure from fishing systm
def save_infrastructure_fishing(idFish, infrastructures, idU, connection):
    cursor = None
    try: 
        cursor = connection.cursor()
        ip = request.remote_addr

        for infrastructure in infrastructures:
            validated = validate_infrastructure_fishing(infrastructure)

            sql = ("""
                INSERT INTO Infraestructura_pesquera(cod_tipo_activo_FK, nombre_equipo, fecha_adquisicion_bien, precio_pagado,
                vlr_invertido_reparacion, cod_novedad_pesquera_FK, cod_tipo_construccion_FK, area_metros_cuadrados_construccion_afectada,
                vlr_invertido_reconstruccion, tiempo_necesario_reconstruccion, cod_tipo_red_fk, cod_tipo_perdida_fk) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_infraestructura_pesquera
            """)

            val = (validated['activoProductivo'], validated['nombreEquipo'], validated['fechaAdquisicion'], 
                validated['valorActivo'],
                validated['valorReponer'], 
                idFish, validated['tipoConstruccion'], validated['areaAfectada'], 
                validated['valorInvertidoAdecuacion'],
                validated['mesesReconstruccion'], 
                validated['tipoRedes'],
                validated['tipoPerdida'])

            cursor.execute(sql, val)

            idR = cursor.fetchone()[0]

            audit = {
                'cod_tipo_activo_FK': validated['activoProductivo'],
                'nombre_equipo': validated['nombreEquipo'],
                'fecha_adquisicion_bien': validated['fechaAdquisicion'],
                'precio_pagado': validated['valorActivo'],
                'vlr_invertido_reparacion': validated['valorReponer'],
                'cod_novedad_pesquera_FK': idFish,
                'cod_tipo_construccion_FK': validated['tipoConstruccion'],
                'area_metros_cuadrados_construccion_afectada': validated['areaAfectada'],
                'vlr_invertido_reconstruccion': validated['valorInvertidoAdecuacion'],
                'tiempo_necesario_reconstruccion': validated['mesesReconstruccion'],
                'cod_tipo_red_fk': validated['tipoRedes'],
                'cod_tipo_perdida_fk': validated['tipoPerdida']
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Creación de registro', 'Infraestructura_pesquera', int(idR), json.dumps(audit)
            )

            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except Exception as e:
        print("ERROR (eventos/database_manager/save_infrastructure_fishing): ", e)
        return CustomException('Ocurrio un error al guardar las infraestructura de pesquero', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Save tracing event
def save_tracing_event(idEvento, observacion, idUsuario, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr
        mail = get_email_service()

        # Fecha actual
        fechaActual = datetime.datetime.utcnow() - datetime.timedelta(minutes=300)

        obj, estadoValidate = validate_tracing_event(idEvento, observacion)

        if estadoValidate == 0:
            raise_exception('Error en validación de datos.', 'Error en validación de datos.')

        sqlInsert = ("""
        INSERT INTO evento_seguimiento (observacion, cod_evento_FK, fecha_registro, cod_usuario_FK)
        VALUES (%s,%s,%s,%s) RETURNING cod_evento_seguimiento
        """)
        val = (obj['observacion'], obj['idEvento'], fechaActual, idUsuario)

        cursor.execute(sqlInsert, val)

        idR = cursor.fetchone()[0]

        res = {
            'id': idR,
        }

        audit = {
            'observacion': obj['observacion'], 
            'cod_evento_FK':  obj['idEvento'], 
            'fecha_registro':  str(fechaActual.date()), 
            'cod_usuario_FK':  idUsuario, 
        }

        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(idUsuario), str(ip), 'Creación de registro', 'Evento_seguimiento', int(idR), json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

        # Send notification to validator
        sql = ("""
            INSERT INTO Notificaciones(titulo, descripcion, id_usuario, id_creador) VALUES(%s, 
            CONCAT('Seguimiento creado por el usuario: ', (SELECT usuario FROM Usuarios WHERE id = %s), ', fecha: {}, contenido: ', %s),
            (SELECT usuario FROM validador_municipal  JOIN Evento on cod_municipio_fk = cod_mun_fk WHERE cod_evento = %s), %s) 
            RETURNING id_notificacion, titulo, descripcion, id_usuario
        """.format(str(fechaActual.date())))

        val = ("Creación de seguimiento", int(idUsuario), str(obj['observacion']), idEvento, int(idUsuario))
        cursor.execute(sql, val)

        values = cursor.fetchall()[0]

        audit = {
            'titulo': values[1],
            'descripcion': values[2],
            'id_usuario': values[3],
            'id_creador': idUsuario
        }

        sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

        val = (
            idUsuario, str(ip), 'Creación de registro', 'Notificaciones', values[0], json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')
        
         # Send notification to event creator
        sql = ("""
            INSERT INTO Notificaciones(titulo, descripcion, id_usuario, id_creador) VALUES(%s, 
            CONCAT('Seguimiento creado por el usuario: ', (SELECT usuario FROM Usuarios WHERE id = %s), ', fecha: {}, contenido: ', %s),
            (SELECT id FROM Usuarios JOIN Evento ON cod_encuestador_fk = id WHERE cod_evento = %s), %s) 
            RETURNING id_notificacion, titulo, descripcion, id_usuario
        """.format(str(fechaActual.date())))

        val = ("Creación de seguimiento", int(idUsuario), str(obj['observacion']), idEvento, int(idUsuario))
        cursor.execute(sql, val)

        values = cursor.fetchall()[0]

        audit = {
            'titulo': values[1],
            'descripcion': values[2],
            'id_usuario': values[3],
            'id_creador': int(idUsuario)
        }

        sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

        val = (
            idUsuario, str(ip), 'Creación de registro', 'Notificaciones', values[0], json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

        # Sending the email to the validator
        sql = ("""
           SELECT u.email FROM Usuarios u JOIN Validador_municipal vm ON vm.usuario = u.id JOIN Evento e ON e.cod_municipio_fk = vm.cod_mun_fk 
           WHERE cod_evento = %s
        """)
        
        val = ([obj['idEvento']])
        cursor.execute(sql,val)

        email = cursor.fetchone()[0]
        
        sended = send_notification_email(Config.EMAIL_SENDER, email, values[1], values[2], mail)
        if sended[1] != 200:
            raise_exception(sended[0].to_dict()['message'],  sended[0].to_dict()['error'])
        
        # Seding email to the event creator
        sql = ("""
            SELECT email FROM Usuarios JOIN Evento ON cod_encuestador_fk = id WHERE cod_evento = %s
        """)

        val = ([obj['idEvento']])

        cursor.execute(sql,val)
        email = cursor.fetchone()[0]

        sended = send_notification_email(Config.EMAIL_SENDER, email, values[1], values[2], mail)
        if sended[1] != 200:
            raise_exception(sended[0].to_dict()['message'],  sended[0].to_dict()['error'])
    
    except CustomException as e:
        print("ERROR (eventos/database_manager/save_tracing_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_tracing_event): ", e)
        return CustomException('Ocurrio un error al guardar el seguimiento del evento', str(e)), 500
    else:
        return res, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Saves the attachements in the event
def save_attached(idEvento, ruta, filename, id_user, connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        sql = ("""
            INSERT INTO Evento_adjunto(ruta, nombre_archivo, cod_evento_fk) VALUES(%s,%s,%s)
            RETURNING cod_evento_adjunto
        """)

        val = (ruta, filename, idEvento)

        cursor.execute(sql, val)
        idR = cursor.fetchone()[0]
        
        res = {
            'id': idR
        }

        audit = {
            'ruta': ruta,
            'nombre_archivo': filename,
            'cod_evento_fk': idEvento
        }

        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(id_user), str(ip), 'Creación de registro', 'Evento_adjunto', int(idR), json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_attached): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_attached): ", e)
        return CustomException('Ocurrio un error al guardar el archivo adjunto', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()

# Save the attached files in the tracing
def save_attached_tracing(idSeguimiento, ruta, filename, idUsuario, connection):
    try:
        # Fecha actual
        fechaActual = datetime.datetime.utcnow() - datetime.timedelta(minutes=300)
        cursor = connection.cursor()
        ip = request.remote_addr
        
        obj, estadoValidate = validate_attached_tracing(idSeguimiento, ruta, filename)

        if estadoValidate == 0:
            raise_exception('Error en validación de datos.', 'Error en validación de datos.')

        sqlInsert = ("""
        INSERT INTO evento_seguimiento_adju (ruta, nombre_archivo, cod_evento_seguimiento_FK)
        VALUES (%s,%s,%s) RETURNING cod_evento_seguimiento_adju
        """)
        val = (obj['ruta'], obj['filename'], obj['idSeguimiento']['id'])

        cursor.execute(sqlInsert, val)
        idR = cursor.fetchone()[0]

        audit = {
            'ruta': obj['ruta'], 
            'nombre_archivo':  obj['filename'], 
            'cod_evento_seguimiento_FK': obj['idSeguimiento']['id'], 
        }

        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(idUsuario), str(ip), 'Creación de registro', 'Evento_seguimiento_adju', int(idR), json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

    except CustomException as e:
        print("ERROR (eventos/database_manager/save_attached_tracing): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/save_attached_tracing): ", e)
        return CustomException('Ocurrio un error al guardar el archivo adjunto', str(e)), 500
    else:
        return True, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search the tracing
def search_tracing(idEvento, connection):
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
        WHERE a.cod_evento_FK = '{}'
        ORDER BY cod_evento_seguimiento DESC
        """.format(idEvento))

        cursor.execute(sqlInsert)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))


        att_traicings = attached_tracings(results, connection)
        if att_traicings[1] != 200:
            raise_exception(att_traicings[0].to_dict()['message'],  att_traicings[0].to_dict()['error'])

    except CustomException as e:
        print("ERROR (eventos/database_manager/search_tracing): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/search_tracing): ", e)
        return CustomException('Ocurrio un error al buscar los seguimientos', str(e)), 500
    else:
        return att_traicings[0], 200
    finally:
        if not cursor.closed:
            cursor.close()


# get the attachements of the event
def attached_event(records, connection):
    atts = []
    try:
        cursor = connection.cursor()
        for record in records:
            sql = ("""
                SELECT cod_evento_adjunto, ruta, 
                nombre_archivo, cod_evento_fk
                FROM evento_adjunto
                WHERE cod_evento_fk = %s
            """)

            val = ([record['cod_evento']])
            cursor.execute(sql, val)

            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            record['adjuntos'] = results
            atts.append(record)

    except Exception as e:
        print("ERROR (eventos/database_manager/attached_event):", e)
        return CustomException('Ocurrió un error al obtener los adjuntos del evento', str(e)), 500
    else:
        return atts, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Search the attached tracings from an event
def attached_tracings(records, connection):
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
            
            cursor.execute(sql, [record['cod_evento_seguimiento']])

            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            record['adjuntos'] = results
            seguimientos.append(record)

    except Exception as e:
        print("ERROR (eventos/database_manager/attached_tracings): ", e)
        return CustomException('Ocurrio un error al obtener los adjuntos de los seguimientos', str(e)), 500
    else:
        return seguimientos, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search direct costs per activity
def direct_costs_activity(idEvento, connection):
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

        cursor.execute(sql, [idEvento])

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))


    except Exception as e:
        print("ERROR (eventos/database_manager/direct_costs_activity): ", e)
        return CustomException('Ocurrio un error al obtener los costos directos por actividad', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search indirect costs per heading 
def indirect_costs_heading(idEvento, connection):
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

        cursor.execute(sql, [idEvento])

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except Exception as e:
        print("ERROR (eventos/database_manager/indirect_costs_heading): ", e)
        return CustomException('Ocurrio un error al obtener los costos indirectos', str(e)), 500
    else:  
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search costs per infrastructure type
def value_infrastructure_type(idEvento, connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/value_infrastructure_type): ", e)
        return CustomException('Ocurrio un error al obtener los costos por tipo de infraestructura', str(e)), 500
    else:
        return results, 200
    finally: 
        if not cursor.closed:
            cursor.close()


# Search percetnage of forest economical loss
def forest_economical_loss(idEvento, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
        SELECT
        a.cod_evento_FK,
        TO_CHAR(COALESCE(a.valor,0), 'l99999999999999D99') AS valor
        FROM indicador_valor a
        JOIN indicador b ON (b.cod_indicador = a.cod_indicador_fk)
        JOIN Evento e ON (e.cod_evento = a.cod_evento_FK)
        WHERE a.cod_evento_FK = %s AND b.siglas = 'PEmf' and e.validado = true""")
        cursor.execute(sql, [idEvento])

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except Exception as e:
        print("ERROR (eventos/database_manager/forest_economical_loss): ", e)
        return CustomException('Ocurrio un error al obtner el porcentaje de la perdida economica forestal', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search the value of the forest economical loss
def value_forest_economical_loss(idEvento, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
        SELECT
        a.cod_evento_FK,
        TO_CHAR(COALESCE(a.valor,0), 'l99999999999999D99') AS valor
        FROM indicador_valor a
        JOIN indicador b ON (b.cod_indicador = a.cod_indicador_fk)
        JOIN Evento e ON (e.cod_evento = a.cod_evento_FK)
        WHERE a.cod_evento_FK = %s AND b.siglas = 'VPEmf' and e.validado = true""")

        cursor.execute(sql, [idEvento])

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except Exception as e:
        print("ERROR (eventos/database_manager/value_forest_economical_loss): ", e)
        return CustomException('Ocurrio un error al obtener el costo de la perdida economica forestal', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search percentage of estimated production loss
def estimated_production_loss(idEvento, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
        SELECT
        a.cod_evento_FK,
        TO_CHAR(COALESCE(a.valor,0), 'l99999999999999D99') AS valor
        FROM indicador_valor a
        JOIN indicador b ON (b.cod_indicador = a.cod_indicador_fk)
        JOIN Evento e ON (e.cod_evento = a.cod_evento_FK)
        WHERE a.cod_evento_FK = %s AND b.siglas = 'PPRmf' and e.validado = true""")

        cursor.execute(sql, [idEvento])

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except Exception as e:
        print("ERROR (eventos/database_manager/estimated_production_loss): ", e)
        return CustomException('Ocurrio un error al obtener el porcentaje estimado de perdida de produccion', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search the sex of the producers
def get_producers_sex(val, connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/get_producers_sex): ", e)
        return CustomException('Ocurrio un error al obtener los datos sobre el sexo de los productores', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search and calc the avergae age of producers
def get_producers_average_age(val, connection):
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


    except Exception as e:
        print("ERROR (eventos/database_manager/get_producers_average_age): ", e)
        return CustomException('Ocurrio un error al obtener la edad promedio de los productores', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search producers ethnical group
def get_producers_ethnical_group(val, connection):
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


    except Exception as e:
        print("ERROR (eventos/database_manager/get_producers_ethnical_group): ", e)
        return CustomException('Ocurrio un error al obtener los grupos etnicos de los productores', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search the types of all registered producers
def get_producer_type_registered(val, connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/get_producer_type_registered): ", e)
        return CustomException('Ocurrio un error al obtener los datos de los tipos de productores', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search affected hectares per specie
def get_specie_hectares(val, connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/get_specie_hectares): ", e)
        return CustomException('Ocurrio un error al obtener las hectareas afectadas por especie', str(e)), 500
    else:
        return results, 200

    finally:
        if not cursor.closed:
            cursor.close()



# Search the location of the events
def get_events_locations(val, connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/get_events_locations): ", e)
        return CustomException('Ocurrio un error al obtener las ubicaciones de los eventos', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()



# Get the wood volume affected
def get_wood_volume(val, connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/get_wood_volume): ", e)
        return CustomException('Ocurrio un error al obtener el volumen de madera afectado', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search damages per infrastructure type
def get_infrastructure_damages(val, connection):
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

    except Exception as e:
        print("ERROR (eventos/database_manager/get_infrastructure_damages): ", e)
        return CustomException('Ocurrio un error al obtener los daños por tipo de infraestructura', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search the loss of the values
def get_loss_values(val, connection):
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
        WHERE e.siglas = 'VPEmf'
        AND  { val }
        AND c.validado = true
        GROUP BY e.cod_indicador """)
        val = (sql)
        cursor.execute(sql)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except Exception as e:
        print("ERROR (eventos/database_manager/get_loss_values): ", e)
        return CustomException('Ocurrio un error al obtener los costos de las perdidas', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Search species data
def get_species_data(connection):
    results = {'cropType': [], 'areaUnity': []}
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
        print("ERROR (eventos/database_manager/get_species_data): ", e)
        return CustomException('Ocurrio un error al obtener los datos de las especies', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()



# Get planting material
def get_planting_material(connection):
    results = {'plantingMaterial': [], 'harvestUnity': [], 'equivCharge': [], 'seedSource': []}
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
        print("ERROR (eventos/database_manager/get_planting_material): ", e)
        return CustomException('Ocurrio un error al obtener los datos del material de plantacion', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Get direct and indirect costs
def get_costs(connection):
    results = {'indirectCosts': [], 'directCosts': []}
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
        print("ERROR (eventos/database_manager/get_costs): ", e)
        return CustomException('Ocurrio un error al obtener los costos directos e indirectos', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()


# Get credit data and assurance data
def credit_data_assurance_data(connection):
    results = {'assruanceType': [], 'bankingEntity': []}
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
        print("ERROR (eventos/database_manager/credit_data_assurance_data): ", e)
        return CustomException('Ocurrio un error al obtener los datos del credito y seguro', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()



# Infrastructure data
def get_data_infrastructure(connection):
    results = {'fertilizerType': [], 'pesticideType': [], 'presentation': []}
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
        print("ERROR (eventos/database_manager/get_data_infrastructure): ", e)
        return CustomException('Ocurrio un error al obtener los datos de las infraestructuras', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()



# Peq affected system data
def get_peq_affected(connection):
    results = {'affectedSistem': [], 'harvestUnity': [], 'equivCharge': [], 'areaUnity': [],
               'typeProduct': [], 'unity': [], 'activity': [], 'rubro': [], 'inputType': [], 'machineryTypeBBA': [],
               'machineryTypePEM': [], 'machneryAq': [], 'machineryAv': [], 'activeType': [], 'constructionType': []}
    try:
        cursor = connection.cursor()
        sql = ('''
        SELECT cod_sistem_afectado AS codSistemaAfectado, sistema_afectado AS sistemaAfectado FROM Sistema_afectado WHERE cod_sistem_afectado NOT IN(2)
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
               "FROM Actividad WHERE cod_actividad NOT IN (1, 2, 3, 4, 5, 6, 7, 8)")
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
            WHERE cod_tipo_maquinaria IN(4,5,6,7,3,8,9,10,11);
            ''')
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Instalaciones y maquinaria manejo de bovinos, bufalinos y afines
            results['machineryTypeBBA'].append(dict(zip(columns, row)))

        sql = (
            '''
        SELECT cod_tipo_maquinaria AS codTipMaquinaria, tipo_maquinaria AS tipMaquinaria FROM Tipo_maquinaria
        WHERE cod_tipo_maquinaria IN(14,4,6,5,7,3,15,10,11,12,13,31);
        ''')
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Instalaciones y maquinaria para la producción de especies menores
            results['machineryTypePEM'].append(dict(zip(columns, row)))

        sql = (
            '''
            SELECT cod_tipo_activo AS codTipActivo, tipo_activo AS tipActivo FROM Tipo_activo
            WHERE cod_tipo_activo IN(1,2,3,4,5,6,7,8,9);
            '''
        )
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['machneryAq'].append(dict(zip(columns, row)))

        sql = (
            '''
            SELECT cod_tipo_maquinaria AS codTipMaquinaria, tipo_maquinaria AS tipMaquinaria FROM Tipo_maquinaria
            WHERE cod_tipo_maquinaria IN(16,17,18,19,20,21,22,23,24,25,26,11,28,29,30,31);
            '''
        )
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['machineryAv'].append(dict(zip(columns, row)))

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
        print("ERROR (eventos/database_manager/get_peq_affected): ", e)
        return CustomException('Ocurrio un error al obtener los datos del sistema pecuario', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close()



# Get the info for the lists on the fishing system from database
def get_fishing_data(connection):
    results = {'fishingType': [], 'activeType': [], 'buildingType': [], 'redType': [], 'lossType': [], 
    'embqMaterial': [], 'propType': []}
    try:
        cursor = connection.cursor()

        sql = (
            '''
            SELECT cod_tipo_pesqueria AS codTipPesq, tipo_pesqueria AS tipPesq FROM Tipo_pesqueria;
            '''
        )
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Pesquería que realiza en el año
            results['fishingType'].append(dict(zip(columns, row)))

        sql = (
            "SELECT cod_tipo_activo AS codTipActivo, tipo_activo AS tipActivo FROM Tipo_activo;")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Por favor seleccione un activo productivo afectado
            results['activeType'].append(dict(zip(columns, row)))

        sql = (
            "SELECT cod_tipo_construccion AS codTipCons, tipo_construccion AS tipCons FROM Tipo_construccion_pesq;")
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Por favor, indique el tipo de construcción afectada
            results['buildingType'].append(dict(zip(columns, row)))

        sql = ("""
            SELECT cod_tipo_red AS codTipRed, tipo_red AS tipoRed FROM Tipo_red;
        """)
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Tipo de redes afectadas
            results['redType'].append(dict(zip(columns, row)))

        sql = ("""
            SELECT cod_tipo_perdida AS codTipPerdida, tipo_perdida AS tipPerdida FROM Tipo_perdida;
        """)
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Tipo de la perdida
            results['lossType'].append(dict(zip(columns, row)))

        
        sql = ("""
            SELECT cod_material_embq AS codEmbqMaterial, material_embq As embqMaterial FROM Material_embarcacion;
        """)
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Tipo material de la embarcacion
            results['embqMaterial'].append(dict(zip(columns, row)))

        sql = ("""
            SELECT cod_tipo_propulsion AS codPropulsion, tipo_propulsion AS tipoPropulsion FROM Tipo_propulsion;
        """)
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            # Tipo de propulsion de la embarcacion
            results['propType'].append(dict(zip(columns, row)))

    except Exception as e:
        print("ERROR (eventos/database_manager/get_fishing_data): ", e)  
        return CustomException('Ocurrio un error al obtener los datos del sistema pesquero', str(e)), 500
    else:
        return results, 200
    finally:
        if not cursor.closed:
            cursor.close() 


# Get all the information of an specific event
def get_specific_event(connection, idEvento):
    try:
        cursor = connection.cursor()

        
        results = {
                'dataEncabezadoEvento': {
                    'sisProds': [],
                    'caladeros': []
                },
                'dataProductor': [],
                "dataEspecies": {
                    "forestal": [],
                    "agropecuario": [],
                    "infoPecuario": [],
                    "infoApicola": [],
                    "infoPesquero": []
                }
        }
        
        
        sql = ("""
           SELECT cod_evento AS "codEvento", cod_tipo_evento_fk AS "tipoEv", coord_x::TEXT AS "latitud", coord_y::TEXT AS "longitud", 
            altitud::TEXT, precision::TEXT, cod_municipio_fk AS "municipio", 
			(SELECT cod_dpto_FK FROM Municipios WHERE cod_municipios = cod_municipio_fk) AS departamento, ubicacion_vereda AS "enVereda", 
			cod_vereda_fk AS "codVereda", nom_puerto_desembarquee AS "nombrePuerto", cod_encuestador_fk AS "idUsuario", 
			descrip_llegada_casco_urbano AS "observacion", cod_tipo_subevento_fk AS "subEv", 
			CASE WHEN cuarentenaria = true THEN 1 ELSE 2 END AS "cuarentenario", 
			cod_plaga_fk AS "plagaCuarente", cod_enfermedad_fk AS "enfermedadCuarente", nom_enfermedad AS "nombreEnfermedad", 
			nom_plaga AS "nombrePlaga", validado FROM Evento WHERE cod_evento = %s
        """)

        cursor.execute(sql, [idEvento])
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        if len(rows) > 0:
            for i in range(len(columns)):
                results['dataEncabezadoEvento'][columns[i]] = rows[0][i]
        else:
            raise_exception('No hay datos de este evento', 'No hay datos de este evento')
        
        prod = get_producers_event(connection, idEvento)
        if prod[1] != 200:
            raise_exception(prod[0].to_dict()['message'],  prod[0].to_dict()['error'])
        results['dataProductor'] = prod[0]['productor']

        
        for caladero in prod[0]['caladero']:
            cal = {
                "nombrePuerto": caladero['nombrePuerto'],
                "position": {
                    "lat": caladero['lat'],
                    "lng": caladero['lng']
                },
                "id": caladero['id'],
                "tooltip": caladero['tooltip'],
                "draggable": True,
                "visible": True,
                "icon": True,
                "tipo": "Caladero"
            }
            results['dataEncabezadoEvento']['caladeros'].append(cal)
        
        sisProd = get_sisprod_event(connection, idEvento)
        if sisProd[1] != 200:
            raise_exception(sisProd[0].to_dict()['message'],  sisProd[0].to_dict()['error'])

        for sis in sisProd[0]:
            results['dataEncabezadoEvento']['sisProds'].append(sis['sisProd'])

        for sis in sisProd[0]:
            if sis['cultAfec']:
                print('agro')
                data_agro = get_agro_spec_event(sis['cultAfec'], connection)
                if data_agro[1] != 200:
                    raise_exception(data_agro[0].to_dict()['message'], data_agro[0].to_dict()['error'])
                
                results['dataEspecies']['agropecuario'].append(data_agro[0])
            
            if sis['espForAfec']:
                data_forestal = get_forestal_spec_event(sis['espForAfec'], connection)
                if data_forestal[1] != 200:
                    raise_exception(data_forestal[0].to_dict()['message'], data_forestal[0].to_dict()['error'])

                results['dataEspecies']['forestal'].append(data_forestal[0])
                print('forestal')

            if sis['peqAfec']:
                data_peq = get_peq_spec_event(sis['peqAfec'], connection)
                if data_peq[1] != 200:
                    raise_exception(data_peq[0].to_dict()['message'],  data_peq[0].to_dict()['error'])
                results['dataEspecies']['infoPecuario'].append(data_peq[0])
                print('pecuario')
            
            if sis['apiAfec']:
                data_api = get_api_spec_event(sis['apiAfec'], connection)
                if data_api[1] != 200:
                    raise_exception(data_api[0].to_dict()['message'],  data_api[0].to_dict()['error'])
                
                results['dataEspecies']['infoApicola'].append(data_api[0])
                print('apicola')

            if sis['pesqAfec']:
                data_pesq = get_pesq_spec_event(sis['pesqAfec'], connection)
                if data_pesq[1] != 200:
                    raise_exception(data_pesq[0].to_dict()['message'],  data_pesq[0].to_dict()['error'])
                
                results['dataEspecies']['infoPesquero'].append(data_pesq[0])
                print('pesquero')

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_specific_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_specific_event): ", e)
        return CustomException('Ocurrio un error al obtener la información del evento', str(e)), 500
    else:
        return {'newEvent': results}, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# This function get the producers associated to an event
def get_producers_event(connection, idEvento):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_productor_agropecuario As "codProductor", cod_condicion_juridica_FK As "condJuridica", condicion_juridica AS "nameCondJuridica", nombre_apellido_productor AS "nombre", 
            cod_tipo_documento_FK AS "tipoDcto", tipo_documento AS "nameTipoDcto", nro_documento AS "dcto", correo AS "email", cod_tipo_productor_FK AS "tipoProd", 
			tipo_productor AS "nameTipoProd", direccion_residencia AS "dirRes", tipo_relacion_predio AS "nameRelPre",
            numero_contacto AS tel, sexo AS "nameSexo", cod_sexo_FK As sexo, fch_nacimiento::TEXT AS "fechaNac", grupo_etnico AS "nameGEtnico" ,cod_grupo_etnico_FK AS "gEtnico" FROM Productor_agropecuario pa
            INNER JOIN Evento_productos_agropecuario epa ON epa.cod_evento_FK = %s AND epa.cod_producto_agro = pa.cod_productor_agropecuario
			INNER JOIN condicion_juridica ON cod_condicion_juridica = cod_condicion_juridica_FK
			INNER JOIN tipo_documento2 ON cod_tipo_documento = cod_tipo_documento_FK
			INNER JOIN tipo_productor ON cod_tipo_productor = cod_tipo_productor_FK
			INNER JOIN predio_productor ON cod_productor_agropecuario = cod_productor_fk
			INNER JOIN tipo_relacion_predio ON cod_tipo_relacion_predio = cod_tipo_relacion_predio_fk
			LEFT JOIN sexo ON cod_sexo = cod_sexo_fk 
			LEFT JOIN grupo_etnico ON cod_grupo_etnico = cod_grupo_etnico_fk
        """)

        cursor.execute(sql, [idEvento])
        columns = [column[0] for column in cursor.description]
        results = {
            'productor': [],
            'caladero': []
        }
        for row in cursor.fetchall():
            n_dict = dict(zip(columns, row))
            n_dict.update({"tratamientoDatos": True})
            results['productor'].append(n_dict)

        producers = [res['codProductor'] for res in results['productor']]

        estate_relation = get_estate_relation(connection, results['productor'])
        if estate_relation[1] != 200:
            raise_exception(estate_relation[0].to_dict()['message'],  estate_relation[0].to_dict()['error'])

        fishing_grounds = get_fishing_grounds_event(connection, producers)
        if fishing_grounds[1] != 200:
            raise_exception(fishing_grounds[0].to_dict()['message'],  fishing_grounds[0].to_dict()['error'])
        
        results['caladero'] = fishing_grounds[0]

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_producers_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_producers_event): ", e)
        return CustomException('Ocurrio un error al obtener los productores del evento', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Get the relation of the productor with the estate
def get_estate_relation(connection, producers):
    try:
        cursor = connection.cursor()
        results = []
        for producer in producers:
            sql = ("""
                SELECT cod_tipo_relacion_predio_FK AS "relPre" FROM Predio_productor WHERE cod_productor_FK = %s
            """)

            cursor.execute(sql, [producer['codProductor']])
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            producer['relPre'] = results[0]['relPre']

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_estate_relation): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_estate_relation): ", e)
        return CustomException('Ocurrio un error al obtener los productores del evento', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close() 


# Get the fishing grounds per specific event
def get_fishing_grounds_event(connection, producers):
    try:
        cursor = connection.cursor()

        results = []

        producer = producers[0]
        sql = ("""
            SELECT cod_caladero AS "codCaladero", descripcion_zona As "nombrePuerto", coord_x::TEXT As lat, coord_y::TEXT AS lng,
            altitud, precision FROM Caladeros c JOIN Productor_agro_caladero pac ON pac.cod_caladero_FK = c.cod_caladero AND cod_productor_agro_FK = %s
        """)

        cursor.execute(sql, [producer])
        columns = [column[0] for column in cursor.description]
        i = 2
        for row in cursor.fetchall():
            n_dict = dict(zip(columns, row))
            n_dict.update({
                "id": i,
                "tooltip": "Caladero "+str(i),
            })
            results.append(n_dict)
            i+=1

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_fishing_grounds_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_fishing_grounds_event): ", e)
        return CustomException('Ocurrio un error al obtener los caladeros del evento', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()



# Get the productive systems of an specific event
def get_sisprod_event(connection, idEvento):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_evento_sist_prod_afectado AS "codProdSis", cod_sist_prod_afect_FK AS "sisProd",
            cod_cultivo_afectado_FK AS "cultAfec", cod_especie_forestal_FK AS "espForAfec", cod_novedad_pesquera_FK AS "pesqAfec",
            cod_novedad_pecuaria_FK AS "peqAfec", cod_novedad_pecuaria_apicola_FK AS "apiAfec" FROM Evento_sist_prod_afectado WHERE cod_evento_FK = %s
        """)

        cursor.execute(sql, [idEvento])
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_sisprod_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_sisprod_event): ", e)
        return CustomException('Ocurrio un error al obtener los sistemas productivos del evento', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()
        


# Get the information of an specific forestal event
def get_forestal_spec_event(id, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
        SELECT cod_especie_forestal_sembrada AS "codEspecie", cod_fase_productiva_FK AS "faseProd", cod_especie_forestal_afec_FK AS "espAfectada",
        nom_comun_especie AS "nombre", cod_objetivo_plantacion_FK AS "objetivo", num_arbol_ha::TEXT AS "noArbolesAntesAfectacion", num_estresacas AS "noEntresacas",
        valor_entresacas::TEXT AS "valEntreSacas", porcentaje_entresacas::TEXT AS "porceEntreSacas", diam_prom_altura_pecho::TEXT AS "diametroPromedio", altura_comercial::TEXT AS "alturaComercial", 
        altura_total::TEXT AS "alturaTotal", turno_plantacion::TEXT As "plantacionAnos", porc_arboles_turno::TEXT AS "porceArbolesTurnoFinal", fch_establecimiento::TEXT AS "fecha", densidad_siembra_Ha::TEXT AS "densHectarea", 
        area_total_sembrada_Ha::TEXT As "areaSembrada", area_afectada_Ha::TEXT AS "areaAfectadaHectareas", fcha_afectacion_sist_forestal::TEXT AS "fechaAfactaForestal", duracion_dias_afectacion::TEXT AS "diasAfectoSistemaForestal",
        num_arboles_afectados AS "noArbolesAfectados", valor_recibir_prod_afectada::TEXT AS "valorVenderProduccionAfectada", volumen_madera_afectados::TEXT AS "vlMaderaAfectado",
        afectacion_infraestructura AS "afectacionesEnMaquinaria", fase_productiva AS "nameFaseProd", especie_forestal_afectada AS "nameEspAfectada",
		objetivo_plantacion AS "nameObjetivo"
		FROM Especie_forestal_sembrada 
		LEFT JOIN Fase_productiva ON cod_fase_productiva = cod_fase_productiva_fk
		LEFT JOIN Especie_forestal_afectada ON cod_esp_forestal_afectada = cod_especie_forestal_afec_fk
		LEFT JOIN Objetivo_plantacion ON cod_objetivo_plantacion = cod_objetivo_plantacion_fk
		WHERE cod_especie_forestal_sembrada = %s
        """)

        val = ([id])

        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        for res in results:
            id_esp = res['codEspecie']

            direct_costs = get_forestal_direct_costs_event(id_esp, connection)
            if direct_costs[1] != 200:
                raise_exception(direct_costs[0].to_dict()['message'],  direct_costs[0].to_dict()['error'])

            res['costosDirectos'] = direct_costs[0]

            non_direct_costs = get_forestal_non_direct_costs_event(id_esp, connection)
            if non_direct_costs[1] != 200:
                raise_exception(non_direct_costs[0].to_dict()['message'],  non_direct_costs[0].to_dict()['error'])        

            res['costosInDirectos'] = non_direct_costs[0]

            seed = get_seed_infrastructure_forestal(id_esp, connection)
            if seed[1] != 200:
                raise_exception(seed[0].to_dict()['message'], seed[0].to_dict()['error'])

            res['semilla'] = seed[0]

            fert = get_fert_infrastructure_forestal(id_esp, connection)
            if fert[1] != 200:
                raise_exception(fert[0].to_dict()['message'],  fert[0].to_dict()['error'])
            
            res['fertilizante'] = fert[0]

            plag = get_plag_infrastructure_forestal(id_esp, connection)
            if plag[1] != 200:
                raise_exception(plag[0].to_dict()['message'],  plag[0].to_dict()['error'])

            res['plaguicida'] = plag[0]

            
            maq = get_maq_infrastructure_forestal(id_esp, connection)
            if maq[1] != 200:
                raise_exception(maq[0].to_dict()['message'],  maq[0].to_dict()['error'])

            res['maquinariaAgricola'] = maq[0]
            

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_forestal_spec_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_forestal_spec_event): ", e)
        return CustomException('Ocurrio un error al obtener la información del evento forestal', str(e)), 500
    else:
        return results[0], 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Get the information of an specific agro event
def get_agro_spec_event(id, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
            SELECT cod_cultivo AS "codCult", cod_nombre_FK AS "nombreCultivo", tipo_cultivo AS "nameTipoCultivo", cod_unidad_area_FK AS "unidadArea", nombre_nueva_unidad_reporte_area_cultivo AS "nombrenuvaunidad", 
            eqv_mt_nueva_unidad_reporte_area_cultivo AS "nuevaunidadmetros", area_total_cultivo_sembrado AS "areaCultivo", area_total_cultivo_Ha AS "areaCultHa",
            cod_tipo_material_siembra_FK AS "materiralSiembra", cantidad_semilla_utilizo_siembra_ha AS "cantSemillas", cod_unidad_cantidad_semilla_FK AS "medidaSemilla",
            equivalencia_kg_carga AS "equivaleKilos", eqv_carga_otro_material_siembra AS "nuevaEquivalencia", cod_fuente_semilla_FK AS "fuenteSemilla", fcha_siembra::TEXT AS "fechaSiembra",
            mes_cosecha_cultivo AS "fechaPrimeCosecha", mes_esperado_cosecha::TEXT AS "fechaEsperaCosecha", cant_cosechada AS "cantCosechada", cod_unidad_consecha_FK AS "medidaCantCosechada", 
            cod_equiva_kg_FK AS "equivaleKilosCosecha", cant_dinero_venta_cosecha AS "totalReciCosechado", fch_inicio_afectacion::TEXT AS "fechaAfectacion", duracion_dias_afectacion AS "diasCultivoExpuesto",
            proyectada_cant_produc_estim_producir AS "cantProduProducir", proyectada_cod_unidad_reporte_FK AS "medidaReportar", proyectada_cod_equiva_kg_FK AS "equivaleKilosReportar", 
            proyectada_precio_por_cada_unidad AS "totalReportado", proyectada_vlr_total_recibir_venta_total_produccion AS "totalProyectaVenta", porc_resiembra AS "porceResiembra",
			unidad_area AS "nameUnidadArea", material AS "nameMateriralSiembra", afectacion_infraestructura AS "afectaMaquinaria", cod_semilla_equiv_Kg_FK AS "equivaleKilos"
            FROM Cultivos_afectados 
			LEFT JOIN Tipo_cultivo ON cod_tipo_cultivo = cod_nombre_fk
			LEFT JOIN Unidad_area ON cod_unidad_area = cod_unidad_area_fk
			LEFT JOIN Material_siembra ON cod_material = cod_tipo_material_siembra_fk
			WHERE cod_cultivo = %s
        """)

        val = ([id])

        cursor.execute(sql, val)
        
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        print(results)
        for res in results:
            cod_cult = res['codCult']

            direct_costs = get_agro_direct_costs_event(cod_cult, connection)
            if direct_costs[1] != 200:
                raise_exception(direct_costs[0].to_dict()['message'],  direct_costs[0].to_dict()['error'])

            res['costosDirectos'] = direct_costs[0]
            if len(direct_costs[0]) > 0:
                res['costoPromeJornal'] = direct_costs[0][0]['costoPromeJornal']

            indirect_costs = get_agro_indirect_costs_event(cod_cult, connection)
            if indirect_costs[1] != 200:
                raise_exception(indirect_costs[0].to_dict()['message'],  indirect_costs[0].to_dict()['error'])
            
            res['costosInDirectos'] = indirect_costs[0]

            credit = get_agro_credit_event(cod_cult, connection)
            if credit[1] != 200:
                raise_exception(credit[0].to_dict()['message'],  credit[0].to_dict()['error'])

            if len(credit[0]) > 0:
                res.update(credit[0][0])
            else:
                res['credito'] = []
            
            assurance = get_agro_assurance_event(cod_cult, connection)
            if assurance[1] != 200:
                raise_exception(assurance[0].to_dict()['message'],  assurance[0].to_dict()['error'])

            if len(assurance[0]) > 0:
                res.update(assurance[0][0])

            infra = get_agro_infra(cod_cult, connection)
            if infra[1] != 200:
                raise_exception(infra[0].to_dict()['message'],  infra[0].to_dict()['error'])

            res.update(infra[0])



    except CustomException as e:
        print("ERROR (eventos/database_manager/get_agro_spec_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_agro_spec_event): ", e)
        return CustomException('Ocurrio un error al obtener la información del evento agricola', str(e)), 500
    else:
        return results[0] if len(results) > 0 else results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Get the information of an specific peq event
def get_peq_spec_event(id, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_novedad_peq AS "codPeq", cod_sistema_afectado_FK AS "sistema", sistema_afectado_nom_otro AS "sistemaNuevo", nombre_raza AS "nombreRaza", num_total_anim_explotacion AS "numAnimal",
            peso_prom_animal_explotacion AS "pesoAnimal", cod_unidad_reporte_FK AS "uniMedidaAnimal", peso_prom_animal_explotacion_nom_otro AS "nombreUnidadMedidaNuevo", eqv_kg_unidad_reportar_otro AS "unidadMedidaNuevo",
            cod_equiva_kg_fk AS "peso", equivalencia_kg_carga AS "pesoNuevo", precio_prom_x_animal AS "valorAnimal", area_usada_animales AS "areaAnimal", cod_unidad_area_FK AS "unidadArea",
            unidad_area_reporte_otro AS "unidadAreaNuevo", fch_inicio_actividad_productiva::TEXT AS "fechaProduccion", fch_inicio_evento::TEXT AS "fechaIniEvento", num_animales_enfermos_afectados AS "numAnimalEnfermos",
            num_animales_hembra_muertos AS "numAnimalHembMuerto", num_animales_macho_muertos AS "numAnimalMachMuerto", edad_promedio_meses_anim_muerto AS "edadAnimal", cod_tipo_producto_FK AS "tipoProducto",
            nombre_producto_obtenido_otro AS "tipoProductoNuevo", prod_mensual_antes_afectacion AS "produMensualAfectacion", prod_mensual_actual_potencial_afectacion AS "produPotencial", cod_unidad_reporte1_fk AS "unidadProdccion",
            kilos_x_unidad_datos_produccion AS "kilosUnidad", nombre_otra_unidad_datos_produccion AS "nombreUnidadProduccionNueva", eqv_kilos_otra_unidad_datos_produccion AS "unidadProduccionNueva", 
            cod_equiva1_kg_carga AS "pesoProduccion", equivalencia1_kg_carga AS "pesoProduccionNuevo", precio_venta_und_producto AS "valorVentaProducto", huevos_producto_diferentes_avicola AS "huevosAvicola", 
            cant_meses_recuperar_capac_perdida AS "mesesRecuperarPecuaria", afectacion_infraestructura AS "afectacion", sistema_afectado AS "nombreSistema"
			FROM Novedad_pecuaria 
			INNER JOIN Sistema_afectado ON cod_sistem_afectado = cod_sistema_afectado_fk
			WHERE cod_novedad_peq = %s
        """)

        val = ([id])

        cursor.execute(sql, val)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        for res in results:
            cod_peq = res['codPeq']

            variable_costs = get_peq_vaiable_costs_event(cod_peq, connection)
            if variable_costs[1] != 200:
                raise_exception(variable_costs[0].to_dict()['message'],  variable_costs[0].to_dict()['error'])

            res['costosVariables'] = variable_costs[0]

            non_variable_costs = get_peq_non_variable_costs_event(cod_peq, connection)
            if non_variable_costs[1] != 200:
                raise_exception(non_variable_costs[0].to_dict()['message'],  non_variable_costs[0].to_dict()['error'])

            res['costosFijos'] = non_variable_costs[0]

            infra = get_infrastructure_peq_event(cod_peq, connection)
            if infra[1] != 200:
                raise_exception(infra[0].to_dict()['message'],  infra[0].to_dict()['error'])

            res.update(infra[0])


    except CustomException as e:
        print("ERROR (eventos/database_manager/get_peq_spec_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_peq_spec_event): ", e)
        return CustomException('Ocurrio un error al obtener la información del evento pecuario', str(e)), 500
    else:
        return results[0], 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Get the information of an specific apiarian event
def get_api_spec_event(id, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_novedad_peq AS "codApicola", num_colmenas_afectadas AS "numColmenas", valor_comercial_prom_colmena AS "valorColmena", prod_mensual_propoleo_kg_antes_afectacion AS "propoleoMensual",
            prod_mensual_miel_litros_antes_afectacion AS "mielMensual", prod_mensual_jalea_litros_antes_afectacion AS "jaleaMensual", vlr_ingreso_prom_mensual_antes_afectacion AS "valorMensual",
            ingreso_mensual_actualmente AS "ingresoMensual", afectacion_infraestructura AS "afectacion" FROM Novedad_pecuaria WHERE cod_novedad_peq = %s
        """)
        val = ([id])

        cursor.execute(sql, val)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        for res in results:
            cod_api = res['codApicola']

            infra = get_infrastructure_api_event(cod_api, connection)
            if infra[1] != 200:
                raise_exception(infra[0].to_dict()['message'],  infra[0].to_dict()['error'])

            res.update(infra[0])
        
    except CustomException as e:
        print("ERROR (eventos/database_manager/get_api_spec_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_api_spec_event): ", e)
        return CustomException('Ocurrio un error al obtener la información del evento apícola', str(e)), 500
    else:
        return results[0], 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


def get_pesq_spec_event(id, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_novedad_pesq AS "codPesq", puerto_desembarque_pesca AS "puertoDesembarque", principales_especies_explotadas AS "especieExplotada", embarcaciones_afectadas AS "embarcacionAfectada",
            instalaciones_afectadas AS "instalacionAfectada", instalacion_maquinaria_afectada AS "maquinariaAfectada", num_redes AS "numeroRedes", vlr_pesos_redes_afectadas AS "valorRedes", num_faenas_pesca AS "numeroFaenas",
            faenas_pesca AS "cantidadFaenasMes", vlr_prom_recibido_venta_peces_faena AS "valorVentaPeces" FROM Novedad_pesquera WHERE cod_novedad_pesq = %s
        """)

        val = ([id])

        cursor.execute(sql, val)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        for res in results:
            cod_pesq = res['codPesq']

            fishing_type = get_fishing_type_pesq_event(cod_pesq, connection)
            if fishing_type[1] != 200:
                raise_exception(fishing_type[0].to_dict()['message'],  fishing_type[0].to_dict()['error'])
            
            res['tipoPesqueria'] = fishing_type[0]

            ebmq_affected = get_embq_affected_event(cod_pesq, connection)
            if ebmq_affected[1] != 200:
                raise_exception(ebmq_affected[0].to_dict()['message'],  ebmq_affected[0].to_dict()['error'])

            res['embarcaciones'] = ebmq_affected[0]

            red_effected = get_red_affected_event(cod_pesq, connection)
            if red_effected[1] != 200:
                raise_exception(red_effected[0].to_dict()['message'], red_effected[0].to_dict()['error'])

            if len(red_effected[0]) > 0:
                res.update(red_effected[0][0])

            infrastructure = get_infrastructure_pesq_event(cod_pesq, connection)
            if infrastructure[1] != 200:
                raise_exception(infrastructure[0].to_dict()['message'],  infrastructure[0].to_dict()['error'])

            res['maquinarias'] = infrastructure[0]

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_pesq_spec_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_pesq_spec_event): ", e)
        return CustomException('Ocurrio un error al obtener la información del evento pesquero', str(e)), 500
    else:
        return results[0], 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Get the direct costs of an specific forestal event
def get_forestal_direct_costs_event(id_especie, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_costo_directo AS "codCostoDirecto", cod_actividad_FK AS "id", gasto_incurrido::TEXT AS "costo",
			actividad AS "rubros"
            FROM Costos_directos 
			INNER JOIN Actividad ON cod_actividad = cod_actividad_fk
			WHERE cod_especie_forestal_FK = %s
        """)

        val = ([id_especie])

        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_forestal_direct_costs_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_forestal_direct_costs_event): ", e)
        return CustomException('Ocurrio un error al obtener los costos directos del evento', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Get the direct costs of an specific agro event
def get_agro_direct_costs_event(id_cult, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_costo_produccion AS "codCostoDirecto", cod_actividad_FK AS "idTipoCostoDirecto", num_jornales::TEXT AS "noJornales",
            gastos AS gastos, costo_promedio_jornal_zona AS "costoPromeJornal", tipo_actividad AS "actividad"
            FROM Costos_de_produccion 
			INNER JOIN Cultivos_afectados ON cod_cultivo = cod_cultivo_afectado_FK 
			INNER JOIN tipo_actividad ON cod_tipo_actividad = cod_actividad_fk
			WHERE cod_cultivo_afectado_FK = %s
        """)

        val = ([id_cult])

        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
    except CustomException as e:
        print("ERROR (eventos/database_manager/get_agro_direct_costs_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_agro_direct_costs_event): ", e)
        return CustomException('Ocurrio un error al obtener los costos directos del evento', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Get the non direct costs of an specific forestal event
def get_forestal_non_direct_costs_event(id_especie, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_costo_fijo_prod AS "codCostoIndirecto", cod_rubro_FK AS "id", gasto_incurrido::TEXT AS "costo",
 			rubros 
            FROM Costos_fijos_indirectos 
			INNER JOIN Rubros ON cod_rubros = cod_rubro_fk
			WHERE cod_especie_forestal_FK = %s
        """)

        val = ([id_especie])

        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_forestal_non_direct_costs_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_forestal_non_direct_costs_event): ", e)
        return CustomException('Ocurrio un error al obtener los costos indirectos del evento', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Get the non direct costs of an specific agro event
def get_agro_indirect_costs_event(id_cult, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
            SELECT cod_costo_indirecto AS "codCostoIndirecto", cod_rubro_FK AS "tipoCostoInDirecto", 
            gastos_incurridos AS "costo", rubros AS "actividad"
			FROM Costos_indirectos_produccion 
			INNER JOIN Rubros ON cod_rubros = cod_rubro_fk
			WHERE cod_cultivo_afectado_FK = %s
        """)

        val = ([id_cult])

        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
    except CustomException as e:
        print("ERROR (eventos/database_manager/get_agro_indirect_costs_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_agro_indirect_costs_event): ", e)
        return CustomException('Ocurrio un error al obtener los costos indirectos del evento', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Get the variable costs of an specific peq event
def get_peq_vaiable_costs_event(cod_peq, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
            SELECT cod_costo_variable AS "idCostoVariable", cod_actividad_FK AS "codCostoVariable", valor AS "costoVariable", 
 			actividad AS "nameCostoVariable"
            FROM Costos_variables_pecuario 
			INNER JOIN Actividad ON cod_actividad = cod_actividad_fk
			WHERE cod_novedad_peq_FK = %s
        """)

        val = ([cod_peq])

        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_peq_vaiable_costs_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_peq_vaiable_costs_event): ", e)
        return CustomException('Ocurrio un error al obtener los costos variables del evento', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Get the non variable costs of an specific peq event
def get_peq_non_variable_costs_event(cod_peq, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
            SELECT cod_costo_fijo_prod AS "idCostoFijo", cod_rubro_FK AS "codCostoFijo", gasto_incurrido AS "costoFijo",
			rubros AS "nameCostoFijo"
            FROM Costos_fijos_pecuarios 
			INNER JOIN Rubros ON cod_rubros = cod_rubro_FK
			WHERE cod_novedad_peq_FK = %s
        """)

        val = ([cod_peq])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_peq_non_variable_costs_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_peq_non_variable_costs_event): ", e)
        return CustomException('Ocurrio un error al obtener los costos fijos del evento', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()

# Get the seed infrastucture of an specific event
def get_seed_infrastructure_forestal(id_especie, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
            SELECT cod_infraestructura_forestal AS "codSemilla", cod_especie_semilla_fk AS "espAfectada", cant_semilla_almacenada::TEXT AS "canSemillas",
            vlr_pesos_afectacion::TEXT AS "valPesos", cant_semilla_siembra AS "cantSemillas", cod_unidad_cantidad_semilla_fk AS "medidaSemilla",
            cod_tip_semilla_FK AS "idTipoSemilla", eqv_kg_carga_semilla_fk AS "equivaleKilos", eqv_kg_carga_otro_semilla_fk AS "nuevaEquivalencia",
            cod_fuente_semilla_fk AS "fuenteSemilla", especie_forestal_afectada AS "especieSemilla", lote_propagacion AS "nameLotePropagacion", cod_lote_propagacion AS "idLotePropagacion",
			tipos_semilla AS "nameTipoSemilla", und_cosecha AS "nameMedidaSemilla", fuente_semilla AS "nameFuenteSemilla", equiv_carga_kg AS "nameEquivalencia"
			FROM Infraestructura_forestal
			LEFT JOIN Especie_forestal_afectada ON cod_esp_forestal_afectada = cod_especie_semilla_fk
			LEFT JOIN Infraestructura_lote_propagacion ON cod_infraestructura_fk = cod_infraestructura_forestal
			LEFT JOIN Lote_propagacion ON cod_lote_propagacion = cod_lote_propagacion_fk
			LEFT JOIN Tipos_semilla ON cod_tipos_semilla = cod_tip_semilla_fk
			LEFT JOIN Unidad_cosecha ON cod_unidad_cantidad_semilla_fk = cod_und_cosecha
			LEFT JOIN Fuente_semilla ON cod_fuente_semilla = cod_fuente_semilla_fk
			LEFT JOIN Equivalencia_carga ON eqv_kg_carga_semilla_fk = cod_equiv_carga
			WHERE cod_especie_forestal_sembrada_FK = %s AND cod_tipo_infraestrucrtura_FK = 1
        """)

        val = ([id_especie])

        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        for seed in results:
            propagation = get_seed_propagation_forestal(seed,connection)
            if propagation[1] != 200:
                raise_exception(propagation[0].to_dict()['message'],  propagation[0].to_dict()['error'])

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_seed_infrastructure_forestal): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_seed_infrastructure_forestal): ", e)
        return CustomException('Ocurrio un error al obtener las semillas del evento', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()  


# Get the propagation of a seed in forestal event
def get_seed_propagation_forestal(seed, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_infraestructura_lote_propagacion AS "codInfraLotProp", cod_lote_propagacion_FK AS "codLotePropagacion" FROM infraestructura_lote_propagacion WHERE cod_infraestructura_FK = %s
        """)

        val = ([seed['codSemilla']])

        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        if len(results) > 0:
            seed['idLotePropagacion'] = results[0]

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_seed_propagation_forestal): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_seed_propagation_forestal): ", e)
        return CustomException('Ocurrio un error al obtener los lotes de propagación de una semilla', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close() 


# Get the fertilizer infrastructure in forestal event
def get_fert_infrastructure_forestal(id_esp, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
            SELECT cod_infraestructura_forestal AS "codFert", cod_tipo_fertilizante_FK AS "idTipoFertilizante", nombre_fertilizante AS nombre,
            fecha_adquisicion_fert::TEXT AS "fechaAdquisicion", cantidad::TEXT AS "canFertilizante", valor_pesos_afectacion::TEXT AS "valPesos",
			tipo_fertilizante AS "nameTipoFertilizante"
			FROM Infraestructura_forestal
			LEFT JOIN Tipo_fertilizante ON cod_tipo_fertilizante = cod_tipo_fertilizante_fk
            WHERE cod_especie_forestal_sembrada_FK = %s AND cod_tipo_infraestrucrtura_FK = 2
        """)
        
        val = ([id_esp])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_fert_infrastructure_forestal): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_fert_infrastructure_forestal): ", e)
        return CustomException('Ocurrio un error al obtener los fertilizantes', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close() 


# Get the plaguicide infrastructure in forestal event
def get_plag_infrastructure_forestal(id_esp, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_infraestructura_forestal AS "codPlag", cod_tipo_plaguicida_FK AS "idTipoPlaguicida", presentacion_plaguicida AS "idTipoPresentacion",
            cant_plaguicidas_kg AS "cantPlaguicidaKg", cant_plaguicidas_lt AS "cantPlaguicidaLt", vlr_pesos_afectacion_pla::TEXT AS "valPesos",
			presentacion AS "nameTipoPresentacion", tipo_plaguicida AS "nameTipoPlaguicida"
			FROM Infraestructura_forestal
            LEFT JOIN Presentacion ON cod_presentacion = presentacion_plaguicida
			LEFT JOIN Tipo_plaguicida ON cod_tip_plaguicida = cod_tipo_plaguicida_fk
			WHERE cod_especie_forestal_sembrada_FK = %s AND cod_tipo_infraestrucrtura_FK = 3 
        """)

        val = ([id_esp])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_plag_infrastructure_forestal): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_plag_infrastructure_forestal): ", e)
        return CustomException('Ocurrio un error al obtener los plaguicidas', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close() 


# Get the affected machinery in forestal event
def get_maq_infrastructure_forestal(id_esp, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_infraestructura_forestal AS "codMaq", cod_tipo_maquinaria_FK AS "idTipoMaquinariaAgricola", 
            date_part('year', CURRENT_DATE)::INT - edad_equipo_maq AS "anoAdquisicion", vlr_pesos_afectacion_maq::TEXT AS "valorPesos",
            porc_dism_prod_maq AS "porceDisminucion", tipo_maquinaria "nameTipoMaquinaria"
			FROM Infraestructura_forestal 
			LEFT JOIN Tipo_maquinaria ON cod_tipo_maquinaria = cod_tipo_maquinaria_fk
			WHERE cod_especie_forestal_sembrada_FK = %s AND 
            cod_tipo_infraestrucrtura_FK = 4
        """)

        val = ([id_esp])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_maq_infrastructure_forestal): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_maq_infrastructure_forestal): ", e)
        return CustomException('Ocurrio un error al obtener la maquinaria afectada', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close() 


# Get the credit data of an agro event
def get_agro_credit_event(cod_cult, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_credito AS "codCredito", cod_entidad_credito_FK AS "idEntidadesBancarias", porc_costos_cultivo AS "porceCostoCredito"
            FROM Credito WHERE cod_cultivo_FK = %s
        """)
        val = ([cod_cult])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_agro_credit_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_agro_credit_event): ", e)
        return CustomException('Ocurrio un error al obtener los datos del crédito', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close() 


# Get the assurance data of an event
def get_agro_assurance_event(cod_cult, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_aseguramiento AS "codAseguramiento", valor_cultivo_asegurado AS "valCultiAsegurado", cod_tipo_seguro_FK AS "tipoSeguro"
            FROM Aseguramiento WHERE cod_cultivo_afectado_FK = %s
        """)

        val = ([cod_cult])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
    except CustomException as e:
        print("ERROR (eventos/database_manager/get_agro_assurance_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_agro_assurance_event): ", e)
        return CustomException('Ocurrio un error al obtener los datos del aseguramiento', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close() 


# Get the infrastructure data of an agro event
def get_agro_infra(cod_cult, connection):
    try:
        cursor = connection.cursor()

        results = {
            'tipoInfraSemilla': [],
            'tipoInfraFertilizante': [],
            'tipoInfraPlaguicidas': [],
            'tipoInfraMaquinaria': []
        }


        sql = ("""
            SELECT cod_infraestructura AS "codInfra", cod_tipo_infraestructura_FK AS "idTipoMaquinaria", cod_especie_FK AS "tipoCultivo", 
            cant_semilla_almacenada_kg AS "canSemillas", vlr_semilla_pesos AS "valPesos", material_siembra_fk AS "materiralSiembra",
            cant_semilla_siembra AS "cantSemillas", unidad_reporte_cant_semilla_fk AS "medidaSemilla", 
            eqv_carga_kg_semilla AS "equivaleKilos", eqv_carga_kg_semilla_otro AS "nuevaEquivalencia", fuente_semilla_fk AS "fuenteSemilla",
			tipo_cultivo AS "nameTipoCultivo", material AS "nameTipoMaterial", und_cosecha AS "nameMedidaSemilla",
			fuente_semilla AS "nameFuenteSemilla"
            FROM infraestructura 
            LEFT JOIN Cultivo_Infraestructura ON cod_infraestructura_FK = cod_infraestructura 
			LEFT JOIN Tipo_cultivo ON cod_tipo_cultivo = cod_especie_fk
			LEFT JOIN Material_siembra ON cod_material = material_siembra_fk
			LEFT JOIN Unidad_cosecha ON unidad_reporte_cant_semilla_fk = cod_und_cosecha
			LEFT JOIN Fuente_semilla ON fuente_semilla_fk = cod_fuente_semilla
            WHERE cod_cultivo_FK = %s AND cod_tipo_infraestructura_FK = 1
        """)

        val = ([cod_cult])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['tipoInfraSemilla'].append(dict(zip(columns, row)))

        sql = ("""
            SELECT cod_infraestructura AS "codInfra", cod_tipo_infraestructura_FK AS "idTipoMaquinaria", cod_tipo_fertilizante_FK AS "idTipoFertilizante",
            nom_fertilizante AS "nombre", fch_adquisicion AS "fechaAdquisicion", cant_fert_almac_afect AS "canFertilizante",
            vlr_fertilizante_almacenado AS "valPesos", tipo_fertilizante AS "nameTipoFertilizante"
            FROM infraestructura 
			LEFT JOIN Cultivo_Infraestructura ON cod_infraestructura_FK = cod_infraestructura 
			LEFT JOIN tipo_fertilizante ON cod_tipo_fertilizante = cod_tipo_fertilizante_FK
            WHERE cod_cultivo_FK = %s AND cod_tipo_infraestructura_FK = 2
        """)

        val = ([cod_cult])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['tipoInfraFertilizante'].append(dict(zip(columns, row)))

        sql = ("""
            SELECT cod_infraestructura AS "codInfra", cod_tipo_infraestructura_FK AS "idTipoMaquinaria", cod_tipo_plaguicida_FK AS "idTipoPlaguicida",
            cod_presentacion_FK AS "idTipoPresentacion", cantidad_plaguicidas_almac_afec_kg AS "cantPlaguicidaKg", cantidad_plaguicidas_almac_afec_litros AS "cantPlaguicidaLt",
            vlr_pesos_plaguicidas AS "valPesos", presentacion AS "nameTipoPresentacion", tipo_plaguicida AS "nameTipoPlaguicida"
            FROM infraestructura 
			LEFT JOIN Cultivo_Infraestructura ON cod_infraestructura_FK = cod_infraestructura 
			LEFT JOIN Presentacion ON cod_presentacion_fk = cod_presentacion 
			LEFT JOIN Tipo_plaguicida ON cod_tip_plaguicida = cod_tipo_plaguicida_fk
            WHERE cod_cultivo_FK = %s AND cod_tipo_infraestructura_FK = 3
        """)

        val = ([cod_cult])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['tipoInfraPlaguicidas'].append(dict(zip(columns, row)))

        sql = ("""
            SELECT cod_infraestructura AS "codInfra", cod_tipo_infraestructura_FK AS "idTipoMaquinaria", cod_tipo_maq_agr_afec_FK AS "idTipoMaquinariaAgricola",
            EXTRACT(YEAR FROM fch_adquisicion_equipo) AS "anoAdquisicion", vlr_pesos_afectacion_maq AS "valorPesos", porc_disminuyo_prod_afect_maq AS "porceDisminucion",
			tipo_maquinaria AS "nameTipoMaquinaria"
            FROM infraestructura 
			LEFT JOIN Cultivo_Infraestructura ON cod_infraestructura_FK = cod_infraestructura 
			LEFT JOIN Tipo_maquinaria ON cod_tipo_maquinaria = cod_tipo_maq_agr_afec_fk
            WHERE cod_cultivo_FK = %s AND cod_tipo_infraestructura_FK = 4
        """)

        val = ([cod_cult])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['tipoInfraMaquinaria'].append(dict(zip(columns, row)))
        
    except CustomException as e:
        print("ERROR (eventos/database_manager/get_agro_infra): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_agro_infra): ", e)
        return CustomException('Ocurrio un error al obtener los datos de la infraestructura agro', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close() 


# Get the infrastructure data of a peq event
def get_infrastructure_peq_event(cod_peq, connection):
    try:
        cursor = connection.cursor()
        results = {
            "dataInsumos": [],
            "dataMaquinaria": [],
            "dataInfraestructura": []
        }

        sql = ("""
            SELECT cod_infraestructura AS "codInfraestructura", cod_tipo_insumo_FK AS "tipoInsumo", tipo_insumo_nom_otro AS "nuevoInsumo", nombre_comercial AS "nombreComercial",
            cantidad_insumos AS "cantInsumo", cod_unidad_FK AS "unidadMedida", vlr_pesos_afectacion AS "valorBienes", tipo_insumo AS "nameTipoInsumo",
			und_cosecha AS "nameUnidadMedida"
			FROM afectacion_peq
            LEFT JOIN Tipo_insumo ON cod_tipo_insumo = cod_tipo_insumo_fk
			LEFT JOIN Unidad_cosecha ON cod_und_cosecha = cod_unidad_FK
			WHERE cod_novedad_pecuaria_FK = %s
        """)

        val = ([cod_peq])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['dataInsumos'].append(dict(zip(columns, row)))


        sql = ("""
            SELECT cod_maquinaria_bba AS "codMaquinariaBBA", cod_tipo_maquinaria_FK AS "tipoMaquinariaBba", nombre_maquinaria AS "nombreMaquinariaBba",
            vlr_pesos_afectacion AS "valorReparacionBba", tipo_maquinaria AS "nombreMaquiBba"
			FROM maquinaria_bba 
			LEFT JOIN Tipo_maquinaria ON cod_tipo_maquinaria = cod_tipo_maquinaria_FK
			WHERE cod_novedad_pecuaria_FK = %s
        """)

        val = ([cod_peq])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['dataMaquinaria'].append(dict(zip(columns, row)))

        sql = ("""
            SELECT cod_maquinaria_pem AS "codMaquinariaPEM", cod_tipo_maquinaria_FK AS "tipoMaquinariaPem", nombre_marca_bien AS "nombreMarcaPem",
            vlr_pesos_afectacion AS "valorReparacionPem" , tipo_maquinaria AS "nombreMaquiPem"
            FROM maquinaria_pem 
            LEFT JOIN Tipo_maquinaria ON cod_tipo_maquinaria = cod_tipo_maquinaria_FK
            WHERE cod_novedad_pecuaria_FK = %s
        """)

        val = ([cod_peq])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['dataMaquinaria'].append(dict(zip(columns, row)))

        sql = ("""
            SELECT cod_infraestructura_pecuario AS "codInfraPeq", cod_tipo_activo_FK AS "tipActivo", nombre_equipo AS "nombreEquipo", 
            fecha_adquisicion_bien::TEXT AS "fechaAdquisicion", fecha_adquisicion_bien::TEXT AS "fechaConstruc", precio_pagado AS "valorPagado",
			precio_pagado AS "valorPagadoConstruc", vlr_invertido_reparacion AS "valorReponer", vlr_invertido_reparacion AS "valorReponerConstruc",
            cod_tipo_construccion_fk AS "tipAfecta", area_m2_construccion_afectada AS "areaAfectada", vlr_invertido_re_construccion AS "valorReparacion",
            tiempo_realizar_reparacion_meses AS "mesesReparacion", tipo_activo AS "nombreActivo", tipo_construccion AS "nombreTipoAfecta"
			FROM Infraestructura_pecuario 
			LEFT JOIN Tipo_activo ON cod_tipo_activo = cod_tipo_activo_fk
			LEFT JOIN Tipo_construccion ON cod_tipo_construccion = cod_tipo_construccion_fk
			WHERE cod_novedad_pecuario_FK = %s
        """)

        val = ([cod_peq])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['dataInfraestructura'].append(dict(zip(columns, row)))
        
    except CustomException as e:
        print("ERROR (eventos/database_manager/get_infrastructure_peq_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_infrastructure_peq_event): ", e)
        return CustomException('Ocurrio un error al obtener los datos de la infraestructura pecuario', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close() 


# Get the infrastructure data of an apiarian event
def get_infrastructure_api_event(cod_api, connection):
    try:
        cursor = connection.cursor()

        results = {
            "insumos": [],
            "maquinarias": []
        }

        sql = ("""
            SELECT cod_infraestructura AS "codInfraestructura", cod_tipo_insumo_FK AS "tipoInsumo", tipo_insumo AS "nameTipoInsumo", tipo_insumo_nom_otro AS "nuevoInsumo", 
			nombre_comercial AS "nombreComercial", cantidad_insumos AS "cantInsumo", cod_unidad_FK AS "unidadMedida", vlr_pesos_afectacion AS "valorBienes",
			unidad AS "nameUnidadMedida"
			FROM afectacion_peq LEFT JOIN tipo_insumo ON cod_tipo_insumo = cod_tipo_insumo_fk LEFT JOIN Unidad ON cod_unidad_fk = cod_unidad
			WHERE cod_novedad_pecuaria_FK = %s
        """)

        val = ([cod_api])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['insumos'].append(dict(zip(columns, row)))

        sql = ("""
            SELECT cod_maquinaria_pem AS "codMaquinariaPEM", cod_tipo_maquinaria_FK AS "tipoMaquinariaPem", nombre_marca_bien AS "nombreMarcaPem",
            tipo_maquinaria AS "nameTipoMaquinariaPem", vlr_pesos_afectacion AS "valorReparacionPem" FROM maquinaria_pem 
			LEFT JOIN tipo_maquinaria ON cod_tipo_maquinaria = cod_tipo_maquinaria_fk 
			WHERE cod_novedad_pecuaria_FK = %s
        """)

        val = ([cod_api])
        cursor.execute(sql, val)

        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results['maquinarias'].append(dict(zip(columns, row)))
        
    except CustomException as e:
        print("ERROR (eventos/database_manager/get_infrastructure_api_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_infrastructure_api_event): ", e)
        return CustomException('Ocurrio un error al obtener los datos de la infraestructura apícola', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()   


# Get the fishing type of an specific pesq event
def get_fishing_type_pesq_event(cod_pesq, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_tipo_pesqueria AS "tipoPesqueria" FROM Tipo_pesqueria INNER JOIN Novedad_pesquera_tipo_pes ON cod_tipo_pesquera_FK = cod_tipo_pesqueria
            WHERE cod_novedad_pesquera_FK = %s
        """)

        val = ([cod_pesq])
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(row[0])

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_fishing_type_pesq_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_fishing_type_pesq_event): ", e)
        return CustomException('Ocurrio un error al obtener los datos del tipo de pesquería', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()   


# Get the embarkations of an specific pesq event
def get_embq_affected_event(cod_pesq, connection):
    try:
        cursor = connection.cursor()
        sql = ("""
            SELECT cod_embarcacion AS "codEmbq", cod_tipo_embarcacion_FK AS "tipoEmbarcacion", tipo_embarcacion AS "tipoEmbarcacionNombre", cod_material_embarcacion_fk "material",
            material_embq As "nameMaterial", cod_tipo_propulsion_fk AS "propulsion", tipo_propulsion AS "namePropulsion", patente_embarcacion AS "patenteEmbarcacion",
            eslora_mts AS "esloraEmbarcacion", edad, valor_afectacion_pesos AS "valorEmbarcacion", observaciones AS "observacionEmbarcacion" FROM Embarcacion LEFT JOIN Tipo_embarcacion 
            ON cod_tipo_embarcacion = cod_tipo_embarcacion_FK LEFT JOIN Material_embarcacion ON cod_material_embq = cod_material_embarcacion_fk LEFT JOIN Tipo_propulsion ON cod_tipo_propulsion = cod_tipo_propulsion_fk
            WHERE cod_novedad_pesquera_fk = %s
        """)

        val = ([cod_pesq])
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_embq_affected_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_embq_affected_event): ", e)
        return CustomException('Ocurrio un error al obtener los datos del tipo de las embarcaciones', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()  


# Get the affected networks of an specific pesq event
def get_red_affected_event(cod_pesq, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_infraestructura_pesquera AS "codInfraestructura", cod_tipo_red_fk AS "tipoRedes", tipo_red AS "tipoRedesNombre", nombre_equipo AS "marcaRed", 
            fecha_adquisicion_bien::TEXT AS "fechaAdquisicion", precio_pagado AS "valorRedes", cod_tipo_perdida_fk AS "tipoPerdida", tipo_perdida AS  "tipoPerdidaNombre"
            FROM Infraestructura_pesquera LEFT JOIN Tipo_perdida ON cod_tipo_perdida = cod_tipo_perdida_fk LEFT JOIN Tipo_red ON cod_tipo_red = cod_tipo_red_fk 
            WHERE cod_novedad_pesquera_FK = %s
        """)

        val = ([cod_pesq])

        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_red_affected_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_red_affected_event): ", e)
        return CustomException('Ocurrio un error al obtener los datos de las redes afectadas', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()  


# Get the infrastructure affected for pesq event
def get_infrastructure_pesq_event(cod_pesq, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_infraestructura_pesquera AS "codInfraestructura", cod_tipo_activo_FK AS "activoProductivo", nombre_equipo AS "nombreEquipo", fecha_adquisicion_bien::TEXT AS "fechaAdquisicion",
            precio_pagado AS "valorActivo", vlr_invertido_reparacion AS "valorReponer", cod_tipo_construccion_fk AS "tipoConstruccion", tipo_construccion AS "nombreTipoConstruccion",
			area_metros_cuadrados_construccion_afectada AS "areaAfectada", vlr_invertido_reconstruccion AS "valorInvertidoAdecuacion", tiempo_necesario_reconstruccion AS "mesesReconstruccion" 
			FROM Infraestructura_pesquera LEFT JOIN tipo_construccion_pesq ON cod_tipo_construccion = cod_tipo_construccion_fk WHERE cod_novedad_pesquera_FK = %s AND 
            cod_tipo_activo_FK IS NOT NULL
        """)

        val = ([cod_pesq])

        cursor.execute(sql,val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_infrastructure_pesq_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_infrastructure_pesq_event): ", e)
        return CustomException('Ocurrio un error al obtener los datos de la infraestructura afectada', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()  

# This function gets the specific calcs for the direct costs agro prediction
def get_calcs(dpto, specie, variable,connection):
    try:
        cursor = connection.cursor()
        if variable == -1:
            results = {
                'costoPromJonal': [],
                'jornales': [],
                'gasto': []
            }
            

            sql = ("""
                SELECT row_to_json(t) FROM (
                SELECT descripcion,valor::TEXT,actividad_calculo, cod_tipo_actividad FROM Calculos JOIN Actividad_calculos 
                ON descripcion = id_actividad_calculo where id_dpto_fk = %s AND id_especie = %s AND 
                SUBSTRING(actividad_calculo, 1, 6) = 'Número') AS t;
            """)

            val = (dpto, specie)

            cursor.execute(sql, val)
            
            for row in cursor.fetchall():
                results['jornales'].append(row[0])

            sql = ("""
                SELECT row_to_json(t) FROM (
                SELECT descripcion,valor::TEXT,actividad_calculo, cod_tipo_actividad FROM Calculos JOIN Actividad_calculos 
                ON descripcion = id_actividad_calculo where id_dpto_fk = %s AND id_especie = %s AND 
                SUBSTRING(actividad_calculo, 1, 5) = 'Gasto') AS t;
            """)

            val = (dpto, specie)

            cursor.execute(sql, val)
            
            for row in cursor.fetchall():
                results['gasto'].append(row[0])
            
            sql = ("""
                SELECT descripcion,valor::TEXT,actividad_calculo, cod_tipo_actividad FROM Calculos JOIN Actividad_calculos 
                ON descripcion = id_actividad_calculo where id_dpto_fk = %s AND id_especie = %s
                AND cod_tipo_actividad = '-1';
            """)

            val = (dpto, specie)

            cursor.execute(sql, val)
            
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                results['costoPromJonal'].append(dict(zip(columns, row)))

            return results, 200
        else:
            sql = ("""
                SELECT row_to_json(row) FROM 
                (SELECT cantidad, valor_unitario, costo FROM Variable_actividad_valores WHERE id_dpto_fk = %s
                AND id_especie_fk = %s AND variable_actividad_fk = %s) AS row;
            """)

            val = (dpto, specie, variable)

            cursor.execute(sql, val)
            results = []

            for row in cursor.fetchall():
                results.append(row[0])

            return results, 200


    except CustomException as e:
        print("ERROR (eventos/database_manager/get_calcs): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_calcs): ", e)
        return CustomException('Ocurrio un error al obtener los datos de los cálculos', str(e)), 500
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Update automatically the values of agro costs 
def update_calcs(dpto, specie,variable,cant,unit,cost,idU,connection):
    try:
        cursor = connection.cursor()
        ip = request.remote_addr

        # Updating values by unit
        sql = ("""
            UPDATE Variable_actividad_valores SET cantidad = %s, valor_unitario = %s, costo = %s 
            WHERE id_dpto_fk = %s AND id_especie_fk = %s AND variable_actividad_fk = %s
            RETURNING id_variable_actividad_valores
        """)

        val = (cant, unit, cost, dpto, specie, variable)

        cursor.execute(sql, val)

        idV = cursor.fetchone()[0]

        audit = {
            'cantidad': cant,
            'valor_unitario': unit,
            'costo': cost
        }

        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(idU), str(ip), 'Actualización de registro', 'Variable_actividad_valores', int(idV), json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')


        # Searching all the calcs involved
        calcs = []

        sql = ("""
            SELECT row_to_json(row) FROM (SELECT * FROM Calculos WHERE id_dpto_fk = %s AND id_especie=%s) AS row;
        """)

        val = (dpto, specie)
        cursor.execute(sql, val)

        for row in cursor.fetchall():
            calcs.append(row)
        
        #Updating each calc involved
        for calc in calcs:
            acum = 0

            descp = calc[0]['descripcion']
            sql = ("""
                SELECT row_to_json(row) FROM (SELECT formula FROM Actividad_calculos WHERE id_actividad_calculo = %s) AS row;
            """)

            val = ([descp])
            cursor.execute(sql, val)

            formula = cursor.fetchone()[0]['formula']
            if formula != None:
                formula_tokens = formula.split('+')

                for form in formula_tokens:
                    sql = ("""
                        SELECT row_to_json(row) FROM (SELECT * FROM Actividad_calculos_variable_actividad_valores 
                        WHERE id_actividad_calculos_variable_actividad_valores = %s) AS row
                    """)

                    val = ([int(form)])

                    cursor.execute(sql, val)

                    var = cursor.fetchone()[0]

                    sql = ("""
                        SELECT row_to_json(row) FROM (SELECT cantidad, valor_unitario, costo FROM Variable_actividad_Valores
                        WHERE id_dpto_fk = %s AND id_especie_fk = %s AND variable_actividad_fk = %s) AS row;
                    """)

                    val = (dpto, specie, int(var['id_variable_actividad_fk']))

                    cursor.execute(sql, val)
                    
                    vals = cursor.fetchone()[0]

                    if var['variable_actividad_valores_sigla'] == 'Ca':
                        acum += int(vals['cantidad'])
                    elif var['variable_actividad_valores_sigla'] == 'Vu':
                        acum += int(vals['valor_unitario'])
                    elif var['variable_actividad_valores_sigla'] == 'Co':
                        acum += int(vals['costo'])
            
            sql = ("""
                UPDATE Calculos SET valor = %s WHERE id_calculo = %s
            """)

            val = (acum, calc[0]['id_calculo'])
            cursor.execute(sql, val)

            audit = {
                'valor': acum
            }

            sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

            val = (
                int(idU), str(ip), 'Actualización de registro', 'Calculos', int(calc[0]['id_calculo']), json.dumps(audit)
            )
            cursor.execute(sql, val)

            if not cursor.fetchone()[0]:
                raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

            

    except CustomException as e:
        print("ERROR (eventos/database_manager/update_calcs): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/update_calcs): ", e)
        return CustomException('Ocurrio un error al actualizar los datos de los cálculos', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Get the actvities of agro calcs
def get_activities_agro_calc(connection):
    try:
        cursor = connection.cursor()
        results = []

        sql = ("""
            SELECT row_to_json(row) FROM (SELECT * FROM Variable_actividad) AS row;
        """)

        cursor.execute(sql)

        for row in cursor.fetchall():
            results.append(row[0])

    except CustomException as e:
        print("ERROR (eventos/database_manager/get_activities_agro_calc): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/get_activities_agro_calc): ", e)
        return CustomException('Ocurrio un error al obtener las actividades de los cálculos', str(e)), 500
    else:
        return results, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()

# Search if the user is allowed to validate the given event
def validate_event(id_event, id_user, rol, connection):
    try:
        cursor=connection.cursor()
        ip = request.remote_addr

        if rol == 7: # Validador municipal
            sql = ("""
                SELECT * FROM Evento JOIN Validador_municipal ON cod_municipio_fk = cod_mun_fk 
                WHERE usuario = %s AND cod_evento = %s
            """)

            val = (id_user, id_event)
            cursor.execute(sql, val)
            
            if len(cursor.fetchall()) > 0:
                validated = validate_event_helper(id_event, id_user, ip, connection)
                if validated[1] != 200:
                    raise_exception(validated[0].to_dict()['message'],  validated[0].to_dict()['error'])
            else:
                raise_exception('Su jurisdicción no le permite validar este evento', 'Intento fallido de validar el evento: '+str(id_event)+
                ' por parte del usuario: '+str(id_user))
        elif rol == 10 or rol == 11: # Admin y super user
            validated = validate_event_helper(id_event, id_user, ip, connection)
            if validated[1] != 200:
                raise_exception(validated[0].to_dict()['message'],  validated[0].to_dict()['error'])
        else:
            raise_exception('No tiene permisos para validar los eventos','No tiene permisos para validar los eventos')

     
    except CustomException as e:
        print("ERROR (eventos/database_manager/validate_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/validate_event): ", e)
        return CustomException('Ocurrio un error al validar el evento', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Validates a given event
def validate_event_helper(id_event, id_user, ip, connection):
    try:
        cursor = connection.cursor()
        mail = get_email_service()
        results = []


        sql = ("""
            SELECT * FROM Evento WHERE cod_evento = %s
        """)

        val = ([id_event])
        cursor.execute(sql,val)
        
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        if results[0]['validado']:
            raise_exception('El evento ya fue validado', 'El evento '+str(id_event)+' ya fue validado')


        sql = ("""
            UPDATE Evento SET validado = true WHERE cod_evento = %s
        """)

        val = ([id_event])

        cursor.execute(sql,val)

        audit = {
            'validado': True
        }

        sql = ("""
            SELECT log_audit(%s,%s,%s,%s,%s,%s)
        """)

        val = (
            int(id_user), str(ip), 'Actualización de registro', 'Evento', int(id_event), json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')

        sql = ("""
            SELECT email FROM Usuarios WHERE id = %s
        """)

        val = ([results[0]['cod_encuestador_fk']])
        cursor.execute(sql, val)

        email = cursor.fetchone()[0]

        title = "Evento validado"
        body = "Su evento "+str(results[0]['cod_evento'])+" registrado el "+str(results[0]['fecha_registro_evento']) +" ha sido validado"

        sql = ("""
            INSERT INTO Notificaciones(titulo, descripcion, id_usuario, id_creador) VALUES(%s,%s,%s,%s) RETURNING id_notificacion
        """)

        val = (title, body, results[0]['cod_encuestador_fk'], id_user)
        cursor.execute(sql, val)

        id_not = cursor.fetchone()[0]

        audit = {
            'titulo': title, 
            'descripcion': body,
            'id_usuario': results[0]['cod_encuestador_fk'],
            "id_creador": id_user 
        }

        sql = ("""
                SELECT log_audit(%s,%s,%s,%s,%s,%s)
            """)

        val = (
            int(id_user), str(ip), 'Creación de registro', 'Notificaciones', int(id_not), json.dumps(audit)
        )

        cursor.execute(sql, val)

        if not cursor.fetchone()[0]:
            raise_exception('Ocurrio un error, intente de nuevo', 'Error al auditar')
        

        sended = send_notification_email(Config.EMAIL_SENDER, email, title, body, mail)
        if sended[1] != 200:
            raise_exception(sended[0].to_dict()['message'],  sended[0].to_dict()['error'])
    except CustomException as e:
        print("ERROR (eventos/database_manager/validate_event_helper): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/validate_event_helper): ", e)
        return CustomException('Ocurrio un error al validar el evento', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


def check_non_validated_event(id_evento, connection):
    try:
        cursor = connection.cursor()
        validated = False

        sql = ("""
            SELECT validado FROM Evento WHERE cod_evento = %s
        """)

        val = ([id_evento])

        cursor.execute(sql, val)

        validated = cursor.fetchone()[0]
    except CustomException as e:
        print("ERROR (eventos/database_manager/check_non_validated_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/check_non_validated_event): ", e)
        return CustomException('Ocurrió un error al editar el evento', str(e)), 500
    else:
        return validated, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()

# This function transfer the tracings from an event to other
def transfer_tracings(idNewEvento, idOldEvento, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            UPDATE Evento_seguimiento SET cod_evento_fk = %s WHERE cod_evento_fk = %s 
        """)

        val = (idNewEvento, idOldEvento)
        cursor.execute(sql, val)

    except CustomException as e:
        print("ERROR (eventos/database_manager/transfer_tracings): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/transfer_tracings): ", e)
        return CustomException('Ocurrió un error al modificar el evento', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Transfer the attached tracings to the new event
def transfer_attached_tracings(idNewEvento, idOldEvento, connection):
    try:
        cursor = connection.cursor()

        ruta = Config.UPLOAD_FOLDER+Config.UPLOAD_SEGUIMIENTO
        rutaOldEvento = ruta +'/'+ str(idOldEvento)
        rutaNewEvento = ruta +'/'+ str(idNewEvento)

        files = os.listdir(ruta)

        existOld = [file for file in files if file == str(idOldEvento)]

        if existOld:
            os.rename(rutaOldEvento, rutaNewEvento)

        sql = ("""
            UPDATE Evento_seguimiento_adju SET ruta = %s WHERE ruta = %s 
        """)

        val = (rutaNewEvento, rutaOldEvento)

        cursor.execute(sql, val)

    except CustomException as e:
        print("ERROR (eventos/database_manager/transfer_attached_tracings): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/transfer_attached_tracings): ", e)
        return CustomException('Ocurrió un error al modificar el evento', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()


# Transfer the attached files of the old event to the new event
def transfer_attached_event(idNewEvento, idOldEvento, connection):
    try:
        cursor = connection.cursor()

        ruta = Config.UPLOAD_FOLDER+Config.UPLOAD_EVENTO
        rutaOldEvento = ruta +'/'+ str(idOldEvento)
        rutaNewEvento = ruta +'/'+ str(idNewEvento)

        files = os.listdir(ruta)

        existNew = [file for file in files if file == str(idNewEvento)]
        existOld = [file for file in files if file == str(idOldEvento)]

        # If both directories exists then the files from the old one are sended to the new one
        if existNew and existOld:
            for file in os.listdir(rutaOldEvento):
                shutil.move(rutaOldEvento+'/'+file, rutaNewEvento+'/'+file)

            # Remove old directory
            os.rmdir(rutaOldEvento)

        # If there are just files in the old event they are sended to a new event folder 
        elif existOld and not existNew:
            os.makedirs(rutaNewEvento, exist_ok=True)

            for file in os.listdir(rutaOldEvento):
                shutil.move(rutaOldEvento+'/'+file, rutaNewEvento+'/'+file)

            # Remove old directory
            os.rmdir(rutaOldEvento)

        sql = ("""
            UPDATE Evento_adjunto SET ruta = %s, cod_evento_fk = %s WHERE ruta = %s 
        """)
        
        val = (rutaNewEvento, idNewEvento,rutaOldEvento)
        
        cursor.execute(sql, val)
        
    except CustomException as e:
        print("ERROR (eventos/database_manager/transfer_attached_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/transfer_attached_event): ", e)
        return CustomException('Ocurrió un error al modificar el evento', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()   



# Deletes an specific event and it's related information
def delete_event(id_evento, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT * FROM Evento_sist_prod_afectado WHERE cod_evento_FK = %s
        """)

        val = ([id_evento])

        cursor.execute(sql, val)

        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        for sis in results:
            if sis['cod_sist_prod_afect_fk'] == 1:
                delete = delete_agro(sis['cod_cultivo_afectado_fk'], connection)
                if delete[1] != 200:
                    raise_exception(delete[0].to_dict()['message'],  delete[0].to_dict()['error'])
                
            elif sis['cod_sist_prod_afect_fk'] == 2:
                delete = delete_peq(sis['cod_novedad_pecuaria_fk'], connection)
                if delete[1] != 200:
                    raise_exception(delete[0].to_dict()['message'],  delete[0].to_dict()['error'])

            elif sis['cod_sist_prod_afect_fk'] == 3:
                delete = delete_forestal(sis['cod_especie_forestal_fk'], connection)
                if delete[1] != 200:
                    raise_exception(delete[0].to_dict()['message'],  delete[0].to_dict()['error'])

            elif sis['cod_sist_prod_afect_fk'] == 4:
                delete = delete_pesq(sis['cod_novedad_pesquera_fk'], connection)
                if delete[1] != 200:
                    raise_exception(delete[0].to_dict()['message'],  delete[0].to_dict()['error'])

            elif sis['cod_sist_prod_afect_fk'] == 5:
                delete = delete_peq(sis['cod_novedad_pecuaria_apicola_fk'], connection)
                if delete[1] != 200:
                    raise_exception(delete[0].to_dict()['message'],  delete[0].to_dict()['error'])
            
        
        deleted_prod = delete_producers(id_evento, connection)
        if deleted_prod[1] != 200:
            raise_exception('No se ha podido actualizar los productores', 'No se ha podido actualizar los productores')


        sql = ("""
            DELETE FROM Evento WHERE cod_evento = %s
        """)

        val = ([id_evento])

        cursor.execute(sql, val)

    except CustomException as e:
        print("ERROR (eventos/database_manager/delete_event): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/delete_event): ", e)
        return CustomException('Ocurrió un error al modificar el evento', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()  


# Delete the producers of an event
def delete_producers(id_evento, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT cod_producto_agro FROM Evento_productos_agropecuario WHERE cod_evento_fk = %s
        """)

        val = ([id_evento])

        cursor.execute(sql, val)

        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        for res in results:
            sql = ("""
                SELECT cod_caladero_fk FROM productor_agro_caladero WHERE cod_productor_agro_fk = %s    
            """)

            val = ([res['cod_producto_agro']])

            cursor.execute(sql, val)

            n_results = []
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                n_results.append(dict(zip(columns, row)))

            for n_res in n_results:
                sql = ("""
                    DELETE FROM Caladeros WHERE cod_caladero =  %s
                """)

                val = ([n_res['cod_caladero_fk']])
                
                cursor.execute(sql, val)

            sql = ("""
                DELETE FROM Productor_agropecuario WHERE cod_productor_agropecuario = %s
            """)

            val = ([res['cod_producto_agro']])

            cursor.execute(sql, val)
        #raise_exception('mm', 'mm')
        
    except CustomException as e:
        print("ERROR (eventos/database_manager/delete_producers): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/delete_producers): ", e)
        return CustomException('Ocurrió un error al modificar los productores', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close() 

# Delete the agro system of an event
def delete_agro(id, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            SELECT * FROM Cultivo_Infraestructura WHERE cod_cultivo_FK = %s
        """)

        val = ([id])

        cursor.execute(sql, val)

        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        for res in results:
            print(res)
            sql = ("""
                DELETE FROM infraestructura WHERE cod_infraestructura = %s
            """)

            val = ([res['cod_infraestructura_fk']])

            cursor.execute(sql, val)

        sql = ("""
            DELETE FROM Cultivos_afectados WHERE cod_cultivo = %s
        """)

        val = ([id])

        cursor.execute(sql, val)

    except CustomException as e:
        print("ERROR (eventos/database_manager/delete_agro): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/delete_agro): ", e)
        return CustomException('Ocurrió un error al modificar el evento', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()  


# Delete the peq and apiarian system of an event
def delete_peq(id, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            DELETE FROM Novedad_pecuaria WHERE cod_novedad_peq = %s
        """)

        val = ([id])

        cursor.execute(sql, val)

    except CustomException as e:
        print("ERROR (eventos/database_manager/delete_peq): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/delete_peq): ", e)
        return CustomException('Ocurrió un error al modificar el evento', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()   


# Delete the forestal system of an event
def delete_forestal(id, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            DELETE FROM Especie_forestal_sembrada WHERE cod_especie_forestal_sembrada = %s
        """)

        val = ([id])

        cursor.execute(sql, val)
    except CustomException as e:
        print("ERROR (eventos/database_manager/delete_forestal): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/delete_forestal): ", e)
        return CustomException('Ocurrió un error al modificar el evento', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()   


# Delete the pesq system of an event
def delete_pesq(id, connection):
    try:
        cursor = connection.cursor()

        sql = ("""
            DELETE FROM Novedad_pesquera WHERE cod_novedad_pesq = %s
        """)

        val = ([id])

        cursor.execute(sql, val)
    except CustomException as e:
        print("ERROR (eventos/database_manager/delete_pesq): ", e.to_dict()['error'])
        return e, 500
    except Exception as e:
        print("ERROR (eventos/database_manager/delete_pesq): ", e)
        return CustomException('Ocurrió un error al modificar el evento', str(e)), 500
    else:
        return True, 200
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()  