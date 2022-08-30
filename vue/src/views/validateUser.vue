<template>
  <div style="height:100vh">

    <v-container class="img-main">
      <validate />
    </v-container>
    <footerInicio />

  </div>
</template>
<script>

import validate from '../components/inicio/validate';
import footerInicio from '@/components/inicio/footerInicio';

export default {
  components: { validate, footerInicio },
  data() {
    return {

    }
  },
}
</script>
