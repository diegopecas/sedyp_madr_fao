<template>
  <v-container>
    <v-row dense>

      <searchCombobox
        :listChips='listChips'
        :datos='dataAuditoria'
        :dataFiltrada='dataEventoFiltrada'
        campoFechaFiltro='fecha_operacion'
      />
      <v-col
        cols="12"
        sm="12"
        md="10"
      >
      </v-col>
      <v-col
        cols="12"
        sm="12"
        md="2"
      >
        <descargaCsv
          :jsonData="dataAuditoria"
          textButton="Descargar"
        />
      </v-col>
      <v-col
        cols="12"
        md="12"
        sm="12"
      >
        <template>
          <v-data-table
            :headers="auditoriaHeader"
            :items="dataAuditoria"
            item-key="idmodulo"
            class="elevation-2"
            :loading="loading"
            loading-text="Cargando datos..."
          >
            <template v-slot:top>
              <v-toolbar
                flat
                class="border-head-table font-weight-bold"
                height="10px"
                style="background-color:#F2F2F2"
              >
              </v-toolbar>
            </template>
            <template v-slot:item.actions="{ item }">
              <descargaCsv :jsonData="[item]" textButton="">
              </descargaCsv>
            </template>
          </v-data-table>
        </template>
      </v-col>

    </v-row>
  </v-container>
</template>
<script>

import { dataGeneral } from '../../services/api';
import jwtDecode from 'jwt-decode';
import descargaCsv from '@/components/shared/descargaCsv';
import searchCombobox from '@/components/shared/searchCombobox'

export default {
  name: 'auditoria',
  components: {
    descargaCsv,
    searchCombobox
  },
  data() {
    return {
      auditoriaHeader: [
        {text: 'Acción', value: 'accion'},
        {text: 'Atributo', value: 'atributo'},
        {text: 'Entidad', value: 'entidad'},
        {text: 'Fecha operación', value: 'fecha_operacion'},
        {text: 'Hora operación', value: 'hora_operacion'},
        {text: 'Identificador', value: 'id_auditoria'},
        {text: 'Usuario', value: 'id_usuario'},
        {text: 'IP', value: 'ip'},
        {text: 'Descargar cambios', value: 'actions', align: 'center'},
      ],
      dataAuditoria: [],
      verAlerta: false,
      loading: false,
      listChips: [
        {nombreFiltro: 'Acción', valor: 'accion'},
        {nombreFiltro: 'Atributo', valor: 'atributo'},
        {nombreFiltro: 'Entidad', valor: 'entidad'},
        {nombreFiltro: 'Fecha operación', valor: 'fecha_operacion'},
        {nombreFiltro: 'Hora operación', valor: 'hora_operacion'},
        {nombreFiltro: 'Identificador', valor: 'id_auditoria'},
        {nombreFiltro: 'Usuario', valor: 'id_usuario'},
        {nombreFiltro: 'IP', valor: 'ip'},
      ],
    }
  },
  async mounted() {
    await this.getData();
  },
  methods: {
    async getData() {

      this.loading = true;

      try {
        const res = await dataGeneral.getDataAudit();

        if (res.status === 200) {

          const encoded = res.data.token
          const decoded = jwtDecode(encoded)
          const data = decoded.auditorias
          this.dataAuditoria = data;
          this.dataAuditoriaCompleta = data;

          this.loading = false;
        } else {
          this.$swal({
            icon: 'error',
            text: error.message,
            confirmButtonText: 'Aceptar',
          });
          this.loading = false;
        }
      } catch (error) {
        this.$swal({
          icon: 'error',
          text: error.response.data.message,
          confirmButtonText: 'Aceptar',
        });
        this.loading = false;
      }
    },
    dataEventoFiltrada(data) {
      this.dataAuditoria = data;
    }
  },
  computed: {
  },
}
</script>
