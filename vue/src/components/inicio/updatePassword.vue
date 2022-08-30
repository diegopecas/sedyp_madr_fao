<template>
  <div>
    <v-card flat class="border-basic">
      <div style="text-align:right">
      </div>
      <v-card-title
        class="title-basic font-weight-bold justify-center"
      >Por favor digite su nueva contraseña</v-card-title>
      <v-card-text>
        <v-form
          lazy-validation
          ref="form"
          v-model="valid"
        >
          <v-row justify="center" no-gutters>
            <v-col cols="12">
              <v-text-field
                label="Nueva contraseña"
                hint="Nueva contraseña"
                prepend-inner-icon="mdi-lock-outline"
                v-model="newPassword"
                outlined
                dense
                @click:append="show1 = !show1"
                :type="show1 ? 'text' : 'password'"
                :append-icon="show1 ? 'mdi-eye-outline' : 'mdi-eye-off-outline'"
                :rules="rules"
                required
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row justify="center" no-gutters>
            <v-col
              cols="12"
            >
              <v-btn
                class="button-basic background-primary-dark"
                @click="updatePassword"
                block
                :loading="loading"
                :disabled="loading"
              >Actualizar</v-btn>
            </v-col>
            <v-col
              cols="12"
              class="text-center"
            >
              <p>
                Regresar al
                <v-btn color="primary" text style="padding: 2px" small @click="$router.push('/inicio')">Inicio</v-btn>
              </p>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>
<script>

import { user } from '../../services/api';

export default {
  name: 'updatePassword',
  data() {
    return {
      form: true,
      valid: true,
      loading: false,
      newPassword: '',
      code: '',
      rules: [
        v => (v && v.length <= 16) || 'No más de 16 caracteres',
        v => (v && v.length >= 3) || 'No menos de 3 caracteres'
      ],
      show1: false,
    }
  },
  created () {
    this.code = this.$route.params.code;
  },
  methods: {
    async updatePassword() {
      if (this.$refs.form.validate()) {

        this.loading = true;

        try {

          const res = await user.updatePassword({ code:this.code, password:this.newPassword });
          console.log(res);
          if (res.status === 200) {
            this.$swal({
              icon: 'success',
              text: 'Contraseña actualizada.',
              confirmButtonText: 'Aceptar',
            });
            this.$router.push('/inicio');
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
  },
}
</script>
