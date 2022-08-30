<template>
  <div>

    <v-overlay :value="overlay">
      <v-progress-circular
        indeterminate
        size="64"
      ></v-progress-circular>
    </v-overlay>

     <v-row dense>

      <v-col
        cols="12"
        sm="12"
        md="10"
      >
        <v-text-field
          label="Nombre rol"
          hint="Nombre rol"
          v-model="nombreRol"
          dense
          solo
          flat
          outlined
          filled
        ></v-text-field>
      </v-col>
      <v-col
        cols="12"
        sm="12"
        md="2"
      >
        <v-btn
          class="background-primary-dark button-basic"
          elevation="2"
          block
          raised
          depressed
          @click="setDataRoles"
        >Crear rol</v-btn>
      </v-col>

    </v-row>
    <div dense class="mt-2">
      <v-chip
        v-if="this.selectedRoles.length>0"
        close-icon="mdi-delete"
      >
        <v-icon
          left
          color="#004884"
        >
        mdi-label
        </v-icon>
        {{selectedRoles[0]['nombre']}}
      </v-chip>
      <v-chip
        class="ml-2"
        v-if="this.selectedModulos.length>0"
        close-icon="mdi-delete"
      >
        <v-icon
          left
          color="#004884"
        >
        mdi-label
        </v-icon>
        {{selectedModulos[0]['nombre']}}
      </v-chip>
    </div>
    <v-row class="mt-5">

      <v-col
        cols="12"
        md="4"
        sm="12"
      >
        <template>
          <v-data-table
            v-model="selectedRoles"
            :headers="headersRoles"
            :items="roles"
            :single-select="true"
            show-select
            item-key="idrol"
            class="elevation-2"
            @input="modulosSegunRol($event)"
            :loading="loadingRoles"
          >
            <template v-slot:top>
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
                @click="eliminarRol(item)"
                color="#004884"
              >
              mdi-delete
              </v-icon>
            </template>
          </v-data-table>
        </template>
      </v-col>
      <v-col
        cols="12"
        md="4"
        sm="12"
      >
        <template>
          <v-data-table
            :headers="headersModulos"
            :items="modulos"
            item-key="idmodulo"
            class="elevation-2"
          >
            <template v-slot:top>
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
                v-if="item.glutenfree"
                small
                @click="moduloSeleccionado(item)"
                color="#004884"
              >
              mdi-eye
              </v-icon>
            </template>
            <template v-slot:item.glutenfree="{ item }">
              <v-simple-checkbox
                v-model="item.glutenfree"
                @input="updateEstadoModulo($event, item)"
              ></v-simple-checkbox>
            </template>
            <template v-slot:expanded-item="{ headers, item  }">
              <td :colspan="headers.length">

              </td>
            </template>
          </v-data-table>
        </template>
      </v-col>
      <v-col
        cols="12"
        md="4"
        sm="12"
      >
        <template>
          <v-data-table
            :headers="headersPermisos"
            :items="permisos"
            item-key="idpermiso"
            class="elevation-2"
          >
            <template v-slot:top>
              <v-toolbar
                flat
                class="border-head-table font-weight-bold"
                height="10px"
                style="background-color:#F2F2F2"
              >
              </v-toolbar>
            </template>
            <template v-slot:item.glutenfree="{ item }">
              <v-simple-checkbox
                v-model="item.glutenfree"
                @input="updateEstadoPermiso($event, item)"
              ></v-simple-checkbox>
            </template>
          </v-data-table>
        </template>
      </v-col>

    </v-row>

  </div>
</template>

<script>
import { user } from '../../services/api';
import jwtDecode from 'jwt-decode';

