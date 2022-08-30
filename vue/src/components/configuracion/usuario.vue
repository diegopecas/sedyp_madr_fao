<template>
  <div>

    <v-overlay :value="overlay">
      <v-progress-circular
        indeterminate
        size="64"
      ></v-progress-circular>
    </v-overlay>

    <v-container>

      <v-row dense>
        <v-expansion-panels
          accordion
          class="border-basic"
        >
          <v-expansion-panel>
            <v-expansion-panel-header>Ver usuarios</v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-divider></v-divider>
              <v-col
                cols="12"
                md="12"
                sm="12"
              >
                <template>
                  <v-data-table
                    :headers="usuariosHeader"
                    :items="usuarios"
                    item-key="idmodulo"
                    class="elevation-0"
                    :loading="loading"
                    :search="filtro"
                    loading-text="Cargando datos..."
                  >
                    <template v-slot:top>
                      <v-layout align-center pa-2>
                        <v-spacer></v-spacer>
                        <v-col >
                          <v-text-field
                            label="Filtrar"
                            outlined
                            dense
                            hide-details
                            prepend-icon="mdi-filter"
                            v-model="filtro"
                            >
                          </v-text-field>
                        </v-col>
                      </v-layout>
                      <v-toolbar
                        flat
                        class="border-head-table font-weight-bold"
                        height="10px"
                        style="background-color:#F2F2F2"
                      >
                      </v-toolbar>
                    </template>
                  <template v-slot:item.actions="{ item }">
                    <v-icon
                      small
                      @click="editar(item)"
                      color="#004884"
                    >
                    mdi-pencil
                    </v-icon>
                  </template>
                  </v-data-table>
                </template>
              </v-col>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-row>

      <v-card
      class="border-basic mt-5"
      elevation-2
      >

        <v-card-text>

          <v-form
            lazy-validation
            ref="form"
            v-model="valid"
            >
            <v-container>
              <v-row>

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
                    :rules="requiredRules"
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
                  <div class="font-weight-light p-content">Rol</div>
                  <v-autocomplete
                    label="Rol"
                    hint="Rol"
                    :items="roles"
                    v-model="rol"
                    item-value="id_rol"
                    item-text="nombre"
                    dense
                    solo
                    flat
                    outlined
                    filled
                    @change="updateRol"
                  >
                  </v-autocomplete>
                </v-col>

                <v-col
                  cols="12"
                  sm="6"
                  md="6"
                  >
                  <div class="font-weight-light p-content">Estado</div>
                  <v-autocomplete
                    label="Rol"
                    hint="Rol"
                    :items="estadosUsuario"
                    v-model="estadoUsuario"
                    item-value="idEstado"
                    item-text="nombre"
                    dense
                    solo
                    flat
                    outlined
                    filled

                  >
                  </v-autocomplete>
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
                    >
                  </v-text-field>
                </v-col>

              </v-row>

              <v-row justify="center">
                <v-col
                cols="6"
                sm="12"
                md="6"
                >
                  <v-btn class="background-primary-dark button-basic" @click="update" style="width: 100%" v-if="updateUser">Actualizar</v-btn>
                </v-col>
              </v-row>

            </v-container>
          </v-form>
        </v-card-text>
      </v-card>

    </v-container>

  </div>
</template>
<script>

