<template>
  <div>

    <v-container>

      <v-row dense>
        <v-col
          cols="12"
        >
          <v-data-table
            :headers="especiesHeader"
            :items="itemsEspecieAgregada"
            class="elevation-2"
          >
            <template v-slot:top>
              <v-toolbar
                flat
                class="background-primary-dropdowns border-head-table font-weight-bold"
              >
                <span class="mr-2">Sistema apícola</span>

                <v-btn
                  class="background-primary-dark"
                  outlined
                  elevation="2"
                  fab
                  dark
                  small
                  @click="dialogApicola = true"
                >
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </v-toolbar>
            </template>
            <template v-slot:item.actions="{ item }">
              <v-icon
                small
                color="#004884"
                @click="editarSistemaApoicola(item)"
              >
              mdi-pencil
              </v-icon>
              <v-icon
                small
                color="#004884"
                @click="eliminarSistemaApicola(item)"
              >
              mdi-delete
              </v-icon>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>

    <v-dialog
      v-model="dialogApicola"
      persistent :overlay="false"
      max-width="100%"
      transition="dialog-transition"
    >

      <v-card
        class="border-basic"
        flat
      >

        <div style="text-align:right">
          <v-btn class="color-primary-dark" icon dark @click="cerrarModal">
            <v-icon>mdi-close-circle</v-icon>
          </v-btn>
        </div>

        <v-card-title
          primary-title
        >
          <v-container class="color-primary-dark font-weight-bold">
            <v-row
              dense
              class="align-center justify-center container-titles"
              style="height:80px"
            >
            <v-col
              cols="12"
              md="12"
              sm="12"
              >
              <center>Sistema apícola</center>
              </v-col>
            </v-row>
          </v-container>
        </v-card-title>

        <v-card-text>
          <v-container>

            <v-form
              lazy-validation
              ref="formSectionOne"
              v-model="validSectionOne"
            >
              <v-row dense class="section mt-3">
                <v-col
                  class="color-black font-weight-bold mt-3"
                  cols="12"
                  md="12"
                  sm="12"
                >
                  <p> Explotación apícola </p>
                </v-col>
                <v-col
                  cols="12"
                  md="4"
                  sm="6"
                >
                  <v-text-field
                    label="Indique el número de colmenas afectadas"
                    hint="Indique el número de colmenas afectadas"
                    v-model.number="dataApicola.numColmenas"
                    type="number"
                    dense
                    outlined
                    solo
                    flat
                    :onkeypress="rules.regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    rules.required
                    :rules="rules.required"
                  ></v-text-field>
                </v-col>
                <v-col
                  cols="12"
                  md="4"
                  sm="6"
                >
                  <v-text-field
                    label="Valor comercial promedio de cada colmena"
                    hint="Valor comercial promedio de cada colmena"
                    v-model="dataApicola.valorColmena"
                    dense
                    outlined
                    solo
                    flat
                    prepend-inner-icon="mdi-currency-usd"
                    @blur="formatCurrency('dataApicola','valorColmena')"
                    :onkeypress="rules.regexNumber"
                  ></v-text-field>
                </v-col>
                <v-col
                  cols="12"
                  md="4"
                  sm="6"
                >
                  <v-text-field
                    label="Indique la producción mensual de propoleo"
                    hint="Producciónen  en kilos antes de la afectación"
                    v-model.number="dataApicola.propoleoMensual"
                    type="number"
                    dense
                    outlined
                    solo
                    flat
                    :onkeypress="rules.regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    rules.required
                    :rules="rules.required"
                  ></v-text-field>
                </v-col>
                <v-col
                  cols="12"
                  md="4"
                  sm="6"
                >
                  <v-text-field
                    label="Indique la producción mensual estimada de miel"
                    hint="Indique la producción mensual estimada de miel"
                    v-model.number="dataApicola.mielMensual"
                    type="number"
                    dense
                    outlined
                    solo
                    flat
                    :onkeypress="rules.regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    rules.required
                    :rules="rules.required"
                  ></v-text-field>
                </v-col>
                <v-col
                  cols="12"
                  md="4"
                  sm="6"
                >
                  <v-text-field
                    label="Indique la producción mensual de jalea real"
                    hint="Indique la producción mensual de jalea real"
                    v-model.number="dataApicola.jaleaMensual"
                    type="number"
                    dense
                    outlined
                    solo
                    flat
                    :onkeypress="rules.regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    rules.required
                    :rules="rules.required"
                  ></v-text-field>
                </v-col>
                <v-col
                  cols="12"
                  md="4"
                  sm="6"
                >
                  <v-text-field
                    label="Valor promedio mensual antes de la afectación"
                    hint="Valor promedio mensual antes de la afectación"
                    v-model="dataApicola.valorMensual"
                    dense
                    outlined
                    solo
                    flat
                    prepend-inner-icon="mdi-currency-usd"
                    @blur="formatCurrency('dataApicola','valorMensual')"
                    :onkeypress="rules.regexNumber"
                  ></v-text-field>
                </v-col>
                <v-col
                  cols="12"
                  md="4"
                  sm="6"
                >
                  <v-text-field
                    label="¿Cuál es su ingreso mensual actualmente?"
                    hint="¿Cuál es su ingreso mensual actualmente?"
                    v-model="dataApicola.ingresoMensual"
                    dense
                    outlined
                    solo
                    flat
                    prepend-inner-icon="mdi-currency-usd"
                    @blur="formatCurrency('dataApicola','ingresoMensual')"
                    :onkeypress="rules.regexNumber"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-form>

            <v-row dense class="section mt-5">
              <v-switch
                class="ml-2"
                cols="12"
                md="12"
                sm="12"
                v-model="dataApicola.afectacion"
                inset
                label="¿Existió afectación en insumos, equipos, maquinaria y herramientas?"
              ></v-switch>
            </v-row>

            <v-col
              cols="12"
              md="12"
              sm="12"
            ></v-col>

            <v-form
              v-if="verCamposSegunTipoInsumo"
              lazy-validation
              ref="formInsumos"
              v-model="validInsumos"
            >
              <v-row
                dense
                class="container-titles mt-5"
              >
                <v-col
                  cols="12"
                  md="12"
                  sm="12"
                  align="center"
                  justify="center"
                  class="mt-3 font-16"
                >
                  <p class="color-black font-weight-bold">Insumos, equipos, maquinaria y herramientas pecuarias</p>
                </v-col>
              </v-row>

              <v-row dense class="section mt-3">
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Insumos, forrajes, alimento para los animales y piensos</p>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="6"
                  >
                    <v-autocomplete
                      v-model="insumos.tipoInsumo"
                      :items="tipoInsumo"
                      item-text="tipinsumo"
                      item-value="codinsumo"
                      :search-input.sync="insumos.nameTipoInsumo"
                      dense
                      outlined
                      solo
                      flat
                      clearable
                      label="Tipo de insumo, forraje, alimento para los animales y piensos"
                      hint="Tipo de insumo, forraje, alimento para los animales y piensos"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    v-if="verNuevoTipoInsumo"
                    cols="12"
                    md="4"
                    sm="6"
                  >
                    <v-text-field
                      label="Indique el otro insumo"
                      hint="Indique el otro insumo"
                      v-model="insumos.nuevoInsumo"
                      dense
                      outlined
                      solo
                      flat
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="6"
                  >
                    <v-text-field
                      label="Nombre comercial"
                      hint="Nombre comercial"
                      v-model="insumos.nombreComercial"
                      dense
                      outlined
                      solo
                      flat
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="6"
                  >
                    <v-text-field
                      label="Cantidad de insumos, forrajes, alimento para los animales y piensos"
                      hint="Cantidad de insumos, forrajes, alimento para los animales y piensos"
                      v-model.number="insumos.cantInsumo"
                      dense
                      outlined
                      solo
                      flat
                      type="number"
                      :onkeypress="rules.regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="6"
                  >
                    <v-autocomplete
                      v-model="insumos.unidadMedida"
                      :items="unidadProduccion"
                      item-text="undcosecha"
                      item-value="codundcosecha"
                      :search-input.sync="insumos.nameUnidadMedida"
                      dense
                      outlined
                      solo
                      flat
                      clearable
                      label="Unidad de medida"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="6"
                  >
                    <v-text-field
                      label="Valor en pesos de la afectación"
                      hint="Indique el valor de reposición de los bienes"
                      v-model="insumos.valorBienes"
                      dense
                      outlined
                      solo
                      flat
                      prepend-inner-icon="mdi-decagram"
                      append-icon="mdi-currency-usd"
                      :onkeypress="rules.regexNumber"
                      rules.required
                      :rules="rules.required"
                      @blur="formatCurrency('insumos','valorBienes')"
                    ></v-text-field>
                  </v-col>
              </v-row>

              <v-row dense class="section mt-3">
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
                  >
                    <v-btn
                    class="background-primary-dark button-basic"
                    elevation="2"
                    block
                    raised
                    depressed
                    @click="guardarInsumo"
                    >Agregar insumo</v-btn>
                  </v-col>
                  <v-col
                    cols="12"
                  >
                    <v-data-table
                      :headers="insumosHeader"
                      :items="itemsInsumos"
                      class="elevation-1"
                    >
                      <template v-slot:top>
                        <v-toolbar
                          flat
                          class="border-head-table font-weight-bold"
                          height="10px"
                          style="background-color:#F2F2F2"
                        ></v-toolbar>
                      </template>
                      <template v-slot:item.actions="{ item }">
                        <v-icon
                          small
                          @click="eliminarInsumo(item)"
                        >
                        mdi-delete
                        </v-icon>
                      </template>
                    </v-data-table>
                  </v-col>
              </v-row>
            </v-form>

            <v-form
              v-if="verCamposSegunTipoInsumo"
              lazy-validation
              ref="formMaquinaria"
              v-model="validMaquinaria"
            >
              <v-row dense class="section mt-3">
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Instalaciones y maquinaria para la producción de especies menores</p>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="6"
                  >
                    <v-autocomplete
                      v-model="afectacionInsumo.tipoMaquinariaPem"
                      :items="tipoMaquinarias"
                      item-text="tipmaquinaria"
                      item-value="codtipmaquinaria"
                      :search-input.sync="afectacionInsumo.nameTipoMaquinariaPem"
                      dense
                      outlined
                      solo
                      flat
                      label="Tipo de maquinaria"
                      hint="Tipo de maquinaria"
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      clearable
                      :rules="rules.required"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="6"
                  >
                    <v-text-field
                      label="Nombre o marca del bien"
                      hint=""
                      v-model="afectacionInsumo.nombreMarcaPem"
                      dense
                      outlined
                      solo
                      flat
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="6"
                  >
                    <v-text-field
                      label="Valor en pesos de la afectación"
                      hint="Indique el valor incurrido en reparar o reponer el bien"
                      v-model="afectacionInsumo.valorReparacionPem"
                      dense
                      outlined
                      solo
                      flat
                      prepend-inner-icon="mdi-decagram"
                      append-icon="mdi-currency-usd"
                      :onkeypress="rules.regexNumber"
                      rules.required
                      :rules="rules.required"
                      @blur="formatCurrency('afectacionInsumo','valorReparacionPem')"
                    ></v-text-field>
                  </v-col>
              </v-row>

              <v-row dense class="section mt-3">
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
                  >
                    <v-btn
                    class="background-primary-dark button-basic"
                    elevation="2"
                    block
                    raised
                    depressed
                    @click="guardarTipoMaquinaria"
                    >Agregar afectación</v-btn>
                  </v-col>
                  <v-col
                    cols="12"
                  >
                    <v-data-table
                      :headers="maquinariaHeader"
                      :items="itemsMaquinaria"
                      class="elevation-1"
                    >
                      <template v-slot:top>
                        <v-toolbar
                          flat
                          class="border-head-table font-weight-bold"
                          height="10px"
                          style="background-color:#F2F2F2"
                        ></v-toolbar>
                      </template>
                      <template v-slot:item.actions="{ item }">
                        <v-icon
                          small
                          @click="eliminarMaquinaria(item)"
                        >
                        mdi-delete
                        </v-icon>
                      </template>
                    </v-data-table>
                  </v-col>
              </v-row>
            </v-form>

            <v-row class="mt-5">
              <v-col
                cols="12"
                md="9"
                sm="12"
              ></v-col>
              <v-col
                cols="12"
                md="3"
                sm="12"
              >
                <v-btn
                class="success button-basic"
                elevation="2"
                block
                raised
                depressed
                @click="guardarSistema"
                >Guardar sistema</v-btn>
              </v-col>
            </v-row>

          </v-container>
        </v-card-text>
      </v-card>
    </v-dialog>

  </div>
