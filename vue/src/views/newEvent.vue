<template>
  <div>

    <v-overlay :value="loading">
      <v-progress-circular
        indeterminate
        size="64"
      ></v-progress-circular>
    </v-overlay>

    <!-- <div ref="dataEventoEnviar">
      <pre style="overflow: scroll; height:500px;">
        <p>Data Encabezado</p>
        {{ dataEncabezado }}
        <p>Data mapa</p>
        {{ dataMapa }}
        <p>Data productor</p>
        {{ dataProductor }}
        <p>Data Especie</p>
        {{ dataEspecie }}
      </pre>
      <v-btn
        class="success button-basic"
        elevation="2"
        block
        title="Copiar en portapapeles"
        @click="copiarEnPortaPapeles()"
      >
        Copiar en portapapele
      </v-btn>
    </div> -->

    <v-container>
      <v-stepper
        class="elevation-0"
        non-linear
        :vertical="width"
        v-model="e6"
      >
        <v-stepper-header
          class="elevation-0"
          v-if="!width"
        >
          <template v-for="(n, index) in steps">
            <v-stepper-step
              :key="index"
              :step="index+1"
              editable
              :complete="n.complete"
              :color="n.color"
              @click="n.method"
            >
              {{ n.name }}
            </v-stepper-step>
            <v-divider v-if="index !== 2"></v-divider>

          </template>
        </v-stepper-header>

        <v-stepper-items>

          <v-stepper-step
            :complete="completeProductor"
            :color="colorProductor"
            step="1"
            v-if="width"
            editable
            class="ma-2 pa-0"
          >
            Prouctor
            <small>Información del productor</small>
          </v-stepper-step>
          <v-stepper-content step="1" class="ma-0 pa-0">
            <productor :obtenerData="onResultadosProductor"></productor>
          </v-stepper-content>


          <v-stepper-step
            :complete="completeUbicacion"
            :color="colorUbicacion"
            step="2"
            v-if="width"
            editable
            class="ma-2 pa-0"
            @click="reloadMap"
          >
            Ubicación
            <small>Ubicación del evento</small>
          </v-stepper-step>
          <v-stepper-content step="2" class="ma-0 pa-0">
            <v-container fluid>
              <mapaEvento :tipoProductor="tipoProductor" :obtenerDataMapa="onResultadosMapa" :reload="reload"></mapaEvento>
            </v-container>
          </v-stepper-content>


          <v-stepper-step
            step="3"
            v-if="width"
            editable
            class="ma-2 pa-0"
          >
            Sistema
          </v-stepper-step>
          <v-stepper-content step="3" class="ma-0 pa-0">
            <v-container fluid>

              <v-form
                lazy-validation
                ref="formEventEncabezado"
                v-model="valFormEventEnca"
              >
                <v-row dense>
                  <v-col
                  cols="12"
                  md="4"
                  >
                    <v-autocomplete
                      label="Tipo de evento"
                      :items="tiposEvento"
                      item-value="valor"
                      v-model="selEvento.tipoEv"
                      :search-input.sync="selEvento.nameTipoEv"
                      dense
                      clearable
                      flat
                      outlined
                      :rules="rulesEventGeneral"
                      required
                      @change="cargarSubEventoSegunEvento()"
                    >
                    </v-autocomplete>
                  </v-col>

                  <v-col
                  cols="12"
                  md="4"
                  >
                    <v-autocomplete
                      label="Tipo de subevento"
                      :items="relEventoSubEvento"
                      item-value="valor"
                      v-model="selEvento.subEv"
                      :search-input.sync="selEvento.nameSubEv"
                      dense
                      clearable
                      flat
                      outlined
                      :rules="rulesEventGeneral"
                      required
                    >
                    </v-autocomplete>
                  </v-col>

                  <v-col
                  cols="12"
                  md="4"
                  v-if="tipoEventoCuarentenario"
                  >
                    <v-autocomplete
                      label="¿Son cuarentenarias?"
                      hint="¿Son cuarentenarias?"
                      :items="cuarentenarias"
                      item-value="id"
                      item-text="text"
                      v-model="selEvento.cuarentenario"
                      dense
                      clearable
                      flat
                      outlined
                      :rules="rulesEventGeneral"
                      required
                      >
                    </v-autocomplete>
                  </v-col>

                  <v-col
                    cols="12"
                    md="4"
                    v-if="verEnfermendad"
                  >
                    <v-autocomplete
                      label="Enfermedades cuarentenarias"
                      hint="Enfermedades cuarentenarias"
                      :items="enfermedadCuarente"
                      item-value="valor"
                      item-text="text"
                      v-model="selEvento.enfermedadCuarente"
                      :search-input.sync="selEvento.nameEnfermedadCuarente"
                      dense
                      clearable
                      flat
                      outlined
                      :rules="rulesEventGeneral"
                      required
                      >
                    </v-autocomplete>
                  </v-col>

                  <v-col
                    cols="12"
                    md="4"
                    v-if="verPlaga"
                  >
                    <v-autocomplete
                      label="Plagas cuarentenarias"
                      hint="Plagas cuarentenarias"
                      :items="plagaCuarente"
                      item-value="valor"
                      item-text="text"
                      v-model="selEvento.plagaCuarente"
                      :search-input.sync="selEvento.namePlagaCuarente"
                      dense
                      clearable
                      flat
                      outlined
                      :rules="rulesEventGeneral"
                      required
                      >
                    </v-autocomplete>
                  </v-col>

                  <v-col
                    cols="12"
                    md="4"
                    v-if="verNombreEnfermedad"
                  >
                    <v-text-field
                      label="Nombre de la enfermedad"
                      hint="Nombre de la enfermedad"
                      v-model="selEvento.nombreEnfermedad"
                      dense
                      outlined
                      solo
                      flat
                      required
                      :rules="rulesEventGeneral"
                      >
                    </v-text-field>
                  </v-col>

                  <v-col
                    cols="12"
                    md="4"
                    v-if="verNombrePlaga"
                  >
                    <v-text-field
                      label="Nombre de la plaga"
                      hint="Nombre de la plaga"
                      v-model="selEvento.nombrePlaga"
                      dense
                      outlined
                      solo
                      flat
                      required
                      :rules="rulesEventGeneral"
                      >
                    </v-text-field>
                  </v-col>

                  <v-col
                    cols="12"
                    md="4"
                    v-if="verOtroSudEvento"
                  >
                    <v-text-field
                      label="Nombre del otro subevento"
                      hint="Nombre del otro subevento"
                      v-model="selEvento.otroSubEvento"
                      dense
                      outlined
                      solo
                      flat
                      required
                      :rules="rulesEventGeneral"
                      >
                    </v-text-field>
                  </v-col>

                  <v-col
                  cols="12"
                  md="4"
                  >
                    <v-autocomplete
                      label="Sistema productivo afectado"
                      :items="sisProds"
                      item-value="valor"
                      item-text="text"
                      v-model="selEvento.sisProds"
                      dense
                      outlined
                      multiple
                      clearable
                      required
                      flat
                      :rules="rulesSelectMulti.select"
                      >
                    </v-autocomplete>
                  </v-col>

                </v-row>
              </v-form>

            </v-container>

            <forestal v-if="contForestal" :obtenerDataEspecie="onResultadosEspecie"></forestal>
            <agropecuario v-if="contAgro" :obtenerDataAgro="onResultadosAgro" :departamento="this.dataMapa.departamento"></agropecuario>
            <pecuarioAcuicola v-if="contPecuario" :obtenerDataPecuaAcui="onResultadosPecuario"></pecuarioAcuicola>
            <apicola v-if="contApicola" :obtenerDataApicola="onResultadosApicola"></apicola>
            <pesquero v-if="contPesquero" :obtenerDataPesquero="onResultadosPesquero"></pesquero>

            <v-row>
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
                v-if="!selEvento.validado"
              >
                <v-btn
                  class="success button-basic"
                  elevation="2"
                  block
                  title="Guardar Evento"
                  @click="guardarEvento()"
                >
                  Guardar evento
                </v-btn>
              </v-col>
            </v-row>

          </v-stepper-content>
        </v-stepper-items>
      </v-stepper>
    </v-container>

  </div>
