<template>
  <div>

    <v-overlay :value="loadingSeeEvent">
      <v-progress-circular
        indeterminate
        size="64"
      ></v-progress-circular>
    </v-overlay>


    <searchCombobox
      :listChips='listChips'
      :datos='eventos'
      :dataFiltrada='dataEventoFiltrada'
      campoFechaFiltro='fecha_registro_evento'
    />

    <v-row class="mt-5">
      <v-col
        cols="12"
        md="12"
        sm="12"
      >
        <v-data-table
          :headers="headers"
          :items="eventos"
          :items-per-page="5"
          class="elevation-1"
          :loading="loading"
          :search="filtro"
          no-data-text="No hay datos."
        >
          <template v-slot:top>
            <v-layout align-center pa-2>
              <v-row>
                <v-col
                  cols="12"
                  md="3"
                  sm="12"
                >
                  <v-btn
                    class="background-primary-dark button-basic"
                    elevation="2"
                    raised
                    depressed
                    block
                    @click="crearEvento"
                    v-if="permisoCrearEvento"
                  >
                    Crear evento
                  </v-btn>
                </v-col>
                <v-col
                  cols="12"
                  sm="12"
                  md="3"
                >
                  <v-btn
                    class="background-primary-dark button-basic"
                    elevation="2"
                    block
                    raised
                    depressed
                    :loading="loadingSincronizar"
                    :disabled="loadingSincronizar"
                    @click="sincronizar"
                    v-if="isOnline && eventosSinTransmitir"
                  >
                    Sincronizar eventos
                    <v-icon
                      right
                      dark
                    >
                      mdi-cloud-sync
                    </v-icon>
                  </v-btn>
                </v-col>
                <v-col
                  cols="12"
                  md="6"
                  sm="12"
                >
                  <v-text-field
                    label="Buscar"
                    outlined
                    dense
                    hide-details
                    prepend-icon="mdi-filter"
                    v-model="filtro"
                    >
                  </v-text-field>
                </v-col>
              </v-row>
            </v-layout>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-icon
              small
              class="mr-1"
              color="#004884"
              @click="verEvento(item)"
              title="Ver evento"
            >
            mdi-eye
            </v-icon>
            <v-icon
              small
              class="mr-1"
              color="#004884"
              @click="eliminarEvento(item)"
              title="Eliminar evento"
              v-if="isOffline || eventosSinTransmitir"
            >
            mdi-trash-can
            </v-icon>
            <v-icon
              small
              class="mr-1"
              color="#004884"
              @click="seguimiento(item)"
              v-if="isOnline && !eventosSinTransmitir"
              title="Ver seguimiento"
            >
            mdi-notebook
            </v-icon>
            <!-- <v-icon
              small
              class="mr-1"
              color="primary"
              @click="generarInformesEvento(item)"
              title="Generar informes"
            >
            mdi-chart-areaspline
            </v-icon> -->
            <v-icon
              small
              class="mr-1"
              color="#004884"
              @click="verAdjuntosEvento(item)"
              title="Ver adjuntos del evento"
              v-if="isOnline && !eventosSinTransmitir"
            >
            mdi-file-download
            </v-icon>
            <v-icon
              small
              class="mr-1"
              :color="item.validado ? 'success' : ''"
              @click="validateEvent(item)"
              title="Aprobar evento"
              v-if="isOnline && !eventosSinTransmitir"
            >
            mdi-check-decagram
            </v-icon>
          </template>
        </v-data-table>
      </v-col>
    </v-row>

    <!-- Modal con listado de adjuntos por evento -->
    <v-dialog
      v-model="dialogAdjuntos"
      scrollable
      max-width="300px"
    >
      <v-card>
        <v-card-title>Adjuntos</v-card-title>
        <v-divider></v-divider>
        <v-card-text style="height: auto;">
          <v-list-item
            v-for="adjunto in adjuntos"
            :key="adjunto.cod_evento_adjunto"
          >
            <v-list-item-icon>
              <v-icon>mdi-download-box</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <a
                @click="descargarAdjunto(adjunto)"
              >
              {{ adjunto.nombre_archivo }}
              </a>
            </v-list-item-content>
          </v-list-item>
          <br>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn
            color="blue darken-1"
            text
            @click="dialogAdjuntos = false"
          >
            Cerrar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </div>

</template>
<script>

import { eventosCreados } from '../../services/api.js';
import jwtDecode from 'jwt-decode';
import { getData } from '../../indexedDb/getData.js';
import { DB_STATUS, DB_NAME, DB_VERSION } from '../../indexedDb/connectDb.js';
import { newEvent } from '../../services/api.js';
import searchCombobox from '@/components/shared/searchCombobox';

