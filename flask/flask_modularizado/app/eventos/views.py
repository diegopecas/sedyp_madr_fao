import re
import jwt
import datetime
import os
import pathlib
import json

from . import event
from app.decorators import token_required
from flask import jsonify, request, flash, send_file
from app.eventos.database_manager import *
from app.config import Config
from werkzeug.utils import secure_filename
from app.helpers import *
from app.exceptions import CustomException
from app.services.database_service import DatabaseService


@event.route('/getEventos', methods=['GET'])
@token_required
def get_events():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso, u.rol FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 2)
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
                rol = perm['rol']
                res = get_event(connection, 1, id_user, rol)
                if(res[1] != 200):
                    raise_exception(res[0].to_dict()['message'], res[0].to_dict()['error'])

                break
            elif perm['id_permiso'] == 2:
                _perm = True
                rol = perm['rol']
                res = get_event(connection, 2, id_user, rol)
                if(res[1] != 200):
                    raise_exception(res[0].to_dict()['message'], res[0].to_dict()['error'])

                break

    except jwt.ExpiredSignature:
        print("ERROR (eventos/views/get_attached): Token expirado")
        return jsonify({'message': 'Su tiempo de permanencia en el sistema ha terminado'}), 408    
    except CustomException as e:
        connection.rollback()
        print("ERROR (eventos/views/get_events): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (eventos/views/get_events): ", e)
        return jsonify({'message': 'No se han podido obtener los eventos'}), 500
    else:
        if len(res)>0:
            return jsonify(res[0]), 200
        else:
            if _perm:
                return jsonify({'message': 'No has creado eventos'}), 200
            else:
                return jsonify({'message': 'No tienes permiso para ver los eventos'}), 401
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()
        if connection and not connection.closed:
            connection.close()    


# Save the online events
@event.route('/guardarEvento', methods=['POST'])
@token_required
def save_event_online():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 2)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        _perm = False 
        token = jwt.encode({'userobj': 'No tiene permisos para crear eventos'}, Config.SECRET_KEY)
        for perm in results:
            if perm['id_permiso'] == 3:
                _perm = True
                # Getting valsues from the request
                
                count = request.form['contador']
                req = {
                   'dataEncabezadoEvento': json.loads(request.form['dataEncabezadoEvento']),
                    'dataProductor': json.loads(request.form['dataProductor']),
                    'dataEspecies': json.loads(request.form['dataEspecies'])
                }

                saved = save_event(count=count, req=req, files=request.files, id_user=id_user, connection=connection)
                
                if saved[1] != 200:
                    raise_exception(saved[0].to_dict()['message'],  saved[0].to_dict()['error'])
                

                token = jwt.encode({'userobj': saved[0]['id']}, Config.SECRET_KEY)
                
                break
    except jwt.ExpiredSignature:
        print("ERROR (eventos/views/get_attached): Token expirado")
        return jsonify({'message': 'Su tiempo de permanencia en el sistema ha terminado'}), 408
    except CustomException as e:
        connection.rollback()
        print("ERROR (eventos/views/save_event_online): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (eventos/views/save_event_online): ", e)
        return jsonify({'message': 'Ocurrio un error al guardar el evento.'}), 500
    else:
        if _perm:
            connection.commit()
            return jsonify({'token': token.decode('UTF-8')}), 200
        else:
            return jsonify({'token': token.decode('UTF-8')}), 401
    finally:
        if cursor:
            if  not cursor.closed:
                cursor.close()
        if connection:
            if not connection.closed:
                connection.close()


