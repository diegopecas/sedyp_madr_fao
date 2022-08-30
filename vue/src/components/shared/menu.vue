<template>
  <div>
    <v-toolbar
      class="d-md-none background-primary-dark"
      flat
    >
      <v-row>
        <v-col>
          <v-toolbar-title
            align="center"
            class="justify-lg-center"
          >
            HERRAMIENTA DE RECOLECCIÓN <br> DE DAÑOS Y PÉRDIDAS
          </v-toolbar-title>
        </v-col>
      </v-row>
    </v-toolbar>

    <v-container
      fluid
      class="ma-0 pa-0 background-primary-dark"
    >
      <v-container>
        <v-toolbar
          class="background-primary-dark"
          flat
          dense
        >
          <v-menu
            left
            bottom
          >
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                color="white"
                class="d-md-none"
                icon
                v-bind="attrs"
                v-on="on"
              >
                <v-icon color="white">mdi-menu</v-icon>
              </v-btn>
            </template>
            <v-container class="background-primary-dark" fluid>
              <v-list class="background-primary-dark">
                <v-row class="mt-1">
                  <v-col
                  class="mr-1"
                  cols="2"
                  sm="2"
                  md="2"
                  >
                  <v-icon color="white" x-large>mdi-account-circle</v-icon>
                  </v-col>
                  <v-col
                  class="ml-2"
                  cols="9"
                  sm="9"
                  md="9"
                  >
                  <v-list-item-title>
                    {{ this.$session.get('usuario') }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ this.$session.get('email') }}
                  </v-list-item-subtitle>
                  </v-col>
                </v-row>

                <v-divider color="white" class="mt-2 mb-2"></v-divider>
                <v-list-item
                  v-for="item in listMenu"
                  v-show="usarEnModoOffline(item.verOffline) && item.visible"
                  :key="item.id"
                  @click="cambiarRuta(item)"
                >
                  <v-icon color="white" class="mr-3">{{ item.icon }}</v-icon>
                  <v-list-item-title style="color:white">{{ item.name }}</v-list-item-title>
                </v-list-item>
                <v-list-item
                  @click="$session.destroy();$router.push('/inicio')"
                >
                  <v-icon color="white" class="mr-3">mdi-logout-variant</v-icon>
                  <v-list-item-title style="color:white">Cerrar cesión</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-container>
          </v-menu>

          <v-img
            class="hidden-sm-and-down mr-5"
            :aspect-ratio="2"
            contain
            max-width="200"
            src="/img/fao_blanco.png"
          ></v-img>

          <v-toolbar-items
            class="ml-4 hidden-sm-and-down cursor-click hover-blue"
            v-for="item in listMenu"
            v-show="item.id != 3 && item.id != 4 && item.id != 5 && item.id != 7 && item.visible"
            :key="item.id"
            @click="cambiarRuta(item)"
          >
            <v-list-item-title>
                  <v-icon color="white" class="icon-white">{{ item.icon }}</v-icon>{{ item.name }}
            </v-list-item-title>
          </v-toolbar-items>
          <v-spacer></v-spacer>
          <!-- <v-offline @detected-condition="onLine"> -->
            <div>
              <v-btn icon v-if="isOnline">
                <v-icon color="white" class="icon-white">mdi-cellphone-nfc</v-icon>
              </v-btn>
              <v-btn icon v-if="isOffline">
                <v-icon color="white" class="icon-white">mdi-cellphone-nfc-off</v-icon>
              </v-btn>
            </div>
            <v-menu
              right
              bottom
            >
              <template v-slot:activator="{ on, attrs }">
                <div>
                  <v-btn
                    icon
                    v-if="isOnline && messages.length > 0"
                    v-bind="attrs"
                    v-on="on"
                  >
                    <v-badge
                      avatar
                      bordered
                      dot
                      color="success"
                    >
                      <v-icon color="white" class="icon-white">mdi-bell-ring</v-icon>
                    </v-badge>
                  </v-btn>
                </div>
              </template>
              <v-responsive
                max-width="800"
                class="mx-auto mb-2"
              >
                <v-card
                  width="800"
                  max-height="450"
                >

                  <v-card-text class="pt-4">
                    Notificación pendientes por gestionar
                  </v-card-text>

                  <v-divider></v-divider>
                  <v-list
                    class="overflow-y-auto"
                    style="width:auto; min-height:220px; max-height: 350px;"
                    three-line
                  >
                    <v-list-item-group
                      active-class="primary--text"
                    >
                      <v-list-item
                        v-for="message in messages"
                        :key="message.id_notificacion"
                        inset
                      >
                        <v-list-item-avatar>
                          <v-avatar
                            :color="colorAvatar(message)"
                            size="56"
                            class="white--text"
                          >
                            {{ message.usuario_creador !== null ? message.usuario_creador.substr(0,2).toUpperCase() : 'US' }}
                          </v-avatar>
                        </v-list-item-avatar>
                        <v-list-item-content>
                          <v-list-item-title >{{ message.titulo }}</v-list-item-title>
                          <p> {{ message.descripcion }} </p>
                        </v-list-item-content>
                        <v-list-item-action>
                        <v-btn
                          icon
                          depressed
                          small
                          @click="limpiarNotificaciones(message)"
                          title="Retirar notificación"
                        >
                          <v-icon
                            right
                            color="#004884"
                          >
                            mdi-delete-circle
                          </v-icon>
                        </v-btn>
                        </v-list-item-action>
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card>
              </v-responsive>
            </v-menu>
          <v-icon class="hidden-sm-and-down  icon-white" color="white" large>mdi-account-circle</v-icon>
          <v-menu
            right
            bottom
          >
            <template v-slot:activator="{ on, attrs }">
              <div>
              <v-btn
                class="hidden-sm-and-down background-primary-dark font-weight-light"
                v-bind="attrs"
                v-on="on"
                outlined
                style="border:none"
              >
                {{ $session.get('usuario') }}
              </v-btn>
              </div>
            </template>
            <v-list>
              <v-list-item
                v-for="item in listMenu"
                v-show="(item.id == 3 || item.id == 4 || item.id == 5 || item.id == 7) && isOnline && item.visible"
                :key="item.id"
                @click="cambiarRuta(item)"
              >
                <v-icon class="mr-3" color="#004884">{{ item.icon }}</v-icon>
                <v-list-item-title>{{ item.name }}</v-list-item-title>
              </v-list-item>
              <v-list-item
                @click="$session.destroy();$router.push('/inicio')"
              >
                <v-icon class="mr-3" color="#004884">mdi-logout-variant</v-icon>
                <v-list-item-title >Cerrar cesión</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>

        </v-toolbar>
      </v-container>
    </v-container>

    <v-container
      class="hidden-sm-and-down"
      fluid
    >
      <v-row>
        <v-col
          cols="12"
          md="8"
          sm="12"
        >
        </v-col>
        <v-col
          cols="2"
          align="right"
        >
          <v-img
            contain
            max-width="180"
            max-height="80px"
            src="/img/fao_logo.png"
          ></v-img>
        </v-col>
        <v-col
          cols="2"
        >
          <v-img
            class="mt-2"
            contain
            max-width="200"
            max-height="100px"
            src="/img/logo_minagricultura.png"
          ></v-img>
        </v-col>
      </v-row>
    </v-container>

    <v-container
      fluid
      class="pa-0"
    >
      <v-img
        :aspect-ratio="16/9"
        :max-height="imageHeight"
        src="/img/img_pages.png"
      >
      </v-img>
    </v-container>
    <v-container fluid
      class="name-moduls color-primary-dark"
    >
      <h3>{{ currentRouteName }}</h3>
    </v-container>

  </div>