export default {
  name: 'eventos',
  // props: ['dataEvento'],
  components: {
    searchCombobox
  },
  data () {
    return {
      headers: [
        { text: 'N°', align: 'center', value: 'cod_evento' },
        { text: 'Tipo Evento', align: 'center', value: 'tipo_evento' },
        { text: 'Fecha registro', align: 'center', value: 'fecha_registro_evento' },
        { text: 'Ubicación', align: 'center', value: 'ubicacion' },
        { text: 'Acciones', value: 'actions', sortable: false }
      ],
      eventos: [],
      loading: false,
      loadingSincronizar: false,
      loadingSeeEvent: false,
      permisoCrearEvento: false,
      filtro: '',
      desserts: [],
      editedIndex: -1,
      editedItem: {},
      eventosSinTransmitir: false,
      dialogAdjuntos: false,
      adjuntos: [],
      listChips: [
        {nombreFiltro: 'Fecha registro', valor: 'fecha_registro_evento'},
        {nombreFiltro: 'Nombre puerto', valor: 'nom_puerto_desembarquee'},
        {nombreFiltro: 'Nombre vereda', valor: 'nom_vereda'},
        {nombreFiltro: 'Sistema productivo', valor: 'sistema_productivo_afectado'},
        {nombreFiltro: 'Tipo evento', valor: 'tipo_evento'},
        {nombreFiltro: 'Ubicación', valor: 'ubicacion'},
        {nombreFiltro: 'Usuario', valor: 'usuario'},
        {nombreFiltro: 'Validado', valor: 'validado'},
      ],
      dataEventos: [],
    }
  },
  created: function () {
    this.validarPermisos();
  },
  async mounted() {
    await this.getEventos();
  },
  methods: {
    async validarPermisos() {
      const login = await getData('login', false);
      let permisos = login[0].permisos_usuario[0];

      for (let index = 0; index < permisos.length; index++) {
        if (permisos[index]['id_modulo'] === 2) {
          this.permisoCrearEvento = permisos[index]['estado'];
        }
      }
    },
    async getEventos() {
      this.loading = true

      try {
        this.eventosSinTransmitir = await this.eventosOffline();

        if (this.isOnline) {

          if (this.eventosSinTransmitir) {
            this.$swal({
              icon: 'info',
              text: 'Existen eventos sin guardar en el servidor, por favor sincronícelos.',
              confirmButtonText: 'Aceptar',
            });
          } else {
            this.loading = true
            await this.eventosOnline();
          }

        }

      } catch (error) {
        console.log(error)
      }

      this.loading = false
    },
    dataEventoFiltrada(data) {
      this.eventos = data;
    },
    async eventosOnline() {
      const res = await eventosCreados.getEventos()

      if (res.status === 200) {
        const encoded = res.data.token
        const decoded = jwtDecode(encoded)
        const data = decoded.eventos
        this.loading = false

        this.eventos = data.eventos
      }
    },
    async eventosOffline() {
      const res = await getData('newEvent', false);
      this.loading = false
      this.eventos = []

      for (const key in res) {
        var data = {
          cod_evento:key,
          tipo_evento:res[key]['dataEncabezadoEvento']['nameTipoEv'],
          fecha_registro_evento:'',
          ubicacion:res[key]['dataEncabezadoEvento']['observacion']+'('+res[key]['dataEncabezadoEvento']['nameDepartamento']+' - '+res[key]['dataEncabezadoEvento']['nameMunicipio']+')',
          data:res[key]
        };
        this.eventos.push(data);
      }

      return Object.keys(res).length > 0 ? true : false;
    },
    async verEvento(item) {
      var evento = [];
      this.loadingSeeEvent = true;
      if (this.isOnline && !this.eventosSinTransmitir) {
        evento = await this.consultarEvento(item);
      } else {
        const index = this.eventos.indexOf(item);
        evento = Object.assign({}, item.data);
      }
      this.loadingSeeEvent = false;
      this.$router.push({
        name: 'actualizarEvento',
        params: { evento: evento }
      })
    },
    async consultarEvento(item) {
      var data = [];
      try {
        const res = await eventosCreados.getEvento({idEvento:item.cod_evento});

        if (res.status === 200) {
          data = res.data.message[0]['newEvent'];
        } else {
          this.$swal({
            icon: 'error',
            text: res.message,
            confirmButtonText: 'Aceptar',
          });
        }
      } catch (error) {
        this.loadingSeeEvent = false;
        console.log(error);
        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar',
        });
      }
      return data;
    },
    eliminarEvento(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar el evento?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          console.log('Eliminación de evento');
          if (DB_STATUS === 200) {

            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onerror = (event) => {
              console.log('Error:');
              console.log(event.target.error.message);
              window.alert('Database error: ' + event.target.error.message);
            };
            request.onsuccess = (event) => {
              this.eliminarStoreItemNewEvent(event, item.data.id_obj);
            }
            this.getEventos();
          } else {
            console.error('500 - conection');
          }
        }
      })
    },
    seguimiento(item) {
      this.$emit("compSeguimiento", item);
    },
    verAdjuntosEvento(item) {
      this.dialogAdjuntos = true;
      this.adjuntos = item.adjuntos;
    },
    async descargarAdjunto(adjunto) {
      const ruta = adjunto.ruta;
      const nombre = adjunto.nombre_archivo;
      const rutaFinal = ruta+'/'+nombre;

      try {
        const res = await eventosCreados.getAdjunto({'ruta': rutaFinal});

        if (res.status === 200) {
          const data = res.data

          const url = window.URL.createObjectURL(new Blob([data]))
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', nombre) // or any other extension
          document.body.appendChild(link)
          link.click()
        } else {
          this.$swal({
            icon: 'error',
            text: error.message,
            confirmButtonText: 'Aceptar',
          });
        }
      } catch (error) {
        console.log(error);
        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar',
        });
      }
    },
    async validateEvent(item) {
      const id = item.cod_evento;
      this.$swal({
          title: 'Confirmación',
          text: 'Aprobar evento?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          this.setAuditar(id);
        } else {
        }
      })
    },
    async setAuditar(id) {
      try {
        const res = await eventosCreados.getValidateEvent({'evento': id});

        if (res.status === 200) {
          this.$swal({
            icon: 'success',
            text: 'Evento aprobado',
            confirmButtonText: 'Aceptar',
          });
          this.getEventos();
        } else {
          this.$swal({
            icon: 'error',
            text: error.message,
            confirmButtonText: 'Aceptar',
          });
        }
      } catch (error) {
        console.log(error);
        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar',
        });
      }
    },
    generarInformesEvento (item) {
      this.$router.push({
        name: 'informesEvento',
        params: { evento: item }
      })
    },
    sincronizar() {
      this.loadingSincronizar = true;

      if (DB_STATUS === 200) {
        try {
          const request = indexedDB.open(DB_NAME, DB_VERSION);

          request.onerror = (event) => {
            this.loadingSincronizar = false;
            console.log('Error:');
            console.log(event.target.error.message);
            window.alert('Database error: ' + event.target.error.message);
          };

          request.onsuccess = (event) => {
            this.crearFormDataOffline(event);
          }

        } catch (error) {
          this.loadingSincronizar = false;
          this.$swal({
            icon: 'error',
            text: error.response.data.message,
            confirmButtonText: 'Aceptar',
          });
        }
      } else {
        console.error('500 - conection');
      }
    },
    async crearFormDataOffline(event) {
      const res = await getData('newEvent', false);
      const formData = new FormData();
      var data = [];

      for (const key in res) {
        var contador = 0;
        let adjuntos = res[key]['dataEncabezadoEvento']['adjuntos'];

        if (adjuntos) {
          for (const file of adjuntos) {
            formData.append('files' + key + contador, file, file.name)
            contador++
          }
        }
        formData.append('contador' + key, contador);
        data.push(res[key]);
      }
      formData.append('eventos', JSON.stringify(data));

      this.enviarFormDataOffline(formData, event);
    },
    async enviarFormDataOffline(formData, event) {

      try {
        const res = await newEvent.setDataEventOffline(formData)

        if (res.status === 200) {
          this.eliminarStoreNewEvent(event);
          this.$swal({
            icon: 'success',
            text: res.message,
            confirmButtonText: 'Aceptar',
          });
          this.getEventos();

        } else {
          this.$swal({
            icon: 'error',
            text: res.message,
            confirmButtonText: 'Aceptar',
          });
        }
        this.loadingSincronizar = false;
      } catch (error) {
        this.loadingSincronizar = false;
        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar',
        });
      }
    },
    eliminarStoreNewEvent(event) {
      const db = event.target.result;
      const txn = db.transaction('newEvent', 'readwrite');
      const store = txn.objectStore('newEvent');
      let query = store.clear();

      query.onsuccess = function(event) {
        console.log('Success:');
        console.log(event);
      };
      query.onerror = function (event) {
        console.log('Error:');
        console.log(event.target.error.message);
        window.alert('Database store error: ' + event.target.error.message);
      };
      txn.oncomplete = function () {
        db.close();
      };
    },
    eliminarStoreItemNewEvent(event, id) {
      const db = event.target.result;
      const txn = db.transaction('newEvent', 'readwrite');
      let request = txn.objectStore('newEvent').delete(id);

      request.onsuccess = function(event) {
        console.log('Success delete item store:');
        console.log(event);
      };
      request.onerror = function (event) {
        console.log('Error:');
        console.log(event.target.error.message);
        window.alert('Database store error: ' + event.target.error.message);
      };
      txn.oncomplete = function () {
        db.close();
      };
    },
    crearEvento() {
      if (this.eventosSinTransmitir) {
        this.$swal({
          icon: 'info',
          text: 'Existen eventos sin guardar en el servidor, por favor sincronícelos.',
          confirmButtonText: 'Aceptar',
        });
        return;
      }
      this.$router.push('/newEvento');
    }
  },
}
</script>
<style scoped>
  .creado {
    background-color: #2196F3;
    color: white;
  }
  .asignado {
    background-color: #8BC34A;
    color: white;
  }
  .verificado {
    background-color: #5E35B1;
    color: white;
  }
  .cerrado {
    background-color: #F44336;
    color: white;
  }
  .alarma {
    background-color: #F44336;
    color: white;
  }
</style>
