<template>
  <div class="home">
    <v-container>
      <updateUser :updateUser="true"></updateUser>
    </v-container>
  </div>
</template>
<script>
import updateUser from '@/components/configuracion/usuario'

export default {
  components: { updateUser },
  name: 'usuario'
}
</script>
