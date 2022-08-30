<template>
  <div>
    <v-container>
    <v-row>
      <v-col
        cols="12"
        md="6"
        sm="12"
      >
        <v-autocomplete
          label="Departamento"
          hint="Departamento"
          :items="departamentos"
          v-model="filtro.departamento"
          :search-input.sync="filtro.nameDepartamento"
          clearable
          item-text="nombre"
          item-value="id"
          dense
          outlined
          solo
          flat
        >
        </v-autocomplete>
      </v-col>
      <v-col
        cols="12"
        md="6"
        sm="12"
      >
        <v-autocomplete
          label="Cultivos"
          hint="Cultivos"
          :items="cultivos"
          v-model="filtro.cultivo"
          :search-input.sync="filtro.nameCultivo"
          clearable
          item-text="tipocultivo"
          item-value="codcultivo"
          dense
          outlined
          solo
          flat
        >
        </v-autocomplete>
      </v-col>
      <v-col
        cols="12"
        md="6"
        sm="12"
      >
        <v-autocomplete
          label="Variables"
          hint="Variables"
          :items="variables"
          v-model="filtro.variables"
          :search-input.sync="filtro.nameVariables"
          clearable
          item-text="variable_actividad"
          item-value="id_variable_actividad"
          dense
          outlined
          solo
          flat
        >
        </v-autocomplete>
      </v-col>
      <v-col
        cols="12"
        md="2"
        sm="12"
        black
      >
        <v-btn
          class="background-primary-dark button-basic"
          elevation="2"
          raised
          block
          depressed
          title="Buscar gastos"
          @click="getGastos()"
        >
          Buscar gastos
        </v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col
        cols="12"
        md="12"
        sm="12"
      >
        <v-data-table
           :headers="headersGastos"
           :items="listadoGastos"
           item-key="nombre"
           class="elevation-2"
           :loading="loadingTable"
           no-data-text="No hay datos."
         >
           <template v-slot:top>
              <v-toolbar
                flat
                class="border-head-table font-weight-bold"
                height="10px"
                style="background-color:#F2F2F2"
              >
              </v-toolbar>
              <v-dialog
                v-model="dialogEdicion"
                max-width="500px"
              >
                <v-card>
                  <v-card-title>
                    <span class="text-h5">Editar {{ editedItem.actividad }}</span>
                  </v-card-title>

                  <v-card-text>
                    <v-container>
                      <v-row>
                        <v-col
                          cols="12"
                          sm="12"
                          md="12"
                        >
                          <v-text-field
                            label="Cantidad"
                            hint="Cantidad"
                            v-model="editedItem.cantidad"
                            type="number"
                            dense
                            outlined
                            solo
                            flat
                            :onkeypress="regexNumber"
                          ></v-text-field>
                        </v-col>
                        <v-col
                          cols="12"
                          sm="12"
                          md="12"
                        >
                          <v-text-field
                            label="Costo"
                            hint="Costo"
                            v-model="editedItem.costo"
                            dense
                            outlined
                            solo
                            flat
                            append-icon="mdi-currency-usd"
                            :onkeypress="regexNumber"
                            @blur="formatCurrency('editedItem','costo')"
                          ></v-text-field>
                        </v-col>
                        <v-col
                          cols="12"
                          sm="12"
                          md="12"
                        >
                          <v-text-field
                            label="Valor unitario"
                            hint="Valor unitario"
                            v-model="editedItem.valor_unitario"
                            dense
                            outlined
                            solo
                            flat
                            append-icon="mdi-currency-usd"
                            onkeypress="regexNumber"
                            @blur="formatCurrency('editedItem','valor_unitario')"
                          ></v-text-field>
                        </v-col>
                      </v-row>
                    </v-container>
                  </v-card-text>

                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn
                      class="background-primary-dark button-basic"
                      text
                      @click="dialogEdicion = false"
                    >
                      Cerrar
                    </v-btn>
                    <v-btn
                      class="background-primary-dark button-basic"
                      text
                     :loading="loadingEditar"
                     :disabled="loadingEditar"
                      @click="guardar"
                    >
                      Guardar
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
           </template>
           <template v-slot:item.actions="{ item }">
             <v-icon
               small
               @click="editarGasto(item)"
               color="#004884"
             >
             mdi-pencil
             </v-icon>
           </template>
        </v-data-table>
      </v-col>
    </v-row>
    </v-container>
  </div>
