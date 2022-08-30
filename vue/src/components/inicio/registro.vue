<template>
  <div>

    <v-row justify="center">
    <v-dialog
      v-model="dialog"
      persistent
      max-width="700px"
    >


    <v-overlay :value="overlay">
      <v-progress-circular
        indeterminate
        size="64"
      ></v-progress-circular>
    </v-overlay>

    <v-card
     class="border-basic"
     flat
    >
      <div style="text-align:right">
        <v-btn class="color-primary-dark" icon dark @click="cerrarModal()">
          <v-icon>mdi-close-circle</v-icon>
        </v-btn>
      </div>
      <v-card-title style="display:inline; text-align: center">
        <p class="title-basic subtitle font-weight-bold" v-if="!updateUser">
          Registro
        </p>
        <p class="title-basic subtitle font-weight-bold" v-if="updateUser">
          Modificar datos
        </p>
        <center>
          <v-divider class="col-11"></v-divider>
        </center>
      </v-card-title>

      <v-card-text>
        <v-form
          lazy-validation
          ref="form"
          v-model="valid"
          >
          <v-container>
            <v-row dense>

              <v-col
                cols="12"
                sm="6"
                md="6"
                >
                <div class="font-weight-light p-content">Nombres</div>
                <v-text-field
                  v-model="firstName"
                  outlined
                  dense
                  :rules="nameRules"
                  maxlength="100"
                  required
                  >
                </v-text-field>
              </v-col>

              <v-col
                cols="12"
                sm="6"
                md="6"
                >
                <div class="font-weight-light p-content">Apellidos</div>
                <v-text-field
                  v-model="lastName"
                  outlined
                  dense
                  :rules="nameRules"
                  maxlength="100"
                  required
                  >
                </v-text-field>
              </v-col>

              <v-col
                cols="12"
                sm="6"
                md="6"
                >
                <div class="font-weight-light p-content">No.Documento</div>
                <v-text-field
                  v-model="numDocument"
                  outlined
                  dense
                  :rules="documentRules"
                  maxlength="15"
                  required
                  onkeypress="return (event.charCode >= 48 && event.charCode <= 57)"
                  >
                </v-text-field>
              </v-col>

              <v-col
                cols="12"
                sm="6"
                md="6"
                >
                <div class="font-weight-light p-content">Tipo Documento</div>
                <v-select
                  :items="typeDocuments"
                  item-value="valor"
                  item-text="text"
                  v-model="typeDocument"
                  outlined
                  dense
                  solo
                  flat
                  required
                  >
                </v-select>
              </v-col>

              <v-col
                cols="12"
                sm="6"
                md="6"
                >
                <div class="font-weight-light p-content">Institución</div>
                <v-text-field
                 v-model="institution"
                 outlined
                 dense
                 :rules="generalRules"
                 maxlength="100"
                 required
                 >
               </v-text-field>
              </v-col>

              <v-col
                cols="12"
                sm="6"
                md="6"
                >
                <div class="font-weight-light p-content">Cargo</div>
                <v-text-field
                  v-model="workCenter"
                  outlined
                  dense
                  :rules="generalRules"
                  maxlength="100"
                  required
                  >
                </v-text-field>
              </v-col>

              <v-col
                cols="12"
                sm="6"
                md="6"
                >
                <div class="font-weight-light p-content">Usuario</div>
                <v-text-field
                  v-model="usuario"
                  outlined
                  dense
                  :rules="usuarioRules"
                  required
                  >
                </v-text-field>
              </v-col>

              <v-col
                cols="12"
                sm="6"
                md="6"
                >
                <div class="font-weight-light p-content">Email</div>
                <v-text-field
                  v-model="email"
                  outlined
                  dense
                  :rules="emailRules"
                  required
                  >
                </v-text-field>
              </v-col>

              <v-col
                cols="12"
                sm="6"
                md="6"
                >
              <div class="font-weight-light p-content">Contraseña</div>
              <v-text-field
                v-model="password"
                outlined
                type="password"
                dense
                :rules="passwordRules"
                required
                >
              </v-text-field>
              </v-col>

              <v-col
                cols="12"
                sm="6"
                md="6"
                >
                <div class="font-weight-light p-content">Confirmar Contraseña</div>
                <v-text-field
                  v-model="checkPassword"
                  outlined
                  type="password"
                  dense
                  :rules="passwordRules"
                  required
                  >
                </v-text-field>
              </v-col>

             <!-- <v-checkbox
              v-model="moderador"
              label="Moderador"
              style="margin: 0px !important"
              >
             </v-checkbox> -->

             <v-checkbox
             v-if="!updateUser"
              v-model="tratamientoDatos"
              label="AUTORIZO EL TRATAMIENTO DE DATOS PERSONALES."
              >
             </v-checkbox>


              <v-row no-gutters align="center" class="my-3"  v-if="!updateUser">

              <!-- <v-row justify="end">
                <v-btn text color="primary" small @click="$emit('login')">return</v-btn>
                <v-btn color="primary" small @click="submit">Send</v-btn>
              </v-row> -->
              </v-row>
            </v-row>

            <v-row  justify="center">
              <v-col
              cols="6"
              sm="12"
              md="6"
              >
                <v-btn class="button-basic background-primary" @click="submit" style="width: 100%" v-if="!updateUser">Registrarse</v-btn>
              </v-col>
            </v-row>

          </v-container>
        </v-form>
      </v-card-text>
    </v-card>

    </v-dialog>

    </v-row>

  </div>
