<template>
  <div>
    <v-container fluid>

      <!-- Listado de productores agregados al evento -->
      <!-- <p class="font-weight-bold"> Información del productor </p> -->
      <v-data-table
        :headers="productoresHeaders"
        :items="productores"
        item-key="nombre"
        class="elevation-2"
      >
        <template v-slot:top>
          <v-toolbar
            flat
            class="border-head-table font-weight-bold"
            height="10px"
            style="background-color:#F2F2F2"
          ></v-toolbar>
        </template>
        <template v-slot:item.actions="{ item }">
          <v-icon
            small
            class="mr-2"
            color="#004884"
            @click="editarProductor(item)"
          >
          mdi-pencil
          </v-icon>
          <v-icon
            small
            color="#004884"
            @click="deleteProductor(item)"
          >
          mdi-delete
          </v-icon>
        </template>
      </v-data-table>
      <v-row class="mt-2">
        <v-col
          cols="12"
          md="9"
          sm="12"
        >
        </v-col>
        <v-col
          cols="12"
          md="3"
          sm="12"
        >
          <v-btn
            class="background-primary-dark button-basic"
            elevation="2"
            block
            @click="dialog = true"
          >
            Agregar productor
          </v-btn>
        </v-col>
      </v-row>

      <!-- Formulario para insertar nuevos productores -->
      <v-dialog
        v-model="dialog"
        persistent :overlay="false"
        max-width="100%"
        transition="dialog-transition"
      >

        <v-card
          class="border-basic"
          flat
        >
          <div style="text-align:right">
            <v-btn class="color-primary-dark" icon dark @click="cerrarModal">
              <v-icon>mdi-close-circle</v-icon>
            </v-btn>
          </div>

          <v-card-title
            primary-title
          >
            <v-container class="color-primary-dark font-weight-bold">
              <v-row
                dense
                class="align-center justify-center container-titles"
                style="height:80px"
              >
               <v-col
                 cols="12"
                 md="12"
                 sm="12"
                 align="center"
                 justify="center"
                >
                  Productor
                </v-col>
              </v-row>
            </v-container>
          </v-card-title>

          <v-container>
          <v-form
            lazy-validation
            ref="form"
            v-model="validateForm"
          >
           <v-row dense class="section">

             <v-col
               cols="12"
               md="4"
               >
               <v-autocomplete
                 label="Condición juridica del productor"
                 :search-input.sync="infoProveedor.nameCondJuridica"
                 :items="condJuridicas"
                 v-model="infoProveedor.condJuridica"
                 item-value="valor"
                 dense
                 outlined
                 solo
                 clearable
                 flat
                 required
                 :rules="required"
                 >
               </v-autocomplete>
             </v-col>

             <v-col
               cols="12"
               md="4"
               >
               <v-text-field
                 :label="esEmpresa ? 'Nombre de la personería jurídica' : 'Nombres y apellidos'"
                 v-model="infoProveedor.nombre"
                 dense
                 outlined
                 solo
                 flat
                 required
                 :rules="required"
                 >
               </v-text-field>
             </v-col>

             <v-col
               cols="12"
               md="4"
               >
               <v-autocomplete
                 label="Tipo documento"
                 :search-input.sync="infoProveedor.nameTipoDcto"
                 :items="compTipoDcto"
                 item-value="valor"
                 v-model="infoProveedor.tipoDcto"
                 dense
                 outlined
                 solo
                 flat
                 required
                 clearable
                 :rules="required"
                 >
               </v-autocomplete>
             </v-col>

             <v-col
               cols="12"
               md="4"
               >
               <v-text-field
                 label="Documento"
                 v-model="infoProveedor.dcto"
                 dense
                 outlined
                 solo
                 flat
                 required
                 :onkeypress="regexNumber"
                 :rules="required"
                 >
               </v-text-field>
             </v-col>

             <v-col
               cols="12"
               md="4"
               >
               <v-text-field
                 label="E-mail"
                 hint="E-mail"
                 v-model="infoProveedor.email"
                 dense
                 outlined
                 solo
                 flat
                 required
                 :rules="emailRules"
                 >
               </v-text-field>
             </v-col>

               <v-col
                 cols="12"
                 md="4"
                 >
                 <v-autocomplete
                   label="Tipo de productor"
                   :search-input.sync="infoProveedor.nameTipoProd"
                   :items="tiposProd"
                   item-value="valor"
                   v-model="infoProveedor.tipoProd"
                   dense
                   outlined
                   solo
                   flat
                   required
                   :rules="required"
                   clearable
                   >
                 </v-autocomplete>
               </v-col>

               <v-col
                 cols="12"
                 md="4"
                 >
                 <v-autocomplete
                   label="Tipo de relación con el predio"
                   :search-input.sync="infoProveedor.nameRelPre"
                   :items="tiposRelPre"
                   item-value="valor"
                   v-model="infoProveedor.relPre"
                   dense
                   solo
                   flat
                   outlined
                   required
                   clearable
                   :rules="required"
                   >
                 </v-autocomplete>
               </v-col>

             <v-col
                cols="12"
                md="4"
              >
               <v-text-field
                 label="Direccion residencia"
                 v-model="infoProveedor.dirRes"
                 dense
                 outlined
                 solo
                 flat
                 required
                 :rules="required"
                 >
               </v-text-field>
             </v-col>

              <v-col
                cols="12"
                md="4"
              >
                <v-text-field
                  label="Número de teléfono"
                  v-model="infoProveedor.tel"
                  dense
                  outlined
                  solo
                  flat
                  required
                  :rules="required"
                >
                </v-text-field>
              </v-col>

              <v-col
               cols="12"
               md="4"
              >
                <v-autocomplete
                 v-if="!esEmpresa"
                 label="sexo"
                 :search-input.sync="infoProveedor.nameSexo"
                 :items="listSexo"
                 item-value="valor"
                 v-model="infoProveedor.sexo"
                 dense
                 outlined
                 solo
                 flat
                 required
                 clearable
                 :rules="required"
                >
               </v-autocomplete>
             </v-col>

             <v-menu
               v-if="!esEmpresa"
               v-model="mfnac"
               :close-on-content-click="false"
               :nudge-right="40"
               transition="scale-transition"
               offset-y
               min-width="auto"
               >
               <template v-slot:activator="{ on, attrs }">

                 <v-col
                   cols="12"
                   md="4"
                   >
                    <v-text-field
                     v-model="infoProveedor.fechaNac"
                     label="Fecha nacimiento"
                     readonly
                     v-bind="attrs"
                     v-on="on"
                     outlined
                     dense
                     solo
                     flat
                     required
                     :rules="required"
                    >
                   </v-text-field>
                 </v-col>
               </template>

               <v-col
                 cols="12"
                 md="4"
                 >
                 <v-date-picker
                   v-model="infoProveedor.fechaNac"
                   @input="mfnac = false"
                   outlined
                 ></v-date-picker>
               </v-col>

             </v-menu>

              <v-col
               cols="12"
               md="4"
              >
                <v-autocomplete
                 v-if="!esEmpresa"
                 label="Grupo étnico"
                 :search-input.sync="infoProveedor.nameGEtnico"
                 :items="gruposEtnicos"
                 item-value="valor"
                 v-model="infoProveedor.gEtnico"
                 dense
                 solo
                 flat
                 outlined
                 required
                 clearable
                 :rules="required"
                >
               </v-autocomplete>
              </v-col>

              <v-col
               cols="12"
               md="12"
              >
                <v-checkbox
                  v-model="infoProveedor.tratamientoDatos"
                  label="¿Acepta la política de tratamiento y protección de datos personales?"
                  required
                  :rules="required"
                >
                </v-checkbox>
              </v-col>
           </v-row>
           </v-form>

            <v-row class="mt-2">
              <v-col
                  cols="12"
                  md="10"
                  sm="12"
              >
              </v-col>
              <v-col
                  cols="12"
                  md="2"
                  sm="12"
              >
                <v-btn
                  class="background-primary-dark button-basic"
                  elevation="2"
                  block
                  @click="addProductor"
                >
                  Agregar
                </v-btn>
              </v-col>
            </v-row>
          </v-container>
      </v-card>

      </v-dialog>

    </v-container>
  </div>
