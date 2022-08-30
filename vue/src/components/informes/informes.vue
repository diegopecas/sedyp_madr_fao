<template>
  <div>
    <v-container
      class="border-basic"
      elevation-2
    >
      <v-row>
        <v-col
          cols="12"
          md="4"
          >
          <v-select
            label="Departamento"
            :items="departamentos"
            v-model="ubicacion.departamento"
            item-value="valor"
            dense
            outlined
            solo
            flat
            @change="cargarMunicipioSegunDepartamento()"
            >
          </v-select>
        </v-col>

        <v-col
          cols="12"
          md="4"
          >
          <v-select
            label="Municipio"
            :items="relMunicipioDepartamento"
            v-model="ubicacion.municipio"
            item-value="valor"
            dense
            outlined
            solo
            flat
            @change="setDataInformes(true)"
            >
          </v-select>
        </v-col>

      </v-row>

      <div style="height: 400px; width: 100%">
          <l-map
          id="map-informes"
          ref="mapEvents"
          :zoom="zoom"
          :center="center"
          :options="mapOptions"
          style="height: 90%"
          @update:center="centerUpdate"
          @update:zoom="zoomUpdate"
          @ready="mapReady()">
            <l-tile-layer
            :url="url"
            :attribution="attribution"
            />
            <l-marker
            v-for="marker in markers"
            :key="marker.id"
            :visible="marker.visible"
            :lat-lng="marker.position"
            >
              <l-icon
              :icon-anchor="[10, 10]"
              class-name="icon-map"
              >
                <v-icon color="red"  class="icon">
               mdi-map-marker
                </v-icon>
              </l-icon>
            </l-marker>
          </l-map>
      </div>

      <v-row>
        <!-- Promedio de edades -->
        <v-col
          cols="12"
          md="6"
        >
          <v-chip
          color="primary"
          >
            Promerio de edad productores: {{ promerioEdad }}
            <v-icon right>
              mdi-account-outline
            </v-icon>
          </v-chip>
        </v-col>
        <v-col
          cols="12"
          md="6"
        >
          <v-chip
          color="primary"
          >
            Valor total en perdidas: {{ valorPedidas }}
            <v-icon right>
              mdi-cash
            </v-icon>
          </v-chip>
        </v-col>
      </v-row>

      <v-row>

        <v-col
          cols="12"
          sm="6"
          lg="4"
          v-for="(item, index) in informes" :key="index"
        >
          <v-card
            class="elevation-0 card-chart"
          >
            <v-card-title>{{ item.titulo }}</v-card-title>
            <v-card-text>
            <apexchart :type="item.tipo" :options="item.chartOptions" :series="item.series"></apexchart>
            </v-card-text>
            <v-divider></v-divider>
            <v-card-actions>
            <p>Total: {{ item.total }}</p>
            </v-card-actions>
          </v-card>
        </v-col>

      </v-row>

    </v-container>
  </div>
</template>

<script>

import { informesEvento } from '../../services/api'
import ApexCharts from 'apexcharts'
import jwtDecode from 'jwt-decode'
import L, { latLng, Icon } from 'leaflet'
import { LMap, LTileLayer, LMarker, LIcon } from 'vue2-leaflet'

delete Icon.Default.prototype._getIconUrl; Icon
Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png')
})