# Save event tracing 
@event.route('/guardarSeguimiento', methods=['POST', 'GET'])
@token_required
def save_tracing():
    if request.method == 'POST':
        try:
            db_service = DatabaseService()
            connection = db_service.get_connection()
            cursor = connection.cursor()

            id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
            sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
            ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
            val = (id_user, 6)
            cursor.execute(sql, val)
            results = []
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
        
            _perm = False 
            token = jwt.encode({'message': 'No tiene permisos para crear eventos', 
                    }, Config.SECRET_KEY)
            for perm in results:
                if perm['id_permiso'] == 3:
                    _perm = True
                    # capture request data
                    idEvento = request.form['idEvento']
                    observacion = request.form['observacion']
                    idUsuario = request.form['idUsuario']
                    ruta = Config.UPLOAD_FOLDER+Config.UPLOAD_SEGUIMIENTO
                    idStrEvento = str(idEvento)
                    i = 0

                    idSeguimiento = save_tracing_event(idEvento, observacion, idUsuario, connection)
                    if idSeguimiento[1] != 200:
                        raise_exception(idSeguimiento[0].to_dict()['message'],  idSeguimiento[0].to_dict()['error'])

                    os.makedirs(ruta+'/'+idStrEvento, exist_ok=True)
                    ruta = ruta+'/'+idStrEvento

                    if int(request.form['contador']) > 0:
                        while i < int(request.form['contador']):
                
                            name = 'files'+str(i)
                    
                            file = request.files[name]
                            
                            # check if the post request has the file part
                            if name not in request.files:
                                flash('No file part')
                                return jsonify({'message': 'No existe el archivo.'}), 400
                        
                
                            if file.filename == '':
                                flash('No selected file')
                                return jsonify({'message': 'El archivo no tiene nombre.'}), 400
                
                            if file and allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
                                filename = secure_filename(file.filename)
                                file.save(os.path.join(ruta, filename))
                            
                            at = save_attached_tracing(idSeguimiento[0], ruta, secure_filename(file.filename), idUsuario, connection)
                            if at[1] != 200:
                                raise_exception(at[0].to_dict()['message'],  at[0].to_dict()['error'])
                            
                            i += 1

                    seguimientos = search_tracing(int(idEvento), connection)
                    if seguimientos[1] != 200:
                        raise_exception(seguimientos[0].to_dict()['message'],  seguimientos[0].to_dict()['error'])

                    resDataSeguimiento = {
                    'seguimientos': seguimientos[0],
                    }

                    token = jwt.encode({'seguimientos': resDataSeguimiento, }, Config.SECRET_KEY)

                    break

        except jwt.ExpiredSignature:
            print("ERROR (eventos/views/get_attached): Token expirado")
            return jsonify({'message': 'Su tiempo de permanencia en el sistema ha terminado'}), 408
        except CustomException as e:
            connection.rollback()
            print("ERROR (eventos/views/save_tracing): ", e.to_dict()['error'])
            return jsonify({'message': e.to_dict()['message']}), 500
        except Exception as e:
            connection.rollback()
            print("ERROR (eventos/views/save_tracing): ", e)
            return jsonify({'message': 'Ocurrio un error al cargar archivos.'}), 400
        else:
            if _perm:
                connection.commit()
                return jsonify({'token': token.decode('UTF-8')}), 200
            else:
                return jsonify({'token': token.decode('UTF-8')}), 401
        finally:
            if cursor and not cursor.closed:
                cursor.close()
            if connection and not connection.closed:
                connection.close()


# Get tracing from an event
@event.route('/getAdjunto', methods=['POST'])
@token_required
def get_attached():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        ruta = request.get_json()['ruta']
        #nombre = request.get_json()['nombre']
        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 6)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        for perm in results:
            if perm['id_permiso'] == 1:
                nueva_ruta=str(pathlib.Path(__file__).parent.parent.parent)+ruta.replace('.', '',1)

                if request.method == 'POST':
                    return send_file(nueva_ruta, as_attachment=True)
            

        return ({'message': 'No tiene permisos para ver los archivos adjuntos'}), 401
    except jwt.ExpiredSignature:
        print("ERROR (eventos/views/get_attached): Token expirado")
        return jsonify({'message': 'Su tiempo de permanencia en el sistema ha terminado'}), 408
    except Exception as e:
      print("ERROR (eventos/views/get_attached): ", e)
      return jsonify({'message': 'Ocurrio un error al descargar los adjuntos.'}), 500
    finally:
        if cursor and not cursor.closed:
            cursor.close()
        if connection and not connection.closed:
            connection.close()


# Search tracings by event
@event.route('/getSeguimiento', methods=['POST'])
@token_required
def get_tracing():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 6)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        _perm = False
        for perm in results:
            if perm['id_permiso'] == 1:
                _perm=True
                idEvento = request.get_json()['idEvento']
                seguimientos = search_tracing(idEvento, connection)
                if seguimientos[1] != 200:
                    raise_exception(seguimientos[0].to_dict()['message'],  seguimientos[0].to_dict()['error'])

                resDataSeguimiento = {
                    'seguimientos': seguimientos[0],
                }

                token = jwt.encode({'seguimientos': resDataSeguimiento}, Config.SECRET_KEY)
                break

    except CustomException as e:
        connection.rollback()
        print("ERROR (eventos/views/get_tracing): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (eventos/views/get_tracing): ", e)
        return jsonify({'message': 'Ocurrio un error al cargar archivos.'}), 500
    else:
        if _perm:
            return jsonify({'token': token.decode('UTF-8')})
        else:
            return jsonify({'token': token.decode('UTF-8')}), 401
    finally:
        if cursor and not cursor.closed:
            cursor.close()
        if connection and not connection.closed:
            connection.close()