export default {
  name:'rolesPermisos',
  data() {
    return {
      overlay: false,
      loadingRoles: false,

      headersRoles :[
        {text: 'Rol', value: 'nombre'},
        {text: 'Eliminar', value: 'actions', align: 'center'},
      ],
      roles: [],
      headersModulos: [
        {text: 'Estado', value: 'glutenfree', align: 'start'},
        {text: 'Módulo', value: 'nombre'},
        {text: 'Ver permisos', value: 'actions', align: 'end'},
      ],
      modulos: [],
      headersPermisos: [
        {text: 'Estado', value: 'glutenfree', align: 'start'},
        {text: 'Permiso', value: 'nombre'},
      ],
      permisos:[],

      nombreRol: '',
      dataRolesGlobal: [],
      dataModuloGlobal: [],
      dataPermisosGlobales: [],
      selectedRoles: [],
      selectedModulos: [],
      selectedPermisos: [],
    }
  },
  async mounted() {
    await this.getData();
  },
  methods: {
    async getData() {
      this.loadingRoles = true;

      try {
        const res = await user.getPermisos();

        if (res.status === 200) {

          const encoded = res.data.message[0]['token']
          const decoded = jwtDecode(encoded);
          const data = decoded.permisos_por_rol;
          this.roles = [];
          this.dataRolesGlobal = [];
          this.moduloData = [];
          this.permisoData = [];
          this.dataRoles(data);

        } else {
          this.$swal({
              icon: 'error',
              text: res.data.message,
              confirmButtonText: 'Aceptar',
          });
        }
        this.loadingRoles = false;

      } catch (error) {
        this.loadingRoles = false;
        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar',
        });
      }
    },
    dataRoles(data) {
      this.dataRolesGlobal = data;
      var rolData = {};

      for(const rol in data) {

        rolData = {'idrol':data[rol]['id_rol'],'nombre': data[rol]['nombre_rol']};
        this.roles.push(rolData);
        var moduloData = {};

        for(const modulo in data[rol]['modulos']) {

          const idModulo = data[rol]['modulos'][modulo]['id_modulo'];
          var moduloExistente = this.modulos.filter(modulo => modulo.idmodulo == idModulo);
          if (moduloExistente.length>0) {continue;}

          moduloData = {'idmodulo'  : idModulo,
                        'nombre'    : data[rol]['modulos'][modulo]['nombre_modulo'],
                        'idrol'     : '',
                        'glutenfree': false};
          this.modulos.push(moduloData);
          this.dataModuloGlobal.push(moduloData);
          var permisoData = {};

          for(const permiso in data[rol]['modulos'][modulo]['permisos']) {

            const idPermiso = data[rol]['modulos'][modulo]['permisos'][permiso]['id_permiso'];
            var permisoExistente = this.permisos.filter(permiso => permiso.idpermiso == idPermiso);
            if (permisoExistente.length>0) {continue;}

            permisoData = {'idpermiso' : idPermiso,
                           'nombre'    : data[rol]['modulos'][modulo]['permisos'][permiso]['nombre_permiso'],
                           'idmodulo'  : '',
                           'glutenfree': false};
            this.permisos.push(permisoData);
            this.dataPermisosGlobales.push(permisoData);
          }
        }

      }
    },
    async setDataRoles() {

      const newRol = {'rol':this.nombreRol}
      this.overlay = true;

      try {
        const res = await user.setRol(newRol);

        if (res.status === 200) {
          const encoded = res.data.message[0]['token']
          const decoded = jwtDecode(encoded);
          const data = decoded.permisos_por_rol;
          this.roles = [];
          this.dataRolesGlobal = [];
          this.moduloData = [];
          this.permisoData = [];
          this.dataRoles(data);
          this.nombreRol = '';

          this.$swal({
             icon: 'success',
             text: 'Rol creado.',
             confirmButtonText: 'Aceptar',
          });

        } else {
          this.$swal({
              icon: 'error',
              text: res.data.message,
              confirmButtonText: 'Aceptar',
          });
        }

      } catch (error) {
        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar',
        });
      }
      this.overlay = false;
    },
    modulosSegunRol(item) {
      if (this.selectedRoles.length > 0) {

        const idRol = item[0].idrol;
        var rolGlobal = this.dataRolesGlobal.filter(rol=>rol.id_rol === idRol);
        this.selectedModulos = [];
        this.permisos = this.dataPermisosGlobales;

        if (rolGlobal.length>0) {
          this.modulos = [];
          var moduloData = {};

          for(const modulo in rolGlobal[0]['modulos']) {

            const idModulo = rolGlobal[0]['modulos'][modulo]['id_modulo'];

            moduloData = {'idmodulo'  : idModulo,
                          'nombre'    : rolGlobal[0]['modulos'][modulo]['nombre_modulo'],
                          'idrol'     : idRol,
                          'glutenfree': rolGlobal[0]['modulos'][modulo]['estado']};
            this.modulos.push(moduloData);
          }
        }

      } else {
        this.modulos = this.dataModuloGlobal;
        this.permisos = this.dataPermisosGlobales;
        this.selectedModulos = [];
      }
    },
    updateEstadoModulo(e, item) {
      const index = this.modulos.indexOf(item);

      if (this.selectedRoles.length > 0) {

        this.selectedModulos = [];
        this.permisos = this.dataPermisosGlobales;
      } else {
        this.modulos[index]['glutenfree']=false;
      }
    },
    moduloSeleccionado(item) {
      if (this.selectedRoles.length === 0) {return;}

      this.selectedModulos = [];
      this.selectedModulos.push(item)

      this.permisosSegunModulo(item);
    },
    permisosSegunModulo(item) {
      if (this.selectedModulos.length > 0) {

        const idRol = item.idrol;
        const idModulo = item.idmodulo;
        var rolGlobal = this.dataRolesGlobal.filter(rol=>rol.id_rol === idRol);
        var moduloGlobal = rolGlobal[0]['modulos'].filter(modulo=>modulo.id_modulo === idModulo);

        if (rolGlobal.length>0 && moduloGlobal.length>0) {
          this.permisos = [];
          var permisoData = {};

          for(const modulo in moduloGlobal[0]['permisos']) {

            permisoData = {'idpermiso' : moduloGlobal[0]['permisos'][modulo]['id_permiso'],
                           'nombre'    : moduloGlobal[0]['permisos'][modulo]['nombre_permiso'],
                           'idmodulo'  : idModulo,
                           'glutenfree': moduloGlobal[0]['permisos'][modulo]['estado']};
            this.permisos.push(permisoData);
          }
        } else {
          this.permisos = this.dataPermisosGlobales;
        }
      } else {
        this.permisos = this.dataPermisosGlobales;
      }
    },
    async updateEstadoPermiso(e, item) {
      const index = this.permisos.indexOf(item);
      let data = {'permiso':{'id_rol':this.selectedRoles[0]['idrol'],'id_modulo':item.idmodulo,'id_permiso':item.idpermiso}};

      if (this.selectedRoles.length > 0 && this.selectedModulos.length > 0) {
        try {
          var res = null;
          this.overlay = true;

          if (item.glutenfree) {
            res = await user.setPermStatus(data);
          } else {
            res = await user.deletePermStatus({ data });
          }

          if (res.status === 200) {
            this.$swal({
              icon: 'success',
              text: res.data.message,
              confirmButtonText: 'Aceptar',
            });
            this.getData();

          } else {
            this.permisos[index]['glutenfree']=false;
            this.$swal({
              icon: 'error',
              text: res.data.message,
              confirmButtonText: 'Aceptar',
            });
          }

        } catch (error) {
          this.permisos[index]['glutenfree']=false;
          this.$swal({
            icon: 'error',
            text: error.response.data.message,
            confirmButtonText: 'Aceptar',
          });
        }
        this.overlay = false;

      } else {
        this.permisos[index]['glutenfree']=false;
        this.$swal({
          icon: 'error',
          text: 'Primero de click en la opción ver permiso.',
          confirmButtonText: 'Aceptar',
        });
      }
    },
    async eliminarRol(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar rol?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          this.rolaEliminar(item);
        }
      })
    },
    async rolaEliminar(item) {
      const rolDelete = {'rol':item.idrol};
      const res = await user.deleteRolUser({ rolDelete });
      this.overlay = true;

      try {
        if (res.status === 200) {

          const encoded = res.data.message[0]['token']
          const decoded = jwtDecode(encoded);
          const data = decoded.permisos_por_rol;
          this.roles = [];
          this.dataRolesGlobal = [];
          this.moduloData = [];
          this.permisoData = [];
          console.log(data);
          this.dataRoles(data);

          this.$swal({
            icon: 'success',
            text: 'Rol eliminado',
            confirmButtonText: 'Aceptar',
          });
          this.overlay = false;
        } else {
          this.overlay = false;
          this.$swal({
            icon: 'error',
            text: res.message,
            confirmButtonText: 'Aceptar',
          });
        }

      } catch (error) {
        this.overlay = false;
        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar',
        });
      }
    },
  },
}
</script>

