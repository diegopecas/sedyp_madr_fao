<template>

    <v-expansion-panels
      v-model="panel"
      class="border-basic"
    >

    <v-expansion-panel class="border-basic">

      <v-expansion-panel-header>
          <v-list>
            <v-list-item>
              <v-list-item-action>
                <v-icon>mdi-filter-variant</v-icon>
              </v-list-item-action>
              <v-list-item-content>
                <v-list-item-title>Filtros</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-divider inset></v-divider>
          </v-list>
        </v-expansion-panel-header>

        <v-expansion-panel-content>
          <v-row
            class="ma-0"
          >
            <v-col
              cols="12"
              md="12"
              sm="12"
            >
              <v-combobox
                v-model="chips"
                :items="items"
                chips
                small-chips
                block
                label="Campos"
                multiple
                outlined
                dense
                :open-on-clear="true"
              >
                <template v-slot:selection="{ attrs, item, select, selected }">
                  <v-chip
                    v-bind="attrs"
                    :input-value="selected"
                    close
                    color="#004884"
                    @click="select"
                    @click:close="remove(item)"
                  >
                    <strong>{{ item }}</strong>
                  </v-chip>
                </template>
              </v-combobox>
            </v-col>
            <v-menu
              v-model="menuFechaInicio"
              :close-on-content-click="false"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              min-width="auto"
              >
              <template v-slot:activator="{ on, attrs }">

                <v-col
                  cols="12"
                  md="5"
                  sm="12"
                  >
                  <v-text-field
                    v-model="fechaInicio"
                    label="Fecha inicio"
                    hint="Fecha inicio"
                    readonly
                    v-bind="attrs"
                    v-on="on"
                    dense
                    solo
                    flat
                    outlined
                    filled
                  ></v-text-field>
                </v-col>

              </template>
              <v-col
                cols="12"
                md="5"
                sm="12"
                >
                <v-date-picker
                    v-model="fechaInicio"
                    @input="menuFechaInicio = false"
                    outlined
                ></v-date-picker>
              </v-col>
            </v-menu>
            <v-menu
              v-model="menuFechaFin"
              :close-on-content-click="false"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              min-width="auto"
              >
              <template v-slot:activator="{ on, attrs }">

                <v-col
                  cols="12"
                  md="5"
                  sm="12"
                  >
                  <v-text-field
                    v-model="fechaFin"
                    label="Fecha fin"
                    hint="Fecha fin"
                    readonly
                    v-bind="attrs"
                    v-on="on"
                    dense
                    solo
                    flat
                    outlined
                    filled
                  ></v-text-field>
                </v-col>

              </template>
              <v-col
                cols="12"
                md="5"
                sm="12"
                >
                <v-date-picker
                    v-model="fechaFin"
                    @input="menuFechaFin = false"
                    outlined
                ></v-date-picker>
              </v-col>
            </v-menu>
            <v-col
              cols="12"
              md="2"
              sm="12"
            >
              <v-btn-toggle
                class="button-basic"
                dense
              >
                <v-btn
                  @click="filtrar()"
                  class="background-primary-dark"
                  title="Filtrar"
                >
                  <v-icon color="white">mdi-filter-menu</v-icon>
                </v-btn>
                <v-btn
                  @click="limpiarFiltro"
                  class="background-primary-dark"
                  title="Limpiar"
                >
                  <v-icon color="white">mdi-filter-remove</v-icon>
                </v-btn>
              </v-btn-toggle>
            </v-col>

          </v-row>

          <v-progress-linear
            class="ml-2"
            style="border-radius:0 0 20px 20px; width: 99%;"
            :active="loading"
            :indeterminate="loading"
            absolute
            bottom
            color="primary"
            rounded
          ></v-progress-linear>

        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>

</template>
<script>

export default {
  name: 'filtros',
  props: ['listChips', 'datos', 'dataFiltrada', 'campoFechaFiltro'],
  data() {
    return {
      loading: false,
      panel: [0],
      chips: [],
      dataParcial: [],
      dataCompleta: [],
      eliminar: false,
      fechaInicio: '',
      menuFechaInicio: false,
      fechaFin: '',
      menuFechaFin: false,
    }
  },
  methods: {
    remove (item) {
      this.eliminar = true;
      this.chips.splice(this.chips.indexOf(item), 1);
      this.chips = [...this.chips];
      this.filtrar();
    },
    filtrar() {

      this.loading = true;
      var cadena = [];
      var igual = true;

      if (this.dataCompleta.length === 0) {
        this.dataCompleta = this.datos;
      }
      this.dataParcial = this.dataCompleta;

      if (this.fechaInicio || this.fechaFin) {
        this.filtrarFechas();
      }

      for (const chip in this.chips) {
        cadena = this.chips[chip].split(' Igual ');
        igual = true;
        if (cadena.length === 1) {
          cadena = this.chips[chip].split(' Diferente ');
          igual = false;
        }

        let campo = this.listChips.filter(item=>item['nombreFiltro'] === cadena[0]);

        if (campo.length === 0) {
          continue;
        }

        if (!igual) {
          this.dataParcial = this.dataParcial.filter(item => {
              if (!item[campo[0].valor]) {
                return false;
              }
              return item[campo[0].valor].toString().toLowerCase() !== cadena[1].toString().toLowerCase();
          })
        } else {
          this.dataParcial = this.dataParcial.filter(item => {
              if (!item[campo[0].valor]) {
                return false;
              }
              return item[campo[0].valor].toString().toLowerCase() === cadena[1].toString().toLowerCase();
          })
        }
      }

      this.loading = false;
      this.dataFiltrada(this.dataParcial);
    },
    filtrarFechas() {
      if ((this.fechaInicio && !this.fechaFin) || (!this.fechaInicio && this.fechaFin)) {
        this.$swal({
          icon: 'error',
          text: 'No se ha registrado la fecha inicio o fin, para aplicar el filtro.',
          confirmButtonText: 'Aceptar',
        });
      }
      if (Date.parse(this.fechaFin) < Date.parse(this.fechaInicio)) {
        this.$swal({
          icon: 'error',
          text: 'La fecha de inicio no puede ser mayor a la fecha fin..',
          confirmButtonText: 'Aceptar',
        });
      }
      this.dataParcial = this.dataParcial.filter(item => {
        return item[this.campoFechaFiltro] >= this.fechaInicio && item[this.campoFechaFiltro] <= this.fechaFin;
      })
    },
    limpiarFiltro() {
      this.chips = [];
      this.fechaInicio = '';
      this.fechaFin = '';
      if (this.dataCompleta.length > 0) {
        this.filtrar();
      }
    }
  },
  computed: {
    items() {
      var list  = [];
      const campos = this.listChips.map((item) => item['nombreFiltro']);

      if (this.chips.length === 0) {
        list = campos;
      } else {
        const dataActual = campos.filter(item=>item === this.chips[this.chips.length - 1]);

        if (dataActual.length > 0) {
          list.push('Igual');
          list.push('Diferente');
        } else {
          if (
            this.chips[this.chips.length - 1] != 'Igual'
            && this.chips[this.chips.length - 1] != 'Diferente'
            && !this.eliminar
          ) {

            var nuevo = this.chips[this.chips.length - 3] + ' ' + this.chips[this.chips.length - 2] + ' ' + this.chips[this.chips.length - 1];
            this.chips.length = this.chips.length - 3;

            this.chips.push(nuevo);
            list = campos;

          }
        }
      }

      if (this.eliminar) {
        if (list.length === 0) {
          list = campos;
        }
        this.eliminar = false;
      }

      return list;
    },
  },
}
</script>
