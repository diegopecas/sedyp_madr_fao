<template>
  <div>
    <v-container>
      <rolesPermisos></rolesPermisos>
    </v-container>
  </div>
</template>
<script>
import rolesPermisos from '@/components/configuracion/rolesPermisos'

export default {
  components: { rolesPermisos },
  name: 'roles'
}
</script>
