<template>
  <div>
    <v-container class="img-main">
      <updatePassword />
    </v-container>
    <footerInicio />
  </div>
</template>
<script>

import updatePassword from '../components/inicio/updatePassword';
import footerInicio from '@/components/inicio/footerInicio';

export default {
  components: { updatePassword, footerInicio },
  data() {
    return {
    }
  },
}
</script>
