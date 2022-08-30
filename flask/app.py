## Modules
from flask import Flask, flash, jsonify, request, render_template, redirect, url_for, make_response, send_file, current_app, send_from_directory
from flask_cors import CORS
from functools import wraps
from datetime import datetime, timedelta
import datetime
from collections import Counter
import json
import os
import errno
import random
import time
import jwt
import requests
import string
import psycopg2
from werkzeug.utils import secure_filename
import base64
from flask_mail import Mail, Message 
import random

## Functions
from endpointFunc import *



app = Flask(__name__)
mail = Mail() # Library to send mails

# Carpeta de subida
UPLOAD_FOLDER = './adjuntos'
UPLOAD_SEGUIMIENTO = '/seguimiento'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_SEGUIMIENTO'] = UPLOAD_SEGUIMIENTO

CORS(app)

# secret for token
app.config['SECRET_KEY'] = 'fbfundplankey' # for the token
# Configurate the Library to send mails
EMAIL_SENDER = 'testingemails266@gmail.com'
app.config.update(dict(
	MAIL_SERVER = 'smtp.gmail.com',
	MAIL_PORT = 587,
	MAIL_USERNAME = EMAIL_SENDER,
	MAIL_PASSWORD = 'testing123*',
	MAIL_USE_TLS = True,
  MAIL_USE_SSL = False,
))
mail.init_app(app)

# SALT encrypt password
salt = os.environ.get('SALT')

# initialing sql
_user = os.environ.get('DB_USER') if (os.environ.get('DB_USER')) else 'itim'
_password = os.environ.get('DB_PASSWORD') if (os.environ.get('DB_PASSWORD')) else 'pgFaoApp2021$'
_host = os.environ.get('DB_IP') if (os.environ.get('DB_IP')) else 'pgfaoserv.postgres.database.azure.com'
connection = psycopg2.connect(user=_user, password=_password, host=_host, port="5432", database="faodb")
# _user = os.environ.get('DB_USER') if (os.environ.get('DB_USER')) else 'faoadmin'
# _password = os.environ.get('DB_PASSWORD') if (os.environ.get('DB_PASSWORD')) else 'Ini0416'
# _host = os.environ.get('DB_IP') if (os.environ.get('DB_IP')) else '127.0.0.1'
# connection = psycopg2.connect(user=_user, password=_password, host=_host, port="5432", database="faodb")
# cursor = connection.cursor()
# Print PostgreSQL details
print("PostgreSQL server information")
# print(cursor)
# cursor.close()
print(connection.get_dsn_parameters(), "\n")


#########################################################################################################
############################################## Token ####################################################
#########################################################################################################

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'No se encontro token!'}), 403
        try:
            data: jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Token error'}), 403
        return f(*args, **kwargs)
    return decorated

#########################################################################################################
###################################### Declaración de routing ###########################################
#########################################################################################################

@app.route('/', methods=['GET'])
def Main():
    try:
        print('ok in main route')
        return jsonify({'success': True}), 200
    except:
        print('error in main route')
        return jsonify({'success': False}), 400



#########################################################################################################
############################################ End points ##################################################
#########################################################################################################

######################################
# login
######################################
@app.route('/login', methods=['POST'])
def login():
    # tomando valores del request
    email = request.get_json()['email']
    password = request.get_json()['password']

    try:
      cursor = connection.cursor()
      encPass = base64.b64encode(password.encode())

      query = ("""
      SELECT
      a.id, a.usuario, a.email, a.password, a.activo, a.nombre,
      a.apellido, a.numero_documento, a.cod_tipo_documento,
      a.institucion, a.cargo, b.tipo_documento
      FROM usuarios a JOIN tipo_documento2 b ON (b.cod_tipo_documento = a.cod_tipo_documento)
      WHERE email = %s AND password = %s AND activo = 'S' AND validated = true
      """)
      cursor.execute(query,(email, encPass.decode()))
      records = cursor.fetchall()

      # si existe le doy el token
      if cursor.rowcount > 0:

          for row in records:
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
                  ##'nombreDocumento': row[11]
              }
          token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
          return jsonify({'token': token.decode('UTF-8')})

      return jsonify({'message': 'Error en autenticación'}), 400
    
    except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error en el login.'}), 400
    
    finally:
         cursor.close()



