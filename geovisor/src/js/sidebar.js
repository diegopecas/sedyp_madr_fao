import {returnPuntos, returnMunicipios, returnDepartamentos} from './map.js'
import {defaultSidebarInformation} from './services'

const sisProductivo = document.querySelector('#sistema_productivo')
const tipoEvento = document.querySelector('#tipo_evento')
const tipoVisualizacion = document.querySelector('#tipo_visualizacion')
const filtrarInformacionBoton = document.querySelector('#filtrar_informacion_boton')
const fechaMinima = document.getElementById('startdate')
const fechaMaxima = document.getElementById('finaldate')
const listadoNombreUerContainer = document.querySelector('#listado_nombre_uer_container')
const textoValidador = document.querySelector('#textovalidador')
const optionContainer = {
    Departamento: [],
    Municipio: []
}

let listUer;

defaultSidebarInformation(sisProductivo, tipoEvento, fechaMinima, optionContainer)

tipoVisualizacion.addEventListener('change', function (event) {

    textoValidador.classList.add('invalid-feedback')
    let tipo = event.target.value   
    if(tipo === "Departamento"|| tipo === "Municipio"){
        let content =`
        <h2 class="card-header bg-fao txt-fao" id="headingThree">
            <button class="btn btn-link txt-fao no-pointer-event" type="button" data-bs-toggle="collapse" data-bs-target="#" aria-expanded="true" aria-controls="collapseThree">
                <b>Nombre de los ${tipo}s</b>
            </button>
        </h2>
        <div id="collapseThree" class="accordion-collapse collapse show" aria-labelledby="headingThree" data-bs-parent="#accordionExample">
            <div class="card-body">
                <select id="listado_uer" class="selectpicker show-tick form-control" data-live-search="true" multiple title="Elegir..." data-actions-box="true">
                </select>
            </div>
        </div>`
        listadoNombreUerContainer.innerHTML = content
        listUer = document.querySelector('#listado_uer')   
        optionContainer[tipo].forEach((option) => {
            listUer.append(option)
        })
        $('#listado_uer').selectpicker();
    }
    else {
        listadoNombreUerContainer.innerHTML = ""
    }
});

const visualizationTypeData = () => {

        let sisProductivoArray = [];
        let tipoEventoArray = [];
        let listadoNombreUerArray = [];

        if(sisProductivo.selectedOptions.length === 0) {
            for (let child of sisProductivo.children) {
                sisProductivoArray.push(child.value)
            }
        } 
        else {
            for (let selected of sisProductivo.selectedOptions) {
                sisProductivoArray.push(selected.value)
            }
        }
    
        if(tipoEvento.value===""){
            for (let child of tipoEvento.children) {
                tipoEventoArray.push(child.value)
            }
            tipoEventoArray.shift()
        } else { tipoEventoArray = tipoEvento.value}
        
        if (tipoVisualizacion.value === "Departamento" || tipoVisualizacion.value === "Municipio"){
            if(listUer.value===""){
                for (let child of listUer.children) {
                    listadoNombreUerArray.push(child.value)
                }
            } 
            else {
                for (let selected of listUer.selectedOptions) {
                    listadoNombreUerArray.push(selected.value)
                }              
            }
        }
        
        switch (tipoVisualizacion.value){
            case 'Departamento':
                returnDepartamentos(sisProductivoArray, tipoEventoArray, listadoNombreUerArray, fechaMinima.value, fechaMaxima.value);
                break;

            case 'Municipio':
                returnMunicipios(sisProductivoArray, tipoEventoArray, listadoNombreUerArray, fechaMinima.value, fechaMaxima.value);
                break;

            case 'Puntual':
                returnPuntos(sisProductivoArray, tipoEventoArray, fechaMinima.value, fechaMaxima.value);
                break;
        }
}

(() => {
    const fecha = new Date()
    let year = fecha.getFullYear()
    let month = (parseInt(fecha.getMonth())+1) < 10 ? '0'+(parseInt(fecha.getMonth())+1) : (parseInt(fecha.getMonth())+1);
    let day = (fecha.getDate()) < 10 ? '0'+fecha.getDate() : fecha.getDate();
    let fechaTexto = (year+'-'+month+'-'+day).toString()

    fechaMaxima.setAttribute("value",fechaTexto)
    fechaMaxima.setAttribute("max",fechaTexto)

    let elem = document.querySelector('#footer')
    elem.append(fecha)
})();

(function () {
    'use strict'
    let forms = document.querySelectorAll('.needs-validation')

    Array.prototype.slice.call(forms).forEach(function (form) {
        filtrarInformacionBoton.addEventListener('click', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
                textoValidador.classList.remove('invalid-feedback')
            }
            else {
                visualizationTypeData()
            }
            
            form.classList.add('was-validated')
        }, false)
      })
})();
