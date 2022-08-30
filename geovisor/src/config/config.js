import north from  '../assets/img/north.png';
import climatico from '../assets/img/Climático.png'
import antropicos from '../assets/img/Eventos antrópicos o por actividades humanas.png'
import financieros from '../assets/img/Financiero y mercados.png'
import sanitario from '../assets/img/Sanitario.png'
import otros_eventos_naturales from '../assets/img/Otros eventos naturales.png'
import faoimg from '../assets/img/fao.png'
import echoimg from '../assets/img/echo.png'
import ministryimg from '../assets/img/ministry.png'
import sidebarFirstStep from '../assets/img/sidebar_paso_uno.jpg'
import sidebarSecondStep from '../assets/img/sidebar_paso_dos.jpg'
import sidebarThirdStep from '../assets/img/sidebar_paso_tres.jpg'

const configs = {
    texts: {
        termsAndConditions: `
        <div class="SweetModalTitle"><b>HERRAMIENTA PARA LA CONSULTA DE DAÑOS Y PÉRDIDAS DEL SECTOR AGROPECUARIO</b></div>
        <br><p align="center"><b>TÉRMINOS Y CONDICIONES</b></p>

        <div style="text-align:justify">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        </div>
        <br>
            <div class="row justify-content-center">
                <img class="col" style="max-height:60px; width: auto;height: auto;" src=${echoimg}>    
                <img class="col" style="max-height:60px; width: auto;height: auto;" src=${faoimg}>
                <img class="col" style="max-height:60px; width: auto;height: auto;" src=${ministryimg}> 
            </div>
        `
    },
    styles : {
        SpatialReferenceStyle: {
            fillColor: "#3366CC",
            color: 'white',
            weight: 2,
            opacity: 0.6,
            fillOpacity: 0.6,
            z_index:1
        },
        SpatialReferencHovereStyle: {
            fillColor: "#0B1AA2",
            weight: 2,
            opacity: 1,
            fillOpacity: 0.6,
            z_index:1
        }
    },
    images: {
        sidebarFirstStep: sidebarFirstStep,
        sidebarSecondStep: sidebarSecondStep,
        sidebarThirdStep: sidebarThirdStep,
        north:north,
        "Climático": climatico,
        "Antrópicos o por actividades humanas": antropicos,
        "Financiero y mercados": financieros,
        "Sanitario": sanitario,
        "Otros eventos naturales": otros_eventos_naturales,
    },
    reportsUrl: {
        forestal: "http://wpfao.azurewebsites.net/tablero-forestal/",
        agricola: "http://wpfao.azurewebsites.net/tablero-agricola/",
        apicola: "http://wpfao.azurewebsites.net/tablero-apicola/",
        pesquero: "http://wpfao.azurewebsites.net/tablero-pesquero/",
        pecuario: "http://wpfao.azurewebsites.net/tablero-pecuario/",
    }
}

export {configs}