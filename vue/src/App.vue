<template>
  <v-app>
    <v-main>
      <menuApp v-if="$route.name != 'inicio' && $route.name != 'validate' && $route.name != 'forgotPassword'"></menuApp>
      <offlineAlert></offlineAlert>
      <router-view style="height:100hv;"/>
    </v-main>
    <v-dialog
      v-model="dialog"
      hide-overlay
      persistent
      width="300"
      >
      <v-card
        color="primary"
        dark
      >
        <v-card-text>
          {{loadingMSG}}
          <v-progress-linear
            indeterminate
            color="white"
            class="mb-0"
          ></v-progress-linear>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script>

import menuApp from '@/components/shared/menu'
import offlineAlert from '@/components/shared/offlineAlert'

export default {
  components: { menuApp, offlineAlert },
  name: 'App',
  data: () => ({
    dialog: false,
    loadingMSG: '',
    user: ''
  }),
  async mounted () {
    this.$root.$on('mainLoading', (text) => {
      this.loadingMSG = text
      this.dialog = !this.dialog
    })
    this.$root.$on('logged', async () => {
      this.user = await this.$session.getAll()
    })
    this.user = await this.$session.getAll()
  }
}
</script>

<style src="./assets/css/base.css">