</template>
<script>

import { getData } from '../indexedDb/getData';
import { update } from '../indexedDb/insertSystemData.js';
import { newEvent } from '../services/api.js';
import jwtDecode from 'jwt-decode';
import productor from '@/components/evento/productor';
import forestal from '@/components/evento/forestal';
import agropecuario from '@/components/evento/agropecuario';
import pecuarioAcuicola from '@/components/evento/pecuarioAcuicola';
import apicola from '@/components/evento/apicola';
import pesquero from '@/components/evento/pesquero';
import mapaEvento from '@/components/evento/mapaEvento';

export default {
  components: { productor, forestal, agropecuario, pecuarioAcuicola, apicola, pesquero, mapaEvento},
  data () {
    return {
      tipo: 'inicioEvent',
      reload: false,
      e6: 1,
      tab: 0,
      steps: [
        {funcion:'validarEstadoProductor',name:'Productor',icon:'mdi-badge-account-outline',complete:false,color:'primary', method: this.notMethod},
        {funcion:'validarEstadoProductor',name:'Ubicación',icon:'mdi-map-legend',complete:false,color:'primary', method: this.reloadMap},
        {funcion:'validarEstadoProductor',name:'Información del evento',icon:'mdi-calendar-text-outline',complete:false,color:'primary',method: this.notMethod},
      ],
      edicion: false,
      id_obj: null,
      completeProductor: false,
      colorProductor: 'primary',
      completeUbicacion: false,
      colorUbicacion: 'primary',
      mfnac: false,
      valFormEventEnca: true,
      dataEventUpdate: [],
      selEvento: {},
      tiposEvento: [],
      tiposSubEvento: [],
      relEventoSubEvento: [],
      sisProds: [],
      enfermedadCuarente: [],
      plagaCuarente: [],
      dataProductor: [],
      dataMapa: [],
      dataEspecie: {
        forestal: [],
        agropecuario: [],
        infoPecuario: [],
        infoApicola: [],
        infoPesquero: [],
      },
      dataAgro: [],
      loading: false,
      dataEncabezado: {},
      cuarentenarias: [
        {id: 1, text:'si'},
        {id: 2, text:'no'}
      ],
      tipoProductor: [],
      // Rules
      rulesEventGeneral: [
        v => !!v || 'Campo obligatorio'
      ],
      rulesSelectMulti: {
        select: [(v) =>  v.length>0 || "Campo obligatorio"],
      },
    }
  },
  created: function () {
  },
  async mounted () {
    await this.getDataEvent()
    await this.edicionEvento();
  },
  methods: {
    edicionEvento() {
      this.edicion = false;
      const dataEvento = this.$route.params.evento;
      if (dataEvento !== undefined) {
        this.edicion = true;
        this.id_obj = dataEvento.id_obj;
        this.onResultadosProductor(dataEvento.dataProductor);
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
        this.onResultadosMapa(dataMapa);

        const dataSistema = {
          'tipoEv': encabezado.tipoEv,
          'subEv': encabezado.subEv,
          'cuarentenario': encabezado.cuarentenario,
          'enfermedadCuarente': encabezado.enfermedadCuarente,
          'plagaCuarente': encabezado.plagaCuarente,
          'nombreEnfermedad': encabezado.nombreEnfermedad,
          'nombrePlaga': encabezado.nombrePlaga,
          'otroSubEvento': encabezado.otroSubEvento,
          'sisProds': encabezado.sisProds,
          'nameTipoEv': encabezado.nameTipoEv,
          'nameSubEv': encabezado.nameSubEv,
          'nameCuarentenario': encabezado.nameCuarentenario,
          'nameEnfermedadCuarente': encabezado.nameEnfermedadCuarente,
          'namePlagaCuarente': encabezado.namePlagaCuarente,
          'nameSisProds': encabezado.nameSisProds,
          'validado': encabezado.validado,
        }
        if (encabezado.codEvento) {
          dataSistema.codEvento = encabezado.codEvento;
        }
        this.selEvento = dataSistema;
        this.cargarSubEventoSegunEvento();

        this.onResultadosEspecie(dataEvento.dataEspecies.forestal);
        this.onResultadosAgro(dataEvento.dataEspecies.agropecuario);
        this.onResultadosPecuario(dataEvento.dataEspecies.infoPecuario);
        this.onResultadosApicola(dataEvento.dataEspecies.infoApicola);
        this.onResultadosPesquero(dataEvento.dataEspecies.infoPesquero);
      }
    },
    notMethod() {
    },
    reloadMap() {
      this.reload = true;
    },
    onResultadosProductor(infoProductor) {
      this.dataProductor = infoProductor;

      this.steps[0].complete = (this.dataProductor.length > 0) ? true :false;
      this.steps[0].color = (this.dataProductor.length > 0) ? 'success' :'primary';
      this.completeProductor = (this.dataProductor.length > 0) ? true :false;
      this.colorProductor = (this.dataProductor.length > 0) ? 'success' :'primary';
      this.tipoProductor = [];
      for(var i=0; i<infoProductor.length; i++){
        this.tipoProductor.push(infoProductor[i].tipoProd);
      }
    },
    onResultadosMapa(infoMapa) {
      this.dataMapa = infoMapa;

      this.steps[1].complete = (this.dataMapa.latitud) ? true :false;
      this.steps[1].color = (this.dataMapa.latitud) ? 'success' :'primary';
      this.completeUbicacion = (this.dataMapa.latitud) ? true :false;
      this.colorUbicacion = (this.dataMapa.latitud) ? 'success' :'primary';
    },
    onResultadosEspecie(infoEspecie) {
      this.dataEspecie['forestal'] = infoEspecie;
    },
    onResultadosAgro(infoAgro) {
      this.dataEspecie['agropecuario'] = infoAgro;
    },
    onResultadosPecuario(infoPecuario) {
      this.dataEspecie['infoPecuario'] = infoPecuario;
    },
    onResultadosApicola(infoApicola) {
      this.dataEspecie['infoApicola'] = infoApicola;
    },
    onResultadosPesquero(infoPesquero) {
      this.dataEspecie['infoPesquero'] = infoPesquero;
    },
    addEspecie() {
      this.selEvento.especies.unshift({
        faseProd: '',
        espAfectada: '',
        espExtractiva: '',
        nombre: '',
        objetivo: '',
        fecha: '',
        densHectarea: '',
        areaSembrada: '',
        menuFecha: false
      })
    },
    delEspecie (esp) {
      const index = this.especies.findIndex(item => item === esp)
      this.selEvento.especies.splice(index, 1)
    },
    valEspecies (result) {
      if (result === false) {
        this.selEvento.especies = []
      }
    },
    async getDataEvent () {

      try {
        const data = await getData('encabezado', true);

        for (const documento in data.tipoEvento) {
          var addTipoEvento = {
            valor: data.tipoEvento[documento][0],
            text: data.tipoEvento[documento][1]
          }
          this.tiposEvento.push(addTipoEvento)
        }

        for (const documento in data.subEvento) {
          var addSubEvento = {
            valor: data.subEvento[documento][0],
            text: data.subEvento[documento][1],
            idEvento: data.subEvento[documento][2]
          }
          this.tiposSubEvento.push(addSubEvento)
        }

        for (const enfermedad in data.enfermedades) {
          var addEnfermedad = {
            valor: data.enfermedades[enfermedad][0],
            text: data.enfermedades[enfermedad][1],
            idEvento: data.enfermedades[enfermedad][2]
          }
          this.enfermedadCuarente.push(addEnfermedad)
        }

        for (const plaga in data.plagas) {
          var addPlagas = {
            valor: data.plagas[plaga][0],
            text: data.plagas[plaga][1],
            idEvento: data.plagas[plaga][2]
          }
          this.plagaCuarente.push(addPlagas)
        }

        for (const documento in data.sistemaProductivo) {
          var addSisProds = {
            valor: data.sistemaProductivo[documento][0],
            text: data.sistemaProductivo[documento][1]
          }
          this.sisProds.push(addSisProds)
        }

      } catch (error) {
        console.log(error)
      }
    },
    cargarSubEventoSegunEvento() {
      this.relEventoSubEvento = this.tiposSubEvento.filter(subEvento => subEvento.idEvento === this.selEvento.tipoEv)
    },
    async guardarEvento () {

      this.loading = true;
      this.validacionCamposObligatorios();
      if (this.loading === false) {
        return;
      }
      const dataEncabezadoEvento = this.dataEncabezadoEvento();
      const dataProductor = this.dataProductor;
      const dataEspecies = this.dataEspecie;
      const res = await getData('newEvent', false);

      if (this.isOnline && Object.keys(res).length === 0) {
          this.setEventOnline(dataEncabezadoEvento, dataProductor, dataEspecies);
      } else {
        this.setEventOffline(dataEncabezadoEvento, dataProductor, dataEspecies);
      }
    },
    async setEventOnline(dataEncabezadoEvento, dataProductor, dataEspecies) {
      const formData = new FormData();
      var contador = 0;

      if (this.dataMapa.adjuntos) {
        for (const file of this.dataMapa.adjuntos) {
          formData.append('files' + contador, file, file.name)
          contador++
        }
      }

      formData.append('contador', contador)
      formData.append('dataEncabezadoEvento',JSON.stringify(dataEncabezadoEvento))
      formData.append('dataProductor',JSON.stringify(dataProductor))
      formData.append('dataEspecies',JSON.stringify(dataEspecies))

      try {

        const res = dataEncabezadoEvento.codEvento ? await newEvent.modifyEvent(formData) : await newEvent.setDataEvento(formData);

        if (res.status === 200) {

          this.$swal({
            icon: 'success',
            text: res.message,
            confirmButtonText: 'Aceptar',
          });
          this.$router.push('/home');

        } else {
          this.$swal({
            icon: 'error',
            text: res.message,
            confirmButtonText: 'Aceptar',
          });
        }
        this.loading = false;

      } catch (error) {
        this.loading = false;
        console.log(error);
        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar',
        });
      }
    },
    async setEventOffline(dataEncabezadoEvento, dataProductor, dataEspecies) {
      const objects = ['newEvent'];
      const res = await getData('newEvent', false);
      let id = (this.edicion && this.id_obj) ? this.id_obj:Object.keys(res).length + 1;

      var data = {'id_obj': id,'dataEncabezadoEvento':dataEncabezadoEvento, 'dataProductor':dataProductor,'dataEspecies': dataEspecies};

      update({'newEvent':data}, objects, false);

      this.$swal({
        icon: 'success',
        text: 'Evento creado exitosamente.',
        confirmButtonText: 'Aceptar',
      });
      this.loading = false;
      this.$router.push('/home');
    },
    dataEncabezadoEvento() {
      const dataUserLocal = JSON.parse(localStorage.getItem('dataUser'));
      this.dataEncabezado = this.dataMapa;
      this.dataEncabezado.idUsuario = dataUserLocal.id;
      for (const key in this.selEvento) {
        this.dataEncabezado[key] = this.selEvento[key];
      }
      return this.dataEncabezado;
    },
    validacionCamposObligatorios() {
      if (Object.keys(this.dataProductor).length === 0) {
        this.loading = false;
        this.$swal({
          icon: 'error',
          text: 'No se han relacionado productores al evento.',
          confirmButtonText: 'Aceptar',
        });
        return;
      }
      if (Object.keys(this.dataMapa).length < 5) {
        this.loading = false;
        this.$swal({
          icon: 'error',
          text: 'La información de la ubicación del evento esta incompleta.',
          confirmButtonText: 'Aceptar',
        });
        return;
      }
      if (!this.$refs.formEventEncabezado.validate()) {
        this.loading = false;
        return;
      }
    },
    copiarEnPortaPapeles() {
      const codigoACopiar = this.$refs.dataEventoEnviar;
      console.log(codigoACopiar);
      try {
          let seleccion = document.createRange();
          seleccion.selectNodeContents(codigoACopiar);
          window.getSelection().removeAllRanges();
          window.getSelection().addRange(seleccion);
          let res = document.execCommand('copy');
          window.getSelection().removeRange(seleccion);
          if(codigoACopiar) {
          this.$swal({
            icon: 'success',
            text: 'Información copiada.',
            confirmButtonText: 'Aceptar',
          });
          }
      }catch (e){
          console.log("-Ocurrió un error al copiar el elemento");
      }
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
    contForestal () {
      var valido = false
      for (const item in this.selEvento.sisProds) {
        if (valido) { break }
        valido = this.selEvento.sisProds[item] === 3
      }
      return valido
    },
    contAgro () {
      var valido = false
      for (const item in this.selEvento.sisProds) {
        if (valido) { break }
        valido = this.selEvento.sisProds[item] === 1
      }
      return valido
    },
    contPecuario () {
      var valido = false
      for (const item in this.selEvento.sisProds) {
        if (valido) { break }
        valido = this.selEvento.sisProds[item] === 2
      }
      return valido
    },
    contApicola () {
      var valido = false
      for (const item in this.selEvento.sisProds) {
        if (valido) { break }
        valido = this.selEvento.sisProds[item] === 5
      }
      return valido
    },
    contPesquero () {
      var valido = false
      for (const item in this.selEvento.sisProds) {
        if (valido) { break }
        valido = this.selEvento.sisProds[item] === 4
      }
      return valido
    },
    esEmpresa () {
      var valido = false
      for (const item in this.selEvento.condJuridica) {
        if (valido) { break }
        valido = this.selEvento.condJuridica[item] === 2
      }
      return valido
    },
    compTipoDcto () {
      if (this.esEmpresa) return this.tiposDcto.filter(item => item.persona === 'juridica')
      return this.tiposDcto.filter(item => item.persona === 'natural')
    },
    especies () {
      return this.selEvento.especies
    },
    tipoEventoCuarentenario() {
      var estado = false;
      if (this.selEvento.tipoEv === 3) {
        estado = true;
      } else {
        this.selEvento.enfermedadCuarente = null;
        this.selEvento.plagaCuarente = null;
        this.selEvento.nombreEnfermedad = null;
        this.selEvento.nombrePlaga = null;
      }
      return estado;
    },
    verEnfermendad() {
      var estado = false;
      if (this.selEvento.tipoEv === 3 && this.selEvento.subEv === 17 && this.selEvento.cuarentenario == 1) {
        estado = true;
      } else {
        this.selEvento.enfermedadCuarente = null;
      }
      return estado;
    },
    verPlaga() {
      var estado = false;
      if (this.selEvento.tipoEv === 3 && this.selEvento.subEv === 16 && this.selEvento.cuarentenario == 1) {
        estado = true;
      } else {
        this.selEvento.plagaCuarente = null;
      }
      return estado;
    },
    verNombreEnfermedad() {
      var estado = false;
      if (this.selEvento.tipoEv === 3 && this.selEvento.subEv === 17 && this.selEvento.cuarentenario == 2) {
        estado = true;
      } else {
        this.selEvento.nombreEnfermedad = null;
      }
      return estado;
    },
    verNombrePlaga() {
      var estado = false;
      if (this.selEvento.tipoEv === 3 && this.selEvento.subEv === 16 && this.selEvento.cuarentenario == 2) {
        estado = true;
      } else {
        this.selEvento.nombrePlaga = null;
      }
      return estado;
    },
    verOtroSudEvento() {
     var estado = false;
      if (this.selEvento.tipoEv === 4 && this.selEvento.subEv === 28) {
        estado = true;
      } else {
        this.selEvento.otroSubEvento = null;
      }
      return estado;
    },
  },
}
</script>
