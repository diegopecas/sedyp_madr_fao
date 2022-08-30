<template>
  <div>
    <JsonExcel
      class="cursor-click"
      :fetch="getData"
      :fields="jsonFields"
      :before-generate="startDownload"
      :before-finish="finishDownload"
      type = "csv"
      name="Auditoria.csv">
      <v-btn
        class="background-primary-dark button-basic"
        elevation="2"
        block
        raised
        depressed
        v-if="textButton.length >= 1"
      >
        {{ textButton }}
      </v-btn>
      <v-icon
        color="#004884"
        v-if="textButton.length === 0"
      > mdi-download-box</v-icon>
    </JsonExcel>
  </div>
</template>

<script>

import JsonExcel from "vue-json-excel";

export default {
  name: 'descargaCsv',
  components: {
    JsonExcel
  },
  props: [
    'jsonData', 'textButton'
  ],
  data() {
    return {
      jsonFields: {},
      data: [],
      json_meta: [
        [
          {
            key: "charset",
            value: "utf-8",
          },
        ],
      ],
    }
  },
  methods: {
    getData(){
      var item = {};

      for (const key in this.jsonData[0]) {
        if (key !== 'valor') {
          this.jsonFields[''+key+''] = key;
          item[''+key+''] = this.jsonData[key];
        }
      }

      return this.jsonData;
    },
    startDownload(){
    },
    finishDownload(){
      this.$swal({
        icon: 'success',
        text: 'Descarga completa',
        confirmButtonText: 'Aceptar',
      });
    }
  },
}
</script>