</template>
<script>

import { getData } from '../../indexedDb/getData';

export default {
  name: 'dataProductor',
  props: ['obtenerData'],
  data () {
    return {

      // variables del sistema
      e6: 3,
      tab: 0,
      mfnac: false,
      infoProveedor: {},
      condJuridicas: [],
      tiposDcto: [],
      listSexo: [],
      gruposEtnicos: [],
      tiposProd: [],
      tiposRelPre: [],
      validateForm: true,
      editedIndex: -1,
      required: [v => !!v || 'Campo requerido',],
      regexNumber: "return (event.charCode >= 48 && event.charCode <= 57)",
      emailRules: [
        v => !!v || 'Campo obligatorio',
        v => /.+@.+\..+/.test(v) || 'E-mail no es valido'
      ],

      // variables de componentes
      // modal agregar nuevo productor
      dialog: false,
      notifications: false,
      sound: true,
      widgets: false,
      // tabla listado de productores agregados al evento
      expanded: [],
      productoresHeaders: [
        {text: 'Productor',align: 'start',sortable: false,value: 'nombre'},
        {text: 'Condición juridica',align: 'start',sortable: false,value: 'nameCondJuridica'},
        {text: 'Tipo documento',align: 'start',sortable: false,value: 'nameTipoDcto'},
        {text: 'No.Documento',align: 'start',sortable: false,value: 'dcto'},
        {text: 'E-mail',align: 'start',sortable: false,value: 'email'},
        {text: 'Tipo',align: 'start',sortable: false,value: 'nameTipoProd'},
        {text: 'Relación predio',align: 'start',sortable: false,value: 'nameRelPre'},
        {text: 'Dirección',align: 'start',sortable: false,value: 'dirRes'},
        {text: 'Teléfono',align: 'start',sortable: false,value: 'tel'},
        {text: 'Sexo',align: 'start',sortable: false,value: 'nameSexo'},
        {text: 'Nacimiento',align: 'start',sortable: false,value: 'fechaNac'},
        { text: 'Acciones', value: 'actions', sortable: false, width: '2%' },
      ],
      productores: []
    }
  },
  async mounted () {
    await this.getDataProductor();
    this.edicionProductor();
  },
  computed: {
    width () {
      let status

      switch (this.$vuetify.breakpoint.name) {
        case 'xs':
          status = true
          break
        case 'sm':
          status = true
          break
        case 'md':
          status = false
          break
        case 'lg':
          status = false
          break
        case 'xl':
          status = false
          break
      }

      return status
    },
    esEmpresa () {
      return (this.infoProveedor.condJuridica === 2)
    },
    compTipoDcto () {
      if (this.esEmpresa) {
        return this.tiposDcto.filter(item => item.persona === 'juridica')
      }
      return this.tiposDcto.filter(item => item.persona === 'natural')
    }
  },
  methods: {
    cerrarModal() {
      this.dialog = false;
    },
    edicionProductor() {
      const dataEvento = this.$route.params.evento;
      if (dataEvento !== undefined) {
        if (dataEvento.dataProductor.length > 0) {
          this.productores = dataEvento.dataProductor;
        }
      }
    },
    addProductor () {
      console.log(this.infoProveedor);
      if (this.$refs.form.validate()) {

        if (Object.entries(this.infoProveedor).length === 0) {
          return
        }
        if (this.editedIndex > -1) {
          Object.assign(this.productores[this.editedIndex], this.infoProveedor);
        } else {
          this.productores.push(this.infoProveedor);
        }
        this.infoProveedor = {};
        this.obtenerData(this.productores);
        this.dialog = false;
        this.editedIndex = -1;
      }
    },
    deleteProductor(item) {
      this.$swal({
          title: 'Confirmación',
          text: 'Eliminar productor?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar',
          showCloseButton: true,
          showLoaderOnConfirm: true
      }).then((result) => {
        if(result.value) {
          const editedIndex = this.productores.indexOf(item)
          this.productores.splice(editedIndex, 1)
          this.obtenerData(this.productores)
        }
      })
    },
    editarProductor(item) {
      this.editedIndex = this.productores.indexOf(item);
      this.infoProveedor = Object.assign({}, item);
      this.dialog = true;
    },
    async getDataProductor () {
      try {
        const data = await getData('productor', true);

        for (const documento in data.tiposDocumento) {
          var addDocument = {
            valor: data.tiposDocumento[documento][0],
            text: data.tiposDocumento[documento][1],
            persona: data.tiposDocumento[documento][2]
          }
          this.tiposDcto.push(addDocument)
        }

        for (const documento in data.condicionJuridica) {
          var addConJuridica = {
            valor: data.condicionJuridica[documento][0],
            text: data.condicionJuridica[documento][1]
          }
          this.condJuridicas.push(addConJuridica)
        }

        for (const documento in data.sexo) {
          var addSexo = {
            valor: data.sexo[documento][0],
            text: data.sexo[documento][1]
          }
          this.listSexo.push(addSexo)
        }

        for (const documento in data.gruposEtnicos) {
          var addGrupoEtnico = {
            valor: data.gruposEtnicos[documento][0],
            text: data.gruposEtnicos[documento][1]
          }
          this.gruposEtnicos.push(addGrupoEtnico)
        }

        for (const documento in data.tipoProductor) {
          var addTipoProductor = {
            valor: data.tipoProductor[documento][0],
            text: data.tipoProductor[documento][1]
          }
          this.tiposProd.push(addTipoProductor)
        }

        for (const documento in data.tipoRelacionPredio) {
          var addTipoRelacion = {
            valor: data.tipoRelacionPredio[documento][0],
            text: data.tipoRelacionPredio[documento][1]
          }
          this.tiposRelPre.push(addTipoRelacion)
        }

      } catch (error) {
        console.log(error)
      }
    }
  },
}
</script>
