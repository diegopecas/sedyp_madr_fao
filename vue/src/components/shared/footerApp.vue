<template>
<v-container>
    <br>
    <br>
    <br>
    <v-footer
      v-bind="localAttrs"
      :padless="padless"
      elevation="2"
    >

      <v-card
        flat
        tile
        max-height="100px"
        width="100%"
        class="footer background-primary-dark"
      >
        <v-expansion-panels
         accordion
         v-model="panel"
         multiple
        >
        <v-expansion-panel class="background-primary-dark p-content-white">
        <v-expansion-panel-header
         :class="heightFooter"

        >
          Información
          <template v-slot:actions>
            <v-icon :class="heightFooter">
              $expand
            </v-icon>
          </template>
        </v-expansion-panel-header>
        <v-expansion-panel-content>

        <v-card-text  class="background-primary-dark p-content-white">

         <v-row>
            <v-col
              cols="12"
              sm="12"
              md="4"
              align="center"
              class="hidden-sm-and-down"
            >
              <v-col
                cols="12"
                sm="12"
                md="5"
                align="left"
              >
                <v-img
                max-width="250"
                src="/img/logo_minagricultura.png"
                ></v-img>
                <v-img
                class="mt-5"
                max-width="250"
                src="/img/fao_blanco.png"
                ></v-img>
                <v-img
                class="mt-5"
                max-width="250"
                src="/img/fao_logo_blanco.png"
                ></v-img>
              </v-col>
            </v-col>
            <v-divider
              color="white"
              inset
              vertical
            >
            </v-divider>
            <v-col
              cols="12"
              sm="12"
              md="4"
              align="left"
            >
              <p class="font-16 font-weight-bold">Herramienta</p>
              <p>Dirección: Calle 72 No.7-82 Piso 7/ - Organización de las Naciones Unidas para la Alimentación y la Agricultura FAO</p>
              <p>Código postal: 110311</p>
            </v-col>
            <v-divider
              color="white"
              inset
              vertical
            >
            </v-divider>
            <v-col
              cols="12"
              sm="12"
              md="3"
              align="left"
            >
              <p class="font-16 font-weight-bold"><v-icon color="white">mdi-phone</v-icon>Contacto</p>
              <p>Teléfono conmutador: +5713465101</p>
              <p>Correo institucional: fao-co@fao.org</p>
            </v-col>
         </v-row>

        </v-card-text>

        </v-expansion-panel-content>

        </v-expansion-panel>
        </v-expansion-panels>

        <v-container
          fluid
          class="d-md-none"
          style="background-color:white;"
        >
          <v-row dense>
            <v-col
              cols="4"
              md="4"
              sm="4"
              align="center"
            >
              <v-img
                max-width="150"
                src="/img/fao_logo.png"
              >
              </v-img>
            </v-col>
            <v-col
              cols="4"
              md="4"
              sm="4"
              class="mt-1"
              align="center"
            >
              <v-img
                max-width="150"
                src="/img/fao_azul.png"
              >
              </v-img>
            </v-col>
            <v-col
              cols="4"
              md="4"
              sm="4"
              class="mt-1"
              align="center"
            >
              <v-img
                max-width="180"
                src="/img/logo_minagricultura.png"
              >
              </v-img>
            </v-col>
          </v-row>
        </v-container>

      </v-card>

    </v-footer>

</v-container>
</template>
<script>
export default {
  name: 'footerApp',
  data: () => ({
    panel: [0, 1],
    padless: true,
    variant: 'absolute'
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
    },
    heightFooter () {
      var color = 'background-primary-dark color-primary-dark';
      switch (this.$vuetify.breakpoint.name) {
        case 'xs':
          color = 'background-primary-dropdowns color-primary-dark font-weight-bold';
          break
        case 'sm':
          color = 'background-primary-dropdowns color-primary-dark font-weight-bold';
          break
      }

      return color;
    },
  }
}
</script>
