<template>
  <div>

    <v-container>
      <v-row>
        <v-col
          cols="12"
        >
          <v-data-table
            :headers="especiesHeaders"
            :items="especies"
            class="elevation-2"
          >
            <template v-slot:top>
              <v-toolbar
                flat
                class="background-primary-dropdowns border-head-table font-weight-bold"
              >
                <span class="mr-2">Sistema forestal</span>

                <v-btn
                  class=" background-primary-dark"
                  elevation="2"
                  fab
                  dark
                  small
                  @click="dialog = true"
                >
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </v-toolbar>
            </template>
            <template v-slot:item.actions="{ item }">
              <v-icon
                small
                color="#004884"
                @click="editarEspecie(item)"
              >
              mdi-pencil
              </v-icon>
              <v-icon
                small
                color="#004884"
                @click="deleteEspecie(item)"
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
        v-model="dialog"
        persistent
        :overlay="false"
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
                  <center>Sistema forestal</center>
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
                <v-row dense class="section">
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                    class="mt-3"
                  >
                    <v-autocomplete
                      label="Fase productiva"
                      hint="Fase productiva"
                      :items="fasesProd"
                      v-model="esp.faseProd"
                      :search-input.sync="esp.nameFaseProd"
                      item-value="valor"
                      item-text="text"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      clearable
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                    ></v-autocomplete>
                  </v-col>

                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                    class="mt-3"
                  >
                    <v-autocomplete
                      label="Especie forestal afectada"
                      hint="Especie forestal afectada"
                      :items="espForestales"
                      v-model="esp.espAfectada"
                      :search-input.sync="esp.nameEspAfectada"
                      item-value="valor"
                      item-text="text"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      clearable
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                    class="mt-3"
                  >
                    <v-text-field
                      label="Nombre común"
                      hint="Nombre común"
                      v-model="esp.nombre"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                  >
                    <v-autocomplete
                      label="Objetivo de plantación"
                      hint="Objetivo de plantación"
                      :items="espObjetivos"
                      v-model="esp.objetivo"
                      :search-input.sync="esp.nameObjetivo"
                      item-value="valor"
                      item-text="text"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      clearable
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                    ></v-autocomplete>
                  </v-col>
                </v-row>

                <v-row
                  dense
                  class="section mt-5"
                  v-if="verDatosAdicionalesObjetivo"
                >
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Datos adicionales al objetivo</p>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                    >
                    <v-text-field
                      label="No.arboles antes de la afectación"
                      hint="No.arboles antes de la afectación"
                      v-model="esp.noArbolesAntesAfectacion"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                      :onkeypress="rules.regexNumber"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                  >
                    <v-text-field
                      label="No.entresacas o raleos a la fecha"
                      hint="No.entresacas o raleos a la fecha"
                      v-model="esp.noEntresacas"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                      :onkeypress="rules.regexNumber"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                  >
                    <v-text-field
                      label="Valor entresacas"
                      hint="Valor entresacas"
                      v-model="esp.valEntreSacas"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      append-icon="mdi-currency-usd"
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                      :onkeypress="rules.regexNumber"
                      @blur="formatCurrency('esp','valEntreSacas')"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                  >
                    <v-text-field
                      label="Porcentaje entresacas"
                      hint="Porcentaje entresacas"
                      v-model="esp.porceEntreSacas"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                      :onkeypress="rules.regexNumber"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                  >
                    <v-text-field
                      label="Diámetro promedio a la altura del pecho (m)"
                      hint="Diámetro promedio a la altura del pecho (m)"
                      v-model="esp.diametroPromedio"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                      :onkeypress="rules.regexNumber"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                  >
                    <v-text-field
                      label="Altura comercial (altura aprovechable del arbol)"
                      hint="Altura comercial (altura aprovechable del arbol)"
                      v-model="esp.alturaComercial"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                      :onkeypress="rules.regexNumber"
                      title="Es la altura aprovechable del arbol"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                  >
                    <v-text-field
                      label="Altura total"
                      hint="Altura total"
                      v-model="esp.alturaTotal"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                      :onkeypress="rules.regexNumber"
                      title="Es la altura de la base a la parte superior de la copa"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                  >
                    <v-text-field
                      label="Turno de plantación en años"
                      hint="Turno de plantación en años"
                      v-model="esp.plantacionAnos"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                      :onkeypress="rules.regexNumber"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                  >
                    <v-text-field
                      label="Porcentaje de árboles al finalizar el turno"
                      hint="Porcentaje de árboles al finalizar el turno"
                      v-model="esp.porceArbolesTurnoFinal"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                      :onkeypress="rules.regexNumber"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row dense class="section mt-5">
                  <v-menu
                    v-model="esp.menuFecha"
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
                        class="mt-3"
                      >
                        <v-text-field
                          v-model="esp.fecha"
                          label="Fecha establecimiento"
                          hint="Fecha establecimiento"
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
                      sm="12"
                    >
                      <v-date-picker
                        v-model="esp.fecha"
                        @input="esp.menuFecha = false"
                        outlined
                      ></v-date-picker>
                    </v-col>
                  </v-menu>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                    class="mt-3"
                  >
                    <v-text-field
                      label="Densidad siembra/hectarea"
                      hint="Densidad siembra/hectarea"
                      v-model="esp.densHectarea"
                      dense
                      solo
                      flat
                      outlined
                      filledf
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                    class="mt-3"
                  >
                    <v-text-field
                      label="Área sembrada/hectarea"
                      hint="Área sembrada/hectarea"
                      v-model="esp.areaSembrada"
                      dense
                      solo
                      flat
                      outlined
                      filled
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row dense class="section mt-5">
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Afectación</p>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                  >
                    <v-text-field
                      label="Área afectada en Hectareas"
                      hint="Área afectada en Hectareas"
                      v-model="esp.areaAfectadaHectareas"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      :onkeypress="rules.regexNumber"
                    ></v-text-field>
                  </v-col>
                  <v-menu
                    v-model="esp.menuFechaAfactaForestal"
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
                          v-model="esp.fechaAfactaForestal"
                          label="Fecha en el cual empezó a afectar el sistema forestal"
                          hint="Fecha en el cual empezó a afectar el sistema forestal"
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
                        v-model="esp.fechaAfactaForestal"
                        @input="esp.menuFechaAfactaForestal = false"
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
                      label="Tiempo en días que afectó el sistema forestal"
                      hint="Tiempo en días que afectó el sistema forestal"
                      type="number"
                      v-model="esp.diasAfectoSistemaForestal"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      :onkeypress="rules.regexNumber"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                  >
                    <v-text-field
                      label="Número de árboles afectados"
                      hint="Número de árboles afectados"
                      v-model="esp.noArbolesAfectados"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      :onkeypress="rules.regexNumber"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    >
                    <v-text-field
                      label="Valor que esperaba recibir al vender la producción afectada"
                      hint="Valor que esperaba recibir al vender la producción afectada"
                      v-model="esp.valorVenderProduccionAfectada"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      append-icon="mdi-currency-usd"
                      @blur="formatCurrency('esp','valorVenderProduccionAfectada')"
                      :onkeypress="rules.regexNumber"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                    v-if="verVolumenMadera"
                  >
                    <v-text-field
                      label="Volumen de madera afectado"
                      hint="Volumen de madera afectado"
                      v-model="esp.vlMaderaAfectado"
                      type="number"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                      :onkeypress="rules.regexNumber"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-form>

              <v-row dense class="section mt-5">
                <v-col
                  cols="12"
                  md="8"
                  sm="12"
                >
                  <v-switch
                    v-model="esp.afectacionesEnMaquinaria"
                    class="ma-2"
                    inset
                    label="Afectaciones en maquinaria, equipo, insumos y herramienta actividad forestal"
                    @click="estadoAfectacion"
                  ></v-switch>
                </v-col>
                <v-col
                  cols="12"
                  md="6"
                  sm="10"
                  v-if="esp.afectacionesEnMaquinaria"
                >
                  <v-autocomplete
                    label="Tipo infraestructura"
                    hint="Tipo infraestructura"
                    :items="tipoInfraestructura"
                    v-model="idTipoInfraestructura"
                    item-value="valor"
                    item-text="text"
                    :search-input.sync="nombreMaquinariaSelect"
                    dense
                    solo
                    flat
                    outlined
                    filled
                    clearable
                    @change="mostrarTipoInfraestructura()"
                  ></v-autocomplete>
                </v-col>
                <v-col
                  cols="12"
                  md="2"
                  sm="2"
                  v-if="esp.afectacionesEnMaquinaria"
                >
                  <v-btn
                    fab
                    dark
                    small
                    class="mx-2 background-primary-dark"
                    @click="addInfraestructura"
                  >
                    <v-icon dark>mdi-plus</v-icon>
                  </v-btn>
                </v-col>
              </v-row>

              <v-row
                dense
                class="section mt-5"
                v-if="esp.afectacionesEnMaquinaria"
              >
                <v-col
                  v-if="semillasadd.length > 0"
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
                    :headers="semillasHeaders"
                    :items="semillasadd"
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
                <v-col
                  v-if="fertilizanteadd.length > 0"
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
                    :headers="fertilizanteHeaders"
                    :items="fertilizanteadd"
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
                <v-col
                  v-if="plaguicidadadd.length > 0"
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
                    :headers="plaguicidaHeaders"
                    :items="plaguicidadadd"
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
                <v-col
                  v-if="maquinariaadd.length > 0"
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
                    :headers="maquinariaHeaders"
                    :items="maquinariaadd"
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

              <v-row dense class="mt-5">
                <v-col
                  cols="12"
                  md="12"
                  sm="12"
                  class="container-titles mt-5"
                  align="center"
                  justify="center"
                >
                  <p class="color-black font-weight-bold font-16">Costos de producción forestal</p>
                </v-col>
              </v-row>

              <v-form
                lazy-validation
                ref="formCostoDirecto"
                v-model="validCostoDirecto"
              >
                <v-row dense class="section mt-5">
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Costos Directos</p>
                  </v-col>
                  <!-- Costos directos-->
                  <v-col
                    cols="12"
                    md="6"
                    sm="12"
                  >
                    <v-select
                      label="Actividad"
                      hint="Actividad"
                      :items="actividades"
                      v-model="esp.actividad"
                      item-value="valor"
                      item-text="text"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      clearable
                      :rules="rules.required"
                    >
                    </v-select>
                  </v-col>
                  <v-col
                    cols="12"
                    md="6"
                    sm="12"
                  >
                    <v-text-field
                      label="Costo generado en pesos colombianos"
                      hint="Costo generado en pesos colombianos"
                      v-model="esp.costoGenerado"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      :rules="rules.required"
                      @blur="formatCurrency('esp','costoGenerado')"
                      :onkeypress="rules.regexNumber"
                    >
                    </v-text-field>
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
                      @click="addCostoDirecto"
                    >Agregar costo</v-btn>
                  </v-col>
                  <v-data-table
                  :headers="costosDirectosHeader"
                  :items="itemsCostosDirectos"
                  class="elevation-1"
                  style="width: 100%"
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
                </v-row>
              </v-form>

             <v-form
                lazy-validation
                ref="formCostoInDirecto"
                v-model="validCostoInDirecto"
              >
                <v-row dense class="section mt-5">
                  <v-col
                    cols="12"
                    md="12"
                    sm="12"
                  >
                    <p class="color-black font-weight-bold">Costos Indirectos</p>
                  </v-col>
                  <v-col
                    cols="12"
                    md="6"
                    sm="12"
                  >
                    <v-select
                      label="Rubro"
                      hint="Rubro"
                      :items="rubros"
                      v-model="esp.rubrosIndirectos"
                      item-value="valor"
                      item-text="text"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      clearable
                      :rules="rules.required"
                    >
                    </v-select>
                  </v-col>

                  <v-col
                    cols="12"
                    md="6"
                    sm="12"
                  >
                    <v-text-field
                      label="Costo generado en pesos colombianos"
                      hint="Costo generado en pesos colombianos"
                      v-model="esp.costoGeneradoIndirecto"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      :rules="rules.required"
                      @blur="formatCurrency('esp','costoGeneradoIndirecto')"
                      :onkeypress="rules.regexNumber"
                    >
                    </v-text-field>
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
                      @click="addCostoIndirecto"
                    >Agregar costo</v-btn>
                  </v-col>
                  <v-data-table
                    :headers="costosIndirectosHeader"
                    :items="itemsCostosIndirectos"
                    class="elevation-1"
                    style="width: 100%"
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
                  @click="addEspecie()"
                >
                  Guardar sistema
                </v-btn>
                </v-col>

              </v-row>

              <!-- <p>{{ esp }}</p> -->
            </v-container>
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
                  <v-col
                    cols="12"
                    md="4"
                    sm="12"
                  >
                    <v-autocomplete
                      label="Especie forestal afectada"
                      hint="Especie forestal afectada"
                      :items="espForestales"
                      v-model="semilla.espAfectada"
                      :search-input.sync="semilla.especieSemilla"
                      item-value="valor"
                      item-text="text"
                      dense
                      solo
                      flat
                      outlined
                      filled
                      clearable
                      prepend-inner-icon="mdi-decagram"
                      rules.required
                      :rules="rules.required"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-autocomplete
                      label="Lotes de propagación"
                      hint="Lotes de propagación"
                      :items="lotePropagacionSemilla"
                      v-model="semilla.idLotePropagacion"
                      item-value="valor"
                      item-text="text"
                      :search-input.sync="semilla.nameLotePropagacion"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="rules.required"
                      >
                    </v-autocomplete>
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
                      :onkeypress="rules.regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="rules.required"
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
                      filled
                      :onkeypress="rules.regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      @blur="formatCurrency('semilla','valPesos')"
                      :rules="rules.required"
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
                      :items="tipoSemilla"
                      v-model="semilla.idTipoSemilla"
                      item-value="valor"
                      item-text="text"
                      :search-input.sync="semilla.nameTipoSemilla"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="rules.required"
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
                      :onkeypress="rules.regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="rules.required"
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
                      :items="unidadSemilla"
                      v-model="semilla.medidaSemilla"
                      item-value="valor"
                      item-text="text"
                      :search-input.sync="semilla.nameMedidaSemilla"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="rules.required"
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
                      item-value="valor"
                      item-text="text"
                      :search-input.sync="semilla.nameEquivalencia"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="rules.required"
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
                      :onkeypress="rules.regexNumber"
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="rules.required"
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
                      item-value="valor"
                      item-text="text"
                      :search-input.sync="semilla.nameFuenteSemilla"
                      dense
                      solo
                      flat
                      clearable
                      outlined
                      filled
                      prepend-inner-icon="mdi-decagram"
                      required
                      :rules="rules.required"
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
                    :items="tipoFertilizante"
                    v-model="fertilizante.idTipoFertilizante"
                    item-value="valor"
                    item-text="text"
                    :search-input.sync="fertilizante.nameTipoFertilizante"
                    dense
                    solo
                    flat
                    clearable
                    outlined
                    filled
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="rules.required"
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
                    :rules="rules.required"
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
                        :rules="rules.required"
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
                    :onkeypress="rules.regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="rules.required"
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
                    outlined
                    filled
                    :onkeypress="rules.regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    required
                    @blur="formatCurrency('fertilizante','valPesos')"
                    :rules="rules.required"
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
                    v-model="plaguicida.idTipoPlaguicida"
                    item-value="valor"
                    item-text="text"
                    :search-input.sync="plaguicida.nameTipoPlaguicida"
                    dense
                    solo
                    flat
                    clearable
                    outlined
                    filled
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="rules.required"
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
                    v-model="plaguicida.idTipoPresentacion"
                    item-value="valor"
                    item-text="text"
                    :search-input.sync="plaguicida.nameTipoPresentacion"
                    solo
                    flat
                    clearable
                    dense
                    outlined
                    filled
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="rules.required"
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
                    v-model="plaguicida.cantPlaguicidaKg"
                    type="number"
                    dense
                    solo
                    flat
                    outlined
                    filled
                    :onkeypress="rules.regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="rules.required"
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
                    v-model="plaguicida.cantPlaguicidaLt"
                    type="number"
                    dense
                    solo
                    flat
                    outlined
                    filled
                    :onkeypress="rules.regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="rules.required"
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
                    v-model="plaguicida.valPesos"
                    dense
                    outlined
                    solo
                    flat
                    append-icon="mdi-currency-usd"
                    filled
                    :onkeypress="rules.regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    required
                    @blur="formatCurrency('plaguicida','valPesos')"
                    :rules="rules.required"
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
                    v-model="maquinariaAgricola.idTipoMaquinariaAgricola"
                    item-value="valor"
                    item-text="text"
                    :search-input.sync="maquinariaAgricola.nameTipoMaquinaria"
                    dense
                    solo
                    flat
                    clearable
                    outlined
                    filled
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="rules.required"
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
                        v-model="maquinariaAgricola.anoAdquisicion"
                        label="Año de adquisición del equipo"
                        hint="Año de adquisición del equipo"
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
                        :rules="rules.required"
                      ></v-text-field>
                    </v-col>

                  </template>
                  <v-col
                    cols="12"
                    md="4"
                    >
                    <v-date-picker
                        v-model="maquinariaAgricola.anoAdquisicion"
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
                    v-model="maquinariaAgricola.valorPesos"
                    dense
                    solo
                    flat
                    append-icon="mdi-currency-usd"
                    outlined
                    filled
                    :onkeypress="rules.regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    required
                    @blur="formatCurrency('maquinariaAgricola','valorPesos')"
                    :rules="rules.required"
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
                    v-model="maquinariaAgricola.porceDisminucion"
                    dense
                    solo
                    flat
                    outlined
                    filled
                    :onkeypress="rules.regexNumber"
                    prepend-inner-icon="mdi-decagram"
                    required
                    :rules="rules.required"
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

