<template>
 <div>

    <v-container
    class="border-basic"
    elevation-2
    >
      <v-row class="ma-5">
        <v-col
          cols="12"
          sm="6"
          lg="4"
          v-for="(item, index) in informes" :key="index"
        >
          <v-card class="elevation-0 card-chart">
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
import VueApexCharts from 'vue-apexcharts'
import jwtDecode from 'jwt-decode'

export default {
  name: 'informesPorEvento',
  components: {apexchart: VueApexCharts},
  data () {
    return {
      dataEvento: [],
      informes: [],
    }
  },
  async mounted () {
    await this.setDataInformes()
  },
  created () {
    this.dataEvento = this.$route.params.evento
  },
  methods: {
    async setDataInformes () {
      var idEvento = this.dataEvento.cod_evento

      try {
        const res = await informesEvento.setDataInformesEvento({ idEvento })

        if (res.status === 200) {
          const encoded = res.data.token
          const decoded = jwtDecode(encoded)
          const data = decoded.dataInformes

          //console.log(data)

          this.costosDirectosPorActividad(data.costosDirectos)
          this.costosInDirectosPorRubro(data.costosInDirectos)
          this.costosInfraestructura(data.tipoInfraestructura)
          this.perdidaEconomicaForestal(data.perdidaEconomicaForestal)
          this.valPerdidaEconomica(data.valPerdidaEconomica)
          this.perdidaEstimadaProduccion(data.perdidaEstimadaProdu)
        }
      } catch (error) {
        console.log(error)
      }
    },
    costosDirectosPorActividad (costosDirectos) {
      var data =  costosDirectos.length > 0? []: [0];
      var categories = costosDirectos.length > 0 ? [] : ['0'];
      var totalCosto = 0;

      for (const documento in costosDirectos) {
        var gasto = parseFloat(costosDirectos[documento].gasto_incurrido.replace('$', ''))
        if (gasto <= 0) {
          continue
        }
        data.push(gasto)
        categories.push(costosDirectos[documento].actividad)
        totalCosto += gasto
      }

      var informe = {
        tipo:   'bar',
        ref:    'barchartDirectos',
        titulo: '$ Costos directos por rubro',
        total:  totalCosto ? '$' + (new Intl.NumberFormat('es-ES').format(totalCosto)) : 'No hay perdida',
        series: [{name: 'cantidad',data: data}],
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
    },
    costosInDirectosPorRubro (costosInDirectos) {
      var data =  costosInDirectos.length > 0? []: [0];
      var categories = costosInDirectos.length > 0 ? [] : ['0'];
      var totalCosto = 0

      for (const documento in costosInDirectos) {
        var gasto = parseFloat(costosInDirectos[documento].gasto_incurrido.replace('$', ''))
        if (gasto <= 0) {
          continue
        }
        data.push(gasto)
        categories.push(costosInDirectos[documento].rubros)
        totalCosto += gasto
      }

      var informe = {
        tipo:   'bar',
        ref:    'barchartInDirectos',
        titulo: '$ Costos indirectos por rubro',
        total:  totalCosto ? '$' + (new Intl.NumberFormat('es-ES').format(totalCosto)) : 'No hay perdida',
        series: [{data: data}],
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
    },
    costosInfraestructura (costoInfraestructura) {
      var data =  costoInfraestructura.length > 0? []: [0];
      var categories = costoInfraestructura.length > 0 ? [] : ['0'];
      var totalCosto = 0

      for (const documento in costoInfraestructura) {
        const semilla =parseFloat(costoInfraestructura[documento].vlr_semilla.replace('$', ''))
        data.push(semilla)
        const fertilizante =parseFloat(costoInfraestructura[documento].vlr_fertilizante.replace('$', ''))
        data.push(fertilizante)
        const plaguicida =parseFloat(costoInfraestructura[documento].vlr_maquinaria.replace('$', ''))
        data.push(plaguicida)
        const maquinaria =parseFloat(costoInfraestructura[documento].vlr_maquinaria.replace('$', ''))
        data.push(maquinaria)

        if (semilla <= 0  && fertilizante <= 0
          && plaguicida <= 0  && maquinaria <= 0) {
          continue
        }

        totalCosto += semilla + fertilizante + plaguicida + maquinaria
      }

      if (costoInfraestructura.length > 0) {
        var categories = ['Vlr.Semilla', 'Vlr.Fertilizante', 'Vlr.Plaguicida', 'Vlr.Maquinaria']
      }

      var informe = {
        tipo:   'donut',
        ref:    'piechartMaquinaria',
        titulo: '$ Costos por infraestructura',
        total:  totalCosto ? '$' + (new Intl.NumberFormat('es-ES').format(totalCosto)) : 'No hay perdida',
        series: data,
        chartOptions: {
          chart: {
            type: 'donut',
          },
          labels: categories,
        },
      };

      this.informes.push(informe);
    },
    perdidaEconomicaForestal (porcPerdida) {
      var data =  porcPerdida.length > 0? []: [0];
      var categories = porcPerdida.length > 0 ? [] : ['0'];
      var totalCosto = 0

      for (const documento in porcPerdida) {
        var gasto = parseFloat(porcPerdida[documento].valor.replace('$', ''))
        if (gasto <= 0) {
          continue
        }
        data.push(gasto)
        categories.push(''+ documento * 1 + 1 +'')
        totalCosto += gasto
      }

      this.porcePerdidaForestal = totalCosto ? '%' + (new Intl.NumberFormat('es-ES').format(totalCosto)) : 'No hay perdida'
      var informe = {
        tipo:   'bar',
        ref:    'barchartPerdidaForestal',
        titulo: '% Perdida plantación forestal',
        total:  totalCosto ? '%' + (new Intl.NumberFormat('es-ES').format(totalCosto)) : 'No hay perdida',
        series: [{data: data}],
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

    },
    valPerdidaEconomica (costoPerdida) {
      var data =  costoPerdida.length > 0? []: [0];
      var categories = costoPerdida.length > 0 ? [] : ['0'];
      var totalCosto = 0

      for (const documento in costoPerdida) {
        var gasto = parseFloat(costoPerdida[documento].valor.replace('$', ''))
        if (gasto <= 0) {
          continue
        }
        data.push(gasto)
        categories.push(''+ documento * 1 + 1 +'')
        totalCosto += gasto
      }

      this.totalPerdidaForestal = totalCosto ? '%' + (new Intl.NumberFormat('es-ES').format(totalCosto)) : 'No hay perdida'
      var informe = {
        tipo:   'bar',
        ref:    'barchartValPerdidaForestal',
        titulo: '$ Valor perdida plantación forestal',
        total:  totalCosto ? '$' + (new Intl.NumberFormat('es-ES').format(totalCosto)) : 'No hay perdida',
        series: [{data: data}],
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
    },
    perdidaEstimadaProduccion (porcePerdidaEstimada) {
      var data =  porcePerdidaEstimada.length > 0? []: [0];
      var categories = porcePerdidaEstimada.length > 0 ? [] : ['0'];
      var totalCosto = 0

      for (const documento in porcePerdidaEstimada) {
        var gasto = parseFloat(porcePerdidaEstimada[documento].valor.replace('$', ''))
        if (gasto <= 0) {
          continue
        }
        data.push(gasto)
        categories.push(''+ documento*1+1 +'')
        totalCosto += gasto
      }

      var informe = {
        tipo:   'bar',
        ref:    'barchartPorcePerdidaEsti',
        titulo: '% Perdida estimada',
        total:  totalCosto > 0 ? '%' + (new Intl.NumberFormat('es-ES').format(totalCosto)) : 'No hay perdida',
        series: [{data: data}],
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

    }
  }
}
</script>
<style scoped>
  .card-chart {
    border: 1px solid rgb(206, 206, 206) !important;
    border-radius: 10px !important;
  }
</style>
