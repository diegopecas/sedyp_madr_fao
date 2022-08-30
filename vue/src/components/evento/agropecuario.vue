<template>
  <div>
        <!--Tabla de especies agregadas-->
    <v-container>
      <v-row>
        <v-col
          cols="12"
        >
          <v-data-table
            :headers="agroHeader"
            :items="especiesAgropecuario"
            class="elevation-2"
          >
            <template v-slot:top>
              <v-toolbar
                flat
                class="background-primary-dropdowns border-head-table font-weight-bold"
              >
                <span class="mr-2">Sistema agropecuario</span>

                <v-btn
                  class="background-primary-dark"
                  elevation="2"
                  fab
                  dark
                  small
                  @click="dialogAgropecuario = true"
                >
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </v-toolbar>
            </template>
            <template v-slot:item.actions="{ item }">
              <v-icon
                small
                color="#004884"
                @click="editarEspecieAgro(item)"
              >
              mdi-pencil
              </v-icon>
              <v-icon
                small
                color="#004884"
                @click="deleteEspecieAgro(item)"
              >
              mdi-delete
              </v-icon>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>

    <v-container>
      <v-dialog
        v-model="dialogAgropecuario"
        persistent :overlay="false"
        max-width="100%"
        transition="dialog-transition"
      >

        <!-- Formulario -->
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
                  <center>Sistema agropecuario</center>
                </v-col>
              </v-row>
            </v-container>
          </v-card-title>

          <v-card-text>
            <v-container>
              <v-row dense>
                <v-col
                  cols="12"
                  md="12"
                  sm="12"
                  class="container-titles mt-5"
                  align="center"
                  justify="center"
                >
                  <p class="color-black font-weight-bold font-16">Cultivos afectados</p>
                </v-col>
              </v-row>

              <v-form
                lazy-validation
                ref="formSectionOne"
                v-model="validFormSectionOne"
              >
                <v-row dense class="section mt-5">
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Datos de la especie</p>
                  </v-col>
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <v-chip
                      class="mt-2 mb-4"
                    >
                      Hectáreas: {{ calcularHectareaSegunArea }}
                    </v-chip>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿Cuál es el nombre del cultivo?"
                      hint="¿Cuál es el nombre del cultivo?"
                      :items="tipoCultivo"
                      v-model="agropecuario.nombreCultivo"
                      :search-input.sync="agropecuario.nameTipoCultivo"
                      item-value="codcultivo"
                      item-text="tipocultivo"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                      @change="consultarGasto"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿Unidad de área se realiza el reporte?"
                      hint="¿Unidad de área se realiza el reporte?"
                      :items="unidadArea"
                      v-model="agropecuario.unidadArea"
                      :search-input.sync="agropecuario.nameUnidadArea"
                      item-value="codundarea"
                      item-text="undarea"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                    v-if="agropecuario.unidadArea === 4"
                  >
                    <v-text-field
                      label="nombre nueva unidad"
                      hint="nombre nueva unidad"
                      v-model="agropecuario.nombrenuvaunidad"
                      dense
                      outlined
                      solo
                      flat
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                    v-if="agropecuario.unidadArea === 4"
                  >
                    <v-text-field
                      label="unidad en metros"
                      hint="unidad en metros"
                      v-model="agropecuario.nuevaunidadmetros"
                      dense
                      outlined
                      solo
                      flat
                      filled
                      :onkeypress="regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="Área total del cultivo sembrado"
                      hint="Área total del cultivo sembrado"
                      v-model="agropecuario.areaCultivo"
                      type="number"
                      dense
                      outlined
                      solo
                      flat
                      filled
                      :onkeypress="regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row dense class="section mt-5">
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Material de la siembra</p>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿Qué tipo de material utilizó para la siembra?"
                      hint="¿Qué tipo de material utilizó para la siembra?"
                      :items="materiralSiembra"
                      v-model="agropecuario.materiralSiembra"
                      :search-input.sync="agropecuario.nameMateriralSiembra"
                      item-value="codmaterial"
                      item-text="material"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      >
                    </v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="¿Cantidad semillas utilizadas en la siembra?"
                      hint="¿Cantidad semillas utilizadas en la siembra?"
                      v-model="agropecuario.cantSemillas"
                      type="number"
                      dense
                      outlined
                      solo
                      flat
                      filled
                      :onkeypress="regexNumber"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿Unidad para reportar la cantidad de semilla?"
                      hint="¿Unidad para reportar la cantidad de semilla?"
                      :items="medidaSemilla"
                      v-model="agropecuario.medidaSemilla"
                      item-value="codundcosecha"
                      item-text="undcosecha"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      >
                    </v-autocomplete>
                  </v-col>
                  <v-col
                    v-if="verCampoCarga"
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿Equivalencia en kilos de la carga?"
                      hint="¿Equivalencia en kilos de la carga?"
                      :items="equivaleKilos"
                      v-model="agropecuario.equivaleKilos"
                      item-value="codequivcarga"
                      item-text="eqvcargakg"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      >
                    </v-autocomplete>
                  </v-col>
                  <v-col
                    v-if="agropecuario.equivaleKilos === 6"
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="ingrese la otra equivalencia"
                      hint="ingrese la otra equivalencia"
                      v-model="agropecuario.nuevaEquivalencia"
                      type="number"
                      dense
                      outlined
                      solo
                      flat
                      filled
                      :onkeypress="regexNumber"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿Cuál es la fuente de la semilla?"
                      hint="¿Cuál es la fuente de la semilla?"
                      :items="fuenteSemilla"
                      v-model="agropecuario.fuenteSemilla"
                      item-value="codfuensemilla"
                      item-text="fuensemilla"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      >
                    </v-autocomplete>
                  </v-col>
                </v-row>

                <v-row  dense class="section mt-5">

                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Datos de la producción</p>
                  </v-col>
                  <v-menu
                    v-model="agropecuario.menuFechaSiembra"
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
                        >
                        <v-text-field
                          v-model="agropecuario.fechaSiembra"
                          label="¿Cuál fue la última fecha de siembra?"
                          hint="¿Cuál fue la última fecha de siembra?"
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
                      md="4"
                      >
                      <v-date-picker
                          v-model="agropecuario.fechaSiembra"
                          @input="agropecuario.menuFechaSiembra = false"
                          outlined
                        ></v-date-picker>
                    </v-col>
                  </v-menu>
                  <v-menu
                    v-model="agropecuario.menuFechaPrimeCosecha"
                    :close-on-content-click="false"
                    :nudge-right="40"
                    transition="scale-transition"
                    offset-y
                    min-width="auto"
                    v-if="agropecuario.nombreCultivo === 73 || agropecuario.nombreCultivo === 70 || agropecuario.nombreCultivo === 69 || agropecuario.nombreCultivo === 68"
                    >
                    <template v-slot:activator="{ on, attrs }">

                      <v-col
                        cols="12"
                        md="4"
                        >
                        <v-text-field
                          v-model="agropecuario.fechaPrimeCosecha"
                          label="¿Mes y año de la primera cosecha?"
                          hint="¿Mes y año de la primera cosecha?"
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
                      md="4"
                      >
                      <v-date-picker
                          v-model="agropecuario.fechaPrimeCosecha"
                          @input="agropecuario.menuFechaPrimeCosecha = false"
                          type="month"
                          outlined
                        ></v-date-picker>
                    </v-col>
                  </v-menu>
                  <v-menu
                    v-model="agropecuario.menuFechaEsperaCosecha"
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
                        >
                        <v-text-field
                          v-model="agropecuario.fechaEsperaCosecha"
                          label="¿Mes que espera cosechar o cosechó el cultivo?"
                          hint="Si no se ha cosechado colocar la fecha esperada para la cosecha"
                          persistent-hint
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
                      md="4"
                      >
                      <v-date-picker
                          v-model="agropecuario.fechaEsperaCosecha"
                          @input="agropecuario.menuFechaEsperaCosecha = false"
                          type="month"
                          outlined
                        ></v-date-picker>
                    </v-col>
                  </v-menu>

                </v-row>

                <v-row dense class="section mt-5">
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Cantidad producida</p>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="¿Cuál fue la cantidad cosechada?"
                      hint="Si la pérdida del cultivo fue total y no se puede o no se espera cosechar , por favor digite 0"
                      v-model="agropecuario.cantCosechada"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      :onkeypress="regexNumber"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿la unidad de medida para reportar la cantidad es?"
                      hint="¿la unidad de medida para reportar la cantidad es?"
                      :items="medidaCantCosechada"
                      v-model="agropecuario.medidaCantCosechada"
                      item-value="codundcosecha"
                      item-text="undcosecha"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      >
                    </v-autocomplete>
                  </v-col>
                  <v-col
                    v-if="verCampoCargaCosecha"
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿Equivalencia en kilos de la carga?"
                      hint="¿Equivalencia en kilos de la carga?"
                      :items="equivaleKilosCosecha"
                      v-model="agropecuario.equivaleKilosCosecha"
                      item-value="codequivcarga"
                      item-text="eqvcargakg"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      >
                    </v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="Total recibido por la venta de lo cosechado"
                      v-model="agropecuario.totalReciCosechado"
                      dense
                      outlined
                      solo
                      flat
                      filled
                      prepend-inner-icon="mdi-currency-usd"
                      @blur="formatCurrency('agropecuario','totalReciCosechado')"
                      :onkeypress="regexNumber"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row dense class="section mt-5">
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Exposición del cultivo al evento</p>
                  </v-col>
                  <v-menu
                    v-model="agropecuario.menuFechaAfectacion"
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
                        >
                        <v-text-field
                          v-model="agropecuario.fechaAfectacion"
                          label="¿En qué fecha inició la afectación?"
                          hint="¿En qué fecha inició la afectación?"
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
                      md="4"
                      >
                      <v-date-picker
                          v-model="agropecuario.fechaAfectacion"
                          @input="agropecuario.menuFechaAfectacion = false"
                          outlined
                        ></v-date-picker>
                    </v-col>
                  </v-menu>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="¿Cuántos días duró expuesto el cultivo?"
                      hint="¿Cuántos días duró expuesto el cultivo?"
                      v-model="agropecuario.diasCultivoExpuesto"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      :onkeypress="regexNumber"
                    ></v-text-field>
                  </v-col>

                </v-row>

                <v-row  dense class="section mt-5">
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Cantidad proyectada</p>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="¿Cantidad de producto que estimaba producir en la cosecha que se afectó?"
                      hint="Cantidad estimada a producir en la cosecha afectada"
                      v-model="agropecuario.cantProduProducir"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      :onkeypress="regexNumber"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿la unidad de medida para reportar la cantidad es?"
                      hint="¿la unidad de medida para reportar la cantidad es?"
                      :items="medidaReportar"
                      v-model="agropecuario.medidaReportar"
                      item-value="codundcosecha"
                      item-text="undcosecha"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      >
                    </v-autocomplete>
                  </v-col>
                  <v-col
                    v-if="verCampoCargaReportar"
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿Equivalencia en kilos de la carga?"
                      hint="¿Equivalencia en kilos de la carga?"
                      :items="equivaleKilosReportar"
                      v-model="agropecuario.equivaleKilosReportar"
                      item-value="codequivcarga"
                      item-text="eqvcargakg"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      >
                    </v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="Precio por kilo"
                      hint="Precio por kilo"
                      v-model="agropecuario.totalReportado"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      prepend-inner-icon="mdi-currency-usd"
                      @blur="formatCurrency('agropecuario','totalReportado')"
                      :onkeypress="regexNumber"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="Cantidad de dinero total que proyectaba recibir por la venta total de la producción"
                      hint="Dinero proyectado a recibir por la venta de la producción."
                      v-model="agropecuario.totalProyectaVenta"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      prepend-inner-icon="mdi-currency-usd"
                      @blur="formatCurrency('agropecuario','totalProyectaVenta')"
                      :onkeypress="regexNumber"
                    ></v-text-field>
                  </v-col>
                  <!-- <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="$Costo promedio del jornal de zona"
                      v-model="agropecuario.costoPromeJornal"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      :onkeypress="regexNumber"
                    ></v-text-field>
                  </v-col> -->
                </v-row>
              </v-form>

              <v-row dense class="mt-5">
                <v-col
                  cols="12"
                  md="12"
                  sm="12"
                  class="container-titles mt-5"
                  align="center"
                  justify="center"
                >
                  <p class="color-black font-weight-bold font-16">Costos de producción (por favor indique los costos asumidos en este último ciclo de cultivo)</p>
                </v-col>
              </v-row>

              <v-form
                lazy-validation
                ref="formCostoDirect"
                v-model="validFormCostoDirect"
              >
                <v-row dense class="section mt-5">
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Costos directos</p>
                  </v-col>
                  <v-col
                    v-if="verGastoJornal && Object.keys(gastosAutomaticos).length > 0"
                    cols="12"
                    sm="12"
                    md="12"
                  >
                    <v-icon
                      color="primary"
                    >
                      mdi-information
                    </v-icon>
                    Los datos cargados por defecto pueden ser cambiados.
                  </v-col>
                  <v-col
                    cols="12"
                    sm="12"
                    md="4"
                  >
                    <v-text-field
                      label="Costo promedio del jornal"
                      hint="Costo promedio del jornal"
                      v-model="agropecuario.costoPromeJornal"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      append-icon="mdi-currency-usd"
                      @blur="formatCurrency('agropecuario','costoPromeJornal')"
                      :onkeypress="regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="12"
                    md="4"
                  >
                    <v-autocomplete
                      label="Actividad"
                      hint="Actividad"
                      :items="tipoCostoDirecto"
                      v-model="costoDirectoCampos.idTipoCostoDirecto"
                      item-value="codtipactividad"
                      item-text="tipactividad"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                      @change="asignarGastoAutomatico"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="12"
                    md="4"
                  >
                    <v-text-field
                      label="Número de jornales"
                      hint="Número de jornales"
                      v-model="costoDirectoCampos.noJornales"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      :onkeypress="regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    v-if="verGastoJornal"
                    cols="12"
                    sm="12"
                    md="4"
                  >
                    <v-text-field
                      label="Gasto jornales"
                      hint="Gasto jornales"
                      v-model="costoDirectoCampos.gastos"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      append-icon="mdi-currency-usd"
                      @blur="formatCurrency('costoDirectoCampos','gastos')"
                      :onkeypress="regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="9"
                    sm="12"
                  ></v-col>
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
                      @click="agregarCostoDirecto"
                    >Agregar costo</v-btn>
                  </v-col>

                  <!-- Listado de costos directos agregados -->
                  <v-col
                    cols="12"
                    sm="12"
                    md="12"
                  >
                  <v-data-table
                    :headers="costoDirectoHeader"
                    :items="costosDirectos"
                    class="elevation-1"
                  >
                    <template v-slot:top>
                    </template>
                    <template v-slot:item.actions="{ item }">
                      <v-icon
                        small
                        @click="deleteCostoDirecto(item)"
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
                ref="formCostoInDirect"
                v-model="validFormCostoInDirect"
              >
                <v-row dense class="section mt-5">
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Costos indirectos</p>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="6"
                  >
                    <v-autocomplete
                      label="Rubro"
                      hint="Rubro"
                      :items="tipoCostoInDirecto"
                      v-model="costoIndirectoCampo.tipoCostoInDirecto"
                      item-value="codrubro"
                      item-text="rubros"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="6"
                  >
                    <v-text-field
                      label="Costo generado en pesos colombianos"
                      hint="Costo generado en pesos colombianos"
                      v-model="costoIndirectoCampo.costo"
                      dense
                      outlined
                      solo
                      flat
                      filled
                      :onkeypress="regexNumber"
                      append-icon="mdi-currency-usd"
                      @blur="formatCurrency('costoIndirectoCampo','costo')"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="9"
                    sm="12"
                  ></v-col>
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
                      @click="agregarCostoIndirecto"
                    >Agregar costo</v-btn>
                  </v-col>

                  <!-- Listado de costos indirectos agregados a la especie agro -->
                  <v-col
                    cols="12"
                    sm="12"
                    md="12"
                  >
                  <v-data-table
                    :headers="costoIndirectoHeader"
                    :items="costosIndirectos"
                    class="elevation-1"
                  >
                    <template v-slot:top>

                    </template>
                    <template v-slot:item.actions="{ item }">
                      <v-icon
                        small
                        @click="deleteCostoIndirecto(item)"
                      >
                      mdi-delete
                      </v-icon>
                    </template>
                  </v-data-table>
                  </v-col>
                </v-row>
              </v-form>

              <v-row
                dense
                class="section mt-5"
                v-if="verDatosCredito"
              >
                <v-col
                  cols="12"
                  md="12"
                  sm="12"
                >
                  <p class="color-black font-weight-bold">Datos de crédito</p>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-autocomplete
                    label="¿Qué entidad bancaria le dio el crédito?"
                    hint="¿Qué entidad bancaria le dio el crédito?"
                    :items="entidadesBancarias"
                    v-model="agropecuario.idEntidadesBancarias"
                    item-value="codentcredito"
                    item-text="entcredito"
                    dense
                    solo
                    flat
                    clearable
                    outlined
                    filled
                    >
                  </v-autocomplete>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-text-field
                    label="¿(%) costos de cultivo que cubrió con el crédito?"
                    hint="¿(%) costos de cultivo que cubrió con el crédito?"
                    v-model="agropecuario.porceCostoCredito"
                    type="number"
                    dense
                    solo
                    flat
                    outlined
                    filled
                  ></v-text-field>
                </v-col>
              </v-row>

              <v-row
                dense
                class="section mt-5"
                v-if="verDatosAeguramiento"
              >
                <v-col
                  cols="12"
                  md="12"
                  sm="12"
                >
                  <p class="color-black font-weight-bold">Datos de aseguramiento</p>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-text-field
                    label="Valor del cultivo asegurado"
                    hint="Valor del cultivo asegurado"
                    v-model="agropecuario.valCultiAsegurado"
                    dense
                    solo
                    flat
                    outlined
                    filled
                    append-icon="mdi-currency-usd"
                    @blur="formatCurrency('agropecuario','valCultiAsegurado')"
                    :onkeypress="regexNumber"
                  ></v-text-field>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-autocomplete
                    label="Tipo de seguro"
                    hint="Tipo de seguro"
                    :items="tiposSeguro"
                    v-model="agropecuario.tipoSeguro"
                    item-value="codtipseguro"
                    item-text="tipseguro"
                    dense
                    solo
                    flat
                    clearable
                    outlined
                    filled
                  ></v-autocomplete>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-text-field
                    label="Porcentaje de resiembra"
                    hint="Porcentaje de resiembra"
                    v-model="agropecuario.porceResiembra"
                    dense
                    outlined
                    solo
                    flat
                    filled
                    :onkeypress="regexNumber"
                  ></v-text-field>
                </v-col>
              </v-row>

              <v-row dense class="section mt-5">
                <v-col
                  cols="12"
                  sm="12"
                  md="12"
                  class="ml-1"
                >
                  <v-switch
                    v-model="agropecuario.afectaMaquinaria"
                    inset
                    label="Afectaciones en maquinaria, equipo e insumos agrícolas almacenados"
                    @click="afectacionMaquinaria"
                  ></v-switch>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-autocomplete
                    v-if="agropecuario.afectaMaquinaria"
                    label="Tipo de maquinaria"
                    hint="Tipo de maquinaria"
                    :items="infraEstructuraTipo"
                    v-model="idTipoMaquinaria"
                    item-value="codInfraestructura"
                    item-text="infraestructura"
                    dense
                    solo
                    flat
                    clearable
                    outlined
                    filled
                    @change="mostrarTipoInfraestructura()"
                    >
                  </v-autocomplete>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-btn
                    v-if="agropecuario.afectaMaquinaria"
                    fab
                    dark
                    small
                    class="mx-2 background-primary-dark"
                    @click="addInfraestructura"
                  >
                    <v-icon dark>
                      mdi-plus
                    </v-icon>
                  </v-btn>
                </v-col>

                <v-row class="mt-1">
                  <!-- Listado de infraestructura semilla -->
                  <v-col
                    v-if="dataTableSemilla.length > 0"
                    cols="12"
                    sm="12"
                    md="6"
                  >
                    <p
                      class="color-black font-weight-bold"
                      align="center"
                      justify="center"
                    >Semilla</p>
                    <v-data-table
                      :headers="semillaHeader"
                      :items="dataTableSemilla"
                      class="elevation-1"
                    >
                      <template v-slot:top>
                      </template>
                      <template v-slot:item.actions="{ item }">
                        <v-icon
                          small
                          @click="deleteSemilla(item)"
                        >
                        mdi-delete
                        </v-icon>
                      </template>
                    </v-data-table>
                  </v-col>

                  <!-- Listado de infraestructura fertilizante -->
                  <v-col
                    v-if="dataTableFertilizante.length > 0"
                    cols="12"
                    sm="12"
                    md="6"
                  >
                    <p
                      class="color-black font-weight-bold"
                      align="center"
                      justify="center"
                    >Fertilizante</p>
                  <v-data-table
                    :headers="fertilizanteHeader"
                    :items="dataTableFertilizante"
                    class="elevation-1"
                  >
                    <template v-slot:top>
                    </template>
                    <template v-slot:item.actions="{ item }">
                      <v-icon
                        small
                        @click="deleteFertilizante(item)"
                      >
                      mdi-delete
                      </v-icon>
                    </template>
                  </v-data-table>
                  </v-col>

                  <!-- Listado de infraestructura plaguicida -->
                  <v-col
                    v-if="dataTablePlaguicida.length > 0"
                    cols="12"
                    sm="12"
                    md="6"
                  >
                    <p
                      class="color-black font-weight-bold"
                      align="center"
                      justify="center"
                    >Plaguicida</p>
                  <v-data-table
                    :headers="plaguicidaHeader"
                    :items="dataTablePlaguicida"
                    class="elevation-1"
                  >
                    <template v-slot:top>
                    </template>
                    <template v-slot:item.actions="{ item }">
                      <v-icon
                        small
                        @click="deletePlaguicida(item)"
                      >
                      mdi-delete
                      </v-icon>
                    </template>
                  </v-data-table>
                  </v-col>

                  <!-- Listado de infraestructura maquinaria -->
                  <v-col
                    v-if="dataTableMaquinaria.length > 0"
                    cols="12"
                    sm="12"
                    md="6"
                  >
                    <p
                      class="color-black font-weight-bold"
                      align="center"
                      justify="center"
                    >Maquinaria</p>
                  <v-data-table
                    :headers="maquinariaHeader"
                    :items="dataTableMaquinaria"
                    class="elevation-1"
                  >
                    <template v-slot:top>
                    </template>
                    <template v-slot:item.actions="{ item }">
                      <v-icon
                        small
                        @click="deleteMaquinaria(item)"
                      >
                      mdi-delete
                      </v-icon>
                    </template>
                  </v-data-table>
                  </v-col>
                </v-row>
              </v-row>

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
                    @click="guardarAgropecuario()"
                  >
                    Guardar sistema
                  </v-btn>
                </v-col>
              </v-row>
            </v-container>
            <!-- <small>*indicates required field</small> -->
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-container>

    <v-container>
      <v-dialog
        v-model="modalMaquinaria"
        persistent
        max-width="80%"
      >
        <v-card
          class="border-basic"
          flat
        >
          <div style="text-align:right">
            <v-btn class="color-primary-dark" icon dark @click="modalMaquinaria = false">
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
                  <center>{{ nombreMaquinariaSelect }}</center>
                </v-col>
              </v-row>
            </v-container>
          </v-card-title>

          <v-card-text>
            <v-form
              lazy-validation
              ref="formInfraestructura"
              v-model="validInfraestructura"
            >
              <v-container v-if="verCamposSemilla">
                <v-row
                  dense
                  class="section"
                >
                  <v-col
                    cols="12"
                    sm="12"
                    md="12"
                  ></v-col>
                  <!-- <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="Especie"
                      hint="Especie"
                      v-model="semilla.especie"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-text-field>
                  </v-col> -->
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿Cuál es el nombre del cultivo?"
                      hint="¿Cuál es el nombre del cultivo?"
                      :items="tipoCultivo"
                      v-model="semilla.tipoCultivo"
                      :search-input.sync="semilla.nameTipoCultivo"
                      item-value="codcultivo"
                      item-text="tipocultivo"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="Cantidad de semilla almacenada"
                      hint="Cantidad de semilla almacenada"
                      v-model="semilla.canSemillas"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      :onkeypress="regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="Valor en pesos de la afectación"
                      hint="Valor en pesos de la afectación"
                      v-model="semilla.valPesos"
                      dense
                      solo
                      flat
                      outlined
                      append-icon="mdi-currency-usd"
                      @blur="formatCurrency('semilla','valPesos')"
                      filled
                      :onkeypress="regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-text-field>
                  </v-col>
                </v-row>
                <v-row dense class="section mt-5">
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Material de la siembra</p>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿Qué tipo de material utilizó para la siembra?"
                      hint="¿Qué tipo de material utilizó para la siembra?"
                      :items="materiralSiembra"
                      v-model="semilla.materiralSiembra"
                      item-value="codmaterial"
                      item-text="material"
                      :search-input.sync="semilla.nameTipoMaterial"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                      >
                    </v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="¿Cantidad semillas utilizadas en la siembra?"
                      hint="¿Cantidad semillas utilizadas en la siembra?"
                      v-model="semilla.cantSemillas"
                      type="number"
                      dense
                      outlined
                      solo
                      flat
                      filled
                      :onkeypress="regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿Unidad para reportar la cantidad de semilla?"
                      hint="¿Unidad para reportar la cantidad de semilla?"
                      :items="medidaSemilla"
                      v-model="semilla.medidaSemilla"
                      item-value="codundcosecha"
                      item-text="undcosecha"
                      :search-input.sync="semilla.nameMedidaSemilla"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    v-if="verCampoCargaSemilla"
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿Equivalencia en kilos de la carga?"
                      hint="¿Equivalencia en kilos de la carga?"
                      :items="equivaleKilos"
                      v-model="semilla.equivaleKilos"
                      item-value="codequivcarga"
                      item-text="eqvcargakg"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    v-if="verOtraUnidadSemilla"
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                      label="ingrese la otra equivalencia"
                      hint="ingrese la otra equivalencia"
                      v-model="semilla.nuevaEquivalencia"
                      type="number"
                      dense
                      outlined
                      solo
                      flat
                      filled
                      :onkeypress="regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="¿Cuál es la fuente de la semilla?"
                      hint="¿Cuál es la fuente de la semilla?"
                      :items="fuenteSemilla"
                      v-model="semilla.fuenteSemilla"
                      item-value="codfuensemilla"
                      item-text="fuensemilla"
                      :search-input.sync="semilla.nameFuenteSemilla"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="required"
                    ></v-autocomplete>
                  </v-col>
                </v-row>
              </v-container>

              <v-row
                v-if="verCamposFertilizante"
                dense class="section"
              >
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-autocomplete
                    label="Tipo de fertilizante"
                    hint="Tipo de fertilizante"
                    :items="tiposFertilizantes"
                    v-model="fertilizante.idTipoFertilizante"
                    item-value="codfertilizante"
                    item-text="tipofertilizante"
                    :search-input.sync="fertilizante.nameTipoFertilizante"
                    dense
                    solo
                    flat
                    clearable
                    outlined
                    filled
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="required"
                  ></v-autocomplete>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-text-field
                    label="Nombre"
                    hint="Nombre"
                    v-model="fertilizante.nombre"
                    dense
                    solo
                    flat
                    outlined
                    filled
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="required"
                  ></v-text-field>
                </v-col>
                <v-menu
                  v-model="fertilizante.menuFechaAdquisicion"
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
                      >
                      <v-text-field
                        v-model="fertilizante.fechaAdquisicion"
                        label="Fecha adquisición"
                        hint="Fecha adquisición"
                        readonly
                        v-bind="attrs"
                        v-on="on"
                        dense
                        solo
                        flat
                        outlined
                        filled
                        prepend-inner-icon="mdi-decagram"
                        required
                        :rules="required"
                      ></v-text-field>
                    </v-col>

                  </template>
                  <v-col
                    cols="12"
                    md="4"
                    >
                    <v-date-picker
                        v-model="fertilizante.fechaAdquisicion"
                        @input="fertilizante.menuFechaAdquisicion = false"
                        outlined
                      ></v-date-picker>
                  </v-col>
                </v-menu>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-text-field
                    label="Cantidad de fertilizante afectado Kg o Litros"
                    hint="Cantidad de fertilizante afectado Kg o Litros"
                    type="number"
                    v-model="fertilizante.canFertilizante"
                    dense
                    solo
                    flat
                    outlined
                    filled
                    :onkeypress="regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="required"
                  ></v-text-field>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-text-field
                    label="Valor en pesos de los fertilizantes almacenados"
                    hint="Valor en pesos de los fertilizantes almacenados"
                    v-model="fertilizante.valPesos"
                    dense
                    solo
                    flat
                    append-icon="mdi-currency-usd"
                    @blur="formatCurrency('fertilizante','valPesos')"
                    outlined
                    filled
                    :onkeypress="regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="required"
                  ></v-text-field>
                </v-col>
              </v-row>

              <v-row
                v-if="verCamposPlaguicidas"
                dense class="section"
              >
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-autocomplete
                    label="Tipo de plaguicida almacenado"
                    hint="Tipo de plaguicida almacenado"
                    :items="tiposPlaguicidas"
                    v-model="plaguicidas.idTipoPlaguicida"
                    item-value="codplaguicida"
                    item-text="tipoplaguicida"
                    :search-input.sync="plaguicidas.nameTipoPlaguicida"
                    dense
                    solo
                    flat
                    clearable
                    outlined
                    filled
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="required"
                  ></v-autocomplete>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-autocomplete
                    label="Presentación"
                    hint="Presentación"
                    :items="presentacion"
                    v-model="plaguicidas.idTipoPresentacion"
                    item-value="codpresentacion"
                    item-text="presentacion"
                    :search-input.sync="plaguicidas.nameTipoPresentacion"
                    solo
                    flat
                    clearable
                    dense
                    outlined
                    filled
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="required"
                  ></v-autocomplete>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-text-field
                    label="Cantidad de plaguicidas almacenados afectados (Kg)"
                    hint="Cantidad de plaguicidas almacenados afectados (Kg)"
                    persistent-hint
                    v-model="plaguicidas.cantPlaguicidaKg"
                    type="number"
                    dense
                    solo
                    flat
                    outlined
                    filled
                    :onkeypress="regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="required"
                  ></v-text-field>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-text-field
                    label="Cantidad de plaguicidas almacenados afectados (Litros)"
                    hint="Cantidad de plaguicidas almacenados afectados (Litros)"
                    persistent-hint
                    v-model="plaguicidas.cantPlaguicidaLt"
                    type="number"
                    dense
                    solo
                    flat
                    outlined
                    filled
                    :onkeypress="regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="required"
                  ></v-text-field>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-text-field
                    label="Valor en pesos de la afectación"
                    hint="Valor en pesos de la afectación"
                    v-model="plaguicidas.valPesos"
                    dense
                    outlined
                    solo
                    flat
                    append-icon="mdi-currency-usd"
                    @blur="formatCurrency('plaguicidas','valPesos')"
                    filled
                    :onkeypress="regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="required"
                  ></v-text-field>
                </v-col>
              </v-row>

              <v-row
                dense
                class="section"
                v-if="verCamposMaquinaria"
              >
                <v-col
                  cols="12"
                  sm="12"
                  md="12"
                >
                  <v-chip
                    v-if="verCamposMaquinaria"
                    dense class="section"
                  >
                    Edad del equipo en años: {{ calcularEdadEquipo }}
                  </v-chip>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-autocomplete
                    label="Tipo de maquinaria agrícola afectada"
                    hint="Tipo de maquinaria agrícola afectada"
                    :items="tipoMaquinariaAgricola"
                    v-model="maquinaria.idTipoMaquinariaAgricola"
                    item-value="codMaquinaria"
                    item-text="maquinaria"
                    :search-input.sync="maquinaria.nameTipoMaquinaria"
                    dense
                    solo
                    flat
                    clearable
                    outlined
                    filled
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="required"
                  ></v-autocomplete>
                </v-col>
                <v-menu
                  v-model="menuFechaAno"
                  ref="menu"
                  :close-on-content-click="false"
                  :nudge-right="40"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                  >
                  <template v-slot:activator="{ on, attrs }">

                    <v-col
                      cols="12"
                      sm="6"
                      md="4"
                    >
                      <v-text-field
                        v-model="maquinaria.anoAdquisicion"
                        label="Año de adquisición del equipo"
                        hint="Año de adquisición del equipo"
                        readonly
                        v-bind="attrs"
                        v-on="on"
                        dense
                        solo
                        flat
                        outlined
                        clearable
                        filled
                        prepend-inner-icon="mdi-decagram"
                        required
                        :rules="required"
                      ></v-text-field>
                    </v-col>

                  </template>
                  <v-col
                    cols="12"
                    md="4"
                    >
                    <v-date-picker
                        v-model="maquinaria.anoAdquisicion"
                        ref="picker"
                        outlined
                        @click:year="saveYear()"
                        @click:month="false"
                      ></v-date-picker>
                  </v-col>
                </v-menu>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-text-field
                    label="Valor en pesos de la afectación"
                    hint="Valor en pesos de la afectación"
                    v-model="maquinaria.valorPesos"
                    dense
                    solo
                    flat
                    append-icon="mdi-currency-usd"
                    @blur="formatCurrency('maquinaria','valorPesos')"
                    outlined
                    filled
                    :onkeypress="regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="required"
                  ></v-text-field>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="4"
                >
                  <v-text-field
                    label="¿% en que disminuyó su producción por la afectación de la maquinaria?"
                    hint="¿% en que disminuyó su producción por la afectación de la maquinaria?"
                    v-model="maquinaria.porceDisminucion"
                    dense
                    solo
                    flat
                    outlined
                    filled
                    :onkeypress="regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="required"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              class="background-primary-dark button-basic"
              elevation="2"
              raised
              depressed
              @click="modalMaquinaria = false"
            >Cerrar</v-btn>
            <v-btn
              class="background-primary-dark button-basic"
              elevation="2"
              raised
              depressed
              @click="agregarTipoInfraestructura()"
            >Agregar</v-btn>

          </v-card-actions>
        </v-card>

      </v-dialog>
    </v-container>

  </div>
