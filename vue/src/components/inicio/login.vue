<template>
  <div>

    <v-overlay :value="overlay">
      <v-progress-circular
        indeterminate
        size="64"
      ></v-progress-circular>
    </v-overlay>

    <v-card
      class="border-basic pa-5"
      flat
      elevation="6"
      max-width="405"
      >
      <v-card-title class="mt-5 justify-center text-center">
          <v-col cols="12 ma-0 pa-0">
            <p class="title-basic title font-weight-bold text-md-h4 text-sm-h5">HERRAMIENTA DE <br> RECOLECCIÓN DE <br> DAÑOS Y PÉRDIDAS</p>
          </v-col>
          <v-col cols="12 ma-0 pa-0">
            <p class="title-basic subtitle-2 font-weight-bold text-md-h5 text-sm-h6">Sector Agropecuario</p>
          </v-col>
      </v-card-title>

      <v-card-text>

        <div class="font-weight-bold p-content">Usuario</div>
        <v-text-field
          prepend-inner-icon="mdi-email-outline"
          v-model="email"
          outlined
          dense
          >
        </v-text-field>

        <div class="font-weight-bold p-content" v-if="this.isOnline">Contraseña</div>
        <v-text-field
          prepend-inner-icon="mdi-lock-outline"
          v-model="password"
          outlined
          dense
          @click:append="show1 = !show1"
          :type="show1 ? 'text' : 'password'"
          :append-icon="show1 ? 'mdi-eye-outline' : 'mdi-eye-off-outline'"
          v-if="this.isOnline"
          >
        </v-text-field>

        <v-btn
          class="button-basic background-primary"
          @click="login"
          style="width: 100%"
        >
          Iniciar
        </v-btn>
        <v-row no-gutters align="center" class="my-3">
          <v-divider></v-divider>
          <v-divider></v-divider>
        </v-row>
        <center class="p-content" v-if="this.isOnline" >
          <p>
            ¿Olvidaste tu constraseña?
            <v-btn color="primary" text style="padding: 2px" small @click="$emit('recover')">Click aquí</v-btn>
          </p>
          <v-btn class="button-basic background-primary-dark" @click="$emit('register')" style="width: 100%">Registrarse</v-btn>
        </center>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>

import axios from 'axios';
import { user } from '../../services/api';
import jwtDecode from 'jwt-decode';
import { newEvent } from '../../services/api.js';
import { update } from '../../indexedDb/insertSystemData.js';
import { getData } from '../../indexedDb/getData';

export default {
  name: 'login',
  data () {
    return {
      overlay: false,
      email: '',
      password: '',
      show1: false,
    }
  },
  mounted() {
  },
  methods: {
    async login() {

      const email = this.email;
      const password = this.password;
      // this.$root.$emit('mainLoading', 'Loading...');
      this.overlay = true;

      try {
        if (this.isOnline) {
          await this.loginOnline(email, password);
        } else {
          await this.loginOffline(email, password);
        }

      } catch (error) {
        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar',
        });
      }
      // this.$root.$emit('mainLoading', 'Loading...');
      this.overlay = false;
    },
    async loginOnline(email, password) {

      const estado = await this.controlEventoOfflinePorUsuario(email);
      if(!estado) {
        return;
      }
      const res = await user.loggin({ email, password })

      if (res.status === 200 && 'token' in res.data) {
        const encoded = res.data.token;
        const decoded = jwtDecode(encoded);
        const obj = decoded.userobj;
        obj.token = encoded;

        this.sessionStar(obj, encoded);

        localStorage.setItem('dataUser', JSON.stringify(obj));

        const objects = ['login'];
        update({'login': obj}, objects, true);
        await this.updateSystemData();

      } else {
        this.$swal({
          icon: 'error',
          text: res.data.message,
          confirmButtonText: 'Aceptar',
        });
      }
    },
    async controlEventoOfflinePorUsuario(email) {
      var estado = true;

      try {

        const res = await getData('login', true);
        const resEvents = await getData('newEvent', false);

        if ((res.email !== email) && Object.keys(resEvents).length > 0) {
          estado = false;
          this.$swal({
            icon: 'error',
            text: 'Existen eventos no sincronizados por el usuario ' +res.email+
            ' en este dispositivo.',
            confirmButtonText: 'Aceptar',
          });
        }

      } catch (error) {
        this.$swal({
          icon: 'error',
          text: 'Error al validar los registros offline.',
          confirmButtonText: 'Aceptar',
        });
      }
      return estado;
    },
    async loginOffline(email, password) {

      try {
        const res = await getData('login', true);
        if (res.email === email) {
          this.sessionStar(res, '');
        } else {
          this.$swal({
            icon: 'error',
            text: 'Los datos de sesión no concuerdan.',
            confirmButtonText: 'Aceptar',
          });
        }

      } catch (error) {
        this.$swal({
          icon: 'error',
          text: 'Error al iniciar sesión en modo offline.',
          confirmButtonText: 'Aceptar',
        });
      }
    },
    sessionStar(obj, encoded) {
      this.$session.start();
      this.$session.set('usuario', obj.usuario);
      this.$session.set('email', obj.email);
      this.$session.set('activo', obj.activo);
      this.$session.set('token', encoded);
      this.$session.set('id_rol', obj.id_rol);
      let token = (this.isOnline) ? encoded : obj.token;
      axios.defaults.params = { token: token };

      this.$root.$emit('logged');
      this.$router.push('/home');
    },
    async updateSystemData() {

      try {

        const res = await newEvent.getSystemData();

        if (res.status === 200) {
          let data = res.data.message;
          const objects = ['forestal', 'pesquero', 'agricola', 'pecuario', 'productor', 'mapa', 'encabezado'];
          update(data, objects, true);

        } else {
          console.log('error');
          console.log(res);
        }

      } catch (error) {
        console.log('error');
        console.log(error);
      }
    },
  }
}
</script>


