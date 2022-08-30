from . import visor
from app.services.database_service import DatabaseService
from app.exceptions import CustomException
from flask import jsonify, request, send_file
from app.visor.database_manager import *
from app.helpers import raise_exception
import pathlib


# Main data for visor
@visor.route('/', methods=['GET'])
def index():
  try:
    db_service = DatabaseService()
    connection = db_service.get_connection()

    res_date = first_date(connection)
    if res_date[1] != 200:
      raise_exception(res_date[0].to_dict()['message'],  res_date[0].to_dict()['error'])

    res_exp = get_exp_types(connection)
    if res_exp[1] != 200:
      raise_exception(res_exp[0].to_dict()['message'],  res_exp[0].to_dict()['error'])
    
    res_event_type = get_events_type(connection)
    if res_event_type[1] != 200:
      raise_exception(res_event_type[0].to_dict()['message'],  res_event_type[0].to_dict()['error'])

    res_town_event = get_town_events(connection)
    if res_town_event[1] != 200:
      raise_exception(res_town_event[0].to_dict()['message'],  res_town_event[0].to_dict()['error'])


    res_dpto_event = get_dpto_events(connection)
    if res_dpto_event[1] != 200:
      raise_exception(res_dpto_event[0].to_dict()['message'],  res_dpto_event[0].to_dict()['error'])

    res = {
        'sistemasProductivos': res_exp[0],
        'tiposEventos': res_event_type[0],
        'municipiosEvento': res_town_event[0],
        'departamentosEvento': res_dpto_event[0],
        'primerFecha': res_date[0]
    }

  except CustomException as e:
    connection.rollback()
    print('ERROR (visor/views/index): ', e.to_dict()['error'])
    return jsonify({'message': e.to_dict()['message']}), 500
  except Exception as e:
    connection.rollback()
    print('ERROR (visor/views/index): ', e)
    return jsonify({'message': 'Ocurrio un error al obtener los eventos'}), 500
  else:
    return jsonify({'message': res}), 200
  finally:
    if connection:
      if not connection.closed:
        connection.close()


# Filter the events by the visor parameters
@visor.route('/filter', methods=['POST'])
def filter_events(): 
  try:
    db_service = DatabaseService()
    connection = db_service.get_connection()

    obj = request.get_json()['obj']

    res_filter = filtered_events(connection, obj)
    if res_filter[1] != 200:
      raise_exception(res_filter[0].to_dict()['message'],  res_filter[0].to_dict()['error'])

    res = {
        'eventos': res_filter[0]
    }

  except CustomException as e:
    connection.rollback()
    print('ERROR (visor/views/filter_events): ', e.to_dict()['error'])
    return jsonify({'message': e.to_dict()['message']}), 500
  except Exception as e:
    connection.rollback()
    print('ERROR (visor/views/filter_events): ', e)
    return jsonify({'message': 'Ocurrio un error al obtener los eventos'}), 500
  else:
    return jsonify({'message': res}), 200
  finally:
    if connection:
      if not connection.closed:
        connection.close()


# Filter events by uer
@visor.route('/filterUER', methods=['POST'])
def filter_by_uer():
  try:
    db_service = DatabaseService()
    connection = db_service.get_connection()

    obj = request.get_json()['obj']
    res = {}

    res_towns = filter_by_town(connection, obj)
    if res_towns[1] != 200:
      raise_exception(res_towns[0].to_dict()['message'],  res_towns[0].to_dict()['error'])

    if 'cod_mun' in obj:
      res = {
        'mun': res_towns[0]
      }
    else:
      res = {
        'dpto': res_towns[0]
      }
  
  except CustomException as e:
    connection.rollback()
    print('ERROR (visor/views/filter_by_uer): ', e.to_dict()['error'])
    return jsonify({'message': e.to_dict()['message']}), 500
  except Exception as e:
    connection.rollback()
    print('ERROR (visor/views/filter_by_uer): ', e)
    return jsonify({'message': 'Ocurrio un error al filtrar por unidad territorial'}), 500
  else:
    return jsonify({'message': res}), 200
  finally:
    if connection:
      if not connection.closed:
        connection.close()


# Endpoint to get attched files
@visor.route('/routes', methods=['POST'])
def get_route_attached_files():
  try:
    db_service = DatabaseService()
    connection = db_service.get_connection()


    id_evento = request.get_json()['id_evento']

    routes = get_routes(id_evento, connection)
    if routes[1] != 200:
      raise_exception(routes[0].to_dict()['message'],  routes[0].to_dict()['error'])

  except CustomException as e:
    connection.rollback()
    print('ERROR (visor/views/get_route_attached_files): ', e.to_dict()['error'])
    return jsonify({'message' : e.to_dict()['message']}), 500
  except Exception as e:
    connection.rollback()
    print('ERROR (visor/views/get_route_attached_files): ', e)
    return jsonify({'message': 'Ocurrio un error al obtener las rutas de los archivos'}), 500
  else:
    return jsonify({'message': routes[0]}), 200
  finally:
    if connection:
      if not connection.closed:
        connection.close()


# Endpoint to send the files by its route
@visor.route('/files', methods=['POST', 'GET'])
def get_attached_files():
  try:
    db_service = DatabaseService()
    connection = db_service.get_connection()

    ruta = request.args.get('ruta')

    nueva_ruta=str(pathlib.Path(__file__).parent.parent.parent)+ruta.replace('.', '',1)
    
    return send_file(nueva_ruta)

  except CustomException as e:
    connection.rollback()
    print('ERROR (visor/views/get_attached_files): ', e.to_dict()['error'])
    return jsonify({'message' : e.to_dict()['message']}), 500
  except Exception as e:
    connection.rollback()
    print('ERROR (visor/views/get_attached_files): ', e)
    return jsonify({'message': 'Ocurrio un error al obtener los archivos adjuntos'}), 500
  finally:
    if connection:
      if not connection.closed:
        connection.close()


# Endpoint to get the information for the graphs by town or department
@visor.route('/graphs', methods=['POST'])
def get_info_graphs(): 
  try:
    db_service = DatabaseService()
    connection = db_service.get_connection()

    obj = request.get_json()['obj']

    res = get_graphs_data(connection, obj)
    if res[1] != 200:
      raise_exception(res[0].to_dict()['message'],  res[0].to_dict()['error'])

  except CustomException as e:
    connection.rollback()
    print('ERROR (visor/views/get_info_graphs): ', e.to_dict()['error'])
    return jsonify({'message' : e.to_dict()['message']}), 500
  except Exception as e:
    connection.rollback()
    print('ERROR (visor/views/get_info_graphs): ', e)
    return jsonify({'message' : 'Ocurrio un error al obtener los datos de las graficas'}), 500
  else:
    return jsonify({'message': res[0]}), 200
  finally:
    if connection:
      if not connection.closed:
        connection.close()
