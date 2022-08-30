<template>
  <div>
    <v-container>
      <v-row>

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
                <span class="mr-2">Sistema pecuario/acuicola</span>

                <v-btn
                  class="background-primary-dark"
                  outlined
                  elevation="2"
                  fab
                  dark
                  small
                  @click="dialogPecuario = true"
                >
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </v-toolbar>
            </template>
            <template v-slot:item.actions="{ item }">
              <v-icon
                small
                color="#004884"
                @click="editarSistemaPecuario(item)"
              >
              mdi-pencil
              </v-icon>
              <v-icon
                small
                color="#004884"
                @click="eliminarSistemaPecuario(item)"
              >
              mdi-delete
              </v-icon>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>

    <v-dialog
      v-model="dialogPecuario"
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
              <center>Sistema pecuario y acuicola</center>
              </v-col>
            </v-row>
          </v-container>
        </v-card-title>

        <v-card-text>
          <v-container grid-list-xs>
            <v-form
              lazy-validation
              ref="form"
              v-model="valid"
            >
              <v-row dense class="section">
                <v-col
                  cols="12"
                  md="12"
                  sm="12"
                >
                  <p class="color-black font-weight-bold">Por favor, indique los datos relacionados al sistema pecuario afectado</p>
                </v-col>
                <v-col
                  cols="12"
                  md="4"
                  sm="12"
                >
                  <v-autocomplete
                    v-model="dataPecuarioAcuicola.sistema"
                    :items="sistemas"
                    item-text="sistemaafectado"
                    item-value="codsistemaafectado"
                    :search-input.sync="dataPecuarioAcuicola.nombreSistema"
                    dense
                    outlined
                    solo
                    flat
                    clearable
                    label="¿Cuál fue el sistema afectado?"
                    hint="¿Cuál fue el sistema afectado?"
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="required"
                    @change="limpiarTablasSegunSistema"
                  ></v-autocomplete>
                </v-col>
                <v-col
                  v-if="verOtroSistema"
                  cols="12"
                  md="4"
                  sm="12"
                >
                  <v-text-field
                    label="¿Si es otro cuál?"
                    hint="¿Si es otro cuál?"
                    v-model="dataPecuarioAcuicola.sistemaNuevo"
                    dense
                    outlined
                    solo
                    flat
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="required"
                  ></v-text-field>
                </v-col>
              </v-row>

              <v-container class="pa-0">
                <v-row dense class="section mt-3">
                  <v-col cols="12" class="color-black font-weight-bold">Datos de la especie</v-col>
                  <v-col
                  cols="12"
                  md="8"
                  sm="12"
                  >
                    <v-text-field
                      label="Nombre de la línea/raza"
                      hint="Nombre de la línea/raza"
                      v-model="dataPecuarioAcuicola.nombreRaza"
                      dense
                      outlined
                      solo
                      flat
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                  cols="12"
                  md="4"
                  sm="12"
                  >
                    <v-text-field
                      label="Total de animales en su explotación"
                      hint="Total de animales en su explotación"
                      v-model.number="dataPecuarioAcuicola.numAnimal"
                      type="number"
                      dense
                      outlined
                      solo
                      flat
                      :onkeypress="regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row dense class="section mt-3">
                    <v-col cols="12" class="color-black font-weight-bold">Pesos y medidas de la especie</v-col>
                    <v-col
                    cols="12"
                    md="4"
                    sm="12"
                    >
                      <v-text-field
                        label="Peso promedio del animal en su explotación"
                        hint="Peso promedio del animal en su explotación"
                        v-model.number="dataPecuarioAcuicola.pesoAnimal"
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
                      md="4"
                      sm="12"
                      >
                        <v-autocomplete
                          v-model="dataPecuarioAcuicola.uniMedidaAnimal"
                          :items="uniMedidaAnimales"
                          item-text="undcosecha"
                          item-value="codundcosecha"
                          dense
                          outlined
                          solo
                          flat
                          clearable
                          label="Unidad de medida para reportar la cantidad"
                          hint="Unidad de medida para reportar la cantidad"
                        ></v-autocomplete>
                      </v-col>
                      <v-col
                        v-if="verUnidadMedidaNuevo"
                        cols="12"
                        md="4"
                        sm="12"
                      >
                        <v-text-field
                          label="Nombre de la otra unidad de medida"
                          hint="Nombre de la otra unidad de medida"
                          v-model="dataPecuarioAcuicola.nombreUnidadMedidaNuevo"
                          dense
                          outlined
                          solo
                          flat
                        ></v-text-field>
                      </v-col>
                      <v-col
                        v-if="verUnidadMedidaNuevo"
                        cols="12"
                        md="4"
                        sm="12"
                      >
                        <v-text-field
                          label="Equivalencia en kilos de la otra unidad"
                          hint="Equivalencia en kilos de la otra unidad"
                          v-model="dataPecuarioAcuicola.unidadMedidaNuevo"
                          dense
                          outlined
                          solo
                          flat
                          prepend-inner-icon="mdi-decagram"
                          required
                          :rules="required"
                          :onkeypress="regexNumber"
                        ></v-text-field>
                      </v-col>

                    <v-col
                      v-if="verPeso"
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-autocomplete
                        v-model="dataPecuarioAcuicola.peso"
                        :items="peso"
                        item-text="eqvcargakg"
                        item-value="codequivcarga"
                        dense
                        outlined
                        solo
                        flat
                        clearable
                        label="Peso kilos"
                        hint="Peso kilos"
                      ></v-autocomplete>
                    </v-col>
                    <v-col
                      v-if="verPesoNuevo"
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="¿Si es otro cuál?"
                        hint="Equivalencia en kilos"
                        v-model="dataPecuarioAcuicola.pesoNuevo"
                        dense
                        outlined
                        solo
                        flat
                        prepend-inner-icon="mdi-decagram"
                        required
                        :rules="required"
                        :onkeypress="regexNumber"
                      ></v-text-field>
                    </v-col>
                </v-row>

                <v-row dense class="section mt-3">
                    <v-col cols="12" class="color-black font-weight-bold">Precio promedio pagado de la especie</v-col>
                    <v-col
                      cols="12"
                      md="4"
                      sm="12"
                    >
                    <v-text-field
                        label="Precio promedio pagado o el valor estimado"
                        hint="Precio pagado estimado por animal en pesos"
                        v-model="dataPecuarioAcuicola.valorAnimal"
                        dense
                        outlined
                        solo
                        flat
                        prepend-inner-icon="mdi-currency-usd"
                        :onkeypress="regexNumber"
                        @blur="formatCurrency('dataPecuarioAcuicola','valorAnimal')"
                      ></v-text-field>
                    </v-col>
                </v-row>

                <v-row dense class="section mt-3">
                    <v-col cols="12" class="color-black font-weight-bold">Área utilizada</v-col>
                    <v-col
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="Área que utiliza para la totalidad de animales"
                        hint="Área que utiliza para la totalidad de animales"
                        v-model="dataPecuarioAcuicola.areaAnimal"
                        dense
                        outlined
                        solo
                        flat
                        :onkeypress="regexNumber"
                      ></v-text-field>
                    </v-col>
                    <v-col
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-autocomplete
                        v-model="dataPecuarioAcuicola.unidadArea"
                        :items="unidadArea"
                        item-text="undarea"
                        item-value="codundarea"
                        dense
                        outlined
                        solo
                        flat
                        clearable
                        label="Indique la unidad área en que se realiza el reporte"
                        hint="Indique la unidad área en que se realiza el reporte"
                      ></v-autocomplete>
                    </v-col>
                    <v-col
                      v-if="verUnidadAreaNuevo"
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="¿Si es otro cuál?"
                        hint="¿Si es otro cuál?"
                        v-model="dataPecuarioAcuicola.unidadAreaNuevo"
                        dense
                        outlined
                        solo
                        flat
                        prepend-inner-icon="mdi-decagram"
                        required
                        :rules="required"
                      ></v-text-field>
                    </v-col>
                </v-row>

                <v-row dense class="section mt-3">
                    <v-col
                      cols="12"
                      md="12"
                      sm="12"
                      class="color-black font-weight-bold"
                    >
                      Fecha de inicio actividad productiva o inicio producción
                    </v-col>
                    <v-menu
                      v-model="dataPecuarioAcuicola.menuFechaProduccion"
                      :close-on-content-click="false"
                      :nudge-right="40"
                      transition="scale-transition"
                      offset-y
                      min-width="auto"
                    >
                      <template v-slot:activator="{ on, attrs }">

                        <v-col
                          cols="12"
                          md="4"
                          sm="12"
                        >
                          <v-text-field
                            v-model="dataPecuarioAcuicola.fechaProduccion"
                            label="Inicio actividad productiva o inicio producción"
                            hint="Inicio actividad productiva o inicio producción"
                            readonly
                            v-bind="attrs"
                            v-on="on"
                            dense
                            outlined
                            solo
                        flat
                          ></v-text-field>
                        </v-col>

                      </template>
                      <v-col
                        cols="12"
                        md="4"
                        sm="12"
                      >
                        <v-date-picker
                          v-model="dataPecuarioAcuicola.fechaProduccion"
                          @input="dataPecuarioAcuicola.menuFechaProduccion = false"
                          outlined
                          ></v-date-picker>
                      </v-col>
                    </v-menu>
                </v-row>

                <v-row dense class="section mt-3">
                    <v-col cols="12" class="color-black font-weight-bold">Exposición de la explotación al evento</v-col>
                      <v-menu
                        v-model="dataPecuarioAcuicola.menuFechaIniEvento"
                        :close-on-content-click="false"
                        :nudge-right="40"
                        transition="scale-transition"
                        offset-y
                        min-width="auto"
                      >
                      <template v-slot:activator="{ on, attrs }">

                        <v-col
                          cols="12"
                          md="4"
                          sm="12"
                        >
                          <v-text-field
                            v-model="dataPecuarioAcuicola.fechaIniEvento"
                            label="Fecha de inicio del evento"
                            hint="Fecha de inicio del evento"
                            readonly
                            v-bind="attrs"
                            v-on="on"
                            dense
                            outlined
                            solo
                        flat
                          ></v-text-field>
                        </v-col>

                      </template>
                      <v-col
                        cols="12"
                        md="4"
                        sm="12"
                      >
                        <v-date-picker
                          v-model="dataPecuarioAcuicola.fechaIniEvento"
                          @input="dataPecuarioAcuicola.menuFechaIniEvento = false"
                          outlined
                          ></v-date-picker>
                      </v-col>
                    </v-menu>
                    <v-col
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="Número de animales enfermos o afectados"
                        hint="Número de animales enfermos o afectados"
                        v-model.number="dataPecuarioAcuicola.numAnimalEnfermos"
                        type="number"
                        dense
                        outlined
                        solo
                        flat
                        :onkeypress="regexNumber"
                        prepend-inner-icon="mdi-decagram"
                        required
                        :rules="required"
                      ></v-text-field>
                    </v-col>
                    <v-col
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="Número de animales hembra muertos"
                        hint="Número de animales hembra muertos"
                        v-model.number="dataPecuarioAcuicola.numAnimalHembMuerto"
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
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="Número de animales machos muertos"
                        hint="Número de animales machos muertos"
                        v-model.number="dataPecuarioAcuicola.numAnimalMachMuerto"
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
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="Edad promedio en meses de los animales muertos"
                        hint="Edad promedio en meses de los animales muertos"
                        v-model.number="dataPecuarioAcuicola.edadAnimal"
                        type="number"
                        dense
                        outlined
                        solo
                        flat
                        :onkeypress="regexNumber"
                        prepend-inner-icon="mdi-decagram"
                        required
                        :rules="required"
                      ></v-text-field>
                    </v-col>
                </v-row>

                <v-row dense class="section mt-3">
                    <v-col cols="12" class="color-black font-weight-bold">Producción</v-col>
                    <v-col
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-autocomplete
                        v-model="dataPecuarioAcuicola.tipoProducto"
                        :items="verTipoProducto"
                        item-text="tipprod"
                        item-value="codtipprod"
                        dense
                        outlined
                        solo
                        flat
                        clearable
                        label="Ttipo de producto obtenido de los animales"
                        hint="Tipo de producto obtenido de los animales"
                      ></v-autocomplete>
                    </v-col>
                    <v-col
                      v-if="verTipoProductoNuevo"
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="¿Si es otro cuál?"
                        hint="¿Si es otro cuál?"
                        v-model="dataPecuarioAcuicola.tipoProductoNuevo"
                        dense
                        outlined
                        solo
                        flat
                        prepend-inner-icon="mdi-decagram"
                        required
                        :rules="required"
                      ></v-text-field>
                    </v-col>
                </v-row>

                <v-row v-if="verDatosProduccionSegunProduccion" dense class="section mt-3">
                    <v-col cols="12" class="color-black font-weight-bold">Datos de producción</v-col>
                    <v-col
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="Producción mensual normal"
                        hint="Producción mensual normal antes de la afectación"
                        v-model="dataPecuarioAcuicola.produMensualAfectacion"
                        dense
                        outlined
                        solo
                        flat
                        prepend-inner-icon="mdi-decagram"
                        required
                        :rules="required"
                      ></v-text-field>
                    </v-col>
                    <v-col
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="Producción mensual actual o potencial"
                        hint="Producción mensual actual o potencial después del evento"
                        v-model="dataPecuarioAcuicola.produPotencial"
                        dense
                        outlined
                        solo
                        flat
                        prepend-inner-icon="mdi-decagram"
                        required
                        :rules="required"
                      ></v-text-field>
                    </v-col>
                    <v-col
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-autocomplete
                        v-model="dataPecuarioAcuicola.unidadProdccion"
                        :items="unidadProduccion"
                        item-text="undcosecha"
                        item-value="codundcosecha"
                        dense
                        outlined
                        solo
                        flat
                        clearable
                        label="¿Unidades a reportar la producción?"
                        hint="¿Unidades a reportar la producción?"
                      ></v-autocomplete>
                    </v-col>
                    <v-col
                      v-if="kilosPorUnidadProducto"
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="Cuantos kilos pesa una unidad de producto que usted comercializa"
                        hint="Cuantos kilos pesa una unidad de producto que usted comercializa"
                        v-model="dataPecuarioAcuicola.kilosUnidad"
                        dense
                        outlined
                        solo
                        flat
                        prepend-inner-icon="mdi-decagram"
                        required
                        :rules="required"
                        :onkeypress="regexNumber"
                      ></v-text-field>
                    </v-col>
                    <v-col
                      v-if="verOtraUnidadProduccion"
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="Nombre de la otra unidad de medida"
                        hint="Nombre de la otra unidad de medida"
                        v-model="dataPecuarioAcuicola.nombreUnidadProduccionNueva"
                        dense
                        outlined
                        solo
                        flat
                        prepend-inner-icon="mdi-decagram"
                        required
                        :rules="required"
                      ></v-text-field>
                    </v-col>
                    <v-col
                      v-if="verOtraUnidadProduccion"
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="Equivalencia en kilos de la otra unidad"
                        hint="Equivalencia en kilos de la otra unidad"
                        v-model="dataPecuarioAcuicola.unidadProduccionNueva"
                        dense
                        outlined
                        solo
                        flat
                        prepend-inner-icon="mdi-decagram"
                        required
                        :rules="required"
                        :onkeypress="regexNumber"
                      ></v-text-field>
                    </v-col>
                    <v-col
                      v-if="verUnidadProduccionNuevo"
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-autocomplete
                        v-model="dataPecuarioAcuicola.pesoProduccion"
                        :items="peso"
                        item-text="eqvcargakg"
                        item-value="codequivcarga"
                        dense
                        outlined
                        solo
                        flat
                        clearable
                        label="Peso de la carga"
                        hint="Peso de la carga"
                      ></v-autocomplete>
                    </v-col>
                    <v-col
                      v-if="verPesoNuevoProduccion"
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="¿Si es otro cuál?"
                        hint="Equivalencia en kilos"
                        v-model="dataPecuarioAcuicola.pesoProduccionNuevo"
                        dense
                        outlined
                        solo
                        flat
                        prepend-inner-icon="mdi-decagram"
                        required
                        :rules="required"
                        :onkeypress="regexNumber"
                      ></v-text-field>
                    </v-col>
                    <v-col
                      cols="12"
                      md="4"
                      sm="12"
                    >
                      <v-text-field
                        label="Precio de venta de la unidad de producto"
                        hint="Precio de venta de la unidad de producto"
                        v-model="dataPecuarioAcuicola.valorVentaProducto"
                        dense
                        outlined
                        solo
                        flat
                        prepend-inner-icon="mdi-currency-usd"
                        @blur="formatCurrency('dataPecuarioAcuicola','valorVentaProducto')"
                        :onkeypress="regexNumber"
                      ></v-text-field>
                    </v-col>
                    <v-col
                      class="ma-2"
                      cols="12"
                      md="12"
                      sm="12"
                    >
                      <v-switch
                        v-if="verHuevoAvicolaSegunProduccion"
                        v-model="dataPecuarioAcuicola.huevosAvicola"
                        inset
                        label="Usted seleccionó huevos como un producto diferente a la parte avícola"
                      ></v-switch>
                    </v-col>
                </v-row>

                <v-col
                  cols="12"
                  md="12"
                  sm="12"
                ></v-col>

                <v-row dense class="container-titles mt-5">
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                    align="center"
                    justify="center"
                    class="mt-3 font-16"
                  >
                    <p class="color-black font-weight-bold">Pérdidas pecuarias</p>
                  </v-col>
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <v-chip class="background-primary-dark">El valor estimado de los animales muertos es de: {{ valorAnimalesmuertos }} </v-chip>
                  </v-col>
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <v-chip class="background-primary-dark">Pérdida en producción: {{ perdidaProduccion }}</v-chip>
                  </v-col>
                </v-row>

                <v-row dense class="section mt-3">
                  <v-col
                    class="color-black font-weight-bold mt-5"
                    cols="12"
                  >
                    <p> Costos de producción pecuario (indique los gastos asumidos durante el último año en los animales muertos) </p>
                  </v-col>
                  <v-col
                    cols="12"
                    md="6"
                    sm="12"
                  >
                    <v-text-field
                      label="Meses para recuperar las perdidas pecuarias"
                      hint="Meses para recuperar las perdidas pecuarias"
                      v-model="dataPecuarioAcuicola.mesesRecuperarPecuaria"
                      dense
                      outlined
                      solo
                      flat
                      :onkeypress="regexNumber"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-container>
            </v-form>

            <v-form
              lazy-validation
              ref="formCostoVariable"
              v-model="validCostoVariable"
            >
                <v-row dense class="section mt-3">
                  <v-col
                    class="color-black font-weight-bold"
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p> Costos variables pecuarios </p>
                  </v-col>
                  <v-col
                    cols="12"
                    md="6"
                    sm="12"
                  >
                    <v-autocomplete
                      v-model="costosVariable.codCostoVariable"
                      :items="tipoCostosVariable"
                      item-text="actividad"
                      item-value="codactividad"
                      :search-input.sync="costosVariable.nameCostoVariable"
                      dense
                      outlined
                      solo
                      flat
                      clearable
                      label="Actividad"
                      hint="Actividad"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    md="6"
                    sm="12"
                  >
                    <v-text-field
                      label="Costo"
                      hint="Costo"
                      v-model="costosVariable.costoVariable"
                      dense
                      outlined
                      solo
                      flat
                      append-icon="mdi-currency-usd"
                      :onkeypress="regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      @blur="formatCurrency('costosVariable','costoVariable')"
                      :rules="required"
                    ></v-text-field>
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
                  >
                    <v-btn
                    class="background-primary-dark button-basic"
                    elevation="2"
                    block
                    raised
                    depressed
                    @click="agregarCosto(1)"
                    >Agregar</v-btn>
                  </v-col>
                  <v-col
                    cols="12"
                  >
                    <v-data-table
                      :headers="costoVariableHeader"
                      :items="itemsCostoVariable"
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
                          @click="eliminarCostos(item, 1)"
                        >
                        mdi-delete
                        </v-icon>
                      </template>
                    </v-data-table>
                  </v-col>
                </v-row>
            </v-form>

            <v-form
              lazy-validation
              ref="formCostoFijo"
              v-model="validCostoFijo"
            >
                <v-row dense class="section mt-3">
                  <v-col
                    class="color-black font-weight-bold mt-3"
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p> Costos fijos pecuarios </p>
                  </v-col>
                  <v-col
                    cols="12"
                    md="6"
                    sm="12"
                  >
                    <v-autocomplete
                      v-model="costosFijos.codCostoFijo"
                      :items="tipoCostosFijos"
                      item-text="rubros"
                      item-value="codrubro"
                      :search-input.sync="costosFijos.nameCostoFijo"
                      dense
                      outlined
                      solo
                      flat
                      clearable
                      label="Rubro"
                      hint="Rubro"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    md="6"
                    sm="12"
                  >
                    <v-text-field
                      label="Costo"
                      hint="Costo"
                      v-model="costosFijos.costoFijo"
                      dense
                      outlined
                      solo
                      flat
                      append-icon="mdi-currency-usd"
                      :onkeypress="regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      @blur="formatCurrency('costosFijos','costoFijo')"
                      :rules="required"
                    ></v-text-field>
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
                  >
                    <v-btn
                    class="background-primary-dark button-basic"
                    elevation="2"
                    block
                    raised
                    depressed
                    @click="agregarCosto(2)"
                    >Agregar</v-btn>
                  </v-col>
                  <v-col
                    cols="12"
                  >
                    <v-data-table
                      :headers="costoFijosHeader"
                      :items="itemsCostoFijos"
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
                          @click="eliminarCostos(item, 2)"
                        >
                        mdi-delete
                        </v-icon>
                      </template>
                    </v-data-table>
                  </v-col>
                </v-row>
            </v-form>

          <v-row dense class="section mt-5">
              <v-switch
                class="ml-2"
                cols="12"
                md="12"
                sm="12"
                v-model="afectacion"
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
                class="section mt-3 font-16"
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
                sm="12"
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
                  prepend-inner-icon="mdi-decagram"
                  required
                  :rules="required"
                ></v-autocomplete>
              </v-col>
              <v-col
                v-if="verNuevoTipoInsumo"
                cols="12"
                md="4"
                sm="12"
              >
                <v-text-field
                  label="Indique el otro insumo"
                  hint=""
                  v-model="insumos.nuevoInsumo"
                  dense
                  outlined
                  solo
                  flat
                  prepend-inner-icon="mdi-decagram"
                  required
                  :rules="required"
                ></v-text-field>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="12"
              >
                <v-text-field
                  label="Nombre comercial"
                  hint=""
                  v-model="insumos.nombreComercial"
                  dense
                  outlined
                  solo
                  flat
                  prepend-inner-icon="mdi-decagram"
                  required
                  :rules="required"
                ></v-text-field>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="12"
              >
                <v-text-field
                  label="Cantidad de insumos, forrajes, alimento para los animales y piensos"
                  hint="para los animales y piensos"
                  v-model.number="insumos.cantInsumo"
                  dense
                  outlined
                  solo
                  flat
                  type="number"
                  :onkeypress="regexNumber"
                  prepend-inner-icon="mdi-decagram"
                  required
                  :rules="required"
                ></v-text-field>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="12"
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
                  prepend-inner-icon="mdi-decagram"
                  label="Unidad de medida"
                  hint="Unidad de medida"
                  required
                  :rules="required"
                ></v-autocomplete>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="12"
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
                  :onkeypress="regexNumber"
                  required
                  @blur="formatCurrency('insumos','valorBienes')"
                  :rules="required"
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
            v-if="verCamposSegunTipoInsumo && dataPecuarioAcuicola.sistema !== 1"
            lazy-validation
            ref="formSectionTwo"
            v-model="validSectionTwo"
          >
            <v-row
              v-if="verMaquinariaSegunSistemaMayores"
              dense
              class="section mt-3"
            >
              <v-col
                cols="12"
                md="12"
                sm="12"
              >
                <p class="color-black font-weight-bold">Instalaciones y maquinaria manejo de bovinos, bufalinos y afines</p>
              </v-col>

              <v-col
                cols="12"
                md="4"
                sm="12"
              >
                <v-autocomplete
                  v-model="afectacionInsumo.tipoMaquinariaBba"
                  :items="verMaquinariasBbaSegunSistema"
                  item-text="tipmaquinaria"
                  item-value="codtipmaquinaria"
                  :search-input.sync="afectacionInsumo.nombreMaquiBba"
                  dense
                  outlined
                  solo
                  flat
                  label="Tipo de maquinaria"
                  hint="Tipo de maquinaria"
                  prepend-inner-icon="mdi-decagram"
                  required
                  clearable
                  :rules="required"
                ></v-autocomplete>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="12"
              >
                <v-text-field
                  label="Nombre de la instalación, maquinaria o herramienta"
                  hint="Nombre de la instalación, maquinaria o herramienta"
                  v-model="afectacionInsumo.nombreMaquinariaBba"
                  dense
                  outlined
                  solo
                  flat
                  prepend-inner-icon="mdi-decagram"
                  required
                  :rules="required"
                ></v-text-field>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="12"
              >
                <v-text-field
                  label="Valor en pesos de la afectación"
                  hint="Indique el valor incurrido en reparar o reponer el bien"
                  v-model="afectacionInsumo.valorReparacionBba"
                  dense
                  outlined
                  solo
                  flat
                  prepend-inner-icon="mdi-decagram"
                  append-icon="mdi-currency-usd"
                  :onkeypress="regexNumber"
                  required
                  @blur="formatCurrency('afectacionInsumo','valorReparacionBba')"
                  :rules="required"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-row
              dense
              class="section mt-3"
              v-if="verMaquinariaSegunSistemaMenores"
            >
              <v-col
                cols="12"
                md="12"
                sm="12"
              >
                <p
                  class="color-black font-weight-bold"
                  v-if="dataPecuarioAcuicola.sistema !== 3"
                >Instalaciones y maquinaria para la producción de especies menores
                </p>
                <p
                  class="color-black font-weight-bold"
                  v-if="dataPecuarioAcuicola.sistema === 3"
                >Instalaciones y maquinarias avícolas
                </p>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="12"
              >
                <v-autocomplete
                  v-model="afectacionInsumo.tipoMaquinariaPem"
                  :items="verMaquinariasPemSegunSistema"
                  item-text="tipmaquinaria"
                  item-value="codtipmaquinaria"
                  :search-input.sync="afectacionInsumo.nombreMaquiPem"
                  dense
                  outlined
                  solo
                  flat
                  label="Tipo de maquinaria"
                  hint="Tipo de maquinaria"
                  prepend-inner-icon="mdi-decagram"
                  required
                  clearable
                  :rules="required"
                ></v-autocomplete>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="12"
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
                  required
                  :rules="required"
                ></v-text-field>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="12"
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
                  :onkeypress="regexNumber"
                  required
                  @blur="formatCurrency('afectacionInsumo','valorReparacionPem')"
                  :rules="required"
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

          <v-form
          lazy-validation
          ref="formSectionThree"
          v-model="validSectionThree"
          v-if="verMaquinariaSegunSistemaAcuicola"
        >
          <v-row dense class="section mt-3">
            <v-col
              cols="12"
              md="12"
              sm="12"
            >
              <p class="color-black font-weight-bold">Infraestructura, instalaciones y maquinaria acuícolas / pesqueras afectadas</p>
            </v-col>
            <v-col
              cols="12"
              md="4"
              sm="12"
            >
              <v-autocomplete
                v-model="dataInfraestructura.tipActivo"
                :items="activoAfectado"
                item-text="tipactivo"
                item-value="codtipactivo"
                dense
                outlined
                solo
                flat
                clearable
                label="Seleccione un activo productivo afectado"
                prepend-inner-icon="mdi-decagram"
                required
                :rules="required"
              ></v-autocomplete>
            </v-col>
          </v-row>
          <v-row
            v-if="verDatosEquipoSegunInfraestructura"
            dense
            class="section mt-3"
          >
            <v-col
              cols="12"
              md="12"
              sm="12
              "
            >
              <p class="color-black font-weight-bold">Datos del equipo / maquinaria afectado</p>
            </v-col>
            <v-col
              cols="12"
              md="4"
              sm="12"
            >
              <v-text-field
                label="Indique el nombre/marca del equipo"
                hint=""
                v-model="dataInfraestructura.nombreEquipo"
                dense
                outlined
                solo
                  flat
                prepend-inner-icon="mdi-decagram"
                required
                :rules="required"
              ></v-text-field>
            </v-col>
            <v-menu
              v-model="dataInfraestructura.menuFechaAdquisicion"
              :close-on-content-click="false"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-col
                  cols="12"
                  md="4"
                  sm="12"
                >
                  <v-text-field
                    v-model="dataInfraestructura.fechaAdquisicion"
                    label="¿Cuál fue la fecha de adquisición del bien?"
                    readonly
                    v-bind="attrs"
                    v-on="on"
                    dense
                    outlined
                    solo
                  flat
                  ></v-text-field>
                </v-col>
              </template>
              <v-col
                cols="12"
                md="4"
                sm="12"
              >
                <v-date-picker
                  v-model="dataInfraestructura.fechaAdquisicion"
                  @input="dataInfraestructura.menuFechaAdquisicion = false"
                  outlined
                  ></v-date-picker>
              </v-col>
            </v-menu>
            <v-col
              cols="12"
              md="4"
              sm="12"
            >
              <v-text-field
                label="¿Cuál fue el precio pagado por el activo?"
                hint=""
                v-model="dataInfraestructura.valorPagado"
                dense
                outlined
                solo
                  flat
                prepend-inner-icon="mdi-decagram"
                append-icon="mdi-currency-usd"
                :onkeypress="regexNumber"
                required
                :rules="required"
              ></v-text-field>
            </v-col>
            <v-col
              cols="12"
              md="4"
              sm="12"
            >
              <v-text-field
                label="¿Valor invertido en reponer, reparar y/o adecuar el/la máquina/equipo?"
                hint="reponer, reparar y/o adecuar el/la máquina/equipo"
                v-model="dataInfraestructura.valorReponer"
                dense
                outlined
                solo
                flat
                prepend-inner-icon="mdi-decagram"
                append-icon="mdi-currency-usd"
                :onkeypress="regexNumber"
                required
                @blur="formatCurrency('dataInfraestructura','valorReponer')"
                :rules="required"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row
            v-if="!verDatosEquipoSegunInfraestructura && this.dataInfraestructura.tipActivo"
            dense
            class="section mt-3"
          >
            <v-col
              cols="12"
              md="12"
              sm="12
              "
            >
              <p class="color-black font-weight-bold">Construcciones</p>
            </v-col>
            <v-col
              cols="12"
              md="4"
              sm="12"
            >
              <v-text-field
                label="Indique el nombre/marca del equipo"
                hint=""
                v-model="dataInfraestructura.nombreEquipoConstruc"
                dense
                outlined
                solo
                  flat
                prepend-inner-icon="mdi-decagram"
                required
                :rules="required"
              ></v-text-field>
            </v-col>
             <v-menu
              v-model="dataInfraestructura.menuFechaConstruc"
              :close-on-content-click="false"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-col
                  cols="12"
                  md="4"
                  sm="12"
                >
                  <v-text-field
                    v-model="dataInfraestructura.fechaConstruc"
                    label="¿Cuál fue la fecha de adquisición del bien?"
                    readonly
                    v-bind="attrs"
                    v-on="on"
                    dense
                    outlined
                    solo
                  flat
                  ></v-text-field>
                </v-col>
              </template>
              <v-col
                cols="12"
                md="4"
                sm="12"
              >
                <v-date-picker
                  v-model="dataInfraestructura.fechaConstruc"
                  @input="dataInfraestructura.menuFechaConstruc = false"
                  outlined
                  ></v-date-picker>
              </v-col>
            </v-menu>
            <v-col
              cols="12"
              md="4"
              sm="12"
            >
              <v-text-field
                label="¿Cuál fue el precio pagado por el activo?"
                hint="¿Cuál fue el precio pagado por el activo?"
                v-model="dataInfraestructura.valorPagadoConstruc"
                dense
                outlined
                solo
                flat
                prepend-inner-icon="mdi-decagram"
                append-icon="mdi-currency-usd"
                :onkeypress="regexNumber"
                required
                @blur="formatCurrency('dataInfraestructura','valorPagadoConstruc')"
                :rules="required"
              ></v-text-field>
            </v-col>
            <v-col
              cols="12"
              md="4"
              sm="12"
            >
              <v-text-field
                label="¿Valor invertido en reponer, reparar y/o adecuar el/la máquina/equipo?"
                hint="reponer, reparar y/o adecuar el/la máquina/equipo"
                v-model="dataInfraestructura.valorReponerConstruc"
                dense
                outlined
                solo
                flat
                prepend-inner-icon="mdi-decagram"
                append-icon="mdi-currency-usd"
                :onkeypress="regexNumber"
                required
                @blur="formatCurrency('dataInfraestructura','valorReponerConstruc')"
                :rules="required"
              ></v-text-field>
            </v-col>
            <v-col
              cols="12"
              md="4"
              sm="12"
            >
              <v-autocomplete
                v-model="dataInfraestructura.tipAfecta"
                :items="tipAfecta"
                item-text="tipconstruccion"
                item-value="codtipconstruccion"
                dense
                outlined
                solo
                flat
                clearable
                label="Por favor, indique el tipo de construcción afectada"
              ></v-autocomplete>
            </v-col>
            <v-col
              cols="12"
              md="4"
              sm="12"
            >
              <v-text-field
                label="¿Área en metros cuadrados de la construcción afectada?"
                hint="¿Área en metros cuadrados de la construcción afectada?"
                v-model.number="dataInfraestructura.areaAfectada"
                type="number"
                dense
                outlined
                solo
                flat
                prepend-inner-icon="mdi-decagram"
                required
                :rules="required"
              ></v-text-field>
            </v-col>
            <v-col
              cols="12"
              md="4"
              sm="12"
            >
              <v-text-field
                label="¿Valor invertido en la re-construcción, reparación y/o adecuación del sitio?"
                hint="Por favor indique el valor que estima deberá invertir para reconstruir, reparar y/o adecuar las construcciones"
                v-model="dataInfraestructura.valorReparacion"
                dense
                outlined
                solo
                flat
                prepend-inner-icon="mdi-decagram"
                append-icon="mdi-currency-usd"
                :onkeypress="regexNumber"
                required
                @blur="formatCurrency('dataInfraestructura','valorReparacion')"
                :rules="required"
              ></v-text-field>
            </v-col>
            <v-col
              cols="12"
              md="4"
              sm="12"
            >
              <v-text-field
                label="¿Tiempo necesario para realizar re-construcción, reparación y/o adecuación del sitio (meses)?"
                hint="re-construcción, reparación y/o adecuación del sitio (meses)"
                v-model.number="dataInfraestructura.mesesReparacion"
                type="number"
                dense
                outlined
                solo
                flat
                :onkeypress="regexNumber"
                prepend-inner-icon="mdi-decagram"
                required
                :rules="required"
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
              @click="guardarInfraestructura"
              >Agregar instalación</v-btn>
            </v-col>
            <v-col
              cols="12"
            >
              <v-data-table
                :headers="infraestructuraHeader"
                :items="itemsInfraestructura"
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
                    @click="eliminarInfraestructura(item)"
                  >
                  mdi-delete
                  </v-icon>
                </template>
              </v-data-table>
            </v-col>
          </v-row>
          </v-form>

          <v-col
            cols="12"
            md="12"
            sm="12"
          ></v-col>

          <v-row class="mt-5">
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
                class="success button-basic"
                elevation="2"
                block
                raised
                depressed
                @click="guardarSistema"
              >Guardar sistema</v-btn>
            </v-col>
          </v-row>

          <!-- <p> Data formulario </p>
          {{dataFormulario}} -->

          </v-container>
        </v-card-text>
      </v-card>
    </v-dialog>

  </div>
