import Vue from 'vue'
import App from './App.vue'
import './registerServiceWorker'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'
import '@babel/polyfill'
import VueSession from 'vue-session'
import axios from 'axios'
import Toasted from 'vue-toasted'
import VueApexCharts from 'vue-apexcharts'
import 'leaflet/dist/leaflet.css'
import 'leaflet-minimap/dist/Control.MiniMap.min.css'
import VueSweetalert2 from 'vue-sweetalert2'
import 'sweetalert2/dist/sweetalert2.min.css'
import createStorage from './indexedDb/createStorage'
import VueOffline from 'vue-offline'
import Vue2Filters from 'vue2-filters'

Vue.use(VueOffline)
Vue.component('VueOffline', VueOffline)
Vue.use(VueApexCharts)
Vue.component('apexchart', VueApexCharts)
Vue.use(VueSession)
Vue.use(Toasted)
Vue.use(VueSweetalert2)
Vue.config.productionTip = false
var Vue2FiltersConfig = {
  percent: {
    decimalDigits: 2,
    multiplier: 100,
    decimalSeparator: '.'
  },
  currency: {
    symbol: '',
    decimalDigits: 2,
    thousandsSeparator: ',',
    decimalSeparator: '.',
    symbolOnLeft: true,
    spaceBetweenAmountAndSymbol: false,
    showPlusSign: false
  },
  pluralize: {
    includeNumber: false
  },
  ordinal: {
    includeNumber: false
  }
}
Vue.use(Vue2Filters, Vue2FiltersConfig)

axios.defaults.headers.Accept = 'application/json'
axios.defaults.baseURL = process.env.NODE_ENV === 'production' ? 'http://faobackend.southcentralus.azurecontainer.io:4000' : 'https://faobackend.azurewebsites.net/'

var self = Vue.prototype

async function restoreSession () {
  const loggedIn = self.$session.exists()
  if (loggedIn) {
    const token = self.$session.get('token')
    axios.defaults.params = { token: token }
  }
}

restoreSession()

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')