import { user, dataGeneral } from '../../services/api'
import jwtDecode from 'jwt-decode'

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
      estadoUsuario: '',
      password: '',
      checkPassword: '',
      moderador: false,
      tratamientoDatos: false,
      comentario: '',
      typeDocuments: [],
      typeDocument: '',
      institution: '',
      workCenter: '',
      loading: false,
      filtro: '',
      usuariosHeader: [
        {text: 'Usuario', value: 'usuario'},
        {text: 'Nombre', value: 'nombre'},
        {text: 'Institución', value: 'institucion'},
        {text: 'Email', value: 'email'},
        {text: 'Rol', value: 'nombre_rol'},
        {text: 'Usuario', value: 'id_usuario'},
        {text: 'Estado', value: 'activo'},
        {text: 'Editar', value: 'actions'},
      ],
      usuarios: [],
      roles: [],
      estadosUsuario: [
        {idEstado:'S', nombre:'Activo'},
        {idEstado:'N', nombre:'Inactivo'},
      ],
      idUser: JSON.parse(localStorage.getItem('dataUser')).id,
      idRol: JSON.parse(localStorage.getItem('dataUser')).id_rol,

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
        v => v.length < 16 || 'No más de 15 caracteres',
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
    if (this.updateUser === true) {
      const dataUserLocal = JSON.parse(localStorage.getItem('dataUser'))
      this.firstName = dataUserLocal.nombre
      this.lastName = dataUserLocal.apellido
      this.numDocument = dataUserLocal.nuDocumento
      this.typeDocument =  dataUserLocal.idDocumento
      this.email = dataUserLocal.email
      this.usuario = dataUserLocal.usuario
      this.institution = dataUserLocal.institucion
      this.workCenter = dataUserLocal.cargo
      this.rol = dataUserLocal.id_rol
      this.estadoUsuario = dataUserLocal.activo
    }
  },
  methods: {
    async getData() {
      try {

        this.loading = true;
        await this.tipoDocumento();
        await this.getUsuarios();
        this.loading = false;
      } catch (error) {
        this.loading = false;
        console.log(error);
      }
    },
    async tipoDocumento() {
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
    },
    async getUsuarios() {
        const res = await user.getAllUsers();

        if (res.status === 200) {

          const encoded = res.data.token;
          const decoded = jwtDecode(encoded);
          const users = decoded.users;
          const roles = decoded.roles;
          console.log(decoded);
          this.usuarios = users;
          this.roles = roles;


        } else {
          this.$swal({
              icon: 'error',
              text: 'Ocurrio un problema al consultar la información del servidor.',
              confirmButtonText: 'Aceptar',
          });
        }
    },
    data () {
      const firstName = this.firstName;
      const lastName = this.lastName;
      const numDocument = this.numDocument;
      const email = this.email;
      const usuario = this.usuario;
      const password = this.password;
      const active = this.estadoUsuario;
      const pascheckPasswordsword = this.checkPassword;
      const moderador = this.moderador;
      const country = this.country;
      const comentario = this.comentario;
      const typeDocument = this.typeDocument;
      const institution = this.institution;
      const workCenter = this.workCenter;
      const id_rol = this.idRol;
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
        workCenter,
        id_rol,
      }

      return obj
    },
    editar(item) {
      this.firstName = item.nombre;
      this.lastName = item.apellido;
      this.numDocument = item.numero_documento;
      this.email = item.email;
      this.usuario = item.usuario;
      this.typeDocument = item.cod_tipo_documento;
      this.institution = item.institucion;
      this.workCenter = item.cargo;
      this.idUser = item.id;
      this.rol = item.rol;
      this.idRol = item.rol;
      this.estadoUsuario = item.activo;
    },
    async update () {

      if (this.$refs.form.validate()) {

        this.overlay = true;
        const obj = this.data()

        if (obj.password !== obj.pascheckPasswordsword) {
          this.$swal({
            icon: 'error',
            text: 'Verifique su contraseña.',
            confirmButtonText: 'Aceptar',
          });
          this.overlay = false;
          return;
        }

        // se captura el id del usuario del localStorage
        const idUser = JSON.parse(localStorage.getItem('dataUser')).id;
        obj.idUser = this.idUser;
        console.log(obj);

        try {
          const res = await user.updateUser({ obj })

          if (res.status === 200) {
            const encoded = res.data.token;
            const decoded = jwtDecode(encoded);
            const obj = decoded.userobj;
            console.log(decoded);
            this.getData();

            // almacenamiento en localStorage
            if (idUser === this.idUser) {
              if (!localStorage.dataUser) {
                localStorage.setItem('dataUser', JSON.stringify(obj));
              }
              this.$session.set('usuario', obj.usuario);
              this.$session.set('email', obj.email);
              this.$session.set('activo', obj.activo);
              this.$session.set('id_rol', obj.id_rol);
            }

            this.$swal({
              icon: 'success',
              text: 'Datos actualizados.',
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
    async updateRol() {

      this.overlay = true;

      try {

        const data = {'obj':{'id_rol': this.rol, 'id': this.idUser}};
        console.log(data);
        const res = await user.changeRol(data);
        console.log(res);
        if (res.status === 200) {
          this.$swal({
            icon: 'success',
            text: res.message,
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
    },
  }
}
</script>
<style scoped>
</style>
