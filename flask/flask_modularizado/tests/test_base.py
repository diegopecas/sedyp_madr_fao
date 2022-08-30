import json
import base64
import pathlib
import os
import jwt
import datetime



from flask_testing import TestCase
from flask.helpers import url_for
from main import app
from flask import current_app
from app.config import Config
from app.helpers import searchUser
from tests.database_functions_test import delete_user, get_user_token
from app.services.database_service import DatabaseService


class MainTest(TestCase):

    db_service = DatabaseService()
    connection = db_service.get_connection()

    # Creates the app that will be tested
    def create_app(self):
        app.config['TESTING'] = True  # Let the app know we're testing
        app.config['WTF_CSRF_ENABLED'] = False  # Disable the CSRF token check
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

        return app

    # Validates that the app exists
    def test_app_exists(self):
        print('test_app_exists')
        self.assertIsNotNone(current_app)

    # Validated that the app is in test mode
    def test_app_in_test_mode(self):
        print('test_app_in_test_mode')
        self.assertTrue(current_app.config['TESTING'])

    # Test that the home route works
    def test_home_route(self):
        print('test_home_route')
        response = self.client.get('/')
        self.assertTrue(json.loads(response.data.decode())['success'])

    # Test the existence of the auth blueprint
    def test_auth_blueprint_exists(self):
        print('test_auth_blueprint_exists')
        self.assertIn('auth', self.app.blueprints)

    # Test login user that exists
    def test_success_login_user_(self):
        print('test_success_login_user_')
        existent_user = {
            'email': 'dieandbonvia@gmail.com',
            'password': 'diego123'
        }

        response = self.client.post('/auth/login', json=existent_user)
        self.assertTrue('token' in json.loads(response.data.decode()))

    # Test login user that not exists
    def test_fail_login_user(self):
        print('test_fail_login_user')
        not_existent_user = {
            'email': 'username@dominio.com',
            'password': 'password'
        }

        response = self.client.post('/auth/login', json=not_existent_user)
        self.assertFalse('token' in json.loads(response.data.decode()))

    # Test a new user register process
    def test_success_user_register(self):
        print('test_success_user_register')
        register_user_new = {
            "obj": {
                "usuario": "diegoandbonvia",
                "numDocument": "123456789002",
                "email": "dieanbonvia@gmail.com",
                "password": "diego123",
                "active": "S",
                "firstName": "Diego prueba modul",
                "lastName": "Bonilla prueba modul",
                "typeDocument": 2,
                "institution": "prueba modul",
                "workCenter": "cargo prueba modul"
            }
        }

        user_to_delete = searchUser(
            register_user_new['obj']['numDocument'], register_user_new['obj']['email'])
        if user_to_delete == False:
            response = self.client.post(
                '/auth/createUser', json=register_user_new)
            self.assertTrue('token' in json.loads(response.data.decode()))
        else:
            delete_user(register_user_new['obj']['email'])
            response = self.client.post(
                '/auth/createUser', json=register_user_new)
            self.assertTrue('token' in json.loads(response.data.decode()))

    # Test an older user register process, is expected to fail cause the user already exists
    def test_fail_user_register(self):
        print('test_fail_user_register')
        register_user_old = {
            "obj": {
                "usuario": "DiegoBonilla",
                "numDocument": "12345678901",
                "email": "dieandbonvia@gmail.com",
                "password": "diego123",
                "active": "S",
                "firstName": "Diego prueba modul",
                "lastName": "Bonilla prueba modul",
                "typeDocument": 2,
                "institution": "prueba modul",
                "workCenter": "cargo prueba modul"
            }
        }

        response = self.client.post('/auth/createUser', json=register_user_old)
        self.assertFalse('token' in json.loads(response.data.decode()))

    # Test the existence of the user blueprint
    def test_user_blueprint_exists(self):
        print('test_user_blueprint_exists')
        self.assertIn('user', self.app.blueprints)

    # Test validate new user that has not been validated yet
    def test_validate_new_user(self):
        print('test_validate_new_user')
        email = "dieanbonvia@gmail.com"
        token = get_user_token(email)

        to_hash = email+'-'+token[0]['token']
        hashed = base64.b64encode(to_hash.encode())

        validate_new_user = {
            "code": hashed.decode()
        }

        response = self.client.post('/user/validate', json=validate_new_user)
        self.assertTrue(json.loads(response.data.decode())
                        ['message'] == "Correo validado")

    # Test validate older user, it should returns an error cause the user has been validated
    def test_validate_older_user(self):
        print('test_validate_older_user')
        email = "dieandbonvia@gmail.com"
        token = get_user_token(email)

        to_hash = email+'-'+token[0]['token']
        hashed = base64.b64encode(to_hash.encode())

        validate_new_user = {
            "code": hashed.decode()
        }

        response = self.client.post('/user/validate', json=validate_new_user)
        self.assertTrue(json.loads(response.data.decode())[
                        'message'] == "El correo ya ha sido validado")

    # Test validate that a user could be updated
    def test_update_user(self):
        print('test_update_user')
        update_user_info = {
            "obj": {
                "numDocument": "12345678901",
                "email": "dieandbonvia@gmail.com",
                "idUser": 31,
                "usuario": "DiegoBonillaUpdateTest",
                "active": "S",
                "firstName": "Diego",
                "lastName": "Bonilla",
                "typeDocument": 2,
                "institution": "Institucion update user",
                "workCenter": "Cargo update user",
                "password": "diego123"
            }
        }

        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)

        response = self.client.post('/user/updateUser', json=update_user_info, query_string={
            "token": token})
        self.assertTrue('token' in json.loads(response.data.decode()))

    
    # Test that the get document type endpoint works properly
    def test_get_data_document_type(self):
        print('test_get_data_document_type')
        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.get('/user/getDataDocumentType', query_string={
            "token": token})
        self.assertFalse(json.loads(response.data.decode())['error'])

    # Test the existence of the event blueprint
    def test_event_blueprint_exists(self):
        print('test_event_blueprint_exists')
        self.assertIn('eventos', self.app.blueprints)

    # Test that the get events endpoint works properly
    def test_get_events(self):
        print('test_get_events')
        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.get('/event/getEventos', query_string={
            "token":token})
        self.assertTrue('token' in json.loads(response.data.decode()))
    
    # Test that the get data productor endpoint works properly
    def test_get_data_productor(self):
        print('test_get_data_productor')
        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.get('/event/dataProductor', query_string={
            "token":token})
        self.assertTrue('token' in json.loads(response.data.decode()))


    # Test that the dataMapa endpoint works properly
    def test_get_data_mapa(self):
        print('test_get_data_mapa')
        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.get('/event/dataMapa', query_string={
            "token": token})
        self.assertTrue('token' in json.loads(response.data.decode()))


    # Test that the get data event returns the needed info
    def test_get_event_data(self):
        print('test_get_event_data')
        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.get('/event/dataEvento', query_string={
            "token": token})
        self.assertTrue('token' in json.loads(response.data.decode()))


    # Test that the get event data specie returns the expected information
    def test_get_event_data_event_specie(self):
        print('test_get_event_data_event_specie')
        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.get('/event/dataEventoEspecie', query_string={
            "token": token})
        self.assertTrue('token' in json.loads(response.data.decode()))


    # Test that the forestal event is beeing saved
    def test_save_event_forestal(self):
        print('test_save_event_forestal')
        event_to_save = {
            "dataEncabezadoEvento": {
                "tipoEv": 2,
                "subEv": 13,
                "sisProds": [
                    3
                ],
                "latitud": 7.086642046163902,
                "longitud": -73.13482761383058,
                "departamento": 1,
                "municipio": 1,
                "precision": "3",
                "altitud": "22",
                "enVereda": "",
                "codVereda": "",
                "nombrePuerto": "",
                "observacion": "asdc",
                "idUsuario": 3,
                "caladeros": [
                    {
                        "position": {
                            "lat": 3.0095,
                            "lng": -76.4849
                        }
                    },
                    {
                        "position": {
                            "lat": 7.086294837280861,
                            "lng": -73.1352996826172
                        }
                    },
                    {
                        "position": {
                            "lat": 7.086431416813995,
                            "lng": -73.1347066210583
                        }
                    }
                ]
            },
            "dataProductor": [
                {
                    "condJuridica": 2,
                    "nombre": "name persona",
                    "tipoDcto": 6,
                    "dcto": "1234234",
                    "tipoProd": 2,
                    "relPre": 2
                }
            ],
            "dataEspecies": {
                "forestal": [
                    {
                        "afectacionesEnMaquinaria": True,
                        "tipoInfraestructura": [
                            1,
                            2,
                            3,
                            4
                        ],
                        "actividad": {},
                        "costoGenerado": "",
                        "rubrosIndirectos": {},
                        "costoGeneradoIndirecto": "",
                        "costosDirectos": [
                            {
                                "costo": "5467568",
                                "id": 3,
                                "rubros": "Mano de obra directa establecimiento"
                            }
                        ],
                        "costosInDirectos": [
                            {
                                "costo": "89098",
                                "id": 5,
                                "rubros": "Arrendamiento de la tierra"
                            }
                        ],
                        "semilla": [
                            {
                                "especieSemilla": "nombre semilla",
                                "tipo": 2,
                                "lotePropagacionSemilla": [
                                    1,
                                    2,
                                    3
                                ],
                                "cantidadAlmacenada": "23",
                                "unidad": 2,
                                "valorPesoAfectado": "345345",
                                "nombreTipo": "Sexual",
                                "lote": " - Rodales semilleros - Jardínes clonales - Otro",
                                "unidadSemilla": "Unidades"
                            }
                        ],
                        "fertilizante": [
                            {
                                "tipoFertilizante": 1,
                                "nombreFertilizante": "nombre fertilizante",
                                "cantidadKgLt": "12",
                                "valorPeso": "345345",
                                "nombreTipo": "Sólido"
                            }
                        ],
                        "plaguicida": [
                            {
                                "nombrePlaguicida": "nombre plaguicida",
                                "listaPresentacion": 2,
                                "cantidad": "45",
                                "valorPeso": "5346456",
                                "nombreTipo": "Fungicidas"
                            }
                        ],
                        "maquinariaAgricola": [
                            {
                                "tipoMaquinariaAgricola": 3,
                                "nombreMarca": "nombre maquinaria",
                                "valorPeso": "345646",
                                "nombreTipo": "Arados e implementos de labranza",
                                "edadMaq": 4,
                                "porcDismProdMaq": 17
                            }
                        ],
                        "faseProd": 2,
                        "espAfectada": 3,
                        "espExtractiva": 3,
                        "nombre": "nombre común forestal",
                        "objetivo": 1,
                        "noArbolesAntesAfectacion": "43",
                        "noEntresacas": "456",
                        "valEntreSacas": "5467567",
                        "porceEntreSacas": "45",
                        "diametroPromedio": "45",
                        "alturaComercial": "45",
                        "alturaTotal": "45",
                        "plantacionAnos": "765",
                        "porceArbolesTurnoFinal": "678",
                        "vlMaderaAfectado": "76",
                        "menuFecha": False,
                        "fecha": "2021-07-21",
                        "densHectarea": "67",
                        "areaSembrada": "678",
                        "areaAfectadaHectareas": "78",
                        "menuFechaAfactaForestal": False,
                        "fechaAfactaForestal": "2021-07-21",
                        "diasAfectoSistemaForestal": "4",
                        "noArbolesAfectados": "6",
                        "valorVenderProduccionAfectada": "789789"
                    }
                ],
                "agropecuario": [],
                "infoPecuario": []
            }
        }

        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.post('/event/guardarEvento', json=event_to_save, query_string={
            "token": token})
        self.assertTrue('token' in json.loads(response.data.decode()))


    # Test that the agro event is beeing saved
    def test_save_event_agro(self):
        print('test_save_event_agro')
        event_to_save = {
            "dataEncabezadoEvento":{
                "tipoEv":2,
                "subEv":12,
                "sisProds":[1],
                "latitud":7.086732544597252,
                "longitud":-73.13486516475679,
                "departamento":1,
                "municipio":1,
                "precision":"3",
                "altitud":"4",
                "enVereda":"",
                "codVereda":1,
                "nombrePuerto":"name puerto",
                "observacion":"asdasd",
                "idUsuario":3,
                "caladeros": [ 
                    { 
                        "position": { 
                            "lat": 3.0095, 
                            "lng": -76.4849 
                        }
                    }, 
                    { 
                        "position": { 
                            "lat": 7.086294837280861, 
                            "lng": -73.1352996826172 
                        }
                    }, 
                    { 
                        "position": { 
                            "lat": 7.086431416813995, 
                            "lng": -73.1347066210583 
                        }  
                    } 
                ]
            },
            "dataProductor":[{
                "condJuridica":2,
                "nombre":"name jurida",
                "tipoDcto":6,
                "dcto":"12323",
                "tipoProd":2,
                "relPre":5
            },{
                "condJuridica":1,
                "nombre":"persona natural",
                "tipoDcto":2,
                "dcto":"232323",
                "dirRes":"crr 25",
                "tel":"3656565",
                "fechaNac":"2021-05-05",
                "sexo":1,
                "gEtnico":4,
                "relPre":3
            }],
            "dataEspecies":{
                "forestal":[],
                "agropecuario":[{
                    "nombreCultivo":1,
                    "unidadArea":2,
                    "areaCultivo":"23",
                    "materiralSiembra":1,
                    "cantSemillas":"2",
                    "medidaSemilla":4,
                    "equivaleKilos":2,
                    "fuenteSemilla":1,
                    "menuFechaAfectacion":False,
                    "fechaAfectacion":"2021-05-06",
                    "diasCultivoExpuesto":"3",
                    "menuFechaSiembra":False,
                    "fechaSiembra":"2021-05-01",
                    "menuFechaPrimeCosecha":False,
                    "fechaPrimeCosecha":"2021-02",
                    "menuFechaEsperaCosecha":False,
                    "fechaEsperaCosecha":"2021-02",
                    "cantCosechada":"2",
                    "medidaCantCosechada":4,
                    "equivaleKilosCosecha":3,
                    "totalReciCosechado":"23333",
                    "cantProduProducir":"3",
                    "medidaReportar":4,
                    "equivaleKilosReportar":4,
                    "totalReportado":"45454",
                    "totalProyectaVenta":"3",
                    "costoPromeJornal":"2345445",
                    "idEntidadesBancarias":2,
                    "porceCostoCredito":"2",
                    "valCultiAsegurado":"34234234",
                    "tipoSeguro":2,
                    "porceResiembra":"2",
                    "afectaMaquinaria":True,
                    "nombre":"Acelga",
                    "costosDirectos":[{
                        "id":1,
                        "noJornales":"1",
                        "costo":"100",
                        "actividad":"Siembra"
                    },{
                        "id":2,
                        "noJornales":"2",
                        "costo":"3",
                        "actividad":"Fertilización"
                    }],
                    "costosInDirectos":[{
                        "id":4,
                        "costo":"2323",
                        "actividad":"Seguros Agrícolas"
                    }],
                    "tipoInfraSemilla":[{
                        "especie":"name semilla",
                        "canSemillas":"2",
                        "valPesos":"32323"
                    }],
                    "tipoInfraFertilizante":[{
                        "idTipoFertilizante":2,
                        "nombre":"name ferti",
                        "menuFechaAdquisicion":False,
                        "fechaAdquisicion":"2021-05-01",
                        "canFertilizante":"2",
                        "valPesos":"323",
                        "nombreTipoFerti":"Líquido"
                    }],
                    "tipoInfraPlaguicidas":[{
                        "idTipoPlaguicida":2,
                        "idTipoPresentacion":2,
                        "cantPlaguicidaKg":"3",
                        "cantPlaguicidaLt":"434",
                        "valPesos":"3454545",
                        "nombreTipoPlaguicida":"Herbicidas"
                    }],
                    "tipoInfraMaquinaria":[{
                        "idTipoMaquinariaAgricola":1,
                        "anoAdquisicion":"2019",
                        "valorPesos":"23434",
                        "porceDisminucion":"3",
                        "nombreTipoMaquinaria":"Arados e implementos de labranza"
                    }]
                }]
            }
        }
        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.post('/event/guardarEvento', json=event_to_save, query_string={
            "token": token})
        self.assertTrue('token' in json.loads(response.data.decode()))


    # Test that the peq event is beeing saved
    def test_save_event_peq(self):
        print('test_save_event_peq')
        event_to_save = {
            "dataEncabezadoEvento": {
                "tipoEv": 2,
                "subEv": 12,
                "sisProds": [2],
                "latitud": 7.086732544597252,
                "longitud": -73.13486516475679,
                "departamento": 1,
                "municipio": 1,
                "precision": "3",
                "altitud": "4",
                "enVereda": "",
                "codVereda": 1,
                "nombrePuerto": "name puerto",
                "observacion": "asdasd",
                "idUsuario": 3,
                "caladeros": [ 
                    { 
                        "position": { 
                            "lat": 3.0095, 
                            "lng": -76.4849 
                        }
                    }, 
                    { 
                        "position": { 
                            "lat": 7.086294837280861, 
                            "lng": -73.1352996826172 
                        }
                    }, 
                    { 
                        "position": { 
                            "lat": 7.086431416813995, 
                            "lng": -73.1347066210583 
                        }  
                    } 
                ]
            },
            "dataProductor": [{
                "condJuridica": 2,
                "nombre": "name jurida",
                "tipoDcto": 6,
                "dcto": "12323",
                "tipoProd": 2,
                "relPre": 5
                },
                {
                "condJuridica": 1,
                "nombre": "persona natural",
                "tipoDcto": 2,
                "dcto": "232323",
                "dirRes": "crr 25",
                "tel": "3656565",
                "fechaNac": "2021-05-05",
                "sexo": 1,
                "gEtnico": 4,
                "relPre": 1
                }
            ],
            "dataEspecies": {
            "forestal": [],
            "agropecuario": [],
            "infoPecuario": [{
                "dataApicola": [{
                "numColmenas": 35,
                "valorColmena": "35",
                "propoleoMensual": 35,
                "mielMensual": 352,
                "jaleaMensual": 3435,
                "valorMensual": "3543",
                "ingresoMensual": "35453",
                "sistema": {
                    "dataCamposNuevos": {
                    "sistemaNuevo": ""
                    },
                    "sistema": 2,
                    "nombreSistema": "Explotación apícola"
                },
                "nombreSistema": "Explotación apícola",
                "dataMaquinaria": [{
                    "dataCamposNuevos": {
                    "nuevoInsumo": ""
                    },
                    "tipoInsumo": 4,
                    "cantInsumo": 34,
                    "unidadMedida": 3,
                    "valorBienes": "3234",
                    "nombreComercial": "comercial",
                    "tipoMaquinariaBba": 7,
                    "nombreMaquinariaBba": "nombre instalacion",
                    "valorReparacionBba": "435",
                    "tipoMaquinariaPem": 7,
                    "nombreMarcaPem": "nombre marca",
                    "valorReparacionPem": "34324",
                    "nombreInsumo": "Medicina",
                    "nombreMedida": "Arroba",
                    "nombreMaquiBba": "Herramientas de mano",
                    "nombreMaquiPem": "Herramientas de mano"
                }],
                "dataInfraestructura": []
                }],
                "dataPecuario": [{
                "dataCamposNuevos": {
                    "pesoNuevo": "200",
                    "unidadMedidaNuevo": {
                    "nombre": "nuevo nombre",
                    "unidad": "129"
                    },
                    "unidadArea": "Unidad nueva",
                    "tipoProductoNuevo": "nuevo producto",
                    "pesoProduccionNuevo": "17"
                },
                "nombreRaza": "nombre avicola",
                "numAnimal": 34234,
                "pesoAnimal": 443,
                "uniMedidaAnimal": 4,
                "peso": 6,
                "valorAnimal": "345",
                "areaAnimal": "34",
                "unidadArea": 4,
                "menuFechaProduccion": False,
                "fechaProduccion": "2021-04-04",
                "menuFechaIniEvento": False,
                "fechaIniEvento": "2021-06-01",
                "numAnimalEnfermos": 34,
                "numAnimalHembMuerto": 345,
                "numAnimalMachMuerto": 354,
                "edadAnimal": 292,
                "tipoProducto": 5,
                "produMensualAfectacion": "453",
                "produPotencial": "34",
                "unidadProdccion": 2,
                "pesoProduccion": 3,
                "valorVentaProducto": "435",
                "huevosAvicola": True,
                "mesesRecuperarPecuaria": "5",
                "sistema": {
                    "dataCamposNuevos": {
                    "sistemaNuevo": ""
                    },
                    "sistema": 3,
                    "nombreSistema": "Explotación avícola"
                },
                "nombreSistema": "Explotación avícola",
                "costosVariables": [
                    [{
                    "tipoCosto": "1",
                    "valor": "45"
                    }, {
                    "tipoCosto": "1",
                    "valor": "435"
                    }]
                ],
                "costosFijos": [
                    [{
                    "tipoCosto": "1",
                    "valor": "345"
                    }, {
                    "tipoCosto": "1",
                    "valor": "345"
                    }]
                ],
                "dataMaquinaria": [{
                    "dataCamposNuevos": {
                    "nuevoInsumo": "nuevo insumo"
                    },
                    "tipoInsumo": 6,
                    "cantInsumo": 34,
                    "unidadMedida": 2,
                    "valorBienes": "345",
                    "nombreComercial": "comercial",
                    "tipoMaquinariaBba": 6,
                    "nombreMaquinariaBba": "nombre instalaciones",
                    "valorReparacionBba": "45",
                    "tipoMaquinariaPem": 3,
                    "nombreMarcaPem": "nombre bin",
                    "valorReparacionPem": "45",
                    "nombreInsumo": "Forraje",
                    "nombreMedida": "Kilogramos",
                    "nombreMaquiBba": "Equipos veterinarios y cirugía",
                    "nombreMaquiPem": "Implementos para el pesaje"
                }],
                "dataInfraestructura": [{
                    "tipActivo": 2,
                    "nombreEquipoConstruc": "nombre equipo",
                    "menuFechaConstruc": False,
                    "fechaConstruc": "2021-06-01",
                    "valorPagadoConstruc": "453",
                    "valorReponerConstruc": "345",
                    "tipAfecta": 1,
                    "areaAfectada": 435,
                    "valorReparacion": "435",
                    "mesesReparacion": 435,
                    "nombreActivo": "Construcciones",
                    "nombreTipoAfecta": "Área de lavado"
                }]
                }],
                "dataMaquinaria": [],
                "dataInfraestructura": [],
                "nombreEspecie": "Nombre especie pecuario/acuicola"
            }]
            }

        }

        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.post('/event/guardarEvento', json=event_to_save, query_string={
        "token": token})
        self.assertTrue('token' in json.loads(response.data.decode()))


    # Test that the fishing info is being saved
    def test_save_fishing_system(self):
        print('test_save_fishing_system')
        event_to_save = {
            "dataEncabezadoEvento": {
                "tipoEv": 2,
                "subEv": 12,
                "sisProds": [
                    4
                ],
                "latitud": 7.086732544597252,
                "longitud": -73.13486516475679,
                "departamento": 1,
                "municipio": 1,
                "precision": "3",
                "altitud": "4",
                "enVereda": "",
                "codVereda": 1,
                "nombrePuerto": "name puerto",
                "observacion": "asdasd",
                "idUsuario": 3,
                "caladeros": [
                    {
                        "position": {
                            "lat": 3.0095,
                            "lng": -76.4849
                        }
                    },
                    {
                        "position": {
                            "lat": 7.086294837280861,
                            "lng": -73.1352996826172
                        }
                    },
                    {
                        "position": {
                            "lat": 7.086431416813995,
                            "lng": -73.1347066210583
                        }
                    }
                ]
            },
            "dataProductor": [
                {
                    "condJuridica": 2,
                    "nombre": "name jurida",
                    "tipoDcto": 6,
                    "dcto": "12323",
                    "tipoProd": 2,
                    "relPre": 5
                },
                {
                    "condJuridica": 1,
                    "nombre": "persona natural",
                    "tipoDcto": 2,
                    "dcto": "232323",
                    "dirRes": "crr 25",
                    "tel": "3656565",
                    "fechaNac": "2021-05-05",
                    "sexo": 1,
                    "gEtnico": 4,
                    "relPre": 7
                }
            ],
            "dataEspecies": {
                "forestal": [],
                "agropecuario": [],
                "infoPecuario": [],
                "infoPesquero": [
                    {
                        "puertoDesembarque": "nombre puerto desembarque",
                        "tipoPesqueria": [
                            1,
                            2,
                            3,
                            4
                        ],
                        "especieExplotada": "principales especies explotadas",
                        "embarcacionAfectada": True,
                        "instalacionAfectada": True,
                        "numeroRedes": "23",
                        "valorRedes": "234",
                        "redesAfectadas": True,
                        "numeroFaenas": "234",
                        "cantidadFaenasMes": "345",
                        "valorVentaPeces": "465",
                        "maquinariaAfectada": True,
                        "embarcaciones": [
                            {
                                "tipoEmbarcacion": "tipo embarcacion",
                                "patenteEmbarcacion": "patente embarcacion",
                                "esloraEmbarcacion": "234",
                                "valorEmbarcacion": "234",
                                "observacionEmbarcacion": "obs embarcacion"
                            }
                        ],
                        "maquinarias": [
                            {
                                "activoProductivo": 4,
                                "nombreEquipo": "nombre equipo",
                                "menuFechaAdquisicion": False,
                                "fechaAdquisicion": "2021-07-01",
                                "valorActivo": "3245",
                                "valorReponer": "345"
                            },
                            {
                                "activoProductivo": 2,
                                "nombreEquipo": "nombre bien",
                                "menuFechaAdquisicion": False,
                                "fechaAdquisicion": "2021-07-02",
                                "valorActivo": "345",
                                "valorReponer": "345",
                                "tipoConstruccion": 2,
                                "areaAfectada": "345",
                                "valorInvertidoAdecuacion": "3546",
                                "valorEstimadoReconstruccion": "456",
                                "mesesReconstruccion": "45",
                                "nombreTipoConstruccion": "Área de almacenamiento"
                            }
                        ]
                    }
                ]
            }
        }

        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.post('/event/guardarEvento', json=event_to_save, query_string={
        "token": token})
        self.assertTrue('token' in json.loads(response.data.decode()))


    # Test the save tracing route
    def test_save_tracing(self):
        print('test_save_tracing')
        main_route = str(pathlib.Path(__file__).parent.absolute())

        files0 = open(main_route+'/test_files/files0.txt', 'r')
        files1 = open(main_route+'/test_files/files1.txt', 'r')


        form_data = {
            'idEvento':'4',
            'observacion':'probando seguimiento',
            'idUsuario':'31',
            'contador':'2',
            'files0': files0,
            'files1': files1
        }

        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)

        response = self.client.post('/event/guardarSeguimiento', content_type='multipart/form-data', data=form_data, query_string={
        "token": token})

        self.assertTrue('token' in json.loads(response.data.decode()))

    
    # Test that get attached returns the needed info
    def test_get_attached(self):
        print('test_get_attached')
        obj = {
            'ruta': '/adjuntos/seguimiento/4',
            'nombre': 'files0.txt'
        }

        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.post('/event/getAdjunto', json=obj, query_string={
        "token": token})

        if response.data.decode():
            return True
        else:
            return False


    # Test that the tracing are returned correctly
    def test_get_tracing(self):
        print('test_get_tracing')
        obj = {
            'idEvento': '31'
        }
        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.post('/event/getSeguimiento', json=obj, query_string={
        "token":token})

        self.assertTrue('token' in json.loads(response.data.decode()))


    # Test that the report per event are returned
    def test_set_data_report_event(self):
        print('test_set_data_report_event')
        obj = {
            'idEvento': '31'
        }

        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.post('/event/setDataInformesEvento', json=obj, query_string={
        "token": token})

        self.assertTrue('token' in json.loads(response.data.decode()))


    # Test that the information for general reports is returned
    def set_data_general_reports(self):
        print('set_data_general_reports')
        obj = {
            'idEvento': '31',
            'ubicacion': {
                'municipio': 1
            }
        }

        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.post('/event/setDataInformesGenerales', json=obj, query_string={
        "token": token})

        self.assertTrue('token' in json.loads(response.data.decode()))

  
    # Test that the needed info for agro module is returned correctly
    def test_get_agro_data(self):
        print('test_get_agro_data')
        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.get('/event/getCultivosAfectadosData', query_string={
        "token": token})

        self.assertFalse(json.loads(response.data.decode())['error'])



    # Test that the needed info for peq module is returned correctly
    def test_get_peq_data(self):
        print('test_get_peq_data')
        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.get('/event/getSistemaProductivoPecuarioData', query_string={
        "token": token})

        self.assertFalse(json.loads(response.data.decode())['error'])

    
    # Test that the needed info for fishing module is returned correctly
    def test_fishing_data(self):
        print('test_fishing_data')
        res = {
            'id': 31,
            'usuario': 'DiegoBonillaUpdateTest',
            'email': "dieandbonvia@gmail.com",
            'activo': "S",
            'nombre': "Diego",
            'apellido': "Bonilla",
            'nuDocumento': "12345678901",
            'idDocumento': "2",
            'institucion': "Institucion update user",
            'cargo': "Cargo update use"
        }

        token = jwt.encode({'userobj': res, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=60)}, Config.SECRET_KEY)
        response = self.client.get('/event/dataPesquero', query_string={
            "token": token})
        self.assertFalse(json.loads(response.data.decode())['error'])
