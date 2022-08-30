<template>
<v-container class="mt-5">

    <v-footer
      v-bind="localAttrs"
      :padless="padless"
      elevation="2"
    >
      <v-card
        flat
        tile
        width="100%"
        class="footer"
      >
        <v-card-text>
         <v-row>
            <v-col
              cols="4"
              sm="12"
              md="4"
              align="right"
            >
              <v-img
              class="mt-2"
              max-height="200"
              max-width="200"
              src="/img/fao_azul.png"
              ></v-img>
            </v-col>
            <v-col
              cols="4"
              sm="12"
              md="4"
              align="center"
            >
              <v-img
              max-height="160"
              max-width="160"
              src="/img/fao_logo.png"
              ></v-img>
            </v-col>
            <v-col
              cols="4"
              sm="12"
              md="4"
              align="left"
            >
              <v-img
              class="mt-3"
              max-height="200"
              max-width="200"
              src="/img/logo_minagricultura.png"
              ></v-img>
            </v-col>
         </v-row>
        </v-card-text>

      </v-card>
    </v-footer>

</v-container>
</template>
<script>
export default {
  name: 'footerInicio',
  data: () => ({
    icons: [
      'mdi-home',
      'mdi-email',
      'mdi-calendar',
      'mdi-delete'
    ],
    padless: true,
    variant: 'fixed'
  }),
  computed: {
    localAttrs () {
      const attrs = {}

      if (this.variant === 'default') {
        attrs.absolute = false
        attrs.fixed = false
      } else {
        attrs[this.variant] = true
      }
      return attrs
    }
  }
}
</script>