import { newEvent } from '../../services/api.js';
import jwtDecode from 'jwt-decode';
import { getData } from '../../indexedDb/getData';

export default {
  name: 'dataEspecie',
  props: ['obtenerDataEspecie'],
  data () {
    return {
      dialog: false,
      notifications: false,
      sound: true,
      widgets: false,
      expanded: [],
      validSectionOne: true,
      modalMaquinaria: false,
      validCostoDirecto: true,
      validCostoInDirecto: true,
      validInfraestructura: true,

      especiesHeaders: [
        { text: 'Fase productiva', align: 'start', sortable: false, value: 'nameFaseProd' },
        { text: 'Nombre especie', align: 'start', sortable: false, value: 'nameEspAfectada' },
        { text: 'Nombre común', align: 'start', sortable: false, value: 'nombre' },
        { text: 'Objetivo', align: 'start', sortable: false, value: 'nameObjetivo' },
        { text: 'Acciones', value: 'actions', sortable: false, width: '2%' },
      ],
      especies: [],
      costosDirectosHeader: [
        { text: 'Id', align: 'start', sortable: false, value: 'id' },
        { text: 'Rubro', align: 'start', sortable: false, value: 'rubros' },
        { text: 'Costo', align: 'start', sortable: false, value: 'costo' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' }
      ],
      itemsCostosDirectos: [],
      costosIndirectosHeader: [
        { text: 'Id', align: 'start', sortable: false, value: 'id' },
        { text: 'Rubro', align: 'start', sortable: false, value: 'rubros' },
        { text: 'Costo', align: 'start', sortable: false, value: 'costo' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' }
      ],
      itemsCostosIndirectos: [],
      semillasHeaders: [
        { text: 'Especie', align: 'start', sortable: false, value: 'especieSemilla' },
        { text: 'Tipo', align: 'start', sortable: false, value: 'nameTipoSemilla' },
        { text: 'Lotes de propagación', align: 'start', sortable: false, value: 'nameLotePropagacion' },
        { text: 'Cant.Semilla', align: 'start', sortable: false, value: 'canSemillas' },
        { text: 'Val.Pesos', align: 'start', sortable: false, value: 'valPesos' },
        { text: 'Cantidad', align: 'start', sortable: false, value: 'cantSemillas' },
        { text: 'Unidad medida', align: 'start', sortable: false, value: 'nameMedidaSemilla' },
        { text: 'Fuente', align: 'start', sortable: false, value: 'nameFuenteSemilla' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      semillasadd: [],
      fertilizanteHeaders: [
        { text: 'Tipo', align: 'start', sortable: false, value: 'nameTipoFertilizante' },
        { text: 'Nombre', align: 'start', sortable: false, value: 'nombre' },
        { text: 'Fch.Adquisición', align: 'start', sortable: false, value: 'fechaAdquisicion' },
        { text: 'Cant.Fertilizante', align: 'start', sortable: false, value: 'canFertilizante' },
        { text: 'Val.Pesos', align: 'start', sortable: false, value: 'valPesos' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      fertilizanteadd: [],
      plaguicidaHeaders: [
        { text: 'Tipo', align: 'start', sortable: false, value: 'nameTipoPlaguicida' },
        { text: 'Presentación', align: 'start', sortable: false, value: 'nameTipoPresentacion' },
        { text: 'Cant.Plaguicida Kg', align: 'start', sortable: false, value: 'cantPlaguicidaKg' },
        { text: 'Cant.Plaguicida Lt', align: 'start', sortable: false, value: 'cantPlaguicidaLt' },
        { text: 'Val.Pesos', align: 'start', sortable: false, value: 'valPesos' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      plaguicidadadd: [],
      maquinariaHeaders: [
        { text: 'Tipo', align: 'start', sortable: false, value: 'nameTipoMaquinaria' },
        { text: 'Año aduisición', align: 'start', sortable: false, value: 'anoAdquisicion' },
        { text: 'Val.Pesos', align: 'start', sortable: false, value: 'valorPesos' },
        { text: '%Disminución', align: 'start', sortable: false, value: 'porceDisminucion' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      maquinariaadd: [],

      esp: {},
      semilla: {},
      fertilizante: {},
      plaguicida: {},
      maquinariaAgricola: {},
      fasesProd: [],
      espForestales: [],
      espExtractivas: [],
      espObjetivos: [],
      tipoInfraestructura: [],
      tipoSemilla: [],
      lotePropagacionSemilla: [],
      unidadSemilla: [],
      tipoFertilizante: [],
      listaPresentacion: [],
      tipoMaquinariaAgricola: [],
      rubros: [],
      actividades: [],
      nombreMaquinariaSelect: '',
      idTipoInfraestructura: '',

      fuenteSemilla: [],
      equivaleKilos: [],
      materiralSiembra: [],
      tiposPlaguicidas: [],
      presentacion: [],
      calcularEdadEquipo: 0,
      menuFechaAno: false,
      editedIndex: -1,

      rules: {
        required: [v => !!v || 'Campo requerido'],
        regexNumber: "return (event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46)",
      },
    }
  },
  async mounted () {
    await this.getDataEventSpecie();
    await this.edicionForestal();
  },
  methods: {
    cerrarModal() {
      this.limpiarCampos();
    },
    addEspecie () {
      if (this.$refs.formSectionOne.validate()) {
        if (this.itemsCostosDirectos.length === 0 || this.itemsCostosIndirectos.length === 0) {
          this.$swal({
            icon: 'error',
            text: 'No se han registrados costos directos o indirectos.',
            confirmButtonText: 'Aceptar',
          });
          return;
        }
        this.esp.costosDirectos = this.itemsCostosDirectos;
        this.esp.costosInDirectos = this.itemsCostosIndirectos;
        this.esp.semilla = this.semillasadd;
        this.esp.fertilizante = this.fertilizanteadd;
        this.esp.plaguicida = this.plaguicidadadd;
        this.esp.maquinariaAgricola = this.maquinariaadd;

        if (this.editedIndex > -1) {
          Object.assign(this.especies[this.editedIndex], this.esp);
        } else {
          this.especies.push(this.esp);
        }

        this.obtenerDataEspecie(this.especies);
        this.limpiarCampos();
      }
    },
    limpiarCampos() {
      this.itemsCostosDirectos = [];
      this.itemsCostosIndirectos = [];
      this.semillasadd = [];
      this.fertilizanteadd = [];
      this.plaguicidadadd = [];
      this.maquinariaadd = [];
      this.esp = {};
      this.editedIndex = -1;
      this.dialog = false;
    },
    deleteEspecie (item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar sistema forestal?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          const editedIndex = this.especies.indexOf(item)
          this.especies.splice(editedIndex, 1)
          this.obtenerDataEspecie(this.especies)
        }
      })
    },
    editarEspecie(item) {
      this.editedIndex = this.especies.indexOf(item);
      this.itemsCostosDirectos = item.costosDirectos;
      this.itemsCostosIndirectos = item.costosInDirectos;
      this.semillasadd = item.semilla;
      this.fertilizanteadd = item.fertilizante;
      this.plaguicidadadd = item.plaguicida;
      this.maquinariaadd = item.maquinariaAgricola;
      this.esp = Object.assign({}, item);
      this.dialog = true;
    },
    mostrarTipoInfraestructura() {
      this.modalMaquinaria = true;
      this.nombreMaquinariaSelect = this.nameTipoInfraestructura;
    },
    addInfraestructura() {
      if (this.idTipoInfraestructura) {
        this.mostrarTipoInfraestructura();
      }
    },
    agregarTipoInfraestructura() {
      if(this.$refs.formInfraestructura.validate()) {
        const idTipoMaquinaria = parseInt(this.idTipoInfraestructura);

        if (idTipoMaquinaria === 1) {
          this.semillasadd.push(this.semilla);
          this.semilla = {};
        }
        if (idTipoMaquinaria === 2) {
          this.fertilizanteadd.push(this.fertilizante);
          this.fertilizante = {};
        }
        if (idTipoMaquinaria === 3) {
          this.plaguicidadadd.push(this.plaguicida);
          this.plaguicida = {};
        }
        if (idTipoMaquinaria === 4) {
          this.maquinariaadd.push(this.maquinariaAgricola);
          this.maquinariaAgricola = {};
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
          const index = this.semillasadd.indexOf(item)
          this.semillasadd.splice(index, 1)
        }
      })
    },
    deleteFertilizante (item) {
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
          const index = this.fertilizanteadd.indexOf(item)
          this.fertilizanteadd.splice(index, 1)
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
          const index = this.plaguicidadadd.indexOf(item)
          this.plaguicidadadd.splice(index, 1)
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
          const index = this.maquinariaadd.indexOf(item)
          this.maquinariaadd.splice(index, 1)
        }
      })
    },
    saveYear() {
      const ano = this.$refs.picker.$data.inputYear;
      this.maquinariaAgricola.anoAdquisicion = ano+''+'';

      // Reset activePicker to type YEAR
      this.$refs.picker.activePicker = 'YEAR';

      // Close the menu/datepicker
      this.menuFechaAno = false;

      const fechaActual = new Date();
      const anoActual = fechaActual.getFullYear();
      this.calcularEdadEquipo = anoActual > ano  ? anoActual - ano : 0;
    },
    deleteCostoDirecto (item) {
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
          const editedIndexCostoDirecto = this.itemsCostosDirectos.indexOf(item)
          this.itemsCostosDirectos.splice(editedIndexCostoDirecto, 1)
        }
      })
    },
    addCostoDirecto () {
      if (this.$refs.formCostoDirecto.validate()) {
        const newCostoDirecto = {}
        newCostoDirecto.costo = this.esp.costoGenerado
        newCostoDirecto.id = this.esp.actividad
        var text = this.actividades.filter(actividad => actividad.valor === this.esp.actividad)
        newCostoDirecto.rubros = text[0].text
        this.itemsCostosDirectos.push(newCostoDirecto)
        this.esp.costoGenerado = ''
        this.esp.actividad = {}
      }
    },
    deleteCostoIndirecto (item) {
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
          const editedIndexCostoIndirecto = this.itemsCostosIndirectos.indexOf(item)
          this.itemsCostosIndirectos.splice(editedIndexCostoIndirecto, 1)
        }
      })
    },
    addCostoIndirecto () {
      if (this.$refs.formCostoInDirecto.validate()) {
        const newCostoIndirecto = {}
        newCostoIndirecto.costo = this.esp.costoGeneradoIndirecto
        newCostoIndirecto.id = this.esp.rubrosIndirectos
        var text = this.rubros.filter(rubro => rubro.valor === this.esp.rubrosIndirectos)
        newCostoIndirecto.rubros = text[0].text
        this.itemsCostosIndirectos.push(newCostoIndirecto)
        this.esp.costoGeneradoIndirecto = ''
        this.esp.rubrosIndirectos = {}
      }
    },
    estadoAfectacion() {
      if (!this.esp.afectacionesEnMaquinaria) {
        this.semillasadd = [];
        this.fertilizanteadd = [];
        this.plaguicidadadd = [];
        this.maquinariaadd = [];
      }
    },
    async getDataEventSpecie () {
      try {

        const data = await getData('forestal', true);

        for (const documento in data.faseProductiva) {
          var addFase = {
            valor: data.faseProductiva[documento][0],
            text: data.faseProductiva[documento][1]
          }
          this.fasesProd.push(addFase)
        }

        for (const documento in data.especieForestal) {
          var addEspecieFor = {
            valor: data.especieForestal[documento][0],
            text: data.especieForestal[documento][1]
          }
          this.espForestales.push(addEspecieFor)
        }

        for (const documento in data.especieExtractiva) {
          var addEspecieEx = {
            valor: data.especieExtractiva[documento][0],
            text: data.especieExtractiva[documento][1]
          }
          this.espExtractivas.push(addEspecieEx)
        }

        for (const documento in data.objePlantacion) {
          var addObje = {
            valor: data.objePlantacion[documento][0],
            text: data.objePlantacion[documento][1]
          }
          this.espObjetivos.push(addObje)
        }

        for (const documento in data.tipoInfraestrcutura) {
          var addInfra = {
            valor: data.tipoInfraestrcutura[documento][0],
            text: data.tipoInfraestrcutura[documento][1]
          }
          this.tipoInfraestructura.push(addInfra)
        }

        for (const documento in data.tipoSemilla) {
          var addSemilla = {
            valor: data.tipoSemilla[documento][0],
            text: data.tipoSemilla[documento][1]
          }
          this.tipoSemilla.push(addSemilla)
        }

        for (const documento in data.fuenteSemilla) {
          var addFuenteSemi = {
            valor: data.fuenteSemilla[documento][0],
            text: data.fuenteSemilla[documento][1]
          }
          this.fuenteSemilla.push(addFuenteSemi)
        }

        for (const documento in data.lotePropaga) {
          var addLoteP = {
            valor: data.lotePropaga[documento][0],
            text: data.lotePropaga[documento][1]
          }
          this.lotePropagacionSemilla.push(addLoteP)
        }

        for (const documento in data.unidadSemilla) {
          var addUnidad = {
            valor: data.unidadSemilla[documento][0],
            text: data.unidadSemilla[documento][1]
          }
          this.unidadSemilla.push(addUnidad)
        }

        for (const documento in data.eqvCarga) {
          var addEquivaK = {
            valor: data.eqvCarga[documento][0],
            text: data.eqvCarga[documento][1]
          }
          this.equivaleKilos.push(addEquivaK)
        }

        for (const documento in data.tipoFertilizante) {
          var addFertilizante = {
            valor: data.tipoFertilizante[documento][0],
            text: data.tipoFertilizante[documento][1]
          }
          this.tipoFertilizante.push(addFertilizante)
        }

        for (const documento in data.tipoPlaguicida) {
          var addPlaguicida = {
            valor: data.tipoPlaguicida[documento][0],
            text: data.tipoPlaguicida[documento][1]
          }
          this.tiposPlaguicidas.push(addPlaguicida)
        }

        for (const documento in data.presentacionPlaguicida) {
          var addPresentacion = {
            valor: data.presentacionPlaguicida[documento][0],
            text: data.presentacionPlaguicida[documento][1]
          }
          this.presentacion.push(addPresentacion)
        }

        for (const documento in data.tipoMaquinaria) {
          var addMaquinaria = {
            valor: data.tipoMaquinaria[documento][0],
            text: data.tipoMaquinaria[documento][1]
          }
          this.tipoMaquinariaAgricola.push(addMaquinaria)
        }

        for (const documento in data.rubros) {
          var addRubros = {
            valor: data.rubros[documento][0],
            text: data.rubros[documento][1]
          }
          this.rubros.push(addRubros)
        }

        for (const documento in data.actividad) {
          var addActividad = {
            valor: data.actividad[documento][0],
            text: data.actividad[documento][1]
          }
          this.actividades.push(addActividad)
        }

      } catch (error) {
        console.log(error)
      }
    },
    edicionForestal() {
      const dataEvento = this.$route.params.evento;
      if (dataEvento !== undefined) {
        if (dataEvento.dataEspecies.forestal.length > 0) {
          this.especies = dataEvento.dataEspecies.forestal;
        }
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
    verDatosAdicionalesObjetivo() {
      const ids = [1,2,4];
      var estado = (ids.includes(this.esp.objetivo)) ? true: false;
      if (!estado) {
        delete this.esp.noArbolesAntesAfectacion;
        delete this.esp.noEntresacas;
        delete this.esp.valEntreSacas;
        delete this.esp.porceEntreSacas;
        delete this.esp.diametroPromedio;
        delete this.esp.alturaComercial;
        delete this.esp.alturaTotal;
        delete this.esp.plantacionAnos;
        delete this.esp.porceArbolesTurnoFinal;
        delete this.esp.vlMaderaAfectado;
      }
      return estado;
    },
    verVolumenMadera() {
      const ids = [1];
      var estado = (ids.includes(this.esp.objetivo)) ? true: false;
      if (!estado) {
        delete this.esp.vlMaderaAfectado;
      }
      return estado;
    },
    verCamposSemilla() {
      var estado = false;
      if (this.idTipoInfraestructura) {
        estado =  this.idTipoInfraestructura === 1 ? true : false;
      }
      return estado;
    },
    verCamposFertilizante() {
      var estado = false;
      if (this.idTipoInfraestructura) {
        estado =  this.idTipoInfraestructura === 2 ? true : false;
      }
      return estado;
    },
    verCamposPlaguicidas() {
      var estado = false;
      if (this.idTipoInfraestructura) {
        estado =  this.idTipoInfraestructura === 3 ? true : false;
      }
      return estado;
    },
    verCamposMaquinaria() {
      var estado = false;
      if (this.idTipoInfraestructura) {
        estado =  this.idTipoInfraestructura === 4 ? true : false;
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
