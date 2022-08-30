<template>

  <v-container fluid>

    <v-row class="mt-2">
      <v-col
        cols="12"
        sm="12"
        md="12"
      >
        <v-alert
          color="#004884"
          border="left"
          elevation="2"
          colored-border
          icon="mdi-information"
        >
          Siempre que realice un cambio en los campos o en la ubicación debe dar click en el botón asignar ubicación.
        </v-alert>
      </v-col>
      <v-col
        cols="12"
        mg="4"
        sm="4"
        class="section"
        style="overflow-y: scroll;max-height:510px"
        order="2"
        order-sm="1"
      >
        <!--  Formulario mapa -->

        <v-form
          lazy-validation
          ref="form"
          v-model="valid"
        >
          <v-row
            no-gutters
          >
            <v-col
              class="mb-5"
              cols="12"
              v-if="permitirCaladeros"
            >
              <v-btn
                class="background-primary-dark button-basic mr-2"
                elevation="2"
                raised
                block
                depressed
                title="Agregar caladero"
                @click="agregarCaladero()"
              >
                Agregar caladero
              </v-btn>
            </v-col>

            <v-col
              cols="12"
            >
              <!-- <v-file-input
                label="Adjunto"
                v-model="ubicacion.adjuntos"
                dense
                outlined
                solo
                flat
                prepend-inner-icon="mdi-paperclip"
                prepend-icon=""
                >
              </v-file-input> -->

              <v-file-input
                class="border-basic"
                prepend-inner-icon="mdi-paperclip"
                prepend-icon=""
                multiple
                dense
                outlined
                solo
                flat
                counter
                small-chips
                show-size
                truncate-length="15"
                label="Adjuntar archivo"
                v-model="ubicacion.adjuntos"
              >
              </v-file-input>
            </v-col>
            <v-col
              cols="12"
              v-if="permitirCaladeros"
            >
              <v-text-field
                label="Nombre puerto desembarque"
                v-model="ubicacion.nombrePuerto"
                dense
                outlined
                solo
                flat
                required
                :rules="documentRules"
                >
              </v-text-field>
            </v-col>

            <v-col
              cols="12"
              >
                <v-switch
                  v-model="ubicacion.enVereda"
                  inset
                  label="Evento ubicado en vereda"
                ></v-switch>
            </v-col>

            <v-col
            cols="12"
            >
              <v-text-field
                label="Latitud(X.Y)º"
                hint="Latitud(X.Y)º"
                v-model="latitudEvento"
                dense
                outlined
                solo
                flat
                required
                :disabled="true"
                :rules="documentRules"
                :onkeypress="regexNumber"
                >
              </v-text-field>
            </v-col>

            <v-col
            cols="12"
            >
              <v-text-field
                label="Longitud(X.Y)º"
                hint="Longitud(X.Y)º"
                v-model="longitudEvento"
                dense
                outlined
                solo
                flat
                required
                :disabled="true"
                :rules="documentRules"
                :onkeypress="regexNumber"
                >
              </v-text-field>
            </v-col>

            <v-col
            cols="12"
            >
              <v-text-field
                label="Precisión(m)"
                v-model="ubicacion.precision"
                dense
                outlined
                solo
                flat
                required
                :rules="documentRules"
                :onkeypress="regexNumber"
                >
              </v-text-field>
            </v-col>

            <v-col
            cols="12"
            md="12"
            >
              <v-text-field
                label="Altitud(m)"
                v-model="ubicacion.altitud"
                dense
                outlined
                solo
                flat
                required
                :rules="documentRules"
                :onkeypress="regexNumber"
                >
              </v-text-field>
            </v-col>

            <v-col
              cols="12"
            >
              <v-autocomplete
                label="Departamento"
                :items="departamentos"
                v-model="ubicacion.departamento"
                :search-input.sync="ubicacion.nameDepartamento"
                clearable
                item-value="valor"
                dense
                outlined
                solo
                flat
                required
                :rules="documentRules"
                @change="cargarMunicipioSegunDepartamento()"
                >
              </v-autocomplete>
            </v-col>

            <v-col
              cols="12"
              >
              <v-autocomplete
                label="Municipio"
                :items="relMunicipioDepartamento"
                v-model="ubicacion.municipio"
                :search-input.sync="ubicacion.nameMunicipio"
                item-value="valor"
                dense
                outlined
                solo
                flat
                required
                clearable
                :rules="documentRules"
                no-data-text="Primero seleccione un departamento"
                @change="cargarVeredaSegunMunicipio()"
                >
              </v-autocomplete>
            </v-col>

            <v-col
              cols="12"
              >
              <v-autocomplete
                label="Vereda"
                :items="relVeredaMunicipio"
                v-model="ubicacion.codVereda"
                :search-input.sync="ubicacion.nameVereda"
                item-value="valor"
                dense
                outlined
                clearable
                solo
                flat
                v-if="ubicacion.enVereda"
                required
                :rules="documentRules"
                >
              </v-autocomplete>
            </v-col>

            <v-col
            cols="12"
            >
              <v-textarea
                label="Observación"
                v-model="ubicacion.observacion"
                dense
                outlined
                solo
                flat
                required
                :rules="documentRules"
                >
              </v-textarea>
            </v-col>

          </v-row>

        </v-form>

      </v-col>

      <!--  mapa -->
      <v-col
        cols="12"
        mg="8"
        sm="8"
        order="1"
        order-sm="2"
      >
        <v-container style="height:500px;" class="ma-0 pa-0">
            <l-map
              ref="eventoMap"
              :zoom="zoom"
              :min-zoom="minZoom"
              :max-zoom="maxZoom"
              :center="center"
              @update:center="centerUpdated"
              @update:bounds="boundsUpdated"
              @ready="loadMap()"
              v-if="reload"
              @click="loadMinMap"
            >

            <l-control-layers
              position="topright"
              v-if="isOnline"
            >
            </l-control-layers>
            <l-tile-layer
              v-for="tileProvider in tileProviders"
              :key="tileProvider.name"
              :name="tileProvider.name"
              :visible="tileProvider.visible"
              :url="isOnline ? tileProvider.url : tileProvider.urlOffline"
              :attribution="tileProvider.attribution"
              layer-type="base"
            />
            <l-control-scale
              position="topright"
              :imperial="true"
              :metric="false"
            >
            </l-control-scale>
            <l-control-fullscreen
              position="topleft"
              :options="{ title: { 'false': 'Ampliar', 'true': 'Reducir' } }"
            />
            <l-marker
              v-for="marker in markers"
              :key="marker.id"
              :visible="marker.visible"
              :draggable="marker.draggable"
              :lat-lng.sync="marker.position"
              @dragend="setMarkerPosition(marker.tipo)"
            >
              <l-tooltip
                :options="{ permanent: true, interactive: false }"
              >
                {{ marker.tooltip }}
              </l-tooltip >
            </l-marker>
            <l-control position="bottomleft">
              <v-col cols="6">
                <v-btn
                  style="background-color:white;"
                  elevation="3"
                  color="primary"
                  icon
                  dark
                  title="Capturar ubicación"
                  @click="pedirUbicacion"
                >
                  <v-icon> mdi-crosshairs-gps </v-icon>
                </v-btn>
              </v-col>
              <v-col cols="6" v-if="isOnline">
                <v-btn
                  style="background-color:white;"
                  elevation="3"
                  color="primary"
                  icon
                  dark
                  title="Dibujar área"
                  @click="flipActiveEdit"
                  v-if="!isActive"
                >
                <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <v-btn
                  style="background-color:white;"
                  elevation="3"
                  color="primary"
                  icon
                  dark
                  title="Guardar área"
                  @click="flipActiveSave"
                  v-if="isActive"
                >
                <v-icon>mdi-content-save</v-icon>
                </v-btn>
              </v-col>
              <v-col cols="6" v-if="isOnline">
                <v-btn
                  style="background-color:white;"
                  elevation="3"
                  color="primary"
                  icon
                  dark
                  title="Limpiar todo el dibujado"
                  v-if="isActive"
                  @click="limpiarDibujo"
                >
                  <v-icon> mdi-close-thick </v-icon>
                </v-btn>
              </v-col>

            </l-control>
            <vue-leaflet-minimap
              ref="miniMap"
              :layer="isOnline?layerOnline:layerOffline"
              :options="optionsMiniMap"
              v-if="seeMiniMap"
            >
            </vue-leaflet-minimap>
            <LFreeDraw
              ref="freeDrawRef"
              v-model="polygons"
              :mode="mode"
              :options="optionsLFreeDraw"
            />

          </l-map>
        </v-container>
      </v-col>

    </v-row>

    <v-row>
      <v-col
        v-if="markers.length > 1"
        cols="12"
        md="12"
        sm="12"
      >
        <p class="font-weight-bold mt-5"> Caladeros </p>
        <v-data-table
           :headers="caladerosHeaders"
           :items="dataCaladeros"
           item-key="nombre"
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
               v-if="item.icon"
               small
               color="#004884"
               @click="deleteCaladero(item)"
             >
             mdi-delete
             </v-icon>
           </template>
        </v-data-table>
      </v-col>
      <v-col
        cols="12"
        md="9"
        sm="12"
      >
      </v-col>
      <v-col
        cols="12"
        md="3"
        sm="12"
        align="end"
        justify="end"
      >
        <v-btn
          class="background-primary-dark button-basic"
          elevation="2"
          raised
          block
          depressed
          title="Asignar ubicación"
          @click="guardarDataMapa()"
        >
          Asignar ubicación
        </v-btn>
      </v-col>
    </v-row>

    <!-- <p>{{ this.ubicacion }}</p> -->
    <!-- <p>acá va:</p>
    <p>{{ this.tipoProductor }}</p>
    <p>{{ this.markers }}</p>
    <p>{{ this.ubicacion }}</p> -->

  </v-container>
