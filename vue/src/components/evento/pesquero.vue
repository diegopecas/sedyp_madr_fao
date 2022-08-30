<template>
  <div>

    <!--Tabla de especies agregadas-->
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
                <span class="mr-2">Sistema pesquero</span>

                <v-btn
                  class=" background-primary-dark"
                  outlined
                  elevation="2"
                  fab
                  dark
                  small
                  @click="dialogPesquero = true"
                >
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </v-toolbar>
            </template>
            <template v-slot:item.actions="{ item }">
              <v-icon
                small
                color="#004884"
                @click="editarSistema(item)"
              >
              mdi-pencil
              </v-icon>
              <v-icon
                small
                color="#004884"
                @click="eliminarSistemaPesquero(item)"
              >
              mdi-delete
              </v-icon>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>

    <!--formulario-->
    <v-dialog
      v-model="dialogPesquero"
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
              <center>Sistema pesquero</center>
            </v-col>
          </v-row>
        </v-container>
      </v-card-title>

      <v-card-text>
        <v-container grid-list-xs>
          <v-form
            lazy-validation
            ref="formSectionOne"
            v-model="validSectionOne"
          >
            <v-row dense class="section">

              <v-col
                class="mt-5"
                cols="12"
                md="12"
                sm="12"
              >
                <v-text-field
                  label="Puerto de desembarque de la pesca"
                  hint="Puerto de desembarque de la pesca"
                  v-model="dataPesquero.puertoDesembarque"
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
            <v-row dense class="section mt-5">

              <v-col
                cols="12"
                md="12"
                sm="12"
              >
                <p class="color-black font-weight-bold">Datos Pesca</p>
              </v-col>
              <v-col
                cols="12"
                md="6"
                sm="6"
              >
                <v-autocomplete
                  v-model="dataPesquero.tipoPesqueria"
                  :items="tipoPesquera"
                  item-text="tippesq"
                  item-value="codtippesq"
                  dense
                  outlined
                  solo
                  flat
                  multiple
                  clearable
                  label="Pesquería que realiza en el año"
                  hint="Pesquería que realiza en el año"
                  prepend-inner-icon="mdi-decagram"
                  required
                  :rules="required"
                >
                </v-autocomplete>
              </v-col>
              <v-col
                cols="12"
                md="6"
                sm="6"
              >
                <v-text-field
                  label="Principales especies explotadas"
                  hint="Principales especies explotadas"
                  v-model="dataPesquero.especieExplotada"
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
          </v-form>

          <v-form
            lazy-validation
            ref="formSectionTwo"
            v-model="validSectionTwo"
            class="mt-5"
          >
            <v-row dense class="section">
              <v-col
                cols="12"
                md="4"
                sm="6"
              >
                <v-switch
                  class="ml-1"
                  v-model="dataPesquero.embarcacionAfectada"
                  inset
                  label="Embarcaciones afectadas"
                ></v-switch>
              </v-col>
            </v-row>

            <v-row
              v-if="verEmbarcacion"
              dense
              class="section mt-3"
            >
              <v-col
                cols="12"
                md="4"
                sm="6"
              >
                <v-text-field
                  label="Tipo embarcación"
                  hint="Listar según tipos más frecuentes"
                  v-model="embarcacion.tipoEmbarcacion"
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
                sm="6"
                md="4"
              >
                <v-autocomplete
                  label="Material de embarcación"
                  hint="Material de embarcación"
                  :items="material"
                  v-model="embarcacion.material"
                  :search-input.sync="embarcacion.nameMaterial"
                  item-value="codembqmaterial"
                  item-text="embqmaterial"
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
                  label="Propulsión"
                  hint="Propulsión, "
                  :items="propulsion"
                  v-model="embarcacion.propulsion"
                  :search-input.sync="embarcacion.namePropulsion"
                  item-value="codpropulsion"
                  item-text="tipopropulsion"
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
                md="4"
                sm="6"
              >
                <v-text-field
                  label="Patente de la embarcación"
                  hint="Patente de la embarcación"
                  v-model="embarcacion.patenteEmbarcacion"
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
                sm="6"
              >
                <v-text-field
                  label="Eslora en metros de la embarcación"
                  hint="Eslora en metros de la embarcación"
                  v-model="embarcacion.esloraEmbarcacion"
                  type="number"
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
                sm="6"
              >
                <v-text-field
                  label="Edad de la embarcación"
                  hint="Edad de la embarcación"
                  v-model="embarcacion.edad"
                  type="number"
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
                sm="6"
              >
                <v-text-field
                  label="Valor de la afectación en pesos"
                  hint="Valor de la afectación en pesos"
                  v-model="embarcacion.valorEmbarcacion"
                  dense
                  outlined
                  solo
                  flat
                  append-icon="mdi-currency-usd"
                  prepend-inner-icon="mdi-decagram"
                  required
                  :onkeypress="regexNumber"
                  @blur="formatCurrency('embarcacion','valorEmbarcacion')"
                  :rules="required"
                ></v-text-field>
              </v-col>
              <v-col
                cols="12"
                md="8"
                sm="6"
              >
                <v-text-field
                  label="Observación"
                  hint="Observación"
                  v-model="embarcacion.observacionEmbarcacion"
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
                  @click="guardarEmbarcacion"
                >Agregar embarcación</v-btn>
              </v-col>
              <v-col
                cols="12"
              >
                <v-data-table
                  :headers="embarcacionesHeader"
                  :items="itemsEmbarcacionesAgregada"
                  class="elevation-2"
                >
                  <template v-slot:top>

                  </template>
                  <template v-slot:item.actions="{ item }">
                    <v-icon
                      small
                      @click="eliminarEmbarcacion(item)"
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
            class="mt-5"
          >
            <v-row dense class="section">

              <v-col
                cols="12"
                md="4"
                sm="6"
              >
                <v-switch
                  class="ml-1"
                  v-model="dataPesquero.instalacionAfectada"
                  inset
                  label="Instalaciones afectadas"
                ></v-switch>
              </v-col>
            </v-row>

            <v-row
              dense
              class="section mt-3"
              v-if="verInstalacion"
            >
              <v-col
                cols="12"
                md="12"
                sm="12"
              >
                <p class="color-black font-weight-bold">Redes afectadas</p>
              </v-col>
              <v-col
                cols="12"
                sm="12"
                md="4"
              >
                <v-autocomplete
                  label="Tipos de redes"
                  hint="Tipos de redes"
                  :items="tipoRedes"
                  v-model="dataPesquero.tipoRedes"
                  item-value="codtipred"
                  item-text="tipored"
                  :search-input.sync="dataPesquero.nameTipoRedes"
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
                md="4"
                sm="12"
              >
                <v-text-field
                  label="Indique el nombre/ marca del equipo"
                  hint="Indique el nombre/ marca del equipo"
                  v-model="dataPesquero.marcaRed"
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
                v-model="dataPesquero.menuFechaAdquisicion"
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
                      v-model="dataPesquero.fechaAdquisicion"
                      label="Indique la fecha de adquisición del bien"
                      hint="Indique la fecha de adquisición del bien"
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
                      v-model="dataPesquero.fechaAdquisicion"
                      @input="dataPesquero.menuFechaAdquisicion = false"
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
                  label="Indique el precio pagado por el activo"
                  hint="Indique el precio pagado por el activo"
                  v-model="dataPesquero.valorRedes"
                  dense
                  outlined
                  solo
                  flat
                  append-icon="mdi-currency-usd"
                  prepend-inner-icon="mdi-decagram"
                  required
                  :onkeypress="regexNumber"
                  @blur="formatCurrency('dataPesquero','valorRedes')"
                  :rules="required"
                ></v-text-field>
              </v-col>
              <v-col
                cols="12"
                sm="12"
                md="4"
              >
                <v-autocomplete
                  label="Indique si el daño en el activo causo una pérdida"
                  hint="Indique si el daño en el activo causo una pérdida"
                  :items="tipoPerdida"
                  v-model="dataPesquero.tipoPerdida"
                  item-value="codtipperdida"
                  item-text="tipperdida"
                  :search-input.sync="dataPesquero.nameTipoPerdida"
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
                md="4"
                sm="12"
              >
                <v-text-field
                  label="Cantidad de redes afectadas"
                  hint="Cantidad de redes afectadas"
                  v-model="dataPesquero.numeroRedes"
                  type="number"
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
          </v-form>

          <v-form
            lazy-validation
            ref="formSectionFour"
            v-model="validSectionFour"
            class="mt-5"
          >
            <v-row dense class="section mt-5">

              <v-col
                cols="12"
                md="12"
                sm="12"
              >
                <p class="color-black font-weight-bold">Datos de pesca</p>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="6"
              >
                <v-text-field
                  label="Número de faenas de pesca mensuales realizadas antes del evento"
                  hint="Número de faenas de pesca mensuales realizadas antes del evento"
                  v-model="dataPesquero.numeroFaenas"
                  type="number"
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
                sm="6"
              >
                <v-text-field
                  label="¿Actualmente cuantas faenas de pesca realiza y/o puede realizar en el siguiente mes?"
                  hint="¿Actualmente cuantas faenas de pesca realiza y/o puede realizar en el siguiente mes?"
                  v-model="dataPesquero.cantidadFaenasMes"
                  type="number"
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
                sm="6"
              >
                <v-text-field
                  label="Valor promedio recibido de la venta de los peces recolectados en cada faena"
                  hint="Valor promedio recibido de la venta de los peces recolectados en cada faena"
                  v-model="dataPesquero.valorVentaPeces"
                  dense
                  outlined
                  solo
                  flat
                  append-icon="mdi-currency-usd"
                  prepend-inner-icon="mdi-decagram"
                  required
                  :rules="required"
                  @blur="formatCurrency('dataPesquero','valorVentaPeces')"
                  :onkeypress="regexNumber"
                ></v-text-field>
              </v-col>

            </v-row>
          </v-form>

          <v-row dense class="section mt-5">

            <v-col
              cols="12"
              md="6"
              sm="6"
            >
              <v-switch
                class="ml-1"
                v-model="dataPesquero.maquinariaAfectada"
                inset
                label="Instalaciones y maquinaria pesquera afectada"
              ></v-switch>
            </v-col>

          </v-row>

           <v-form
            lazy-validation
            ref="formSectionFive"
            v-model="validSectionFive"
            v-if="verMaquinaria"
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
                sm="6"
              >
                <v-autocomplete
                  v-model="maquinaria.activoProductivo"
                  :items="tipoActivo"
                  item-text="tipactivo"
                  item-value="codtipactivo"
                  dense
                  outlined
                  solo
                  flat
                  clearable
                  label="Por favor seleccione un activo productivo afectado"
                  hint="Por favor seleccione un activo productivo afectado"
                  prepend-inner-icon="mdi-decagram"
                  required
                  :rules="required"
                >
                </v-autocomplete>
              </v-col>
            </v-row>

            <v-row dense class="section mt-3">
              <v-col
                cols="12"
                md="12"
                sm="12"
              >
                <p class="color-black font-weight-bold">Datos del equipo / maquinaria afectado</p>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="6"
              >
                <v-text-field
                  label="Indique el nombre / marca del equipo"
                  hint="Indique el nombre / marca del equipo"
                  v-model="maquinaria.nombreEquipo"
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
                  v-model="maquinaria.menuFechaAdquisicion"
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
                    sm="6"
                  >
                    <v-text-field
                      v-model="maquinaria.fechaAdquisicion"
                      label="¿Cuál fue la fecha de adquisición de bien?"
                      hint="¿Cuál fue la fecha de adquisición de bien?"
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
                  sm="6"
                >
                  <v-date-picker
                    v-model="maquinaria.fechaAdquisicion"
                    @input="maquinaria.menuFechaAdquisicion = false"
                    outlined
                    ></v-date-picker>
                </v-col>
              </v-menu>
              <v-col
                cols="12"
                md="4"
                sm="6"
              >
                <v-text-field
                  label="¿Cuál fue el precio pagado por el activo?"
                  hint="¿Cuál fue el precio pagado por el activo?"
                  v-model="maquinaria.valorActivo"
                  dense
                  outlined
                  solo
                  flat
                  append-icon="mdi-currency-usd"
                  prepend-inner-icon="mdi-decagram"
                  required
                  :rules="required"
                  @blur="formatCurrency('maquinaria','valorActivo')"
                  :onkeypress="regexNumber"
                ></v-text-field>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="6"
              >
                <v-text-field
                  label="Valor invertido en reponer, reparar y/o adecuar el/la maquina/equipo"
                  hint="Valor invertido en reponer, reparar y/o adecuar el/la maquina/equipo"
                  v-model="maquinaria.valorReponer"
                  dense
                  outlined
                  solo
                  flat
                  append-icon="mdi-currency-usd"
                  prepend-inner-icon="mdi-decagram"
                  required
                  :rules="required"
                  @blur="formatCurrency('maquinaria','valorReponer')"
                  :onkeypress="regexNumber"
                ></v-text-field>
              </v-col>

            </v-row>
            <v-row dense class="section" v-if="verConstruccion">

              <v-col
                cols="12"
                md="12"
                sm="12"
              >
                <p class="color-black font-weight-bold">Construcciones</p>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="6"
              >
                <v-autocomplete
                  v-model="maquinaria.tipoConstruccion"
                  :items="tipoConstruccion"
                  item-text="tipcons"
                  item-value="codtipcons"
                  dense
                  outlined
                  solo
                  flat
                  clearable
                  label="Por favor, indique el tipo de construcción afectada"
                  hint="Por favor, indique el tipo de construcción afectada"
                  prepend-inner-icon="mdi-decagram"
                  required
                  :rules="required"
                >
                </v-autocomplete>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="6"
              >
                <v-text-field
                  label="¿Cuál es el área en metros cuadrados de la construcción afectada?"
                  hint="¿Cuál es el área en metros cuadrados de la construcción afectada?"
                  v-model="maquinaria.areaAfectada"
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
                sm="6"
              >
                <v-text-field
                  label="¿Cuál será el valor invertido en la re-construcción, reparación y/o adecuación del sitio?"
                  hint="Por favor indique el valor que estima deberá invertir para reconstruir, reparar y/o adecuar las construcciones"
                  v-model="maquinaria.valorInvertidoAdecuacion"
                  dense
                  outlined
                  solo
                  flat
                  append-icon="mdi-currency-usd"
                  @blur="formatCurrency('maquinaria','valorInvertidoAdecuacion')"
                  :onkeypress="regexNumber"
                ></v-text-field>
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="6"
              >
                <v-text-field
                  label="Tiempo necesario para realizar re-construcción, reparación y/o adecuación del sitio (meses)"
                  hint="Tiempo necesario para realizar re-construcción, reparación y/o adecuación del sitio (meses)"
                  v-model="maquinaria.mesesReconstruccion"
                  type="number"
                  dense
                  outlined
                  solo
                  flat
                  :onkeypress="regexNumber"
                ></v-text-field>
              </v-col>

            </v-row>
            <v-row dense class="section">

              <v-col
                cols="12"
                md="8"
                sm="12"
              >
              </v-col>
              <v-col
                cols="12"
                md="4"
                sm="12"
              >
                <v-btn
                  class="background-primary-dark button-basic"
                  elevation="2"
                  block
                  raised
                  depressed
                  @click="guardarMaquinaria"
                >Agregar instalación/maquinaria</v-btn>
              </v-col>
              <v-col
                cols="12"
              >
                <v-data-table
                  :headers="maquinariasHeader"
                  :items="itemsMaquinariasAgregada"
                  class="elevation-2"
                >
                  <template v-slot:top>

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
  name:'pesquero',
  props:['obtenerDataPesquero'],
  data() {
    return {
      dialogPesquero: false,
      validSectionOne: true,
      validSectionTwo: true,
      validSectionThree: true,
      validSectionFour: true,
      validSectionFive: true,

      especiesHeader: [
        { text: 'Puerto desembarque', align: 'start', sortable: false, value: 'puertoDesembarque' },
        { text: 'Especie explotada', align: 'start', sortable: false, value: 'especieExplotada' },
        { text: 'Número faenas', align: 'start', sortable: false, value: 'numeroFaenas' },
        { text: 'Cantidad faenas(mes)', align: 'start', sortable: false, value: 'cantidadFaenasMes' },
        { text: 'Valor venta faenas', align: 'start', sortable: false, value: 'valorVentaPeces' },
        { text: 'Acciones', value: 'actions', sortable: false, width: '2%' },
      ],
      itemsEspecieAgregada: [],
      embarcacionesHeader: [
        { text: 'Tipo', align: 'start', sortable: false, value: 'tipoEmbarcacion' },
        { text: 'Material', align: 'start', sortable: false, value: 'nameMaterial' },
        { text: 'Propulsión', align: 'start', sortable: false, value: 'namePropulsion' },
        { text: 'Patente', align: 'start', sortable: false, value: 'patenteEmbarcacion' },
        { text: 'Eslora', align: 'start', sortable: false, value: 'esloraEmbarcacion' },
        { text: 'Edad', align: 'start', sortable: false, value: 'edad' },
        { text: 'Valor', align: 'start', sortable: false, value: 'valorEmbarcacion' },
        { text: 'Observación', align: 'start', sortable: false, value: 'observacionEmbarcacion' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      itemsEmbarcacionesAgregada: [],
      maquinariasHeader: [
        { text: 'Activo productivo', align: 'start', sortable: false, value: 'activoProductivo' },
        { text: 'Nombre equipo', align: 'start', sortable: false, value: 'nombreEquipo' },
        { text: 'Fecha adquisición', align: 'start', sortable: false, value: 'fechaAdquisicion' },
        { text: 'Valor activo', align: 'start', sortable: false, value: 'valorActivo' },
        { text: 'Valor reparación equipo', align: 'start', sortable: false, value: 'valorReponer' },
        { text: 'Tipo construcción', align: 'start', sortable: false, value: 'nombreTipoConstruccion' },
        { text: 'Área afectada', align: 'start', sortable: false, value: 'areaAfectada' },
        { text: 'Valor invetido adecuaciones', align: 'start', sortable: false, value: 'valorInvertidoAdecuacion' },
        { text: 'Meses reconstrucción', align: 'start', sortable: false, value: 'mesesReconstruccion' },
        { text: 'Eliminar', value: 'actions', sortable: false, width: '2%' },
      ],
      itemsMaquinariasAgregada: [],

      dataPesquero: {},
      embarcacion: {},
      maquinaria: {},
      tipoPesquera: [],
      tipoActivo: [],
      tipoConstruccion: [],
      material: [],
      propulsion: [],
      tipoRedes: [],
      tipoPerdida: [],
      editedIndex: -1,

      regexNumber: "return (event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46)",
      required: [v => !!v || 'Campo requerido',],
    }
  },
  created() {

  },
  async mounted() {
    await this.obtenerData();
    await this.edicionPesquero();
  },
  methods: {
    async obtenerData() {
      try {
        const res = await getData('pesquero', true);
        this.addDataCampos(res);

      } catch (error) {
        console.log(error);
      }
    },
    edicionPesquero() {
      const dataEvento = this.$route.params.evento;
      if (dataEvento !== undefined) {
        if (dataEvento.dataEspecies.infoPesquero.length > 0) {
          this.itemsEspecieAgregada = dataEvento.dataEspecies.infoPesquero;
        }
      }
    },
    addDataCampos(data) {
      this.tipoPesquera = data.fishingType;
      this.tipoActivo   = data.activeType;
      this.tipoConstruccion = data.buildingType;
      this.material = data.embqMaterial;
      this.propulsion = data.propType;
      this.tipoRedes = data.redType;
      this.tipoPerdida = data.lossType;
    },
    cerrarModal() {
      this.limpiarCampos();
    },
    limpiarCampos() {
      this.dataPesquero = {};
      this.itemsEmbarcacionesAgregada = {};
      this.itemsMaquinariasAgregada = {};
      this.editedIndex = -1;
      this.dialogPesquero = false;
    },
    editarSistema(item) {
      this.editedIndex = this.itemsEspecieAgregada.indexOf(item)
      console.log(this.editedIndex);
      this.itemsEmbarcacionesAgregada = item.embarcaciones;
      this.itemsMaquinariasAgregada = item.maquinarias;
      this.dataPesquero = Object.assign({}, item)
      this.dialogPesquero = true;
    },
    eliminarSistemaPesquero(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar sistema pesquero?',
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
          this.obtenerDataPesquero(this.itemsEspecieAgregada)
        }
      })
    },
    guardarEmbarcacion() {
      if (this.$refs.formSectionTwo.validate()) {
        this.itemsEmbarcacionesAgregada.push(this.embarcacion);
        this.embarcacion = {};
      }
    },
    eliminarEmbarcacion(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar embarcación?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          const editedIndex = this.itemsEmbarcacionesAgregada.indexOf(item);
          this.itemsEmbarcacionesAgregada.splice(editedIndex, 1);
        }
      })
    },
    guardarMaquinaria() {
      if (this.$refs.formSectionFive.validate()) {
        let tipo = this.maquinaria.tipoConstruccion;
        if (tipo) {
          let nombre = this.tipoConstruccion.filter(item => item.codtipcons === tipo);
          this.maquinaria.nombreTipoConstruccion = nombre[0]['tipcons'];
        }
        this.itemsMaquinariasAgregada.push(this.maquinaria);
        this.maquinaria = {};
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
          const editedIndex = this.itemsMaquinariasAgregada.indexOf(item);
          this.itemsMaquinariasAgregada.splice(editedIndex, 1);
        }
      })
    },
    guardarSistema() {
      const embarcacionAfectada = this.dataPesquero.embarcacionAfectada;
      const instalacionAfectada = this.dataPesquero.instalacionAfectada;
      const maquinariaAfectada = this.dataPesquero.maquinariaAfectada;

      if (embarcacionAfectada) {
        if (!this.itemsEmbarcacionesAgregada.length) {
          this.$swal({
            icon: 'error',
            text: 'No se han registrado datos de embarcación.',
            confirmButtonText: 'Aceptar',
          });
          return;
        }
      }
      if (instalacionAfectada) {
        if (!this.itemsEmbarcacionesAgregada.length) {
          this.$swal({
            icon: 'error',
            text: 'No se han registrado datos de redes afectadas.',
            confirmButtonText: 'Aceptar',
          });
          return;
        }
      }
      if (maquinariaAfectada) {
        if (!this.itemsMaquinariasAgregada.length) {
          this.$swal({
            icon: 'error',
            text: 'No se han registrado datos de maquinaria.',
            confirmButtonText: 'Aceptar',
          });
          return;
        }
      }

      if (this.$refs.formSectionOne.validate() && this.$refs.formSectionFour.validate()) {
        this.dataPesquero.embarcaciones = this.itemsEmbarcacionesAgregada;
        this.dataPesquero.maquinarias = this.itemsMaquinariasAgregada;

        if (this.editedIndex > -1) {
          Object.assign(this.itemsEspecieAgregada[this.editedIndex], this.dataPesquero)
        } else {
            this.itemsEspecieAgregada.push(this.dataPesquero);
        }

        this.obtenerDataPesquero(this.itemsEspecieAgregada);
        this.limpiarCampos();
      }
    },
    eliminarSistemaPecuario(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar especie pecuaria?',
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
        }
      })
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
    verEmbarcacion() {
      let estado = this.dataPesquero.embarcacionAfectada ? true: false;
      if (!estado) {
        this.embarcacion = {};
        this.itemsEmbarcacionesAgregada = [];
      }
      return estado;
    },
    verInstalacion() {
      let estado = this.dataPesquero.instalacionAfectada ? true: false;
      if (!estado) {
        delete this.dataPesquero.tipoRedes;
        delete this.dataPesquero.marcaRed;
        delete this.dataPesquero.fechaAdquisicion;
        delete this.dataPesquero.numeroRedes;
        delete this.dataPesquero.tipoPerdida;
        delete this.dataPesquero.valorRedes;
      }
      return estado;
    },
    verMaquinaria() {
      let estado = this.dataPesquero.maquinariaAfectada ? true: false;
      if (!estado) {
        delete this.dataPesquero.activoProductivo;
        this.maquinaria = {};
        this.itemsMaquinariasAgregada = [];
      }
      return estado;
    },
    verConstruccion() {
      let estado = this.maquinaria.activoProductivo === 2 ? true: false;
      if (!estado) {
        delete this.maquinaria.tipoConstruccion;
        delete this.maquinaria.areaAfectada;
        delete this.maquinaria.valorInvertidoAdecuacion;
        // delete this.maquinaria.valorEstimadoReconstruccion;
        delete this.maquinaria.tiempoMesesReconstruccion;
      }
      return estado;
    },
  },
}
</script>