</template>
<script>

import { user, dataGeneral } from '../../services/api'

export default {
  name: 'registro',
  props: ['updateUser'],
  data () {
    return {
      // Data
      dialog: true,
      overlay: false,
      valid: true,
      firstName: '',
      lastName: '',
      numDocument: '',
      email: '',
      usuario: '',
      password: '',
      checkPassword: '',
      moderador: false,
      tratamientoDatos: false,
      comentario: '',
      typeDocuments: [],
      typeDocument: '',
      institution: '',
      workCenter: '',

      // Rules form
      nameRules: [
        v => !!v || 'Campo obligatorio',
        v => (v && v.length <= 100) || 'No más de 100 caracteres',
        v => (v && v.length >= 3) || 'No menos de 3 caracteres'
      ],
      documentRules: [
        v => !!v || 'El número de documento es requerido',
        v => (v && v.length <= 15) || 'No más de 15 caracteres',
        v => (v && v.length >= 3) || 'No menos de 3 caracteres'
      ],
      usuarioRules: [
        v => !!v || 'Campo obligatorio',
        v => (v && v.length <= 50) || 'No más de 50 caracteres'
      ],
      emailRules: [
        v => !!v || 'Campo obligatorio',
        v => /.+@.+\..+/.test(v) || 'E-mail no es valido'
      ],
      passwordRules: [
        v => !!v || 'Campo obligatorio',
        v => (v && v.length > 5) || 'No puede ser menor a 6 caracteres',
        v => (v && v.length < 16) || 'No puede ser mayor a 15 caracteres'
      ],
      generalRules: [
        v => !!v || 'Campo obligatorio',
        v => (v && v.length < 100) || 'No más de 100 caracteres'
      ],
      requiredRules: [
        v => !!v || 'Campo obligatorio',
      ]
    }
  },
  computed: {
  },
  async mounted () {
    await this.getData();
  },
  created () {
  },
  methods: {
    async getData() {
      try {

        const res = await dataGeneral.getDataDocumentoType();

        if (res.status === 200) {
          const data = res.data.message.documentType;

          for (const documento in data) {
            var addDocument = {
              valor: data[documento][0],
              text: data[documento][1],
              persona: data[documento][2]
            }
            this.typeDocuments.push(addDocument)
          }

        } else {
          this.$swal({
              icon: 'error',
              text: 'Ocurrio un problema al consultar la información del servidor.',
              confirmButtonText: 'Aceptar',
          });
        }

      } catch (error) {
        console.log(error);
      }
    },
    data () {
      const firstName = this.firstName
      const lastName = this.lastName
      const numDocument = this.numDocument
      const email = this.email
      const usuario = this.usuario
      const password = this.password
      const active = 'S'
      const pascheckPasswordsword = this.checkPassword
      const moderador = this.moderador
      const country = this.country
      const comentario = this.comentario
      const typeDocument = this.typeDocument
      const institution = this.institution
      const workCenter = this.workCenter
      const obj = {
        firstName,
        lastName,
        numDocument,
        email,
        usuario,
        password,
        pascheckPasswordsword,
        active,
        moderador,
        country,
        comentario,
        typeDocument,
        institution,
        workCenter
      }

      return obj
    },
    async submit () {
      if (this.$refs.form.validate()) {

        this.overlay = true;
        const obj = this.data()

        if (obj.password !== obj.pascheckPasswordsword) {
          this.$toasted.error('Verifique su contraseña.', { duration: 5000 })
          return
        }

        if (!this.tratamientoDatos) {
          this.overlay = false;
          this.$swal({
            icon: 'error',
            text: 'Para terminar el proceso debe aceptar el tratamiento de datos.',
            confirmButtonText: 'Aceptar',
          });
          return
        }

        try {

          const res = await user.createUser({ obj });

          if (res.status === 200) {

            this.$emit('login');
            this.$swal({
              icon: 'success',
              text: 'Verifique su correo para terminar el proceso de registro.',
              confirmButtonText: 'Aceptar',
            });

          } else {
            this.$swal({
              icon: 'error',
              text: res.message,
              confirmButtonText: 'Aceptar',
            });
          }

          this.overlay = false;

        } catch (error) {
          this.overlay = false;
          this.$swal({
            icon: 'error',
            text: error.response.data.message,
            confirmButtonText: 'Aceptar',
          });
        }
      } else {
        console.log('Errores en formulario')
      }
    },
    cerrarModal() {
      if (this.updateUser) {
        this.$emit('home');
      } else {
        this.$emit('login');
      }
    }
  }
}
</script>
<style scoped>
  .subtitulo {
    font-family: 'veneerregular';
    font-size: 2.4rem;
    line-height : 35px;
  }
</style>