export default {
  name: 'informesGenerales',
  components: {
    LMap,
    LTileLayer,
    LMarker,
    LIcon
  },
  data () {
    return {
      // data mapa
      zoom: 10,
      center: latLng(7.086594479396249, -73.13499631331399),
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution: '',
      currentZoom: 11.5,
      currentCenter: latLng(7.086594479396249, -73.13499631331399),
      showParagraph: false,
      mapOptions: {
        zoomSnap: 0.5
      },
      showMap: true,
      markers: [],
      informes:[],

      departamentos: [],
      municipios: [],
      relMunicipioDepartamento: [],
      ubicacion: {},
      totalTipoProductor: 0,
      totalSexo: 0,
      totalEtnico: 0,
      totalHectarea: 0,
      promerioEdad: '',
      totalVolumen: 0,
      valorPedidas: '',
    }
  },
  async mounted () {
    await this.setDataInformes(false)
  },
  methods: {
    async setDataInformes (aplicarFiltro) {

      const ubicacion = this.ubicacion

      if (aplicarFiltro) {
        this.informes = [];
      }

      try {
        const res = await informesEvento.setDataInformesGenerales({ ubicacion })

        if (res.status === 200) {
          const encoded = res.data.token
          const decoded = jwtDecode(encoded)
          const data = decoded.dataInformes

          this.llenarSelect(data);
          this.promerioEdad = data.promerioEdad[0]['edad'].replace('$', '');
          var valorPedidas = data.valorPerdida[0]['valor'].replace('$', '');
          this.valorPedidas = valorPedidas > 0 ? new Intl.NumberFormat('es-ES').format(data.valorPerdida[0]['valor']) : 'No hay perdida';
          this.ubicacionEventos(data.ubicacionEventos);
          this.graficaTipoProductor(data.tipoProductor);
          this.graficaSexoProductor(data.sexoProductores);
          this.graficaGrupoEtnico(data.grupoEtnico);
          this.graficaHectaresEspecie(data.hectareasEspecie);
          this.graficaVolumenMadera(data.volumenMadera);
          this.graficaDanosInfraestructura(data.danosInfraestructura);
        }
      } catch (error) {
        console.log(error)
      }
    },
    mapReady () {
      console.log('ready map go!')
    },
    zoomUpdate (zoom) {
      this.currentZoom = zoom
    },
    centerUpdate (center) {
      this.currentCenter = center
    },
    llenarSelect (data) {
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
    },
    ubicacionEventos (ubicacionEventos) {
      this.markers = []
      for (const itemUbica in ubicacionEventos) {
        var corrX = ubicacionEventos[itemUbica].coord_x.replace('$', '');
        var corrY = ubicacionEventos[itemUbica].coord_y.replace('$', '');

        var addUbicacion = {
          id: itemUbica,
          position: { lat: corrX, lng: corrY }
        }
        this.markers.push(addUbicacion)
      }
    },
    cargarMunicipioSegunDepartamento () {
      this.relMunicipioDepartamento = this.municipios.filter(municipio => municipio.idDepartamento === this.ubicacion.departamento)
    },
    graficaTipoProductor (tipoProductor) {
      var data =  tipoProductor.length > 0? []: [0];
      var categories = tipoProductor.length > 0 ? [] : ['0'];
      var total = 0

      for (const documento in tipoProductor) {
        data.push(parseFloat(tipoProductor[documento].cantidad))
        categories.push(tipoProductor[documento].tipo_productor)
        total += parseFloat(tipoProductor[documento].cantidad)
      }

      this.graficaBarras(data, categories, 'Productores afectados', total, 'barchartTipoProductor');

    },
    graficaSexoProductor (sexoProductores) {
      var data =  sexoProductores.length > 0? []: [0];
      var categories = sexoProductores.length > 0 ? ['Hombres', 'Mujeres'] : ['0'];
      var total = 0

      for (const documento in sexoProductores) {
        var hombres = parseFloat(sexoProductores[documento].hombres.replace('$', ''))
        var mujeres = parseFloat(sexoProductores[documento].mujeres.replace('$', ''))

        data.push(hombres)
        data.push(mujeres)
        total += hombres + mujeres
      }

      this.graficaBarras(data, categories, 'Sexo productores', total, 'barchartSexo');

    },
    graficaGrupoEtnico (grupoEtnico) {
      var data =  grupoEtnico.length > 0? []: [0];
      var categories = grupoEtnico.length > 0 ? [] : ['0'];
      var total = 0

      for (const documento in grupoEtnico) {
        data.push(parseFloat(grupoEtnico[documento].cantidad))
        categories.push(grupoEtnico[documento].grupo_etnico)
        total += parseFloat(grupoEtnico[documento].cantidad)
      }

      this.graficaBarras(data, categories, 'Grupos étnicos', total, 'barchartEtnico');

    },
    graficaHectaresEspecie (hectareasEspecie) {
      var data =  hectareasEspecie.length > 0? []: [0];
      var categories = hectareasEspecie.length > 0 ? [] : ['0'];
      var total = 0

      for (const documento in hectareasEspecie) {
        var cantidad = parseFloat(hectareasEspecie[documento].cantidad.replace('$', ''))
        data.push(cantidad)
        categories.push(hectareasEspecie[documento].especie_forestal_afectada)
        total += cantidad
      }

      this.graficaBarras(data, categories, 'Hectareas por especie', total, 'barchartHectarea');
    },
    graficaVolumenMadera(volumenMadera) {
      var data =  volumenMadera.length > 0? []: [0];
      var categories = volumenMadera.length > 0 ? [] : ['0'];
      var total = 0;

      for (const documento in volumenMadera) {
        var volumen = parseFloat(volumenMadera[documento].volumen.replace('$', ''))
        data.push(volumen);
        categories.push(volumenMadera[documento].tipo_evento)
        total += volumen;
      }

      this.graficaBarras(data, categories, 'Volumen Madera', total, 'barchartVolumenMadera');
    },
    graficaDanosInfraestructura(danosInfraestructura) {
      var data =  danosInfraestructura.length > 0? []: [0];
      var categories = danosInfraestructura.length > 0 ? ['Semillas', 'Fertilizantes', 'Plaguicidas', 'Maquinaria'] : ['0'];
      var total = 0;

      for (const documento in danosInfraestructura) {
        var semilla = parseFloat(danosInfraestructura[documento].vlr_semilla.replace('$', ''));
        var fertilizante = parseFloat(danosInfraestructura[documento].vlr_fertilizante.replace('$', ''));
        var plaguicida = parseFloat(danosInfraestructura[documento].vlr_plaguicida.replace('$', ''));
        var maquinaria = parseFloat(danosInfraestructura[documento].vlr_maquinaria.replace('$', ''));
        data.push(semilla);
        data.push(fertilizante);
        data.push(plaguicida);
        data.push(maquinaria);

        total += semilla + fertilizante + plaguicida + maquinaria;
      }

      this.graficaBarras(data, categories, 'Daños por infraestructura', total, 'barchartDanosInfraEstructura');
    },
    graficaBarras(data, categories, nameChart, totalCosto, ref) {

      var informe = {
        tipo:   'bar',
        ref:    ref,
        titulo: nameChart,
        total:  totalCosto ? '$' + (new Intl.NumberFormat('es-ES').format(totalCosto)) : 'No hay perdida',
        series: [{name:'valor', data: data}],
        chartOptions: {
          xaxis:{categories: categories},
          grid: {
            xaxis: {
              lines: {
                show: true
              }
            }
          },
          plotOptions: {
            bar: {
              borderRadius: 10,
              horizontal: false
            }
          },
        },
      };

      this.informes.push(informe);

      // return {
      //   series: [{
      //     name: 'cantidad',
      //     data: data
      //   }],
      //   chart: {
      //     height: 350,
      //     type: 'bar'
      //   },
      //   plotOptions: {
      //     bar: {
      //       borderRadius: 10,
      //       dataLabels: {
      //         position: 'top' // top, center, bottom
      //       }
      //     }
      //   },
      //   dataLabels: {
      //     enabled: true,
      //     formatter: function (val) {
      //       return val + ''
      //     },
      //     offsetY: -20,
      //     style: {
      //       fontSize: '12px',
      //       colors: ['#304758']
      //     }
      //   },

      //   xaxis: {
      //     categories: categories,
      //     position: 'bottom',
      //     axisBorder: {
      //       show: false
      //     },
      //     axisTicks: {
      //       show: false
      //     },
      //     crosshairs: {
      //       fill: {
      //         type: 'gradient',
      //         gradient: {
      //           colorFrom: '#D8E3F0',
      //           colorTo: '#BED1E6',
      //           stops: [0, 100],
      //           opacityFrom: 0.4,
      //           opacityTo: 0.5
      //         }
      //       }
      //     },
      //     tooltip: {
      //       enabled: true
      //     }
      //   },
      //   yaxis: {
      //     axisBorder: {
      //       show: false
      //     },
      //     axisTicks: {
      //       show: false
      //     },
      //     labels: {
      //       show: false,
      //       formatter: function (val) {
      //         return val + ''
      //       }
      //     }

      //   },
      //   title: {
      //     text: nameChart,
      //     floating: true,
      //     offsetY: 2,
      //     align: 'center',
      //     style: {
      //       color: '#444'
      //     }
      //   }
      // }
    }

  }
}
</script>

<style scoped>
  .icon {
    opacity:0.8;
  }
  .card-chart {
    border: 1px solid rgb(206, 206, 206) !important;
    border-radius: 10px !important;
  }
</style>
