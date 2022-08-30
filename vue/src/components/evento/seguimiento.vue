<template>
  <div>

    <v-dialog
      v-model="dialogSeguimiento"
      persistent
      max-width="850px"
    >

      <v-overlay :value="loading">
        <v-progress-circular
          indeterminate
          size="64"
        ></v-progress-circular>
      </v-overlay>

      <v-card
      class="border-basic"
      flat
      >
        <div style="text-align:right">
          <v-btn class="color-primary-dark" icon dark @click="cerrarModal()">
            <v-icon>mdi-close-circle</v-icon>
          </v-btn>
        </div>

        <v-container>

          <v-subheader class="title-basic subtitle font-weight-bold">
            <span>Seguimientos</span>
          </v-subheader>
          <v-subheader><span>{{ dataEvento.descrip_llegada_casco_urbano }} </span></v-subheader>
          <v-divider></v-divider>

          <v-chip class="ma-2">Fecha Evento: {{ dataEvento.fecha_registro_evento }} </v-chip>
          <v-chip class="ma-2">Tipo Evento: {{ dataEvento.tipo_evento }} </v-chip>

          <v-container>
            <v-row>
              <v-col
                cols="12"
                md="6"
                sm="12"
              >
              <v-row>
                <v-col
                class="mt-3"
                style="padding:0px;"
                cols="12"
                md="12"
                sm="12"
                >
                  <v-text-field
                    label="Filtrar"
                    v-model="searchSeguimientos"
                    dense
                    outlined
                    prepend-inner-icon="mdi-filter"
                    v-on:keyup="filtrarSeguimiento"
                    >
                  </v-text-field>
                </v-col>

                <v-col
                  style="margin-top:0px;padding:0px;"
                  cols="12"
                  md="12"
                  sm="12"
                >
                  <v-list
                  class="border-basic overflow-y-auto"
                  style="width:auto; min-height:220px; max-height: 220px; border:1px solid LightGray;"
                  three-line
                  >
                    <v-list-item-group
                    active-class="primary--text"
                    multiple
                    >
                      <v-list-item
                      style="border-bottom:1px solid LightGray"
                      v-for="message in filter"
                      :key="message.cod_evento_seguimiento"
                      inset
                      >
                        <v-list-item-avatar
                        class="background-primary-dark"
                        style="width:auto; height:40px; border-radius:5px;"
                        >
                          <span style="color:white;">{{ message.nombre_usuario.substr(0,2).toUpperCase() }}</span>
                        </v-list-item-avatar>

                        <v-list-item-content>
                            <v-list-item-title>
                              <strong>{{ message.nombre_usuario }}</strong>
                            </v-list-item-title>
                            <p align="start">{{message.observacion}}</p>
                          </v-list-item-content>

                          <v-list-item-action>
                            {{ message.fecha_registro }}
                            <v-btn icon>
                              <v-icon  v-if="message.adjuntos.length > 0" @click="listadoAdjuntos(message.adjuntos)">mdi-paperclip</v-icon>
                            </v-btn>
                          </v-list-item-action>

                      </v-list-item>
                    </v-list-item-group>
                </v-list>

                </v-col>
              </v-row>
              </v-col>
              <v-col
            cols="12"
            md="6"
            sm="12"
            >
              <v-row>
                <v-col
                cols="12"
                md="12"
                sm="12"
                >

                  <v-form
                    lazy-validation
                    ref="form"
                    name="form1"
                    v-model="valid"
                    >
                      <v-row no-gutters>
                        <v-col
                        cols="12"
                        md="12"
                        >
                          <v-file-input
                          class="border-basic"
                          prepend-inner-icon="mdi-paperclip"
                          prepend-icon=""
                          multiple
                          dense
                          outlined
                          solo
                          flat
                          counter
                          small-chips
                          show-size
                          truncate-length="15"
                          label="Adjuntar archivo"
                          v-model="seguimiento.adjuntos"
                          >
                          </v-file-input>
                        </v-col>

                      <v-col
                      cols="12"
                      md="12"
                      >
                        <v-textarea
                        outlined
                        solo
                        flat
                        label="Observación"
                        v-model="seguimiento.observacion"
                        :rules="nameRules"
                        required
                        maxlength="180"
                        >
                        </v-textarea>
                      </v-col>

                      <v-col
                      cols="12"
                      md="12"
                      >
                        <v-btn
                        class="background-primary-dark button-basic"
                        elevation="2"
                        block
                        raised
                        depressed
                        @click="guardarSeguimiento()"
                        >Agregar</v-btn>
                      </v-col>
                    </v-row>

                  </v-form>
                </v-col>
              </v-row>
              </v-col>
            </v-row>
          </v-container>

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

        </v-container>
      </v-card>

    </v-dialog>
  </div>
</template>

<script>
// import { VueEditor } from 'vue2-editor'
import { seguimientoEvento } from '../../services/api'
import jwtDecode from 'jwt-decode'

export default {
  name: 'seguimientos',
  props: ['dataEvento'],
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
      const idEvento = this.dataEvento.cod_evento

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
        const idEvento = this.dataEvento.cod_evento
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

            this.$swal({
              icon: 'success',
              text: 'Seguimiento creado.',
              confirmButtonText: 'Aceptar',
            });

            this.seguimiento = {}
          } else {
            console.log(res)
          }
        } catch (error) {
          this.$swal({
            icon: 'error',
            text: error.response.data.message,
            confirmButtonText: 'Aceptar',
          });
          console.log(error)
        }
      } else {
        this.$swal({
          icon: 'error',
          text: 'Errores en el formulario.',
          confirmButtonText: 'Aceptar',
        });
      }

      this.loading = false
    },
    cerrarModal() {
      this.$emit('compList');
    }
  },
  created () {
    this.filter = this.messages
  },
  computed: {
  }
}
</script>