</template>

<script>

import { newEvent } from '../../services/api.js';
import { getData } from '../../indexedDb/getData';

export default {
  name:'pecuarioAcuicola',
  props:['obtenerDataPecuaAcui'],
  data() {
    return {
      dialogPecuario: false,
      valid: true,
      validCostoVariable: true,
      validCostoFijo: true,
      validInsumos: true,
      validSectionTwo: true,
      validSectionThree: true,

      especiesHeader: [
        { text: 'Especie', align: 'start', sortable: false, value: 'nombreSistema'},
        { text: 'Nombre raza', align: 'start', sortable: false, value: 'nombreRaza'},
        { text: 'Total animales', align: 'start', sortable: false, value: 'numAnimal'},
        { text: 'Precio promedio', align: 'start', sortable: false, value: 'valorAnimal'},
        { text: 'Acciones', value: 'actions', sortable: false, width: '2%' },
      ],
      itemsEspecieAgregada: [],
      costoVariableHeader: [
        { text: 'Actividad', align: 'start', sortable: false, value: 'nameCostoVariable' },
        { text: 'Valor', align: 'start', sortable: false, value: 'costoVariable' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      itemsCostoVariable: [],
      costoFijosHeader: [
        { text: 'Rubro', align: 'start', sortable: false, value: 'nameCostoFijo' },
        { text: 'Valor', align: 'start', sortable: false, value: 'costoFijo' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      itemsCostoFijos: [],
      insumosHeader: [
        { text: 'Tipo insumo', align: 'start', sortable: false, value: 'nameTipoInsumo' },
        { text: 'Cant. insumo', align: 'start', sortable: false, value: 'cantInsumo' },
        { text: 'Nombre comercial', align: 'start', sortable: false, value: 'nombreComercial' },
        { text: 'Unidad medida', align: 'start', sortable: false, value: 'nameUnidadMedida' },
        { text: 'Valor', align: 'start', sortable: false, value: 'valorBienes' },
        { text: 'valor', align: 'start', sortable: false, value: 'valorReparacionPem' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      itemsInsumos: [],
      maquinariaHeader: [
        { text: 'Maquinaria especies mayores', align: 'start', sortable: false, value: 'nombreMaquiBba' },
        { text: 'Nombre', align: 'start', sortable: false, value: 'nombreMaquinariaBba' },
        { text: 'valor', align: 'start', sortable: false, value: 'valorReparacionBba' },
        { text: 'Maquinaria especies menores', align: 'start', sortable: false, value: 'nombreMaquiPem' },
        { text: 'Nombre', align: 'start', sortable: false, value: 'nombreMarcaPem' },
        { text: 'valor', align: 'start', sortable: false, value: 'valorReparacionPem' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      itemsMaquinaria: [],
      infraestructuraHeader: [
        { text: 'Tipo activo', align: 'start', sortable: false, value: 'nombreActivo' },
        { text: 'Nombre equipo', align: 'start', sortable: false, value: 'nombreEquipo' },
        { text: 'Fch. adquisicón', align: 'start', sortable: false, value: 'fechaAdquisicion' },
        { text: 'Vlr. pagado', align: 'start', sortable: false, value: 'valorPagado' },
        { text: 'Vlr. reponer', align: 'start', sortable: false, value: 'valorReponer' },
        { text: 'Nomb. equipo construc.', align: 'start', sortable: false, value: 'nombreEquipoConstruc' },
        { text: 'Fch.adquisición construc.', align: 'start', sortable: false, value: 'fechaConstruc' },
        { text: 'Vlr. pagado construc.', align: 'start', sortable: false, value: 'valorPagadoConstruc' },
        { text: 'Vlr. reponder construc.', align: 'start', sortable: false, value: 'valorReponerConstruc' },
        { text: 'Tipo construc. afectada', align: 'start', sortable: false, value: 'nombreTipoAfecta' },
        { text: 'Área afectada', align: 'start', sortable: false, value: 'areaAfectada' },
        { text: 'Vlr. reparación', align: 'start', sortable: false, value: 'valorReparacion' },
        { text: 'Meses reparación', align: 'start', sortable: false, value: 'mesesReparacion' },
        { text: 'Meses reparación', align: 'start', sortable: false, value: 'mesesReparacion' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      itemsInfraestructura: [],

      dataPecuarioAcuicola: {},
      dataApicola: {},
      insumos:{},
      afectacionInsumo:{},
      afectacion: false,
      activoAfectado: [],
      dataInfraestructura:{},

      sistemas:[],
      uniMedidaAnimales:[],
      peso:[],
      unidadArea:[],
      tipoProducto:[],
      completo:[],
      unidadProduccion:[],
      valorAnimalesmuertos: '',
      perdidaProduccion: '',
      costosVariable: {},
      tipoCostosVariable:[],
      costosFijos: {},
      tipoCostosFijos:[],
      tipoInsumo: [],
      tipoMaquinariaBba: [],
      tipoMaquinariaBbaComple: [],
      tipoMaquinariaPem: [],
      tipoMaquinariaAvicola: [],
      tipAfecta: [],
      editedIndex: -1,

      regexNumber: "return (event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46)",
      name: '',
      required: [v => !!v || 'Campo requerido',],
    }
  },
  async mounted () {
    await this.getDataPecuario();
    await this.edicionPecuario();
  },
  methods: {
    cerrarModal() {
      this.limpiarCampos();
    },
    async getDataPecuario() {
      try {
        const res = await getData('pecuario', true);
        this.addDataCampos(res);

      } catch (error) {
        console.log(error);
      }
    },
    edicionPecuario() {
      const dataEvento = this.$route.params.evento;
      if (dataEvento !== undefined) {
        if (dataEvento.dataEspecies.infoPecuario.length > 0) {
          this.itemsEspecieAgregada = dataEvento.dataEspecies.infoPecuario;
        }
      }
    },
    addDataCampos(data) {
      this.sistemas = data.affectedSistem;
      this.uniMedidaAnimales = data.harvestUnity;
      data.equivCharge.push({codequivcarga:6, eqvcargakg:'Otro'});
      this.peso = data.equivCharge;
      this.unidadArea = data.areaUnity;
      this.tipoProducto = data.typeProduct;
      this.completo  = data.typeProduct;
      this.unidadProduccion = data.unity;
      this.tipoInsumo = data.inputType;
      this.tipoMaquinariaBba = data.machineryTypeBBA;
      this.tipoMaquinariaBbaComple = data.machineryTypeBBA;
      this.tipoMaquinariaPem = data.machineryTypePEM;
      this.tipoMaquinariaAvicola = data.machineryAv;
      this.activoAfectado = data.activeType;
      this.tipAfecta = data.constructionType;
      this.tipoCostosVariable = data.activity;
      this.tipoCostosFijos = data.rubro;
    },
    agregarCosto(tipo) {
      if (tipo === 1) {
        if (this.$refs.formCostoVariable.validate()) {
          this.itemsCostoVariable.push(this.costosVariable);
          this.costosVariable = {};
        }
      }
      if (tipo === 2) {
        if (this.$refs.formCostoFijo.validate()) {
          this.itemsCostoFijos.push(this.costosFijos);
          this.costosFijos = {};
        }
      }
    },
    eliminarCostos(item, tipo) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar costo?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          if (tipo === 1) {
            const editedIndex = this.itemsCostoVariable.indexOf(item);
            this.itemsCostoVariable.splice(editedIndex, 1);
          }
          if (tipo === 2) {
            const editedIndex = this.itemsCostoFijos.indexOf(item);
            this.itemsCostoFijos.splice(editedIndex, 1);
          }
        }
      })
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
    guardarTipoMaquinaria() {
      if (this.$refs.formSectionTwo.validate()) {
        this.itemsMaquinaria.push(this.afectacionInsumo);
        this.afectacionInsumo  = {}
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
    guardarInfraestructura() {
      if (this.$refs.formSectionThree.validate()) {
        var tipActivo = this.dataInfraestructura.tipActivo;
        let nombretipActivo = this.activoAfectado.filter(item => item.codtipactivo === tipActivo);
        this.dataInfraestructura.nombreActivo = nombretipActivo[0]['tipactivo'];

        if (this.dataInfraestructura.tipActivo === 2 && this.dataInfraestructura.tipAfecta) {
          var tipAfecta = this.dataInfraestructura.tipAfecta;
          let nombreTipoAfecta = this.tipAfecta.filter(item => item.codtipconstruccion === tipAfecta);
          this.dataInfraestructura.nombreTipoAfecta = nombreTipoAfecta[0]['tipconstruccion'];
        }

        this.itemsInfraestructura.push(this.dataInfraestructura);
        this.dataInfraestructura = {};
      }
    },
    eliminarInfraestructura(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar infraestructura?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          const editedIndex = this.itemsInfraestructura.indexOf(item);
          this.itemsInfraestructura.splice(editedIndex, 1);
        }
      })
    },
    limpiarCamposDataInfraestruc() {
      var tipActivo = this.dataInfraestructura.tipActivo;

      if (tipActivo && tipActivo !== 2) {
        delete this.dataInfraestructura.nombreEquipoConstruc;
        delete this.dataInfraestructura.menuFechaAdquisicionConstruc;
        delete this.dataInfraestructura.fechaConstruc;
        delete this.dataInfraestructura.valorPagadoConstruc;
        delete this.dataInfraestructura.valorReponerConstruc;
        delete this.dataInfraestructura.tipAfecta;
        delete this.dataInfraestructura.areaAfectada;
        delete this.dataInfraestructura.valorReparacion;
        delete this.dataInfraestructura.mesesReparacion;
      } else if (tipActivo) {
        delete this.dataInfraestructura.nombreEquipo;
        delete this.dataInfraestructura.menuFechaAdquisicion;
        delete this.dataInfraestructura.fechaAdquisicion;
        delete this.dataInfraestructura.valorPagado;
        delete this.dataInfraestructura.valorReponer;
      }
    },
    guardarSistema() {
      if (this.$refs.form.validate()) {
        if (this.itemsCostoVariable.length === 0 || this.itemsCostoFijos.length === 0) {
          this.$swal({
            icon: 'error',
            text: 'No se han registrados costos variables o fijos.',
            confirmButtonText: 'Aceptar',
          });
          return;
        }
        this.dataPecuarioAcuicola.costosVariables = this.itemsCostoVariable;
        this.dataPecuarioAcuicola.costosFijos = this.itemsCostoFijos;
        this.dataPecuarioAcuicola.dataInsumos = this.itemsInsumos;
        this.dataPecuarioAcuicola.dataMaquinaria = this.itemsMaquinaria;
        this.dataPecuarioAcuicola.dataInfraestructura = this.itemsInfraestructura;
        this.dataPecuarioAcuicola.afectacion = this.afectacion;

        if (this.editedIndex > -1) {
          Object.assign(this.itemsEspecieAgregada[this.editedIndex], this.dataPecuarioAcuicola);
        } else {
          this.itemsEspecieAgregada.push(this.dataPecuarioAcuicola);
        }

        this.obtenerDataPecuaAcui(this.itemsEspecieAgregada);
        this.limpiarCampos();
      }
    },
    limpiarCampos() {
      this.dataPecuarioAcuicola = {};
      this.itemsCostoVariable = [];
      this.itemsCostoFijos = [];
      this.itemsInsumos = [];
      this.itemsMaquinaria = [];
      this.itemsInfraestructura = [];
      this.editedIndex = -1;
      this.dialogPecuario = false;
    },
    editarSistemaPecuario(item) {
      this.editedIndex = this.itemsEspecieAgregada.indexOf(item);
      this.itemsCostoVariable = item.costosVariables;
      this.itemsCostoFijos = item.costosFijos;
      this.itemsInsumos = item.dataInsumos;
      this.itemsMaquinaria = item.dataMaquinaria;
      this.itemsInfraestructura = item.dataInfraestructura;
      this.afectacion = item.afectacion;
      this.dataPecuarioAcuicola = Object.assign({}, item);
      this.dialogPecuario = true;
    },
    eliminarSistemaPecuario(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar sistema pecuario/acuicola?',
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
          this.obtenerDataPecuaAcui(this.itemsEspecieAgregada);
        }
      })
    },
    limpiarTablasSegunSistema() {
        this.itemsInsumos = [];
        this.itemsMaquinaria = [];
        this.itemsInfraestructura = [];
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
    verOtroSistema() {
      var estado = (this.dataPecuarioAcuicola.sistema === 11) ? true: false;
      if (!estado) {
        delete this.dataPecuarioAcuicola.sistemaNuevo;
      }
      return estado;
    },
    verUnidadMedidaNuevo() {
      var estado = false;
      var medida = this.dataPecuarioAcuicola.uniMedidaAnimal;
      estado = (medida && medida === 8) ? true: false;
      if (!estado) {
        delete this.dataPecuarioAcuicola.nombreUnidadMedidaNuevo;
        delete this.dataPecuarioAcuicola.unidadMedidaNuevo;
      }
      return estado;
    },
    verPeso() {
      var estado = false;
      var medida = this.dataPecuarioAcuicola.uniMedidaAnimal;
      var estado = (medida === 4 && medida) ? true: false;
      if (!estado) {
        delete  this.dataPecuarioAcuicola.peso;
      }
      return estado;
    },
    verPesoNuevo() {
      var estado = false;
      var medida = this.dataPecuarioAcuicola.uniMedidaAnimal;
      var peso   = this.dataPecuarioAcuicola.peso;
      estado = ((peso === 6 && peso) && (medida === 4 && medida)) ? true: false;
      if (!estado) {
        delete this.dataPecuarioAcuicola.pesoNuevo;
      }
      return estado;
    },
    verUnidadAreaNuevo() {
      var estado = false;
      var unidad = this.dataPecuarioAcuicola.unidadArea;
      estado = (unidad === 4 && unidad) ? true: false;
      if (!estado) {
        delete this.dataPecuarioAcuicola.unidadAreaNuevo;
      }
      return estado;
    },
    verDatosProduccionSegunProduccion() {
      var estado = false;
      var tipoProducto = this.dataPecuarioAcuicola.tipoProducto;
      estado = (tipoProducto !== 6 && tipoProducto) ? true: false;
      if (!estado) {
        delete this.dataPecuarioAcuicola.produMensualAfectacion;
        delete this.dataPecuarioAcuicola.produPotencial;
        delete this.dataPecuarioAcuicola.unidadProdccion;
        delete this.dataPecuarioAcuicola.pesoProduccion;
        delete this.dataPecuarioAcuicola.valorVentaProducto;
      }
      return estado;
    },
    verTipoProducto() {
      var sistema = this.dataPecuarioAcuicola.sistema;
      var productos = this.tipoProducto;

      if (sistema === 3 && sistema) {
        productos = productos.filter(producto => producto.codtipprod != 4);
      } else if (sistema) {
        productos = this.completo.filter(producto => producto.codtipprod != 3);
      }

      return productos;
    },
    verTipoProductoNuevo() {
      var estado = false;
      var tipoProducto = this.dataPecuarioAcuicola.tipoProducto;
      estado = (tipoProducto === 5 && tipoProducto) ? true: false;
      if (!estado) {
        delete this.dataPecuarioAcuicola.tipoProductoNuevo;
      }
      return estado;
    },
    verUnidadProduccionNuevo() {
      var estado = false;
      var unidadProdccion = this.dataPecuarioAcuicola.unidadProdccion;
      estado = (unidadProdccion === 4 && unidadProdccion) ? true: false;
      if (!estado) {
        delete this.dataPecuarioAcuicola.pesoProduccion;
        delete this.dataPecuarioAcuicola.pesoProduccionNuevo;
      }
      return estado;
    },
    kilosPorUnidadProducto() {
      var unidadProdccion = this.dataPecuarioAcuicola.unidadProdccion;
      var estado = (unidadProdccion && unidadProdccion === 6) ? true: false;
      if (!estado) {
        delete this.dataPecuarioAcuicola.kilosUnidad;
      }
      return estado;
    },
    verOtraUnidadProduccion() {
      var estado = false;
      var unidadProdccion = this.dataPecuarioAcuicola.unidadProdccion;
      estado = (unidadProdccion === 8 && unidadProdccion) ? true: false;
      if (!estado) {
        delete this.dataPecuarioAcuicola.nombreUnidadProduccionNueva;
        delete this.dataPecuarioAcuicola.unidadProduccionNueva;
      }
      return estado;
    },
    verPesoNuevoProduccion() {
      var estado = false;
      var unidadProdccion = this.dataPecuarioAcuicola.unidadProdccion;
      var peso = this.dataPecuarioAcuicola.pesoProduccion;
      estado = ((peso === 6 && peso) && (unidadProdccion === 4 && unidadProdccion)) ? true: false;
      if (!estado) {
        delete this.dataPecuarioAcuicola.pesoProduccionNuevo;
      }
      return estado;
    },
    verHuevoAvicolaSegunProduccion() {
      var estado = false;
      var tipoProducto = this.dataPecuarioAcuicola.tipoProducto;

      estado = (tipoProducto === 3 && tipoProducto) ? true: false;
      if (!estado) {
        delete this.dataPecuarioAcuicola.huevosAvicola;
      }
      return estado;
    },
    verCamposSegunTipoInsumo() {
      if (!this.afectacion) {
        this.afectacionInsumo  = {}
        this.itemsMaquinaria = [];
        this.itemsInsumos = [];
      }
      return this.afectacion;
    },
    verNuevoTipoInsumo() {
      var estado = false;
      if (this.afectacionInsumo.tipoInsumo === 6) {
        estado = true;
      } else {
        this.afectacionInsumo.nuevoInsumo = '';
      }
      return estado;
    },
    verDatosEquipoSegunInfraestructura() {
      var estado = false;
      var tipActivo = this.dataInfraestructura.tipActivo;
      estado = (tipActivo !== 2 && tipActivo) ? true: false;
      this.limpiarCamposDataInfraestruc();
      return estado;
    },
    verMaquinariaSegunSistemaAcuicola() {
      var sistema = this.dataPecuarioAcuicola.sistema;
      const ids = [1];
      var estado = (sistema && ids.includes(sistema)) ? true: false;
      if (!estado) {
        this.dataInfraestructura = {};
        this.itemsInfraestructura = [];
      }
      return estado;
    },
    verMaquinariaSegunSistemaMayores() {
      var sistema = this.dataPecuarioAcuicola.sistema;
      const ids = [4,5,6,8,9];
      var estado = (sistema && ids.includes(sistema)) ? true: false;
      if (!estado) {
        delete this.afectacionInsumo.tipoMaquinariaBba;
        delete this.afectacionInsumo.nombreMaquinariaBba;
        delete this.afectacionInsumo.valorReparacionBba;
      }
      return estado;
    },
    verMaquinariaSegunSistemaMenores() {
      var sistema = this.dataPecuarioAcuicola.sistema;
      const ids = [1,4,5,6,8,9];
      var estado = (sistema && !ids.includes(sistema)) ? true: false;
      if (!estado) {
        delete this.afectacionInsumo.tipoMaquinariaPem;
        delete this.afectacionInsumo.nombreMarcaPem;
        delete this.afectacionInsumo.valorReparacionPem;
      }
      return estado;
    },
    verMaquinariasBbaSegunSistema() {
      var sistema = this.dataPecuarioAcuicola.sistema;
      var maquinarias = this.tipoMaquinariaBba;
      if (sistema === 3 && sistema) {
        maquinarias = maquinarias.filter(maquinaria => maquinaria.codtipmaquinaria != 9);
      } else if (sistema) {
        maquinarias = this.tipoMaquinariaBbaComple;
      }
      return maquinarias;
    },
    verMaquinariasPemSegunSistema() {
      var sistema = this.dataPecuarioAcuicola.sistema;
      var maquinarias = [];
      if (sistema && sistema === 3) {
        maquinarias = this.tipoMaquinariaAvicola;
      } else if (sistema) {
        maquinarias = this.tipoMaquinariaPem;
      }
      return maquinarias;
    },
  }
}
</script>