# Search data for agro module
@event.route('/getCultivosAfectadosData', methods=['GET'])
@token_required
def get_agro_data():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 2)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        _perm = False 
        for perm in results:
            if perm['id_permiso'] == 3:
                _perm = True
                species = get_species_data(connection)
                if species[1] != 200:
                    raise_exception(species[0].to_dict()['message'],  species[0].to_dict()['error'])

                plantingMaterial = get_planting_material(connection)
                if plantingMaterial[1] != 200:
                    raise_exception(plantingMaterial[0].to_dict()['message'],  plantingMaterial[0].to_dict()['error'])

                costs = get_costs(connection)
                if costs[1] != 200:
                    raise_exception(costs[0].to_dict()['message'],  costs[0].to_dict()['error'])

                creditData = credit_data_assurance_data(connection)
                if creditData[1] != 200:
                    raise_exception(creditData[0].to_dict()['message'],  creditData[0].to_dict()['error'])

                machineData = []
                infra_type =  search_infrastructure_type(connection)
                if infra_type[1] != 200:
                    raise_exception(infra_type[0].to_dict()['message'],  infra_type[0].to_dict()['error'])
                for item in infra_type[0]:
                    machineData.append({'codInfraestructura': item[0], 'infraestructura': item[1]})
                
                infraestructuraData = get_data_infrastructure(connection)
                if infraestructuraData[1] != 200:
                    raise_exception(infraestructuraData[0].to_dict()['message'],  infraestructuraData[0].to_dict()['error'])

                machineryData = []
                mach_type = search_machinery_type(connection, 2)
                if mach_type[1] != 200:
                    raise_exception(mach_type[0].to_dict()['message'],  mach_type[0].to_dict()['error'])
                for item in mach_type[0]:
                    machineryData.append({'codMaquinaria': item[0], 'maquinaria': item[1]})
                
                break

    except CustomException as e:
        connection.rollback()
        print("ERROR (eventos/views/get_agro_data): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message'], 'error': True}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (eventos/views/get_agro_data): ", e)
        return jsonify({'message': 'Ha ocurrido un error al obtener los datos', 'error': True}), 500
    else:
        if _perm:
            return jsonify({
                'message':
                    {
                        **species[0],
                        **plantingMaterial[0],
                        **costs[0],
                        **creditData[0],
                        'infraestructureType': machineData,
                        **infraestructuraData[0],
                        'machineryData': machineryData
                    },
                'error': False
            }), 200
        else:
            return jsonify({'message': 'No tiene permisos para esta operacion'}), 401
    finally:
        if not connection.closed:
            connection.close()


# Search data for the peq system
@event.route('/getSistemaProductivoPecuarioData', methods=['GET'])
@token_required
def get_peq_data():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 2)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        _perm = False 
        for perm in results:
            if perm['id_permiso'] == 3:
                _perm = True
                affectedSistem = get_peq_affected(connection)
                if affectedSistem[1] != 200:
                    raise_exception(affectedSistem[0].to_dict()['message'],  affectedSistem[0].to_dict()['error'])
                break
       
    except CustomException as e:
        connection.rollback()
        print("ERROR (eventos/views/get_peq_data): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message'], 'error': True}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (eventos/views/get_peq_data): ", e)
        return jsonify({'message': 'Ocurrio un error al obtener los datos', 'error': True}), 500
    else:
        if _perm:
            return jsonify({
                'message': {
                    **affectedSistem[0]
                },
                'error': False 
            }), 200
        else:
            return jsonify({'message': 'No tiene permisos para esta operacion'}), 401
    finally:
        if not connection.closed:
            connection.close()


# Get the needed info for the fishing system
@event.route('/dataPesquero', methods=['GET'])
@token_required
def fishing_data():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 2)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        _perm = False 
        for perm in results:
            if perm['id_permiso'] == 3:
                _perm = True
                fishing_lists_data = get_fishing_data(connection)
                if fishing_lists_data[1] != 200:
                    raise_exception(fishing_lists_data[0].to_dict()['message'],  fishing_lists_data[0].to_dict()['error'])
                break

    except CustomException as e:
        connection.rollback()
        print("ERROR (eventos/views/fishing_data): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message'], 'error': True}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (eventos/views/fishing_data): ", e)
        return jsonify({'message': 'Ocurrio un error al obtener los datos', 'error': True}), 500
    else:
        if _perm:
            return jsonify({
                'message': {
                    **fishing_lists_data[0]
                },
                'error': False
            }), 200
        else:
            return jsonify({'message': 'No tiene permisos para esta operacion'}), 401
    finally:
        if not connection.closed:
            connection.close()