</template>
<script>

import { getData } from '../../indexedDb/getData';
import { configuracionGastos } from '../../services/api';
import gastosAgricolasVue from '../../views/gastosAgricolas.vue';

export default {
  name: "configuracionGatos",
  data() {
    return {
      dialogEdicion: false,
      loadingTable: false,
      loadingEditar: false,
      filtro: {},
      departamentos: [],
      cultivos: [],
      variables: [],
      editedIndex: -1,
      editedItem: {
        cantidad: 0,
        costo: 0,
        valor_unitario: 0,
      },
      headersGastos: [
        { text: 'Cantidad', align: 'start', sortable: false, value: 'cantidad' },
        { text: 'Costo', align: 'start', sortable: false, value: 'costo' },
        { text: 'Valor unitario', align: 'start', sortable: false, value: 'valor_unitario' },
        { text: 'Acciones', value: 'actions', sortable: false, align: 'center'},
      ],
      listadoGastos: [],

      regexNumber: "return (event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46)",
      required: [v => !!v || 'Campo requerido',],
    }
  },
  async mounted() {
    await this.getData();
  },
  methods: {
    async getData() {

      try {
        const derpartamento = await getData('mapa', true);
        const cultivo = await getData('agricola', true);
        const res = await configuracionGastos.getAgroCalcAct();

        if (res.status === 200) {

          const data = res.data.message;
          this.variables = data;

          for (const itemDepa in derpartamento.departamentos) {
            var addDepartamento = {
              id: derpartamento.departamentos[itemDepa][0],
              nombre: derpartamento.departamentos[itemDepa][1]
            }
            this.departamentos.push(addDepartamento)
          }

          this.cultivos = cultivo.cropType;

        } else {
          this.$swal({
            icon: 'error',
            text: res.data.message,
            confirmButtonText: 'Aceptar',
          });
        }
      } catch(error) {
        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar',
        });
      }
    },
    async getGastos() {

      if ( !this.filtro.departamento || !this.filtro.cultivo){
        this.$swal({
          icon: 'error',
          text: 'Debe seleccionar el departamento y el cultivo',
          confirmButtonText: 'Aceptar',
        });
        return;
      }

      this.loadingTable = true;

      try {

        const parametros = {
          "dpto":     this.filtro.departamento,
          "especie":  this.filtro.cultivo,
          "variable": this.filtro.variables
        };
        const res = await configuracionGastos.postAgroCal(parametros);

        if (res.status === 200) {
          const data = res.data.message;
          this.listadoGastos = data;
          this.loadingTable = false;
        } else {
          this.loadingTable = false;
          this.$swal({
            icon: 'error',
            text: res.data.message,
            confirmButtonText: 'Aceptar'
          });
        }
      } catch(error) {
        this.loadingTable = false;
        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar'
        });
      }
    },
    async editarGasto(item) {
      this.editedIndex = this.listadoGastos.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialogEdicion = true;
    },
    async guardar() {
      this.loadingEditar = true;

      try {
        const parametros = {
          "dpto": this.filtro.departamento,
          "especie": this.filtro.cultivo,
          "variable": this.filtro.variables,
          "cantidad": this.editedItem.cantidad,
          "unitario": this.editedItem.valor_unitario,
          "costo": this.editedItem.costo
        };
        const res = await configuracionGastos.putAgroCal(parametros);

        if (res.status === 200) {
          this.$swal({
            icon: 'success',
            text: 'Datos actualizados',
            confirmButtonText: 'Aceptar'
          });
          this.loadingEditar = false;
          if (this.editedIndex > -1) {
            Object.assign(this.listadoGastos[this.editedIndex], this.editedItem);
          }
          this.dialogEdicion = false;
        }else {
          this.loadingEditar = false;
          this.$swal({
            icon: 'error',
            text: res.data.message,
            confirmButtonText: 'Aceptar'
          });
        }

      } catch(error) {
        this.loadingEditar = false;
        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar'
        });
      }
    },
    formatCurrency(obj, campo) {
      if (!this[obj][campo]) {
        return;
      }
      this[obj][campo]  = this[obj][campo].toString();
      this[obj][campo]  = parseFloat(this[obj][campo].replace(/[^\d\.]/g, ""));
      this[obj][campo]  = this.$options.filters.currency(this[obj][campo])
    },
  },
}
</script>