</template>

<script>

import { getData } from '../../indexedDb/getData';

export default {
  name: 'apicola',
  props: ['obtenerDataApicola'],
  data() {
    return {
      dialogApicola: false,
      validSectionOne: true,
      validMaquinaria: true,
      validInsumos: true,

      tipoInsumo: [],
      tipoMaquinarias: [],
      unidadProduccion: [],
      editedIndex: -1,

      especiesHeader: [
        { text: 'No.Colmenas', align: 'start', sortable: false, value: 'numColmenas'},
        { text: 'Val.Colmenas', align: 'start', sortable: false, value: 'valorColmena'},
        { text: 'Propoleo mensual', align: 'start', sortable: false, value: 'propoleoMensual'},
        { text: 'Miel mensual', align: 'start', sortable: false, value: 'mielMensual'},
        { text: 'Jalea mensual', align: 'start', sortable: false, value: 'jaleaMensual'},
        { text: 'Val.Antes de afectación', align: 'start', sortable: false, value: 'valorMensual'},
        { text: 'Ingresos mensuales', align: 'start', sortable: false, value: 'ingresoMensual'},
        { text: 'Existio afectación', align: 'start', sortable: false, value: 'afectacion'},
        { text: 'Acciones', value: 'actions', sortable: false, width: '2%' },
      ],
      itemsEspecieAgregada: [],
      insumosHeader: [
        { text: 'Tipo insumo', align: 'start', sortable: false, value: 'nameTipoInsumo' },
        { text: 'Cant. insumo', align: 'start', sortable: false, value: 'cantInsumo' },
        { text: 'Nombre comercial', align: 'start', sortable: false, value: 'nombreComercial' },
        { text: 'Unidad medida', align: 'start', sortable: false, value: 'nameUnidadMedida' },
        { text: 'Valor', align: 'start', sortable: false, value: 'valorBienes' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      itemsInsumos: [],
      maquinariaHeader: [
        { text: 'Maquinaria', align: 'start', sortable: false, value: 'nameTipoMaquinariaPem' },
        { text: 'Nombre', align: 'start', sortable: false, value: 'nombreMarcaPem' },
        { text: 'valor', align: 'start', sortable: false, value: 'valorReparacionPem' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      itemsMaquinaria: [],

      dataApicola: {},
      insumos: {},
      afectacionInsumo: {},

      rules: {
        required: [v => !!v || 'Campo requerido'],
        regexNumber: "return (event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46)",
      },
    }
  },
  async mounted() {
    await this.getDataApicola();
    await this.edicionApicola();
  },
  methods: {
    async getDataApicola() {
      try {
        const res = await getData('pecuario', true);
        this.addDataCampos(res);

      } catch (error) {

        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar',
        });
      }
    },
    edicionApicola() {
      const dataEvento = this.$route.params.evento;
      if (dataEvento !== undefined) {
        if (dataEvento.dataEspecies.infoApicola.length > 0) {
          this.itemsEspecieAgregada = dataEvento.dataEspecies.infoApicola;
        }
      }
    },
    addDataCampos(data) {
      this.tipoInsumo = data.inputType;
      this.unidadProduccion = data.unity;
      this.tipoMaquinarias = data.machineryTypePEM;
    },
    cerrarModal() {
      this.limpiarCampos();
    },
    limpiarCampos() {
      this.dataApicola = {};
      this.itemsInsumos = [];
      this.itemsMaquinaria = [];
      this.editedIndex = -1;
      this.dialogApicola = false;
    },
    eliminarInsumo(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar insumo?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          const editedIndex = this.itemsInsumos.indexOf(item);
          this.itemsInsumos.splice(editedIndex, 1);
        }
      })
    },
    guardarInsumo() {
      if (this.$refs.formInsumos.validate()) {
        this.itemsInsumos.push(this.insumos);
        this.insumos = {};
      }
    },
    eliminarMaquinaria(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar maquinaria?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          const editedIndex = this.itemsMaquinaria.indexOf(item);
          this.itemsMaquinaria.splice(editedIndex, 1);
        }
      })
    },
    guardarTipoMaquinaria() {
      if (this.$refs.formMaquinaria.validate()) {
        this.itemsMaquinaria.push(this.afectacionInsumo);
        this.afectacionInsumo = {};
      }
    },
    editarSistemaApoicola(item) {
      console.log(item);
      this.editedIndex = this.itemsEspecieAgregada.indexOf(item);
      this.itemsInsumos = item.insumos;
      this.itemsMaquinaria = item.maquinarias;
      this.dataApicola = Object.assign({}, item);
       console.log(item);
      this.dialogApicola = true;
    },
    eliminarSistemaApicola(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar sistema apícola?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          const editedIndex = this.itemsEspecieAgregada.indexOf(item);
          this.itemsEspecieAgregada.splice(editedIndex, 1);
          this.obtenerDataApicola(this.itemsEspecieAgregada);
        }
      })
    },
    guardarSistema() {
      if (this.$refs.formSectionOne.validate()) {

        if (this.dataApicola.afectacion) {
          if (this.itemsMaquinaria.length === 0 || this.itemsInsumos.length === 0) {
            this.$swal({
              icon: 'error',
              text: 'No se han registrado Insumos, equipos, maquinaria y herramientas pecuarias.',
              confirmButtonText: 'Aceptar',
            });
            return;
          }
        }

        this.dataApicola.insumos = this.itemsInsumos;
        this.dataApicola.maquinarias = this.itemsMaquinaria;

        if (this.editedIndex > -1) {
          Object.assign(this.itemsEspecieAgregada[this.editedIndex], this.dataApicola)
        } else {
          this.itemsEspecieAgregada.push(this.dataApicola);
        }

        this.obtenerDataApicola(this.itemsEspecieAgregada);
        this.limpiarCampos();
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
  computed: {
    verCamposSegunTipoInsumo() {
      var estado = this.dataApicola.afectacion;
      if (!estado) {
        this.afectacionInsumo = {};
        this.itemsMaquinaria  = [];
        this.itemsInsumos = [];
      }

      return estado;
    },
    verNuevoTipoInsumo() {
      var estado     = false;
      var tipoInsumo = this.afectacionInsumo.tipoInsumo;
      var afectacion = this.dataApicola.afectacion;

      if (tipoInsumo === 6 && tipoInsumo && afectacion) {
        estado = true;
      } else {
        this.afectacionInsumo.nuevoInsumo = '';
      }

      return estado;
    },
  }
}
</script>