# Get the info about an specfic event
@event.route('/getEvento', methods=['POST'])
@token_required
def get_spec_event():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 2)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        res_evento = []
        _perm = False
        for perm in results:
            if perm['id_permiso'] == 1 or perm['id_permiso'] == 2:
                _perm = True
                idEvento = request.get_json()['idEvento']
                res_evento = get_specific_event(connection, idEvento)
                if res_evento[1] != 200:
                    raise_exception(res_evento[0].to_dict()['message'],  res_evento[0].to_dict()['error'])
                break

    
    except CustomException as e:
        connection.rollback()
        print("ERROR (eventos/views/get_spec_event): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (eventos/views/get_spec_event): ", e)
        return jsonify({'message': 'Ocurrio un error al obtener la información del evento'}), 500
    else:
        if _perm:
            return jsonify({'message': res_evento}), 200
        else:
            return jsonify({'message': 'No tiene permisos para esta operacion'}), 401

    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()

        if connection:
            if not connection.closed:
                connection.close()


# This endpoint returns all the information needed for the event modules, in order to get it all ready for offline working
@event.route('/systemData', methods=['GET'])
@token_required
def system_data():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 2)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        _perm = False 
        for perm in results:
            if perm['id_permiso'] == 3:
                _perm = True

                # forestal
                faseProductiva = search_productive_phase(connection)
                especieForestal = search_forestal_specie(connection)
                ##especieExtractiva = search_extractive_specie(connection)
                objePlantacion = search_plantation_objective(connection)
                tipoInfraestrcutura = search_infrastructure_type(connection)
                tipoSemilla = search_seed_type(connection)
                lotePropaga = search_batch_spread(connection)
                unidad = search_unity(connection)
                unidad_semilla = search_seed_unity(connection)
                tipoFertilizante = search_fertilizer_type(connection)
                tipoPlaguicida = search_pesticide_type(connection)
                tipoMaquinaria = search_machinery_type(connection, 1)
                rubros = search_headings(connection)
                actividad = search_activity(connection)
                fuenteSemilla = search_seed_source(connection)
                presentacionPlaguicida = search_pesticide_presentation(connection)
                eqv_carga = search_eqv_load(connection)
                
                forestal = {
                    'faseProductiva': faseProductiva[0] if faseProductiva[1] == 200 else raise_exception(faseProductiva[0].to_dict()['message'], faseProductiva[0].to_dict()['error']),
                    'especieForestal': especieForestal[0] if especieForestal[1] == 200 else raise_exception(especieForestal[0].to_dict()['message'], especieForestal[0].to_dict()['error']),
                    #'especieExtractiva': especieExtractiva[0] if especieExtractiva[1] == 200 else raise_exception(especieExtractiva[0].to_dict()['message'], especieExtractiva[0].to_dict()['error']),
                    'objePlantacion': objePlantacion[0] if objePlantacion[1] == 200 else raise_exception(objePlantacion[0].to_dict()['message'], objePlantacion[0].to_dict()['error']),
                    'tipoInfraestrcutura': tipoInfraestrcutura[0] if tipoInfraestrcutura[1] == 200 else raise_exception(tipoInfraestrcutura[0].to_dict()['message'], tipoInfraestrcutura[0].to_dict()['error']),
                    'tipoSemilla': tipoSemilla[0] if tipoSemilla[1] == 200 else raise_exception(tipoSemilla[0].to_dict()['message'], tipoSemilla[0].to_dict()['error']),
                    'lotePropaga': lotePropaga[0] if lotePropaga[1] == 200 else raise_exception(lotePropaga[0].to_dict()['message'], lotePropaga[0].to_dict()['error']),
                    'unidad': unidad[0] if unidad[1] == 200 else raise_exception(unidad[0].to_dict()['message'], unidad[0].to_dict()['error']),
                    'unidadSemilla': unidad_semilla[0] if unidad_semilla[1] == 200 else raise_exception(unidad_semilla[0].to_dict()['message'], unidad_semilla[0]),
                    'tipoFertilizante': tipoFertilizante[0] if tipoFertilizante[1] == 200 else raise_exception(tipoFertilizante[0].to_dict()['message'], tipoFertilizante[0].to_dict()['error']),
                    'tipoPlaguicida': tipoPlaguicida[0] if tipoPlaguicida[1] == 200 else raise_exception(tipoPlaguicida[0].to_dict()['message'], tipoPlaguicida[0].to_dict()['error']),
                    'tipoMaquinaria': tipoMaquinaria[0] if tipoMaquinaria[1] == 200 else raise_exception(tipoMaquinaria[0].to_dict()['message'], tipoMaquinaria[0].to_dict()['error']),
                    'rubros': rubros[0] if rubros[1] == 200 else raise_exception(rubros[0].to_dict()['message'], rubros[0].to_dict()['error']),
                    'actividad': actividad[0] if actividad[1] == 200 else raise_exception(actividad[0].to_dict()['message'], actividad[0].to_dict()['error']),
                    'fuenteSemilla': fuenteSemilla[0] if fuenteSemilla[1] == 200 else raise_exception(fuenteSemilla[0].to_dict()['message'], fuenteSemilla[0].to_dict()['error']),
                    'presentacionPlaguicida': presentacionPlaguicida[0] if presentacionPlaguicida[1] == 200 else raise_exception(presentacionPlaguicida[0].to_dict()['message'], presentacionPlaguicida[0].to_dict()['error']),
                    'eqvCarga': eqv_carga[0] if eqv_carga[1] == 200 else raise_exception(eqv_carga[0].to_dict()['message'], eqv_carga[0].to_dict()['error'])
                }

                # agro
                species = get_species_data(connection)
                if species[1] != 200:
                    raise_exception(species[0].to_dict()['message'],  species[0].to_dict()['error'])

                plantingMaterial = get_planting_material(connection)
                if plantingMaterial[1] != 200:
                    raise_exception(plantingMaterial[0].to_dict()['message'],  plantingMaterial[0].to_dict()['error'])

                costs = get_costs(connection)
                if costs[1] != 200:
                    raise_exception(costs[0].to_dict()['message'],  costs[0].to_dict()['error'])

                creditData = credit_data_assurance_data(connection)
                if creditData[1] != 200:
                    raise_exception(creditData[0].to_dict()['message'],  creditData[0].to_dict()['error'])

                machineData = []
                infra_type =  search_infrastructure_type(connection)
                if infra_type[1] != 200:
                    raise_exception(infra_type[0].to_dict()['message'],  infra_type[0].to_dict()['error'])
                for item in infra_type[0]:
                    machineData.append({'codInfraestructura': item[0], 'infraestructura': item[1]})
                
                infraestructuraData = get_data_infrastructure(connection)
                if infraestructuraData[1] != 200:
                    raise_exception(infraestructuraData[0].to_dict()['message'],  infraestructuraData[0].to_dict()['error'])

                machineryData = []
                mach_type = search_machinery_type(connection, 2)
                if mach_type[1] != 200:
                    raise_exception(mach_type[0].to_dict()['message'],  mach_type[0].to_dict()['error'])
                for item in mach_type[0]:
                    machineryData.append({'codMaquinaria': item[0], 'maquinaria': item[1]})

                agro = {
                    **species[0],
                    **plantingMaterial[0],
                    **costs[0],
                    **creditData[0],
                    'infraestructureType': machineData,
                    **infraestructuraData[0],
                    'machineryData': machineryData
                }

                # pecuario
                affectedSistem = get_peq_affected(connection)
                if affectedSistem[1] != 200:
                    raise_exception(affectedSistem[0].to_dict()['message'],  affectedSistem[0].to_dict()['error'])
                
                peq = {
                    **affectedSistem[0]
                }

                # pesquero
                fishing_lists_data = get_fishing_data(connection)
                if fishing_lists_data[1] != 200:
                    raise_exception(fishing_lists_data[0].to_dict()['message'],  fishing_lists_data[0].to_dict()['error'])
                
                fish = {
                    **fishing_lists_data[0]
                }

                # Productor
                tiposDocumento = search_document_type(connection) 
                condicionJuridica = search_legal_condition(connection)
                sexo = search_sex(connection)
                gruposEtnicos = search_ethnic_groups(connection)
                tipoProductor = search_producer_type(connection)
                tipoRelacionPredio = search_estate_relation_type(connection)

                # Search document types.
                provider = {
                    'tiposDocumento': tiposDocumento[0] if tiposDocumento[1] == 200 else raise_exception(tiposDocumento[0].to_dict()['message'], tiposDocumento[0].to_dict()['error']),
                    'condicionJuridica': condicionJuridica[0] if condicionJuridica[1] == 200 else raise_exception(condicionJuridica[0].to_dict()['message'], condicionJuridica[0].to_dict()['error']),
                    'sexo': sexo[0] if sexo[1] == 200 else raise_exception(sexo[0].to_dict()['message'], sexo[0].to_dict()['error']),
                    'gruposEtnicos': gruposEtnicos[0] if gruposEtnicos[1] == 200 else raise_exception(gruposEtnicos[0].to_dict()['message'], gruposEtnicos[0].to_dict()['error']),
                    'tipoProductor': tipoProductor[0] if tipoProductor[1] == 200 else raise_exception(tipoProductor[0].to_dict()['message'], tipoProductor[0].to_dict()['error']),
                    'tipoRelacionPredio': tipoRelacionPredio[0] if tipoRelacionPredio[1] == 200 else raise_exception(tipoRelacionPredio[0].to_dict()['message'], tipoRelacionPredio[0].to_dict()['error'])
                }

                # Mapa

                departamentos = search_departaments(connection)
                municipios = search_township(connection)
                veredas = search_rural_town(connection)

                mapData = {
                    'departamentos': departamentos[0] if departamentos[1] == 200 else raise_exception(departamentos[0].to_dict()['message'], departamentos[0].to_dict()['error']),
                    'municipios': municipios[0] if municipios[1] == 200 else raise_exception(municipios[0].to_dict()['message'], municipios[0].to_dict()['error']),
                    'veredas': veredas[0] if veredas[1] == 200 else raise_exception(veredas[0].to_dict()['message'], veredas[0].to_dict()['error']),
                }

                # Encabezado

                tipoEvento = search_event_type(connection)
                subEvento = search_sub_event(connection)
                sistemaProductivo = search_productive_affected_system(connection)
                plagas = search_pests(connection)
                enfermedades = search_diseases(connection)

                encabezado = {
                    'tipoEvento': tipoEvento[0] if tipoEvento[1] == 200 else raise_exception(tipoEvento[0].to_dict()['message'], tipoEvento[0].to_dict()['error']),
                    'subEvento': subEvento[0] if subEvento[1] == 200 else raise_exception(subEvento[0].to_dict()['message'], subEvento[0].to_dict()['error']),
                    'sistemaProductivo': sistemaProductivo[0] if sistemaProductivo[1] == 200 else raise_exception(sistemaProductivo[0].to_dict()['message'], sistemaProductivo[0].to_dict()['error']),
                    'plagas': plagas[0] if plagas[1] == 200 else raise_exception(plagas[0].to_dict()['message'], plagas[0].to_dict()['error']),
                    'enfermedades': enfermedades[0] if enfermedades[1] == 200 else raise_exception(enfermedades[0].to_dict()['message'], enfermedades[0].to_dict()['error'])
                }
                
                data_systems = {
                    'forestal': forestal,
                    'agricola': agro,
                    'pecuario': peq,
                    'pesquero': fish,
                    'productor': provider,
                    'mapa': mapData,
                    'encabezado': encabezado
                }
                
                break
    except CustomException as e:
        connection.rollback()
        print("ERROR (eventos/views/system_data): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message'], 'error': True}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (eventos/views/system_data): ", e)
        return jsonify({'message': 'Ocurrio un error al obtener los datos', 'error': True}), 500
    else:
        if _perm:
            return jsonify({
                'message': {
                    **data_systems
                },
                'error': False
            }), 200
        else:
            return jsonify({'message': 'No tiene permisos para esta operacion'}), 401
    finally:
        if not connection.closed:
            connection.close()


