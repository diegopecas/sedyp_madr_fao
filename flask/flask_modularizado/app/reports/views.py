from . import report
from flask import jsonify
from app.exceptions import CustomException
from app.services.database_service import DatabaseService
from app.reports.database_manager import *
from app.helpers import raise_exception

@report.route('/<int:id>')
def index(id):
  try:
    db_service = DatabaseService()
    connection = db_service.get_connection()

    obj = get_reports_system(id, connection)
    if obj[1] != 200:
      raise_exception(obj[0].to_dict()['message'],  obj[0].to_dict()['error'])

  except CustomException as e:
    connection.rollback()
    print("ERROR (eventos/views/index): ", e.to_dict()['error'])
    return jsonify({'message': e.to_dict()['message']}), 500
  except Exception as e:
    connection.rollback()
    print("ERROR (eventos/views/index): ", e)
    return jsonify({'message': 'No se han podido obtener los datos'}), 500
  else:
    return jsonify(obj[0]), 200
  finally:
    if connection and not connection.closed:
        connection.close()
