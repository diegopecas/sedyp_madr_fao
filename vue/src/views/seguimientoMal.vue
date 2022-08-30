<template>
  <div>
  <v-dialog
    v-model="dialogSeguimiento"
    persistent
    max-width="700px"
  >

    <v-card
     class="border-basic"
     flat
    >
    <div style="text-align:right">
      <v-btn class="color-primary-dark" icon dark @click="cerrarModal()">
        <v-icon>mdi-close-circle</v-icon>
      </v-btn>
    </div>

    <v-subheader>
      <v-icon>mdi-map-marker</v-icon>
      <span>Observación de la ubicación</span>
    </v-subheader>
    <v-subheader><span>{{ $route.params.evento.descrip_llegada_casco_urbano }} </span></v-subheader>
    <v-divider ></v-divider>
    <v-chip class="ma-2">Fecha Evento: {{ $route.params.evento.fecha_registro_evento }} </v-chip>
    <v-chip class="ma-2">Tipo Evento: {{ $route.params.evento.tipo_evento }} </v-chip>
    <br>
    <br>
    <v-row justify="space-around">
      <v-card width="100%">

        <v-card-text>
          <div class="ml-8 mb-2">
            <v-container>
              <v-row>
                  <v-col
                  cols="12"
                  md="4"
                  >
                    <v-text-field
                      label="Filtrar"
                      v-model="searchSeguimientos"
                      dense
                      outlined
                      filled
                      prepend-icon="mdi-filter"
                      v-on:keyup="filtrarSeguimiento"
                      >
                    </v-text-field>
                  </v-col>
                </v-row>
              </v-container>
          </div>

          <div style="width:auto; height:auto; max-height: 500px; overflow: auto;">
            <v-timeline
              align-top
              dense
            >
              <v-timeline-item
                v-for="message in filter"
                :key="message.cod_evento_seguimiento"
                color="primary"
              >
                <template v-slot:icon>
                  <span style="color:white;">{{ message.nombre_usuario.substr(0,2).toUpperCase() }}</span>
                </template>
                <v-card class="elevation-1" width="80%">
                  <div class="ml-2">
                    <div class="font-weight-normal">
                      <strong>{{ message.nombre_usuario }}</strong> @{{ message.fecha_registro }}
                      <v-icon  v-if="message.adjuntos.length > 0" @click="listadoAdjuntos(message.adjuntos)">mdi-attachment</v-icon>
                    </div>
                    <div>{{ message.observacion }}</div>
                  </div>
                </v-card>
              </v-timeline-item>
            </v-timeline>
          </div>

          <v-container>

            <v-progress-linear
              class="mt-1"
              :active="loading"
              :indeterminate="loading"
              color="green accent-4"
              rounded
              height="6"
            ></v-progress-linear>

            <v-form
              lazy-validation
              ref="form"
              name="form1"
              v-model="valid"
              >
                <v-row :no-gutters="noGutters">
                  <v-col
                  cols="12"
                  md="12"
                  >
                    <v-file-input
                    multiple
                    dense
                    counter
                    small-chips
                    show-size
                    truncate-length="15"
                    v-model="seguimiento.adjuntos"
                    >
                    </v-file-input>
                  </v-col>

                  <v-col
                  cols="12"
                  md="12"
                  >
                    <v-textarea
                    dense
                    outlined
                    filled
                    label="Observación"
                    v-model="seguimiento.observacion"
                    :rules="nameRules"
                    required
                    >
                    </v-textarea>
                  </v-col>
                </v-row>
                <v-btn
                block
                elevation="2"
                raised
                depressed
                color="error"
                @click="guardarSeguimiento()"
                >Agregar</v-btn>
            </v-form>
          </v-container>

        </v-card-text>
      </v-card>
    </v-row>
    <br>
    <br>
    <br>

    <!-- Modal con listado de adjuntos por seguimiento -->
    <v-dialog
      v-model="dialog"
      scrollable
      max-width="300px"
    >

      <v-card>
        <v-card-title>Adjuntos</v-card-title>
        <v-divider></v-divider>
        <v-card-text style="height: auto;">
          <v-list-item
            v-for="adjunto in descargaAdjuntos"
            :key="adjunto.id"
          >
            <v-list-item-icon>
               <v-icon>mdi-download-box</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <a
                @click="descargarAdjunto(adjunto)"
              >
              {{ adjunto.nombre }}
              </a>
            </v-list-item-content>
          </v-list-item>
          <br>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn
            color="blue darken-1"
            text
            @click="dialog = false"
          >
            Cerrar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-card>

  </v-dialog>
  </div>