# This endpoint gets the calcs for the direct costs in agro system
@event.route('/agroCalc', methods=['POST', 'PUT'])
@token_required
def agro_calc():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        _perm = False 
        
        if request.method == 'POST':
            sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
            ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
            val = (id_user, 2)
            cursor.execute(sql, val)
            results = []
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            dpto = request.get_json()['dpto']
            specie = request.get_json()['especie']
            variable = -1
            if 'variable' in request.json:
                variable = request.json['variable']
            
            for perm in results:
                if perm['id_permiso'] == 1:
                    _perm = True
                    calcs = get_calcs(dpto, specie, variable, connection)
                    if calcs[1] != 200:
                        raise_exception(calcs[0].to_dict()['message'],  calcs[0].to_dict()['error'])
                    break

        elif request.method == 'PUT':
            sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
            ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
            val = (id_user, 2)
            cursor.execute(sql, val)
            results = []
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            dpto = request.get_json()['dpto']
            specie = request.get_json()['especie']
            variable = request.get_json()['variable']
            cant = int(str(request.get_json()['cantidad']).replace(',','').split('.')[0])
            unit = int(str(request.get_json()['unitario']).replace(',','').split('.')[0])
            cost = int(str(request.get_json()['costo']).replace(',','').split('.')[0])

            for perm in results:
                if perm['id_permiso'] == 4:
                    _perm = True
                    updated = update_calcs(dpto, specie,variable,cant,unit,cost,id_user,connection)
                    if updated[1] != 200:
                        raise_exception(updated[0].to_dict()['message'],  updated[0].to_dict()['error'])
                    break


    except CustomException as e:
        connection.rollback()
        print("ERROR (eventos/views/agro_calc): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (eventos/views/agro_calc): ", e)
        return jsonify({'message': 'Ocurrio un error al obtener los datos de los cálculos'}), 500
    else:
        if _perm:
            if request.method == 'POST':
                return jsonify({
                    'message': calcs[0]
                }), 200
            if request.method == 'PUT':
                connection.commit()
                return jsonify({'message': 'OK'}), 200
        else:
            return jsonify({'message': 'No tiene permisos para esta operacion'}), 401
    finally:
        if not connection.closed:
            connection.close()


