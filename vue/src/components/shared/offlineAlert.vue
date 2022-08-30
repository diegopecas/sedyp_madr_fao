<template>
  <!-- <VueOffline @detected-condition="amIOnline"> -->
    <div>

      <v-snackbar
      v-model="snackbar"
      >
        <p v-if="isOnline"><v-icon>mdi-wifi-strength-outline</v-icon> Aplicación Online</p>
        <p v-if="isOffline"><v-icon>mdi-wifi-strength-off-outline</v-icon> Aplicación Offline</p>
        <template v-slot:action="{ attrs }">
          <v-btn
            :color="colorAlert"
            text
            v-bind="attrs"
            @click="snackbar = false"
          >
            Cerrar
          </v-btn>
        </template>
      </v-snackbar>

    </div>

    <!-- <div slot="offline">
    </div>

  </VueOffline> -->
</template>

<script>
// import { VueOffline } from 'vue-offline'

export default {
  // components : { VueOffline },
  data: () => ({
    statusOnline: null,
    snackbar: true,
  }),
  methods: {
    // amIOnline (e) {
    //   this.statusOnline = e
    //   this.colorAlert = (e) ? 'indigo' : 'pink'
    // }
  },
  computed: {
    colorAlert() {
      return this.isOnline ? 'indigo' : 'pink'
    }
  }
}

</script>
