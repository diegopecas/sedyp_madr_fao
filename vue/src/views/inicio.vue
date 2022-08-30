<template>
  <div style="height:100vh">

      <v-container class="img-main">

        <login @register="tipo='registro'" @recover="tipo='recover'"></login>
        <registro @login="tipo='login'" v-if="tipo === 'registro'" :updateUser="false"></registro>
        <recPassword  @login="tipo='login'" v-if="tipo === 'recover'"></recPassword>

      </v-container>
      <br>
      <footerInicio />

  </div>
</template>

<script>

import login from '@/components/inicio/login'
import registro from '@/components/inicio/registro'
import recPassword from '@/components/inicio/recPassword'
import footerInicio from '@/components/inicio/footerInicio'

export default {
  components: { login, registro, recPassword, footerInicio },
  data () {
    return {
      tipo: 'login'
    }
  },
  computed: {
    medida () {
      if (this.tipo === 'registro') return { lg: 4, offsetlg: 4, md: 4, offsetmd: 4 }
      if (['login', 'recover'].includes(this.tipo)) return { lg: 6, md: 4, offsetmd: 4 }
      return {}
    },
    height () {
      switch (this.$vuetify.breakpoint.name) {
        case 'xs': return 220
        case 'sm': return 400
        case 'md': return 500
        case 'lg': return 600
        case 'xl': return 800
      }
      return 1200
    }
  }
}
</script>