</template>
<script>
import { getData } from '../../indexedDb/getData.js';
import { update } from '../../indexedDb/insertSystemData.js';
import { dataGeneral } from '../../services/api.js';

export default {
  name: "menuApp",
  data() {
    return {
      drawer: false,
      model: 1,
      group: null,
      miniVariant: false,
      onLine: true,
      loading: true,
      listMenu: [
        {id:1,name:'Inicio',icon:'mdi-home',route:'/home',verOffline:true,visible:true},
        {id:2,name:'Crear evento',icon:'mdi-shape-square-rounded-plus',route:'/newEvento',verOffline:true,visible:false},
        // {id:3,name:'Informes',icon:'mdi-chart-box-outline',route:'/informesGenerales', verOffline: true},
        {id:3,name:'Datos de usuario',icon:'mdi-account-edit',route:'/updateUser',verOffline:false,visible:true},
        {id:7,name:'Roles',icon:'mdi-sitemap',route:'/roles', verOffline:false,visible:false},
        {id:4,name:'Auditoria',icon:'mdi-shield-check',route:'/auditoria',verOffline:false,visible:false},
        {id:5,name:'Configuración de gastos',icon:'mdi-cogs',route:'/gastosAgricolas',verOffline:false,visible:false},
      ],
      login: [],
      messages: [],
    };
  },
  created: function () {
    this.notifications();
  },
  methods: {
    async notifications() {
      const login = await getData('login', false);
      this.login = login;
      this.messages = login[0].notificaciones;
      this.validarPermisos(login[0].permisos_usuario[0]);
    },
    validarPermisos(permisos) {

      for(let i = 0; i < this.listMenu.length; i++) {
        for (let index = 0; index < permisos.length; index++) {

          if (this.listMenu[i]['id'] !== 3 && this.listMenu[i]['id'] !== 1 && (this.listMenu[i]['id'] === permisos[index]['id_modulo'])) {

            this.listMenu[i]['visible'] = permisos[index]['estado'];

            if (permisos[index]['id_modulo'] === 2) {
              const crearEvento = permisos[index]['permisos'].filter((item)=>item.nombre_permiso === "Crear");
              if (crearEvento.length > 0) {
                this.listMenu[i]['visible'] = crearEvento[0]['estado'];
              }
            }

          }
        }
      }
    },
    usarEnModoOffline(verOffline) {
      var estado = true;
      if (this.isOffline && !verOffline) {
        estado = false;
      }
      return estado;
    },
    async cambiarRuta(item) {
      const res = await getData('newEvent', false);
      if (this.isOnline && Object.keys(res).length > 0 && item.id === 2) {
        this.$swal({
          icon: 'info',
          text: 'Existen eventos sin guardar en el servidor, por favor sincronícelos.',
          confirmButtonText: 'Aceptar',
        });
        return;
      }
      this.$router.push(item.route);
    },
    async limpiarNotificaciones(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Borrar la notificación?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          this.leerNotifcacion(item);
        } else {
        }
      })
    },
    async leerNotifcacion(item) {

      try {

        const id = {'notificacion': item.id_notificacion};
        const res = await dataGeneral.readNotification(id);

        if (res.status === 200) {
          const index = this.login[0].notificaciones.indexOf(item);
          this.login[0].notificaciones.splice(index, 1);

          update({'login':this.login[0]}, ['login'], true);

          this.$swal({
            icon: 'success',
            text: 'Notificaciones',
            confirmButtonText: 'Aceptar',
          });

        } else {
          this.$swal({
            icon: 'error',
            text: res.message,
            confirmButtonText: 'Aceptar',
          });
        }
      } catch(error) {
        console.log(error);
        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar',
        });
      }
    },
    colorAvatar(item) {
      const index = this.messages.indexOf(item);
      return index%2===0 ? '#004884':'#3366CC';
    },
  },
  computed: {
    currentRouteName() {
      const name = this.$route.name;
      var nombreModulo = "";
      var inicio = 0;
      var fin = 0;

      if (!name) {
        return;
      }

      for (var index = 0; index <= name.length; index++) {
        var letraActual = name.charAt(index);

        if (letraActual === letraActual.toUpperCase()) {
          fin = index;
          nombreModulo = nombreModulo + " " + name.substring(inicio, fin);
          inicio = fin;
        }
      }

      return nombreModulo.toUpperCase();
    },
    imageHeight() {
        switch (this.$vuetify.breakpoint.name) {
          case 'xs': return '97px'
          case 'sm': return '97px'
          case 'md': return '213px'
          case 'lg': return '213px'
          case 'xl': return '250px'
        }
    },
    heightList() {
      var caracteres = 0;
      var entradaAnterior = 0;

      for (let index = 0; index < this.messages.length; index++) {
        caracteres = this.messages[index]['descripcion'].length;
        if (caracteres > entradaAnterior) {
          entradaAnterior = caracteres;
        }
      }

      let height = caracteres > entradaAnterior ? caracteres:entradaAnterior;

      switch (this.$vuetify.breakpoint.name) {
          case 'md':
          case 'lg':
          case 'xl':
            height = 120
            break;
          default:
            height += 100;
            break;
        }
      return height;
    },
  },
}
</script>

<style scoped>
.v-navigation-drawer {
  z-index: 999999 !important;
}
.name-moduls {
  min-width: 100%;
  background: #F2F2F2;
  text-align: center;
}
</style>