</template>

<script>

import { getData } from '../../indexedDb/getData';
import { newEvent } from '../../services/api.js';

export default {
  name: 'agropecuario',
  props: ['obtenerDataAgro', 'departamento'],
  data() {
    return {
      dialogAgropecuario: false,
      validFormSectionOne: true,
      validFormCostoDirect: true,
      validFormCostoInDirect: true,
      validInfraestructura: true,
      expanded: [],

      agroHeader: [
        { text: 'Especie Agropecuaria', align: 'start', sortable: false, value: 'nameTipoCultivo' },
        { text: 'Unidad de área', align: 'start', sortable: false, value: 'nameUnidadArea' },
        { text: 'Área del cultivo', align: 'start', sortable: false, value: 'areaCultivo' },
        { text: 'Material siembra', align: 'start', sortable: false, value: 'nameMateriralSiembra' },
        { text: 'Acciones', value: 'actions', sortable: false, width: '2%' },
      ],
      especiesAgropecuario: [],
      costoDirectoHeader: [
        { text: 'Actividad', align: 'start', sortable: false, value: 'actividad' },
        { text: 'No.Jornales', align: 'start', sortable: false, value: 'noJornales' },
        { text: 'Gasto', align: 'start', sortable: false, value: 'gastos' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      costosDirectos: [],
      costoIndirectoHeader: [
        { text: 'Rubro', align: 'start', sortable: false, value: 'actividad' },
        { text: 'Costo', align: 'start', sortable: false, value: 'costo' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      costosIndirectos: [],
      semillaHeader: [
        { text: 'Tipo cultivo', align: 'start', sortable: false, value: 'nameTipoCultivo' },
        { text: 'Cant.Semilla', align: 'start', sortable: false, value: 'canSemillas' },
        { text: 'Val.Pesos', align: 'start', sortable: false, value: 'valPesos' },
        { text: 'Material', align: 'start', sortable: false, value: 'materiralSiembra' },
        { text: 'Material siembra', align: 'start', sortable: false, value: 'nameTipoMaterial' },
        { text: 'Cantidad', align: 'start', sortable: false, value: 'cantSemillas' },
        { text: 'Unidad medida', align: 'start', sortable: false, value: 'nameMedidaSemilla' },
        { text: 'Fuente', align: 'start', sortable: false, value: 'nameFuenteSemilla' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      dataTableSemilla: [],
      fertilizanteHeader: [
        { text: 'Tipo', align: 'start', sortable: false, value: 'nameTipoFertilizante' },
        { text: 'Nombre', align: 'start', sortable: false, value: 'nombre' },
        { text: 'Fch.Adquisición', align: 'start', sortable: false, value: 'fechaAdquisicion' },
        { text: 'Cant.Fertilizante', align: 'start', sortable: false, value: 'canFertilizante' },
        { text: 'Val.Pesos', align: 'start', sortable: false, value: 'valPesos' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      dataTableFertilizante: [],
      plaguicidaHeader: [
        { text: 'Tipo', align: 'start', sortable: false, value: 'nameTipoPlaguicida' },
        { text: 'Presentación', align: 'start', sortable: false, value: 'nameTipoPresentacion' },
        { text: 'Cant.Plaguicida Kg', align: 'start', sortable: false, value: 'cantPlaguicidaKg' },
        { text: 'Cant.Plaguicida Lt', align: 'start', sortable: false, value: 'cantPlaguicidaLt' },
        { text: 'Val.Pesos', align: 'start', sortable: false, value: 'valPesos' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      dataTablePlaguicida: [],
      maquinariaHeader: [
        { text: 'Tipo', align: 'start', sortable: false, value: 'nameTipoMaquinaria' },
        { text: 'Año aduisición', align: 'start', sortable: false, value: 'anoAdquisicion' },
        { text: 'Val.Pesos', align: 'start', sortable: false, value: 'valorPesos' },
        { text: '%Disminución', align: 'start', sortable: false, value: 'porceDisminucion' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      dataTableMaquinaria: [],

      agropecuario: {},
      tipoCultivo: [],
      unidadArea: [],
      materiralSiembra: [],
      cantSemillas: [],
      medidaSemilla: [],
      equivaleKilos: [],
      fuenteSemilla: [],
      medidaCantCosechada: [],
      equivaleKilosCosecha: [],
      medidaReportar: [],
      equivaleKilosReportar: [],
      costoDirectoCampos: {},
      costoIndirectoCampo: {},
      tipoCostoDirecto: [],
      tipoCostoInDirecto: [],
      entidadesBancarias: [],
      idEntidadesBancarias: '',
      tiposSeguro: [],
      infraEstructuraTipo: [],
      idTipoMaquinaria: '',
      modalMaquinaria: false,
      maquinariasHeaders: [],
      maquinarias: [],
      nombreMaquinariaSelect: '',
      semilla: {},
      verSemilla: false,
      fertilizante: {},
      tiposFertilizantes:[],
      plaguicidas: {},
      tiposPlaguicidas:[],
      presentacion: [],
      maquinaria: {},
      tipoMaquinariaAgricola: [],
      menuFechaAno: false,
      calcularEdadEquipo: 0,
      gastosAutomaticos: {},
      editedIndex: -1,

      regexNumber: "return (event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46)",
      required: [v => !!v || 'Campo requerido',],
    }
  },
  async mounted () {
    await this.dataAgropecuario();
    await this.edicionAgropecuario();
  },
  watch: {
    menuFechaAno (val) {
      console.log(val);
      val && this.$nextTick(() => (this.$refs.picker.activePicker = 'YEAR'))
    }
  },
  methods: {
    async dataAgropecuario() {
      try {
        const res = await getData('agricola', true);
        this.addDataCampos(res);

      } catch (error) {
        console.log(error);
      }
    },
    edicionAgropecuario() {
      const dataEvento = this.$route.params.evento;
      if (dataEvento !== undefined) {
        if (dataEvento.dataEspecies.agropecuario.length > 0) {
          this.especiesAgropecuario = dataEvento.dataEspecies.agropecuario;
        }
      }
    },
    addDataCampos(data) {
      this.tipoCultivo = data.cropType;
      this.unidadArea = data.areaUnity;
      this.materiralSiembra = data.plantingMaterial;
      this.medidaSemilla = data.harvestUnity;
      this.equivaleKilos = data.equivCharge;
      this.fuenteSemilla = data.seedSource;
      this.medidaCantCosechada = data.harvestUnity;
      this.equivaleKilosCosecha = data.equivCharge;
      this.medidaReportar = data.harvestUnity;
      this.equivaleKilosReportar = data.equivCharge;
      this.tipoCostoDirecto = data.directCosts;
      this.tipoCostoInDirecto = data.indirectCosts;
      this.entidadesBancarias = data.bankingEntity;
      this.tiposSeguro = data.assruanceType;
      this.infraEstructuraTipo = data.infraestructureType;
      this.tiposFertilizantes = data.fertilizerType;
      this.tiposPlaguicidas =data.pesticideType;
      this.presentacion =data.presentation;
      this.tipoMaquinariaAgricola =data.machineryData;
    },
    agregarCostoDirecto() {
      if (this.$refs.formCostoDirect.validate()) {
        const idTipoCostoDirecto = this.costoDirectoCampos.idTipoCostoDirecto;
        let name = this.tipoCostoDirecto.filter(tipoCosto => tipoCosto.codtipactividad === idTipoCostoDirecto);
        this.costoDirectoCampos.actividad = name[0]['tipactividad'];
        this.costosDirectos.push(this.costoDirectoCampos);
        this.costoDirectoCampos = {};
      }
    },
    deleteCostoDirecto(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar costo directo?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          const editedIndexCostoDirecto = this.costosDirectos.indexOf(item);
          this.costosDirectos.splice(editedIndexCostoDirecto, 1);
        }
      })
    },
    agregarCostoIndirecto() {
      if (this.$refs.formCostoInDirect.validate()) {
        const idTipoCostoInDirecto = this.costoIndirectoCampo.tipoCostoInDirecto;
        let name = this.tipoCostoInDirecto.filter(tipoCosto => tipoCosto.codrubro === idTipoCostoInDirecto);
        this.costoIndirectoCampo.actividad = name[0]['rubros'];
        this.costosIndirectos.push(this.costoIndirectoCampo);
        this.costoIndirectoCampo = {};
      }
    },
    deleteCostoIndirecto(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar costo indirecto?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          const editedIndexCostoInDirecto = this.costosIndirectos.indexOf(item);
          this.costosIndirectos.splice(editedIndexCostoInDirecto, 1);
        }
      })
    },
    mostrarTipoInfraestructura() {
      this.modalMaquinaria = true;
      const idTipoMaquinaria = this.idTipoMaquinaria;
      let name = this.infraEstructuraTipo.filter(maquinaria => maquinaria.codInfraestructura === idTipoMaquinaria);
      this.nombreMaquinariaSelect = name[0]['infraestructura'];
    },
    addInfraestructura() {
      if (this.idTipoMaquinaria) {
        this.mostrarTipoInfraestructura();
      }
    },
    agregarTipoInfraestructura() {
      if(this.$refs.formInfraestructura.validate()) {
        const idTipoMaquinaria = parseInt(this.idTipoMaquinaria);

        if (idTipoMaquinaria === 1) {
          this.dataTableSemilla.push(this.semilla);
          this.semilla = {};
        }
        if (idTipoMaquinaria === 2) {
          this.dataTableFertilizante.push(this.fertilizante);
          this.fertilizante = {};
        }
        if (idTipoMaquinaria === 3) {
          this.dataTablePlaguicida.push(this.plaguicidas);
          this.plaguicidas = {};
        }
        if (idTipoMaquinaria === 4) {
          this.dataTableMaquinaria.push(this.maquinaria);
          this.maquinaria = {};
          this.calcularEdadEquipo = 0;
        }

        this.modalMaquinaria = false;
      }
    },
    deleteSemilla(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar semilla?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          const editedIndexSemilla = this.dataTableSemilla.indexOf(item);
          this.dataTableSemilla.splice(editedIndexSemilla, 1);
        }
      })
    },
    deleteFertilizante(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar fertilizante?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          const editedIndexFertilizante = this.dataTableFertilizante.indexOf(item);
          this.dataTableFertilizante.splice(editedIndexFertilizante, 1);
        }
      })
    },
    deletePlaguicida(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar plaguicida?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          const editedIndexPlaguicida = this.dataTablePlaguicida.indexOf(item);
          this.dataTablePlaguicida.splice(editedIndexPlaguicida, 1);
        }
      })
    },
    deleteMaquinaria(item) {
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
          const editedIndexMaquinaria = this.dataTableMaquinaria.indexOf(item);
          this.dataTableMaquinaria.splice(editedIndexMaquinaria, 1);
        }
      })
    },
    saveYear() {
      const ano = this.$refs.picker.$data.inputYear;
      this.maquinaria.anoAdquisicion = ano+''+'';

      // Reset activePicker to type YEAR
      this.$refs.picker.activePicker = 'YEAR';

      // Close the menu/datepicker
      this.menuFechaAno = false;

      const fechaActual = new Date();
      const anoActual = fechaActual.getFullYear();
      this.calcularEdadEquipo = anoActual > ano  ? anoActual - ano : 0;
    },
    guardarAgropecuario() {
      if (this.$refs.formSectionOne.validate()) {
        if (this.costosDirectos.length === 0 || this.costosIndirectos.length === 0) {
          this.$swal({
            icon: 'error',
            text: 'No se han registrados costos directos o indirectos.',
            confirmButtonText: 'Aceptar',
          });
          return;
        }
        this.agropecuario.costosDirectos = this.costosDirectos;
        this.agropecuario.costosInDirectos = this.costosIndirectos;
        this.agropecuario.tipoInfraSemilla = this.dataTableSemilla;
        this.agropecuario.tipoInfraFertilizante = this.dataTableFertilizante;
        this.agropecuario.tipoInfraPlaguicidas = this.dataTablePlaguicida;
        this.agropecuario.tipoInfraMaquinaria = this.dataTableMaquinaria;

        if (this.editedIndex > -1) {
          Object.assign(this.especiesAgropecuario[this.editedIndex], this.agropecuario)
        } else {
          this.especiesAgropecuario.push(this.agropecuario);
        }

        this.obtenerDataAgro(this.especiesAgropecuario);
        this.limpiarCampos();
      }
    },
    afectacionMaquinaria() {
      if (!this.agropecuario.afectaMaquinaria) {
        this.dataTableSemilla = [];
        this.dataTableFertilizante = [];
        this.dataTablePlaguicida = [];
        this.dataTableMaquinaria = [];
      }
    },
    editarEspecieAgro(item) {
      console.log(item);
      console.log(item.costosInDirectos);
      this.editedIndex = this.especiesAgropecuario.indexOf(item);
      this.costosDirectos = item.costosDirectos;
      this.costosIndirectos = item.costosInDirectos;
      this.dataTableSemilla = item.tipoInfraSemilla;
      this.dataTableFertilizante = item.tipoInfraFertilizante;
      this.dataTablePlaguicida = item.tipoInfraPlaguicidas;
      this.dataTableMaquinaria = item.tipoInfraMaquinaria;
      this.agropecuario = Object.assign({}, item);
      this.dialogAgropecuario = true;
    },
    deleteEspecieAgro(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar sistema agropecuario?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          const editedIndex = this.especiesAgropecuario.indexOf(item);
          this.especiesAgropecuario.splice(editedIndex, 1);
          this.obtenerDataAgro(this.especiesAgropecuario);
        }
      })
    },
    async consultarGasto() {
      const dataGasto = {"dpto":this.departamento, "especie":this.agropecuario.nombreCultivo};
      if (!dataGasto['dpto'] || !dataGasto['especie']) {
        return;
      }

      try {
        const res = await newEvent.getAgroCalc(dataGasto);

        if (res.status === 200) {
            this.gastosAutomaticos = res.data.message;
            this.asignarGastoAutomatico();
        } else {
          this.$swal({
            icon: 'error',
            text: res.message,
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
    asignarGastoAutomatico() {

      if (Object.keys(this.gastosAutomaticos).length > 0) {
        if (this.gastosAutomaticos.gasto.length > 0) {
          if (this.costoDirectoCampos.idTipoCostoDirecto) {

            const idTipoCosto = this.costoDirectoCampos.idTipoCostoDirecto;

            const gasto = this.gastosAutomaticos.gasto.filter(
              item=> item.cod_tipo_actividad == idTipoCosto
            );
            const jornal = this.gastosAutomaticos.jornales.filter(
              function(item) {
                if (item.cod_tipo_actividad === '4,5,6,7') {
                  return item.cod_tipo_actividad.split(',').includes(idTipoCosto.toString());
                } else {
                  return item.cod_tipo_actividad == idTipoCosto;
                }
              }
            );

            if (this.gastosAutomaticos.costoPromJonal.length > 0) {
              this.agropecuario.costoPromeJornal = this.gastosAutomaticos.costoPromJonal[0].valor;
            }
            if (gasto.length > 0) {
              this.costoDirectoCampos.gastos = gasto[0].valor * jornal[0].valor;
            }
            if (jornal.length > 0) {
              this.costoDirectoCampos.noJornales = jornal[0].valor;
            }
          }
        } else {
          this.agropecuario.costoPromeJornal = '';
          this.costoDirectoCampos.gastos = '';
          this.costoDirectoCampos.noJornales = '';
          this.gastosAutomaticos = {};
        }
      }
    },
    cerrarModal() {
      this.limpiarCampos();
    },
    limpiarCampos() {
      this.agropecuario = {};
      this.costosDirectos = [];
      this.costosIndirectos = [];
      this.dataTableSemilla = [];
      this.dataTableFertilizante = [];
      this.dataTablePlaguicida = [];
      this.dataTableMaquinaria = [];
      this.gastosAutomaticos = {};
      this.editedIndex = -1;
      this.dialogAgropecuario = false;
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
    calcularHectareaSegunArea() {
      var hectarea = 0;

      if (this.agropecuario.unidadArea === 3 ) {// metros
        hectarea = this.agropecuario.areaCultivo * 0.0001;
      }
      if (this.agropecuario.unidadArea === 2 ) {// fanegada
        hectarea = this.agropecuario.areaCultivo * 0.64;
      }
      if (this.agropecuario.unidadArea === 1 ) {// hectarea
        hectarea = this.agropecuario.areaCultivo;
      }
      if (this.agropecuario.unidadArea === 4 ) {// otro
        hectarea = (this.agropecuario.areaCultivo  * this.agropecuario.nuevaunidadmetros) / 10000;
      }

      return hectarea ? hectarea: 0;
    },
    verCampoCarga() {
      var estado = false;
      if (this.agropecuario.medidaSemilla) {
        estado =  this.agropecuario.medidaSemilla === 4 ? true : false;
      }
      return estado;
    },
    verCampoCargaCosecha() {
      var estado = false;
      if (this.agropecuario.medidaCantCosechada) {
        estado =  this.agropecuario.medidaCantCosechada === 4 ? true : false;
      }
      return estado;
    },
    verCampoCargaReportar() {
      var estado = false;
      if (this.agropecuario.medidaReportar) {
        estado =  this.agropecuario.medidaReportar === 4 ? true : false;
      }
      return estado;
    },
    verGastoJornal() {
      const ids  = [1,2,3];
      var estado = false;

      if (this.costoDirectoCampos.idTipoCostoDirecto) {
        estado = ids.includes(this.costoDirectoCampos.idTipoCostoDirecto);
      }
      return estado;
    },
    verDatosCredito() {
      var estado = false;
      let costo  = this.costosIndirectos.filter((costo)=>costo.tipoCostoInDirecto === 7 && parseFloat(costo.costo) > 0);

      if (costo.length > 0) {
        estado = true;
      }
      return estado;
    },
    verDatosAeguramiento() {
      var estado = false;
      let costo  = this.costosIndirectos.filter((costo)=>costo.tipoCostoInDirecto === 4 && parseFloat(costo.costo) > 0);

      if (costo.length > 0) {
        estado = true;
      }
      return estado;
    },
    verCamposSemilla() {
      var estado = false;
      if (this.idTipoMaquinaria) {
        estado =  this.idTipoMaquinaria === 1 ? true : false;
      }
      return estado;
    },
    verCamposFertilizante() {
      var estado = false;
      if (this.idTipoMaquinaria) {
        estado =  this.idTipoMaquinaria === 2 ? true : false;
      }
      return estado;
    },
    verCamposPlaguicidas() {
      var estado = false;
      if (this.idTipoMaquinaria) {
        estado =  this.idTipoMaquinaria === 3 ? true : false;
      }
      return estado;
    },
    verCamposMaquinaria() {
      var estado = false;
      if (this.idTipoMaquinaria) {
        estado =  this.idTipoMaquinaria === 4 ? true : false;
      }
      return estado;
    },
    verCampoCargaSemilla() {
      var estado = false;
      if (this.semilla.medidaSemilla === 4) {
        estado = true;
      } else {
        this.semilla.nuevaEquivalencia = null;
      }
      return estado;
    },
    verOtraUnidadSemilla() {
      var estado = false;
      if (this.semilla.medidaSemilla === 4 && this.semilla.equivaleKilos === 6) {
        estado = true;
      }
      return estado;
    },
  }
}
</script>