# Get the calcs of the costs of the agro system
@event.route('/agroCalcAct', methods=['GET'])
@token_required
def activities_agro_calc():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        _perm = False 

        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 2)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        for perm in results:
                if perm['id_permiso'] == 4:
                    _perm = True
                    activities = get_activities_agro_calc(connection)
                    if activities[1] != 200:
                        raise_exception(activities[0].to_dict()['message'],  activities[0].to_dict()['error'])
                    break
    except CustomException as e:
        connection.rollback()
        print("ERROR (eventos/views/activities_agro_calc): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (eventos/views/activities_agro_calc): ", e)
        return jsonify({'message': 'Ocurrio un error al obtener los datos de las actividades de los cálculos'}), 500
    else:
        if _perm:
                return jsonify({
                    'message': activities[0]
                }), 200
        else:
            return jsonify({'message': 'No tiene permisos para esta operacion'}), 401
    finally:
        if not connection.closed:
            connection.close()


# This endpoint validates a specific event
@event.route('/validate', methods=['POST'])
@token_required
def validate():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso, u.rol FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 6)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        id_event = request.get_json()['evento']
        
        _perm = False 
        for perm in results:
            if perm['id_permiso'] == 3:
                _perm=True
                rol = perm['rol']
                validated = validate_event(id_event, id_user, rol, connection)
                if validated[1] != 200:
                    raise_exception(validated[0].to_dict()['message'],  validated[0].to_dict()['error'])
                break
    except CustomException as e:
        connection.rollback()
        print("ERROR (eventos/views/agro_calc): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (eventos/views/agro_calc): ", e)
        return jsonify({'message': 'Ocurrio un error al validar el evento'}), 500
    else:
        if _perm:
            connection.commit()
            return jsonify({
                'message': 'Validado'
            }), 200
        else:
            return jsonify({'message': 'No tiene permisos para esta operacion'}), 401
    finally:
        if not connection.closed:
            connection.close()


