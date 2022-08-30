import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    evento: {
      condJuridica: '',
      nombre: '',
      tiposDcto: '',
      dcto: '',
      dirRes: '',
      tel: '',
      sexo: '',
      fechaNac: '',
      gEtnico: '',
      tipoProd: '',
      relPre: '',
      tipoEv: '',
      subEv: '',
      sisProds: ['3'],
      especies: [
        {
          faseProd: '',
          espAfectada: '',
          espExtractiva: '',
          nombre: '',
          objetivo: '',
          fecha: '',
          densHectarea: '',
          areaSembrada: '',
          menuFecha: false
        }
      ]
    }
  },
  mutations: {
  },
  actions: {
  },
  modules: {
  }
})