######################################
# create user
######################################
@app.route('/createUser', methods=['POST'])
def createUser():
    # capture request data
    obj = request.get_json()['obj']


    try:
      # open conection
      cursor = connection.cursor()
      # validaciones creación de un usuario nuevo
      dataUserExisting = searchUser(obj['numDocument'], obj['email'], connection)
      if dataUserExisting:
          return jsonify({'message': 'Ya existe un usuario con el mismo número de documento o email'}), 400

      msg = Message("Confirmación de correo",
					sender=EMAIL_SENDER,
					recipients=[obj['email']])
			
      token_email = '{}{}{}'.format(random.choice(string.ascii_letters), random.randint(1000,9999), random.choice(string.ascii_letters))
      to_hash = obj['email'] +'-'+ token_email
      hashed = base64.b64encode(to_hash.encode())
      hashed_password = base64.b64encode(obj['password'].encode())

      url = ''
      if request.url_root == 'http://localhost:4000/':
        url = 'http://0.0.0.0:4000'
      else:
        url = 'http://faofrontend.southcentralus.azurecontainer.io'

      link = '{}/validate/{}'.format(url, hashed.decode())
      msg.html = '''
					<h4>Para completar tu registro en la aplicación por favor accede a esta página</h4>
					<h3>{}</h3>
			'''.format(link)

      sqlInsertUser = ("""
      INSERT INTO usuarios (usuario,email,password,activo,nombre,apellido,numero_documento,cod_tipo_documento,institucion,cargo,token,validated)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, false) RETURNING id
      """)
      val = (obj['usuario'], obj['email'], hashed_password.decode(), obj['active'], obj['firstName'], obj['lastName'], obj['numDocument'], 
      obj['typeDocument'], obj['institution'], obj['workCenter'], token_email)

      cursor.execute(sqlInsertUser,val)
      connection.commit()
      mail.send(msg)

      res = {
        'id': cursor.fetchone()[0],
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
      token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
      return jsonify({'token': token.decode('UTF-8')})

    except ValueError:
      connection.rollback()
      print(ValueError)
      return jsonify({'message': 'Ocurrio un error al crear el usuario.'}), 400

    finally:
      cursor.close()


## Validate user email 
@app.route("/validate", methods=['GET', 'POST'])
def verifyCode():

  code = request.get_json()['code']

  try:
    cursor = connection.cursor()
    data = base64.b64decode(code).decode().split('-')
    
    _email = data[0]
    _code = data[1]

    sql = ("""
      SELECT token, validated FROM usuarios WHERE email = '{}'
    """.format(_email))

    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
    	results.append(dict(zip(columns, row)))
		
    if len(results) == 0:
    	return jsonify({'message': "El usuario no existe"}), 400

    if results[0]['validated'] == True:
    	return jsonify({'message': "El correo ya ha sido validado"}), 400
      
    if results[0]['token'] == _code:
	    sql = ("""
				UPDATE usuarios SET validated = true WHERE email = '{}'
			""".format(_email))
	    cursor.execute(sql)
	    connection.commit()
	    return jsonify({'message': "Correo validado"}), 200
    else:
    	return jsonify({'message': "El codigo no coincide"}), 400

  except Exception as e:
    connection.rollback()
    print(e)
    return jsonify({'message': 'Ocurrio un error al validar el correo.'}), 400
  finally:
    cursor.close()

######################################
# update user
######################################
@app.route('/updateUser', methods=['POST'])
@token_required
def updateUser():
    # capture request data
    obj = request.get_json()['obj']


    try:
      # open conection
      cursor = connection.cursor()
      # validaciones creación de un usuario nuevo
      dataUserExisting = searchUser(obj['numDocument'], obj['email'], connection, obj['idUser'])
      if dataUserExisting:
          return jsonify({'message': 'Ya existe un usuario con el mismo número de documento o email'}), 400

      if obj['password']:
        hashed_password = base64.b64encode(obj['password'].encode())
        sqlUpdateUser = ("""
        UPDATE usuarios SET usuario=%s,email=%s,password=%s,activo=%s,nombre=%s,apellido=%s,numero_documento=%s,cod_tipo_documento=%s,institucion=%s,cargo=%s
        WHERE id=%s
        """)
        val = (obj['usuario'], obj['email'], hashed_password.decode(), obj['active'], obj['firstName'], obj['lastName'], obj['numDocument'], obj['typeDocument'], obj['institution'], obj['workCenter'], obj['idUser'])
      else:
        sqlUpdateUser = ("""
        UPDATE usuarios SET usuario=%s,email=%s,activo=%s,nombre=%s,apellido=%s,numero_documento=%s,cod_tipo_documento=%s,institucion=%s,cargo=%s
        WHERE id=%s
        """)
        val = (obj['usuario'], obj['email'], obj['active'], obj['firstName'], obj['lastName'], obj['numDocument'], obj['typeDocument'], obj['institution'], obj['workCenter'], obj['idUser'])

      cursor.execute(sqlUpdateUser,val)
      connection.commit()

      res = {
        'id': obj['idUser'],
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

      token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
      return jsonify({'token': token.decode('UTF-8')})

    except ValueError:
      connection.rollback()
      print(ValueError)
      return jsonify({'message': 'Ocurrio un error al crear el usuario.'}), 400

    finally:
      cursor.close()


######################################
# Consultar eventos creados
######################################
@app.route('/getEventos', methods=['GET'])
@token_required
def getEventos():
  
  try:
    
    cursor = connection.cursor()
    # consultar eventos
  

    '''
    sql = ("""
          SELECT
            a.cod_evento,
            a.cod_tipo_evento_FK,
            b.tipo_evento,
            TO_CHAR(a.coord_x, 'l99999D99999999') AS coord_x,
            TO_CHAR(a.coord_y, 'l99999D99999999') AS coord_y,
            TO_CHAR(a.altitud, 'l99999D99999999') AS altitud,
            TO_CHAR(a.precision, 'l99999D99999999') AS precision_a,
            TO_CHAR(a.fecha_registro_evento, 'YYYY-MM-DD') AS fecha_registro_evento,
            a.cod_municipio_FK,
            a.ubicacion_vereda,
            a.cod_vereda_FK,
            a.nom_puerto_desembarquee,
            a.cod_encuestador_FK,
            a.descrip_llegada_casco_urbano
          FROM evento a
          JOIN tipo_evento b ON (b.cod_tip_evento = a.cod_tipo_evento_FK)
          ORDER BY a.cod_evento DESC""")
    '''
    # Consulta eventos reducida
    sql = ('''
      SELECT
        a.cod_evento,
        b.tipo_evento,
        TO_CHAR(a.fecha_registro_evento, 'YYYY-MM-DD') AS fecha_registro_evento,
		    CONCAT(d.nombre_dpto,' - ',m.nom_municipio, ' / ', a.descrip_llegada_casco_urbano) ubicacion
      	FROM evento a
      	JOIN tipo_evento b ON (b.cod_tip_evento = a.cod_tipo_evento_FK)
	  	  JOIN Municipios m ON (a.cod_municipio_FK = m.cod_municipios)
	  	  JOIN Departamentos d ON(m.cod_dpto_FK = d.cod_dpto)
      	ORDER BY a.cod_evento DESC;
    ''')
    cursor.execute(sql);
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))

    cursor.close()
    #eventos = diccionarioEvento(results, connection)
    '''
    resDataEvento = {
      'eventos': eventos,
    }
    '''

    resDataEvento = {
      'eventos': results,
    }

    token = jwt.encode({'eventos': resDataEvento, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
    return jsonify({'token': token.decode('UTF-8')})

  except ValueError:
    connection.rollback()
    print(ValueError)
    cursor.close()
    return jsonify({'message': 'Ocurrio un error al crear el usuario.'}), 400



######################################
# Consultar información necesaria para
# la creación del productor en el evento.
######################################
@app.route('/dataProductor', methods=['GET'])
@token_required
def dataProveedor():

  # consultar tipos de documento.
  resDataProveedor = {
    'tiposDocumento': searchTipoDocumento(connection),
    'condicionJuridica': searchCondicionJuridica(connection),
    'sexo': searchSexo(connection),
    'gruposEtnicos': searchGruposEtnicos(connection),
    'tipoProductor': searchTipoProductor(connection),
    'tipoRelacionPredio': searchtTipoRelacionPredio(connection)
  }

  token = jwt.encode({'data': resDataProveedor, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
  return jsonify({'token': token.decode('UTF-8')})


######################################
# Consultar información necesaria para
# la creación del mapa
######################################
@app.route('/dataMapa', methods=['GET'])
@token_required
def dataMapa():

  try:

    resDataMapa = {
      'departamentos': searchDepartamentos(connection),
      'municipios': searchMunicipios(connection),
      'veredas': searchVeredas(connection),
    }

    token = jwt.encode({'dataMapa': resDataMapa, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
    return jsonify({'token': token.decode('UTF-8')})

  except ValueError:
    print(ValueError)
    return jsonify({'message': 'Ocurrio un error al crear el usuario.'}), 400


######################################
# Consultar información necesaria para
# la creación del evento
######################################
@app.route('/dataEvento', methods=['GET'])
@token_required
def dataEvento():

  # consultar tipos de documento.
  resDataEvento = {
    'tipoEvento': searchTipoEvento(connection),
    'subEvento': searchSubEvento(connection),
    'sistemaProductivo': searchSistemaProductivoAfectado(connection),
  }

  token = jwt.encode({'dataEvent': resDataEvento, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
  return jsonify({'token': token.decode('UTF-8')})


######################################
# Consultar información necesaria para
# la creación dee evento-> especie
######################################
@app.route('/dataEventoEspecie', methods=['GET'])
@token_required
def dataEventoEspecie():

  # consultar datos especie
  resDataEventoEspecie = {
    'faseProductiva': searchFaseProductiva(connection),
    'especieForestal': searchEspecieForestal(connection),
    'especieExtractiva': searchEspecieExtractiva(connection),
    'objePlantacion': searchObjePlantacion(connection),
    'tipoInfraestrcutura': searchTipoInfraestructura(connection),
    'tipoSemilla': searchTipoSemilla(connection),
    'lotePropaga': searchLotePropaga(connection),
    'unidad': searchUnidad(connection),
    'tipoFertilizante': searchTipoFertilizante(connection),
    'tipoPlaguicida': searchTipoPlaguicida(connection),
    'tipoMaquinaria': searchTipoMaquinaria(connection),
    'rubros': searchRubros(connection),
    'actividad': searchActividad(connection),
  }

  token = jwt.encode({'dataEventSpecie': resDataEventoEspecie, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
  return jsonify({'token': token.decode('UTF-8')})


######################################
# Guardar evento
######################################
@app.route('/guardarEvento', methods=['POST'])
@token_required
def guardarEvento(): 
    # tomando valores del request
    dataEncabezadoEvento = request.get_json()['dataEncabezadoEvento'] ## Guarda en tabla evento, informacion de localizacion mayormente
    dataProductor = request.get_json()['dataProductor'] ## Guarda en productor_agropecuario, informacion sobre productor
    dataEspecie = request.get_json()['dataEspecies'] ## Debe guardar la informacion del detalle del evento, actualmente solo guarda
    # la informacion de forestal, falta agropecuario

    print(dataEspecie)

    if len(dataEncabezadoEvento) == 0:
      return jsonify({'message': 'No hay datos para guardar el evento.'}), 400

    try:
      idEvento = guardarEncabezadoEvento(dataEncabezadoEvento, connection) ## Tabla evento
      guardarDataProductor(idEvento, dataProductor, connection) ## Tabla productor
      guardarEventoSistema(idEvento, dataEspecie, dataEncabezadoEvento['sisProds'], connection)

     # connection.commit()

      token = jwt.encode({'userobj': idEvento, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
      return jsonify({'token': token.decode('UTF-8')})

    except ValueError:
      print(ValueError)
      #connection.rollback()
      return jsonify({'message': 'Ocurrio un error al guardar el evento.'}), 400


######################################
# Guardar seguimiento de evento
######################################
@app.route('/guardarSeguimiento', methods=['GET', 'POST'])
@token_required
def guardarSeguimiento():

    if request.method == 'POST':
      
      # capture request data
      idEvento = request.form['idEvento']
      observacion = request.form['observacion']
      idUsuario = request.form['idUsuario']
      ruta = app.config['UPLOAD_FOLDER']+app.config['UPLOAD_SEGUIMIENTO']
      idStrEvento = str(idEvento)
      i = 0

      try:

        idSeguimiento = guardarSeguimientoEvento(idEvento, observacion, idUsuario, connection)

        os.makedirs(ruta+'/'+idStrEvento, exist_ok=True)
        ruta = ruta+'/'+idStrEvento

        if int(request.form['contador']) > 0:

           while i < int(request.form['contador']):
  
            name = 'files'+str(i)
    
            file = request.files[name]
            
            # check if the post request has the file part
            if name not in request.files:
                flash('No file part')
                return jsonify({'message': 'no existe el archivo.'}), 400
        
  
            if file.filename == '':
              flash('No selected file')
              return jsonify({'message': 'El archivo no tiene nombre.'}), 400
  
            if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
                filename = secure_filename(file.filename)
                file.save(os.path.join(ruta, filename))
            
            guardarAdjuntoSeguimiento(idSeguimiento, ruta, file.filename, connection)
            
            i += 1

        connection.commit()

        seguimientos = consultarSeguimientos(int(idEvento), connection)

        resDataSeguimiento = {
          'seguimientos': seguimientos,
        }

        token = jwt.encode({'seguimientos': resDataSeguimiento, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

      except ValueError:
        connection.rollback()
        print(ValueError)
        return jsonify({'message': 'Ocurrio un error al cargar archivos.'}), 400


######################################
# Guardar seguimiento de evento
######################################
@app.route('/getAdjunto', methods=['POST'])
@token_required
def getAdjunto():

    # capture request data
    ruta = request.get_json()['ruta']
    nombre = request.get_json()['nombre']
    # extension = nombre

    try:

      if request.method == 'POST':
        return send_file(ruta, as_attachment=True)

    except ValueError:
      print(ValueError)
      return jsonify({'message': 'Ocurrio un error al descargar los adjuntos.'}), 400


######################################
# Consultar seguimientos por evento
######################################
@app.route('/getSeguimiento', methods=['POST'])
@token_required
def getSeguimiento() :

    # tomando valores del request
    idEvento = request.get_json()['idEvento']

    try:

      seguimientos = consultarSeguimientos(idEvento, connection)

      resDataSeguimiento = {
        'seguimientos': seguimientos,
      }

      token = jwt.encode({'seguimientos': resDataSeguimiento, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
      return jsonify({'token': token.decode('UTF-8')})

    except ValueError:
      print(ValueError)
      return jsonify({'message': 'Ocurrio un error al cargar archivos.'}), 400


######################################
# Información para informes por evento
######################################
@app.route('/setDataInformesEvento', methods=['POST'])
@token_required
def setDataInformesEvento() :

    # tomando valores del request
    idEvento = request.get_json()['idEvento']

    try:

      costosDirectos = costosDirectosActividad(idEvento, connection)
      costosInDirectos = costosInDirectosRubro(idEvento, connection)
      tipoInfraestructura = valorTipoInfraestructura(idEvento, connection)
      perdidaEconomica = perdidaEconomicaForestal(idEvento, connection)
      valPerdidaEconomica = valorPerdidaEconomicaForestal(idEvento, connection)
      perdidaEstimadaProdu = perdidaEstimadaProduccion(idEvento, connection)

      resDataInformes = {
        'costosDirectos': costosDirectos,
        'costosInDirectos': costosInDirectos,
        'tipoInfraestructura': tipoInfraestructura,
        'perdidaEconomicaForestal': perdidaEconomica,
        'valPerdidaEconomica': valPerdidaEconomica,
        'perdidaEstimadaProdu': perdidaEstimadaProdu
      }

      token = jwt.encode({'dataInformes': resDataInformes, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
      return jsonify({'token': token.decode('UTF-8')})

    except ValueError:
      print(ValueError)
      return jsonify({'message': 'Ocurrio un error al cargar archivos.'}), 400


######################################
# Información para informes generales
######################################
@app.route('/setDataInformesGenerales', methods=['POST'])
@token_required
def setDataInformesGenerales() :

    # tomando valores del request
    ubicacion = request.get_json()['ubicacion']

    try:
      
      val = ("d.cod_municipio_FK = "+ str(ubicacion['municipio'])) if ubicacion else ("1 = 1")

      sexoProductores = getSexoProductores(ubicacion, val, connection)
      promerioEdad = getPromedioEdad(ubicacion, val, connection)
      grupoEtnico = getGrupoEtnico(ubicacion, val, connection)
      tipoProductor = getTipoProductorProductores(ubicacion, val, connection)
      hectareasEspecie = getHectareasEspecie(ubicacion, val, connection)
      ubicacionEventos = getUbicacionEventos(ubicacion, val, connection)
      volumenMadera = getVolumenMadera(ubicacion, val, connection)
      danosInfraestructura = getDanosInfraestructura(ubicacion, val, connection)
      valorPerdida = getValorPedidas(ubicacion, val, connection)

      resDataInformes = {
        'departamentos': searchDepartamentos(connection),
        'municipios': searchMunicipios(connection),
        'sexoProductores': sexoProductores,
        'promerioEdad': promerioEdad,
        'grupoEtnico': grupoEtnico,
        'tipoProductor': tipoProductor,
        'hectareasEspecie': hectareasEspecie,
        'ubicacionEventos': ubicacionEventos,
        'volumenMadera': volumenMadera,
        'danosInfraestructura': danosInfraestructura,
        'valorPerdida': valorPerdida,
      }

      token = jwt.encode({'dataInformes': resDataInformes, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
      return jsonify({'token': token.decode('UTF-8')})

    except ValueError:
      print(ValueError)
      return jsonify({'message': 'Ocurrio un error al cargar archivos.'}), 400


@app.route('/getCultivosAfectadosData', methods=['GET'])
@token_required
def getAgroData():
    try:
        species = getSpeciesData(connection)
        plantingMaterial = getPlantingMaterial(connection)
        costs = getCosts(connection)
        creditData = creditData_AssuranceData(connection)
        machineData = []
        for item in searchTipoInfraestructura(connection):
            machineData.append({'codInfraestructura': item[0], 'infraestructura': item[1]})

        infraestructuraData = getDataInfraestructura(connection)
        machineryData = []
        for item in searchTipoMaquinaria(connection):
            machineryData.append({'codMaquinaria': item[0], 'maquinaria': item[1]})

        if species['error'] or plantingMaterial['error'] or costs['error'] or creditData['error'] or infraestructuraData['error']:
            return jsonify({'message': 'Error al adquirir los datos', 'error': True})

        deleteFields = ('error', 'errorMessage')
        for k in deleteFields:
            species.pop(k, None)
            plantingMaterial.pop(k, None)
            costs.pop(k, None)
            creditData.pop(k, None)
            infraestructuraData.pop(k, None)


        return jsonify({'message':
                            {
                                **species,
                                **plantingMaterial,
                                **costs,
                                **creditData,
                                'infraestructureType': machineData,
                                **infraestructuraData,
                                'machineryData': machineryData
                            },
                        'error': False
                        })
    except Exception as e:
        print(e)
        return jsonify({'message': 'Ha ocurrido un error, intente de nuevo', 'error': True})


@app.route('/getSistemaProductivoPecuarioData', methods=['GET'])
@token_required
def getSistemaProductivoPecuarioData():
  try:
    affectedSistem = getSistemaPecuarioAfectado(connection)


    if affectedSistem['error']:
      return jsonify({'message': 'Error al adquirir los datos', 'error': True})

    deleteFields = ('error', 'errorMessage')
    for k in deleteFields:
      affectedSistem.pop(k, None)

    return jsonify({
      'message': {
        **affectedSistem
      } 
    })

  except Exception as e:
    print(e)
    return jsonify({'message': 'No se han podido obtener los datos', 'error': True}), 500



######################################
# Consultar los tipos de documento.
######################################
@app.route('/getDataDocumentType', methods=['GET'])
def getDataDocumentType():
  try:
    # consultar tipos de documento.
    resData = {'documentType':searchTipoDocumento(connection)}

    return jsonify({
      'message': {
        **resData
      } 
    })

  except Exception as e:
    print(e)
    return jsonify({'message': 'No se han podido obtener los datos', 'error': True}), 500



######################################
# declración app
######################################
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000)
