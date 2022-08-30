<template>
  <div>
    <v-card
      class="border-basic"
      elevation="2"
      max-width="600px"
      width="600px"
    >
      <v-divider></v-divider>
      <v-card-text>
        <v-container class="p-content text-center">

          <v-row>
            <v-col cols="12">
              {{ textEstado }}
              <v-progress-circular
                v-if="!estadoCorreo"
                :size="30"
                color="primary"
                indeterminate
              ></v-progress-circular>
              <v-icon
                v-if="estadoCorreo"
                color="success"
              >
               {{ iconEstado }}
              </v-icon>
            </v-col>
          </v-row>

        </v-container>
      </v-card-text>
    </v-card>
  </div>
</template>
<script>

import { user } from '../../services/api'

export default {
  name: 'validateUser',
  data() {
    return {

      code: '',
      textEstado: 'Esperando respuesta',
      estadoCorreo: false,
      iconEstado: 'mdi-check-all',

    }
  },
  created () {
    this.code = this.$route.params.code;
  },
  async mounted(){
   await this.validateUserToken();
  },
  methods: {
    async validateUserToken() {

      const code = this.code;

      if (!code) {
        this.textEstado = 'Ocurrio un error al validar su cuenta.';
        this.iconEstado = 'mdi-lock-alert-outline';
      }

      try {
        const res = await user.validateAccount({ code });
        if (res.status === 200) {
          this.textEstado = 'Correo validado';
          this.estadoCorreo = true;
          this.$router.push('/inicio');
        }
      } catch (error) {
        console.log(error)
      }

    }
  },
}
</script>
