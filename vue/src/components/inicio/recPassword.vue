<template>
  <div>
    <v-row justify="center">
      <v-dialog
        v-model="dialog"
        persistent
        max-width="700px"
      >
        <v-card flat>
          <div style="text-align:right">
            <v-btn class="color-primary-dark" icon dark @click="$emit('login')">
              <v-icon>mdi-close-circle</v-icon>
            </v-btn>
          </div>
          <v-card-title
          class="title-basic font-weight-bold justify-center"
          >
          <center>
          ¿HA OLVIDADO SU USUARIO O CONTRASEÑA?
          </center>
          </v-card-title>
          <v-card-text>
            <v-form
              lazy-validation
              ref="form"
              v-model="valid"
              >
              <v-row justify="center" no-gutters>
                <v-col cols="8">
                  <v-text-field
                    label="Correo electrónico"
                    v-model="email"
                    outlined
                    dense
                    :rules="emailRules"
                    required
                    >
                  </v-text-field>
                </v-col>
              </v-row>
              <v-row justify="center" no-gutters>
                <v-col
                cols="8"
                >
                  <v-btn
                    class="button-basic background-primary"
                    @click="recoverPassword"
                    style="width: 100%"
                    :loading="loading"
                    :disabled="loading"
                  >ENVIAR</v-btn>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-row>

  </div>
</template>
<script>

import {user} from '../../services/api'

export default {
  name: 'recuperarPassword',
  data () {
    return {
      dialog: true,
      loading: false,
      valid: true,
      email: '',
      emailRules: [
        v => !!v || 'E-mail is required',
        v => /.+@.+\..+/.test(v) || 'E-mail not valid'
      ]
    }
  },
  methods: {
    async recoverPassword() {
      if (this.$refs.form.validate()) {

        this.loading = true;

        try {

          const res = await user.forgotPassword({ email: this.email });
          console.log(res);
          if (res.status === 200) {
            this.$swal({
              icon: 'success',
              text: 'Correo de recuperación enviado.',
              confirmButtonText: 'Aceptar',
            });
            this.dialog = false;
          } else {
            this.$swal({
              icon: 'error',
              text: res.message,
              confirmButtonText: 'Aceptar',
            });
          }
          this.loading = false;
        } catch (error) {
          console.log(error);
          this.loading = false;
          this.$swal({
            icon: 'error',
            text: error.response.data.message,
            confirmButtonText: 'Aceptar',
          });
        }
      }
    }
  }
}
</script>