</template>

<script>

import { getData } from '../../indexedDb/getData';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import * as Vue2Leaflet from 'vue2-leaflet'
import LControlFullscreen from 'vue2-leaflet-fullscreen';
import VueLeafletMinimap from 'vue-leaflet-minimap';
import LFreeDraw from 'vue2-leaflet-freedraw';
import { NONE, ALL } from 'leaflet-freedraw';

export default {
  name: 'EventoUbicacion',
  components: {
    LMap: Vue2Leaflet.LMap,
    LTileLayer: Vue2Leaflet.LTileLayer,
    VueLeafletMinimap,
    LMarker: Vue2Leaflet.LMarker,
    LIcon: Vue2Leaflet.LIcon,
    LTooltip: Vue2Leaflet.LTooltip,
    LControl: Vue2Leaflet.LControl,
    LControlLayers: Vue2Leaflet.LControlLayers,
    LControlScale: Vue2Leaflet.LControlScale,
    LControlFullscreen,
    LFreeDraw,
  },
  props: ['obtenerDataMapa','tipoProductor', 'reload'],
  data () {
    return {
      // Vairables necesarias para el funcionamiento del mapa.
      createMap: null,
      seeMiniMap: false,
      bounds: null,
      staticAnchor: [20, 40],
      caladerosHeaders: [
        { text: 'Item', align: 'start', sortable: false, value: 'id' },
        { text: 'Latitud', align: 'start', sortable: false, value: 'position.lat' },
        { text: 'Longitud', align: 'start', sortable: false, value: 'position.lng' },
        { text: 'Tipo Ubicación', align: 'start', sortable: false, value: 'tipo' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      markers: [
        {
          id: 1,
          position: { lat: 7.086594479396249, lng: -73.13499631331399 },
          tooltip: ' Evento ',
          draggable: true,
          visible: true,
          icon: false,
          tipo: 'Evento'
        }
      ],
      center: new L.latLng(7.086594479396249, -73.13499631331399),
      // url: '/map/{z}/{x}/{y}.png',
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      tileProviders: [
        {
          name: 'Street Map',
          visible: true,
          url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
          saveToCache: true,
          urlOffline:"./img/map/{z}/{x}/{y}.png",
        },
        {
          name: 'Transport Map',
          visible: false,
          url: 'https://tile.thunderforest.com/transport/{z}/{x}/{y}.png?apikey=e955b6c9bc0b4ec6a38495e3f90d87b5',
          saveToCache: true,
          urlOffline:"./img/map/{z}/{x}/{y}.png",
        },
      ],
      layerOnline: new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'),
      layerOffline: new L.TileLayer('./img/map/{z}/{x}/{y}.png'),
      optionsMiniMap: {
        position: 'bottomright',
        width: 200,
        height: 175,
        toggleDisplay: true,
        minimized: true,
      },

      // Reglas
      documentRules: [
        v => !!v || 'Campo obligatorio'
      ],
      regexNumber: "return (event.charCode >= 48 && event.charCode <= 57)",

      // Variables del formulario de ubicación.
      valid: false,
      eventoVereda: false,
      departamentos: [],
      municipios: [],
      relVeredaMunicipio: [],
      veredas: [],
      relMunicipioDepartamento: [],
      ubicacion: {
        departamento: '',
        municipio: '',
        latitud: '',
        longitud: '',
        precision: '',
        altitud: '',
        enVereda: false,
        codVereda: '',
        nombrePuerto: '',
        observacion: ''
      },
      archivoUbicacion: [],
      // map: new L.Map(node),
      mapSee: false,
      polygons: [],
      isActive: false,
      optionsLFreeDraw: {
        leaveModeAfterCreate:true,
      },
    }
  },
  async mounted () {
    await this.getDataMapa();
    await this.edicionMapa();

    // await this.$nextTick(() => {
    //   const eventoMap = this.$refs.eventoMap;
    //   setTimeout(function () {
    //     eventoMap.mapObject.invalidateSize();
    //   }, 5000)
    // });

  },
  created: function () {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(

        ubicacion => {
          const coordenadas = ubicacion.coords

          this.markers[0].position.lat = 0
          this.markers[0].position.lng = 0
          this.center.lat = 0
          this.center.lng = 0

          this.center.lat = coordenadas.latitude
          this.center.lng = coordenadas.longitude
          this.markers[0].position.lat = coordenadas.latitude
          this.markers[0].position.lng = coordenadas.longitude
          this.ubicacion.latitud = coordenadas.latitude
          this.ubicacion.longitud = coordenadas.longitude
        },
        () => {
          this.$toasted.error('No se pudo obtener su ubicación, intentelo mas tarde.', { duration: 5000 })
        },
        {
          enableHighAccuracy: true
        }
      )
    } else this.$toasted.error('Lo sentimos, su navegador no tiene soporte para obtener su ubicación.', { duration: 5000 })

  },
  methods: {
    loadMap() {
      const eventoMap = this.$refs.eventoMap;
      setTimeout(function () {
        eventoMap.mapObject.invalidateSize();
      }, 1000)
    },
    loadMinMap() {
      this.seeMiniMap = true;
    },
    async getDataMapa () {
      try {
        const data = await getData('mapa', true);

        for (const itemDepa in data.departamentos) {
          var addDepartamento = {
            valor: data.departamentos[itemDepa][0],
            text: data.departamentos[itemDepa][1]
          }
          this.departamentos.push(addDepartamento)
        }

        for (const itemMuni in data.municipios) {
          var addMunicipio = {
            valor: data.municipios[itemMuni][0],
            text: data.municipios[itemMuni][2],
            idDepartamento: data.municipios[itemMuni][3]
          }
          this.municipios.push(addMunicipio)
        }

        for (const itemVereda in data.veredas) {
          var addVereda = {
            valor: data.veredas[itemVereda][0],
            text: data.veredas[itemVereda][1],
            idMunicipio: data.veredas[itemVereda][2]
          }
          this.veredas.push(addVereda)
        }

      } catch (error) {
        console.log('error:');
        console.log(error);
      }
    },
    edicionMapa() {
      const dataEvento = this.$route.params.evento;
      console.log('dataEvento mapa:');
      console.log(dataEvento);
      if (dataEvento !== undefined) {
        if (Object.keys(dataEvento.dataEncabezadoEvento).length > 0) {
          const encabezado = dataEvento.dataEncabezadoEvento;
          const dataMapa = {
            'adjuntos': encabezado.adjuntos,
            'altitud': encabezado.altitud,
            'caladeros': encabezado.caladeros,
            'codVereda': encabezado.codVereda,
            'departamento': encabezado.departamento,
            'enVereda': encabezado.enVereda,
            'latitud': encabezado.latitud,
            'longitud': encabezado.longitud,
            'municipio': encabezado.municipio,
            'nameDepartamento': encabezado.nameDepartamento,
            'nameMunicipio': encabezado.nameMunicipio,
            'nombrePuerto': encabezado.nombrePuerto,
            'observacion': encabezado.observacion,
            'precision': encabezado.precision,
          }
          this.markers[0].position = {'lat': dataMapa.latitud, 'lng': dataMapa.longitud}
          for(const key in dataMapa.caladeros) {
            this.markers.push(dataMapa.caladeros[key]);
          }
          this.ubicacion = dataMapa;
          this.cargarMunicipioSegunDepartamento();
          this.cargarVeredaSegunMunicipio();
        }
      }
    },
    agregarCaladero() {
      const indice = this.markers.length - 1;
      const id = this.markers[indice].id + 1;

      this.markers.push({
          id: id,
          position: { lat: this.markers[0]['position']['lat'], lng: this.markers[0]['position']['lng'] },
          tooltip: ' Caladero '+ id,
          draggable: true,
          visible: true,
          icon: true,
          tipo: 'Caladero'
      })
    },
    deleteCaladero(item) {
      const editedIndex = this.markers.indexOf(item)
      this.markers.splice(editedIndex, 1)
    },
    cargarMunicipioSegunDepartamento() {
      this.relMunicipioDepartamento = this.municipios.filter(municipio => municipio.idDepartamento === this.ubicacion.departamento)
    },
    cargarVeredaSegunMunicipio() {
      this.relVeredaMunicipio = this.veredas.filter(vereda => vereda.idMunicipio === this.ubicacion.municipio)
    },
    centerUpdated (center) {
      this.center = center
    },
    boundsUpdated (bounds) {
      this.bounds = bounds
    },
    pedirUbicacion () {
      if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(

          ubicacion => {
            const coordenadas = ubicacion.coords
            this.markers[0].position.lat = 0
            this.markers[0].position.lng = 0
            this.center.lat = 0
            this.center.lng = 0

            this.center.lat = coordenadas.latitude
            this.center.lng = coordenadas.longitude
            this.markers[0].position.lat = coordenadas.latitude
            this.markers[0].position.lng = coordenadas.longitude
            this.ubicacion.latitud = coordenadas.latitude
            this.ubicacion.longitud = coordenadas.longitude
          },
          () => {
            this.$toasted.error('No se pudo obtener su ubicación, intentelo mas tarde.', { duration: 5000 })
          },
          {
            enableHighAccuracy: true
          }
        )
      } else this.$toasted.error('Lo sentimos, su navegador no tiene soporte para obtener su ubicación.', { duration: 5000 })
    },
    // setPos(e) {
    //   const layer = e.target
    //   const ll = layer.getLatLng()
    //   layer.setLatLng(ll)
    //   return [ll.lat, ll.lng]
    // },
    setMarkerPosition(tipo) {
      // const position = this.setPos(e);
      var position = this.markers.filter((data)=>data.tipo === 'Evento');
      this.ubicacion.latitud = position[0].position.lat;
      this.ubicacion.longitud = position[0].position.lng;
      if (tipo === 'Evento') {
        this.$refs.freeDrawRef.mapObject.clear();
      }
    },
    guardarDataMapa() {
      if (this.$refs.form.validate()) {
        this.ubicacion.caladeros = this.markers.filter((data)=>data.tipo !== 'Evento');
        this.obtenerDataMapa(this.ubicacion);
        this.$swal({
          icon: 'success',
          text: 'Ubicación agregada',
          confirmButtonText: 'Aceptar',
        });
      }
    },
    flipActiveEdit() {
      if (this.polygons.length>0) {
        this.$refs.freeDrawRef.mapObject.clear();
      }
      this.isActive = !this.isActive;
    },
    flipActiveSave() {
      if (this.polygons.length>0) {
        const centro = this.centroide(this.polygons[0]);

        this.center.lat = centro[0];
        this.center.lng = centro[1];
        this.markers[0].position.lat = centro[0];
        this.markers[0].position.lng = centro[1];
        this.ubicacion.latitud = centro[0];
        this.ubicacion.longitud = centro[1];
      }

      this.isActive = !this.isActive;
    },
    centroide(arr) {
        var twoTimesSignedArea = 0;
        var cxTimes6SignedArea = 0;
        var cyTimes6SignedArea = 0;

        var length = arr.length

        var x = function (i) { return arr[i % length]['lat'] };
        var y = function (i) { return arr[i % length]['lng'] };

        for ( var i = 0; i < arr.length; i++) {
            var twoSA = x(i)*y(i+1) - x(i+1)*y(i);

            twoTimesSignedArea += twoSA;
            cxTimes6SignedArea += (x(i) + x(i+1)) * twoSA;
            cyTimes6SignedArea += (y(i) + y(i+1)) * twoSA;
        }
        var sixSignedArea = 3 * twoTimesSignedArea;
        return [ cxTimes6SignedArea / sixSignedArea, cyTimes6SignedArea / sixSignedArea];
    },
    limpiarDibujo() {
      this.$refs.freeDrawRef.mapObject.clear();
      this.isActive = !this.isActive;
    },
  },
  computed: {
    mode() {
      for(let i = 0; i < this.markers.length; i++){
        this.markers[i].visible = !this.isActive;
      }

      console.log('markers');
      console.log(this.markers);

      return this.isActive ? ALL: NONE;
    },
    width () {
      let status

      switch (this.$vuetify.breakpoint.name) {
        case 'xs':
          status = true
          break
        case 'sm':
          status = true
          break
        case 'md':
          status = false
          break
        case 'lg':
          status = false
          break
        case 'xl':
          status = false
          break
      }

      return status
    },
    permitirCaladeros() {
      var estado = false;
      const idPescadores = [4,5,6];
      var productores = this.tipoProductor.filter((tipo)=>idPescadores.includes(tipo));

      if (productores.length>0) {
        estado = true;
      } else {
        if (this.markers.length>0) {
          this.markers = this.markers.filter((data)=>data.tipo !== 'Caladero');
          this.ubicacion.nombrePuerto = '';
        }
      }

      return estado;
    },
    dataCaladeros() {
      return this.markers.filter((data)=>data.tipo !== 'Evento');
    },
    latitudEvento() {
      var position = this.markers.filter((data)=>data.tipo === 'Evento');
      this.ubicacion.latitud = position[0].position.lat;
      return this.ubicacion.latitud;
    },
    longitudEvento() {
      var position = this.markers.filter((data)=>data.tipo === 'Evento');
      this.ubicacion.longitud = position[0].position.lng;
      return this.ubicacion.longitud;
    },
    zoom() {
      // this.loadMap();
      return this.isOnline ? 10: 7;
    },
    minZoom() {
      return this.isOnline ? 2: 7;
    },
    maxZoom() {
      return this.isOnline ? 17: 8;
    },
  },
}
</script>
<style>@import '~leaflet-minimap/dist/Control.MiniMap.min.css';</style>