# Save offline event
@event.route('/guardarEventoOffline', methods=['POST'])
@token_required
def save_event_offline():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 2)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        _perm = False 
        saved_arr = ''
        token = jwt.encode({'userobj': 'No tiene permisos para crear eventos'}, Config.SECRET_KEY)
        
        for perm in results:
            if perm['id_permiso'] == 3:
                _perm = True
                for i in range(len(json.loads(request.form['eventos']))):
                    count = request.form['contador'+str(i)]
                    
                    req = json.loads(request.form['eventos'])[i]
                    saved = save_event(count=count, req=req, files=request.files, id_user=id_user, connection=connection, i=i)
                    if saved[1] != 200:
                        raise_exception(saved[0].to_dict()['message'],  saved[0].to_dict()['error'])
                    saved_arr = saved_arr + str(saved[0]['id']) + ' '
                break
        
        token = jwt.encode({'userobj': saved_arr}, Config.SECRET_KEY)

    except CustomException as e:
        connection.rollback()
        print("ERROR (eventos/views/save_event_offline): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        print("ERROR (eventos/views/save_event_offline): ", e)
        return jsonify({'message': 'Ocurrio un error al sincronizar los eventos.'}), 500
    else:
        if _perm:
            connection.commit()
            return jsonify({'token': token.decode('UTF-8')}), 200
        else:
            return jsonify({'token': token.decode('UTF-8')}), 401
    finally:
        if cursor and not cursor.closed:
            cursor.close()
        if connection and not connection.closed:
            connection.close()


# Modify the event and it's information
@event.route('/modifyEvent', methods=['POST'])
@token_required
def modify_event():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 2)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        _perm = False 
        idNewEvento = -1
        # Check that the event has not been validated yet
        idOldEvento = json.loads(request.form['dataEncabezadoEvento'])['codEvento']
        checked = check_non_validated_event(idOldEvento, connection)

        if checked[1] != 200:
            raise_exception(checked[0].to_dict()['message'],  checked[0].to_dict()['error'])

        if checked[0]:
            raise_exception('El evento ya fue validado, no se puede editar','El evento '+str(idOldEvento)+'ya fue validado, no se puede editar')
        else:
            # Crear el nuevo evento usando el metodo ya existente
            for perm in results:
                if perm['id_permiso'] == 4 or perm['id_permiso'] == 5:
                    _perm = True
                    # Getting valsues from the request
                    
                    count = request.form['contador']
                    req = {
                    'dataEncabezadoEvento': json.loads(request.form['dataEncabezadoEvento']),
                        'dataProductor': json.loads(request.form['dataProductor']),
                        'dataEspecies': json.loads(request.form['dataEspecies'])
                    }

                    sql = ("SELECT fecha_registro_evento FROM Evento WHERE cod_evento = %s")
                    cursor.execute(sql, [idOldEvento])

                    old_date = cursor.fetchone()[0]

                    saved = save_event(count=count, req=req, files=request.files, id_user=id_user, connection=connection, old_date=old_date)
                    
                    if saved[1] != 200:
                        raise_exception(saved[0].to_dict()['message'],  saved[0].to_dict()['error'])

                    idNewEvento = saved[0]['id']

                    token = jwt.encode({'userobj': saved[0]['id']}, Config.SECRET_KEY)
                    
                    break


            # Transferir los seguimientos a este nuevo evento
            transferred = transfer_tracings(idNewEvento, idOldEvento, connection)
            if transferred[1] != 200:
                raise_exception(transferred[0].to_dict()['message'],  transferred[0].to_dict()['error'])

            # Transferir los adjuntos de seguimientos a este nuevo evento
            transferred = transfer_attached_tracings(idNewEvento, idOldEvento, connection)
            if transferred[1] != 200:
                raise_exception(transferred[0].to_dict()['message'],  transferred[0].to_dict()['error'])

            # Transferir los adjuntos del evento al nuevo evento (primero revisar si la carpeta del nuevo evento ya existe y mezclarlas, si no, crearla)
            transferred = transfer_attached_event(idNewEvento, idOldEvento, connection)
            if transferred[1] != 200:
                raise_exception(transferred[0].to_dict()['message'],  transferred[0].to_dict()['error'])

            # Borrar el evento y sus demás implicados
            deleted = delete_event(idOldEvento, connection)
            if deleted[1] != 200:
                raise_exception(deleted[0].to_dict()['message'],  deleted[0].to_dict()['error'])


    except CustomException as e:
        connection.rollback()
        transfer_attached_event(idOldEvento, idNewEvento, connection)
        transfer_attached_tracings(idOldEvento, idNewEvento, connection)
        print("ERROR (eventos/views/modify_event): ", e.to_dict()['error'])
        return jsonify({'message': e.to_dict()['message']}), 500
    except Exception as e:
        connection.rollback()
        transfer_attached_event(idOldEvento, idNewEvento, connection)
        transfer_attached_tracings(idOldEvento, idNewEvento, connection)
        print("ERROR (eventos/views/modify_event): ", e)
        return jsonify({'message': 'Ocurrio un error al modificar el evento'}), 500
    else:
        if _perm:
            connection.commit()
            return jsonify({'token': token.decode('UTF-8')}), 200
        else:
            return jsonify({'token': token.decode('UTF-8')}), 401
    finally:
        if cursor and not cursor.closed:
            cursor.close()
        if connection and not connection.closed:
            connection.close()


'''
@event.route('/downloadAtt', methods=['POST'])
def download_attachement():
    try:
        db_service = DatabaseService()
        connection = db_service.get_connection()
        cursor = connection.cursor()

        ruta = request.get_json()['ruta']
        
        id_user = jwt.decode(request.args.get('token'), Config.SECRET_KEY)['userobj']['id']
        sql = ("""SELECT rm.id_permiso FROM Usuarios u JOIN Rol_modulo_permisos rm 
        ON u.rol = rm.id_rol AND u.id = %s AND rm.id_modulo=%s;""")
        val = (id_user, 6)
        cursor.execute(sql, val)
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        _perm = False 
        token = {'userobj': 'No tiene permisos para crear eventos'}
        for perm in results:
            if perm['id_permiso'] == 1:
                _perm = True

    except CustomException as e:
        print(e)
        return e, 500
    except Exception as e:
        print(e)
    else:
        return token, 500
    finally:
        if cursor:
            if not cursor.closed:
                cursor.close()
        
        if connection:
            if not connection.closed:
                connection.close()
'''