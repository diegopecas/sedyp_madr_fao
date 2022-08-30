<template>
  <div class="home">
    <br>
    <br>
    <v-container class="mt-5">
      <eventos @compSeguimiento="onResulrseguimiento" />
    </v-container>
    <seguimiento @compList="tipo='listado'" v-if="tipo === 'seguimiento'" :dataEvento="dataEvento"/>
    <footerApp class="mt-5" v-if="$route.name != 'inicio' && $route.name != 'validate'"></footerApp>
  </div>
</template>
<script>

import footerApp from '@/components/shared/footerApp'
import eventos from '@/components/eventosCreados/eventos'
import seguimiento from '@/components/evento/seguimiento'

export default {
  components: { footerApp, eventos, seguimiento },
  name: 'Home',
  data () {
    return {
      tipo: 'listado',
      dataEvento: [],
    }
  },
  methods: {
     onResulrseguimiento(item) {
      this.tipo='seguimiento';
      this.dataEvento = item;
    },
  }
}
</script>
