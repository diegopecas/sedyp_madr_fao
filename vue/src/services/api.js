import axios from 'axios'

const user = {
  loggin: params => axios.post('/auth/login', params),
  createUser: params => axios.post('/auth/createUser', params),
  updateUser: params => axios.post('/user/updateUser', params),
  storeSolicitud: params => axios.post('solicitud', params),
  getSolicitudes: () => axios.get('solicitudes'),
  approve: params => axios.post('approve', params),
  reject: params => axios.post('reject', params),
  getUsers: () => axios.get('users'),
  editUser: params => axios.put('user', params),
  changePassword: params => axios.post('changePassword', params),
  recoverPassword: params => axios.post('recoverPassword', params),
  validateAccount: params => axios.post('/user/validate', params),
  getPermisos: params => axios.get('permits', params),
  deletePermStatus: params => axios.delete('/permits/permStatus', params),
  setPermStatus: params => axios.post('/permits/permStatus', params),
  setRol: params => axios.post('permits/', params),
  deleteRolUser: params => axios.post('permits/deleteRol', params),
  getAllUsers: params => axios.get('/user/getUsers'),
  changeRol: params => axios.post('/user/changeRol', params),
  forgotPassword: params => axios.post('/auth/forgotPassword', params),
  updatePassword: params => axios.post('/user/forgotPassword', params),
}

const eventosCreados = {
  getEventos: () => axios.get('/event/getEventos'),
  getValidateEvent: params => axios.post('event/validate', params),
  getAdjunto: params => axios.post('/event/getAdjunto', params),
  getEvento: params => axios.post('/event/getEvento', params),
}

const newEvent = {
  getSystemData: params => axios.get('/event/systemData', params),
  getDataProductor: params => axios.get('/event/dataProductor', params),
  getDataMapa: params => axios.get('/event/dataMapa', params),
  getDataEvent: params => axios.get('/event/dataEvento', params),
  getDataEventSpecie: params => axios.get('/event/dataEventoEspecie', params),
  setDataEvento: params => axios.post('/event/guardarEvento', params, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  setDataEventOffline: params => axios.post('/event/guardarEventoOffline', params, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  modifyEvent: params => axios.post('/event/modifyEvent', params, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  getDataAgropecuario: params => axios.get('/event/getCultivosAfectadosData', params),
  getDataPecuario: params => axios.get('/event/getSistemaProductivoPecuarioData', params),
  getDataPesquero: params => axios.get('/event/dataPesquero', params),
  getAgroCalc: params => axios.post('/event/agroCalc' , params),
}

const seguimientoEvento = {
  getSeguimiento: params => axios.post('/event/getSeguimiento', params),
  setSeguimiento: params => axios.post('/event/guardarSeguimiento', params, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  getAdjunto: params => axios.post('/event/getAdjunto', params, { responseType: 'blob' }),
}

const informesEvento = {
  setDataInformesEvento: params => axios.post('/event/setDataInformesEvento', params),
  setDataInformesGenerales: params => axios.post('/event/setDataInformesGenerales', params)
}

const dataGeneral = {
  getDataDocumentoType: params => axios.get('/user/getDataDocumentType', params),
  getDataAudit: params => axios.get('audit/'),
  readNotification: params => axios.post('/user/notifications', params),
}

const configuracionGastos = {
  getAgroCalcAct: params => axios.get('/event/agroCalcAct', params),
  postAgroCal: params => axios.post('/event/agroCalc', params),
  putAgroCal: params => axios.put('/event/agroCalc', params),
}

export {
  user,
  eventosCreados,
  newEvent,
  seguimientoEvento,
  informesEvento,
  dataGeneral,
  configuracionGastos
}