</template>

<script>
// import { VueEditor } from 'vue2-editor'
import { seguimientoEvento } from '../services/api'
import jwtDecode from 'jwt-decode'

export default {
  name: 'seguimientos',

  data: () => ({
    dialogSeguimiento: true,
    loading: false,
    valid: true,
    // Rules
    nameRules: [
      v => !!v || 'Campo obligatorio'
    ],
    content: '',
    seguimiento: [],
    searchSeguimientos: '',
    filter: [],
    noGutters: true,
    messages: [],
    dialog: false,
    descargaAdjuntos: []
  }),
  async mounted () {
    await this.getSeguimientos()
  },
  methods: {
    filtrarSeguimiento () {
      var result = this.messages.filter(item => {
        return item.observacion.toLowerCase().includes(this.searchSeguimientos.toLowerCase())
      })

      if (!result) {
        this.filter = this.messages
      } else {
        this.filter = result
      }
    },
    listadoAdjuntos (adjuntos) {
      this.dialog = true
      this.descargaAdjuntos.splice(0)

      for (const adjunto in adjuntos) {
        const newAdjunto = {
          id: adjuntos[adjunto].cod_evento_seguimiento_adju,
          nombre: adjuntos[adjunto].nombre_archivo,
          rutaFinal: adjuntos[adjunto].ruta + '/' + adjuntos[adjunto].nombre_archivo
        }

        this.descargaAdjuntos.push(newAdjunto)
      }
    },
    async descargarAdjunto (adjunto) {
      const ruta = adjunto.rutaFinal
      const nombre = adjunto.nombre

      try {
        const res = await seguimientoEvento.getAdjunto({ ruta, nombre })

        if (res.status === 200) {
          const data = res.data

          const url = window.URL.createObjectURL(new Blob([data]))
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', nombre) // or any other extension
          document.body.appendChild(link)
          link.click()
        }
      } catch (error) {
        console.log(error)
      }
    },
    async getSeguimientos () {
      const idEvento = this.$route.params.evento.cod_evento

      try {
        const res = await seguimientoEvento.getSeguimiento({ idEvento })

        if (res.status === 200) {
          const encoded = res.data.token
          const decoded = jwtDecode(encoded)
          const obj = decoded.seguimientos
          this.messages.splice(0)

          for (const seguimiento in obj.seguimientos) {
            this.messages.push(obj.seguimientos[seguimiento])
          }
        }
      } catch (error) {
        console.log(error)
      }
    },
    async guardarSeguimiento () {
      if (this.$refs.form.validate()) {
        const idEvento = this.$route.params.evento.cod_evento
        const observacion = this.seguimiento.observacion
        this.loading = true
        const formData = new FormData()
        var contador = 0

        if (this.seguimiento.adjuntos) {
          for (const file of this.seguimiento.adjuntos) {
            formData.append('files' + contador, file, file.name)
            contador++
          }
        }

        // se captura el id del usuario del localStorage
        const dataUserLocal = JSON.parse(localStorage.getItem('dataUser'))

        formData.append('idUsuario', dataUserLocal.id)
        formData.append('contador', contador)
        formData.append('idEvento', idEvento)
        formData.append('observacion', observacion)

        if (!idEvento) {
          this.$toasted.error('Ocurrio un erro al capturar el ID del evento.', { duration: 4000 })
          this.loading = false
          return
        }

        try {
          const res = await seguimientoEvento.setSeguimiento(formData)

          if (res.status === 200) {
            const encoded = res.data.token
            const decoded = jwtDecode(encoded)
            const obj = decoded.seguimientos

            this.messages.splice(0)

            for (const seguimiento in obj.seguimientos) {
              this.messages.push(obj.seguimientos[seguimiento])
            }

            this.$toasted.success('Se creo el seguimiento.', { duration: 4000 })
            this.seguimiento = {}
          } else {
            console.log(res)
          }
        } catch (error) {
          this.$toasted.error(error.response.data.message, { duration: 4000 })
          console.log(error)
        }
      } else {
        this.$toasted.error('Errores en el formulario.', { duration: 4000 })
      }

      this.loading = false
    },
    cerrarModal() {
      this.dialogSeguimiento = false;
    }
  },
  created () {
    this.filter = this.messages
  },
  computed: {
  }
}
</script>
