import '../css/map.css'
import './lib/L.Control.Coordinates'
import './lib/L.EasyButton'
import './lib/L.Control.PanelLayer'
import './lib/L.Control.Sidebar'
import {informationEndPoint} from './services'
import { configs } from '../config/config'
import {TermsAndConditions} from './TermsAndConditions'
import {ModalUer} from './ModalUer'
import jwt_decode from 'jwt-decode'


const map = L.map('mymap',{
    attributionControl: false,
    maxZoom:17, 
    minZoom:2.5,
	EPSG:4326
}).setView([4.505, -75.09], 6);

const basemap = L.esri.basemapLayer('Imagery').addTo(map);

const sidebar = L.control.sidebar('left_sidebar', {
    position: 'left'
});

map.addControl(sidebar);

const clusterGroup = L.markerClusterGroup({
	showCoverageOnHover: false,
    spiderfyOnMaxZoom:true,
})

const subGroupClimatico = L.featureGroup.subGroup(clusterGroup,{spiderfyOnMaxZoom: false,
	showCoverageOnHover: false,
	zoomToBoundsOnClick: true,
	disableClusteringAtZoom: 17});

const subGroupFinanciero = L.featureGroup.subGroup(clusterGroup,{spiderfyOnMaxZoom: false,
	showCoverageOnHover: false,
	zoomToBoundsOnClick: true,
	disableClusteringAtZoom: 17});

const subGroupSanitario= L.featureGroup.subGroup(clusterGroup,{spiderfyOnMaxZoom: false,
	showCoverageOnHover: false,
	zoomToBoundsOnClick: true,
	disableClusteringAtZoom: 17});

const subGroupAntropicos= L.featureGroup.subGroup(clusterGroup,{spiderfyOnMaxZoom: false,
	showCoverageOnHover: false,
	zoomToBoundsOnClick: true,
	disableClusteringAtZoom: 17});
const subGroupOtros = L.featureGroup.subGroup(clusterGroup,{spiderfyOnMaxZoom: false,
	showCoverageOnHover: false,
	zoomToBoundsOnClick: true,
	disableClusteringAtZoom: 17});

let eventosPuntuales;
let eventosMunicipio;
let eventosDepartamento;

const eventTypeSubGroup = {
    "Climático": subGroupClimatico,
    "Antrópicos o por actividades humanas": subGroupAntropicos,
    "Financiero y mercados": subGroupFinanciero,
    "Sanitario": subGroupSanitario,
    "Otros eventos naturales": subGroupOtros
}

L.esri.basemapLayer('ImageryLabels').addTo(map);
L.control.coordinates({
    position: "bottomleft" ,
    decimalSeperator:".",
    labelTemplateLat:"Latitude: {y}",
    labelTemplateLng:"Longitude: {x}",
    enableUserInput:false,
    useLatLngOrder: true,
    labelFormatterLng : function(lng){return `Longitud: ${lng.toFixed(4)}`},
    labelFormatterLat : function(lat){return `Latitud: ${lat.toFixed(4)}`},
}).addTo(map);

L.easyButton(`<i class="fas fa-home txt-fao fa-lg"></i>`, function(){
    map.setView([4.505, -75.09], 6);
}).addTo(map); 

L.easyButton(`<i class="fas fa-bars txt-fao fa-lg"></i>`, function(){
    document.getElementById("mymap").classList.toggle('active');
	document.getElementById("right_sidebar").classList.toggle('active');
}).addTo(map);

L.easyButton(`<i class="fas fa-info txt-fao fa-lg"></i>`, function(){
    new TermsAndConditions(configs.texts.termsAndConditions)
}).addTo(map);

let north = L.control({position: "bottomleft"});
north.onAdd = function(map) {
    let div = L.DomUtil.create("div", "info legend");
    div.innerHTML = `<img src=${configs.images.north} width="50px">`;
    return div;
}
north.addTo(map)

let baseMaps = [
	{
		active: true,
		name: "Mapa base",
		layer: basemap
	}
];

const layerControl =  new L.Control.PanelLayers(baseMaps, null,{
    compact: true,
    collapsed:true,
});
map.addControl(layerControl)

const iconType = (feature) => {

    let icon = configs.images[feature.properties.tipo_evento]
    
    return L.icon({
        iconUrl: icon,
        iconSize:     [40, 40/(551/701)],
        iconAnchor:   [20, 40/(551/701)], 
    });
}

const featureSubGroupAssignment = (feature, layer) => {
    layer.addTo(eventTypeSubGroup[feature.properties.tipo_evento])
}

const sidebarDefaultInformation = () => {
    let content = `
    <table style="height: 100%;">
        <tbody>
            <tr>
                <td class="align-middle">
                    <div class="row">
                        <img src=${configs.images.sidebarFirstStep} class="mx-auto w-75">  
                    </div>
                </td>
            </tr>
            <tr>
                <td class="align-middle">
                    <div class="row">
                        <img src=${configs.images.sidebarSecondStep} class="mx-auto w-75">
                    </div>
                </td>
            </tr>
            <tr>
                <td class="align-middle">
                    <div class="row">
                        <img src=${configs.images.sidebarThirdStep} class="mx-auto w-75">
                    </div>
                </td>
            </tr>
        </tbody>
    </table> 
    `
    sidebar.setContent(content)
}

const clusterGroupManager = (metric) =>{
    if(metric === 'add'){
        clusterGroup.addTo(map);
        subGroupClimatico.addTo(map);
        subGroupAntropicos.addTo(map);
        subGroupFinanciero.addTo(map);
        subGroupSanitario.addTo(map);
        subGroupOtros.addTo(map);
    } else{
        subGroupClimatico.clearLayers();
        subGroupAntropicos.clearLayers();
        subGroupFinanciero.clearLayers();
        subGroupSanitario.clearLayers();
        subGroupOtros.clearLayers();
        clusterGroup.clearLayers();

        layerControl.removeLayer(subGroupClimatico);
		layerControl.removeLayer(subGroupAntropicos);
		layerControl.removeLayer(subGroupFinanciero);
		layerControl.removeLayer(subGroupSanitario);
		layerControl.removeLayer(subGroupOtros);
        layerControl.removeLayer(clusterGroup);
    }
    
}

const clearMap = () => {
    try {
        clusterGroupManager('delete')
    }
    catch (e) {}

    try {
        map.removeLayer(eventosDepartamento);
        layerControl.removeLayer(eventosDepartamento);
    }
    catch (e) {}

    try {
        map.removeLayer(eventosMunicipio);
        layerControl.removeLayer(eventosMunicipio);
    }
    catch (e) {}
}

const evalDataResponse = (icon, title, iconColor) => {
    Swal.fire({
        position: 'bottom-end',
        toast: true,
        icon: icon,
        title: title,
        showConfirmButton: false,
        timerProgressBar: true,
        timer: 2000,
        iconColor: iconColor
    })
}

const returnMunicipios = async (sist, event, mun, inif, finalf) =>{

    let objFetch = {
        "obj": {
            "prodSis": sist,
            "tipoEvento": event,
            "cod_mun": mun,
            "fechaInicial": inif,
            "fechaFinal": finalf
        }
    };

    informationEndPoint('filterUER',objFetch).then((data) => {
        
        let response = (data.message)

        if(response.mun.length>0){

            sidebarDefaultInformation();
            clearMap();

            document.getElementById("mymap").classList.toggle('active');
	        document.getElementById("right_sidebar").classList.toggle('active');

            if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)){
                ''
            }else{
                sidebar.show()
            }

            eventosMunicipio = L.geoJSON(response.mun[0].row_to_json,{onEachFeature: function(feature, layer){

                layer.setStyle(configs.styles.SpatialReferenceStyle)

                layer.on('mouseover', function(){
                    layer.setStyle(configs.styles.SpatialReferencHovereStyle)
                });

                layer.on('mouseout', function(){
                    layer.setStyle(configs.styles.SpatialReferenceStyle)
                });
                
                layer.on('click',  function (){
                    let modal = new ModalUer(feature.properties, 'Municipio',{
                        "Departamento": feature.properties.nombre_dpto,
                        "Municipio": feature.properties.nom_municipio
                    }, sist, objFetch)

                    sidebar.setContent(modal.content)
                    modal._disableNavs(sist)
                    sidebar.show()
                })
            }}).addTo(map);

            map.fitBounds(eventosMunicipio.getBounds())
            layerControl.addOverlay({
                active:true,
                name: "Municipios",
                icon: '<i class="fas fa-square txt-fao opacity-fao"></i>',
                layer: eventosMunicipio            
            })
            evalDataResponse('success','Datos añadidos correctamente', '#004884');
        }
        else {
            evalDataResponse('error','No hay datos para los filtros seleccionados', 'red');
        }

    }).catch((err) => {evalDataResponse('error',err, 'red');})
}

const returnDepartamentos = (sist, event, dpto, inif, finalf) =>{

    let objFetch = {
        "obj": {
            "prodSis": sist,
            "tipoEvento": event,
            "cod_dpto": dpto,
            "fechaInicial": inif,
            "fechaFinal": finalf
        }
    };

    informationEndPoint('filterUER',objFetch).then((data) => {
    
        let response = (data.message)

        if(response.dpto.length>0){

            sidebarDefaultInformation();
            clearMap();

            document.getElementById("mymap").classList.toggle('active');
	        document.getElementById("right_sidebar").classList.toggle('active');
            if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)){
                ''
            }else{
                sidebar.show()
            }

            eventosDepartamento = L.geoJSON(response.dpto[0].row_to_json,{onEachFeature: function(feature, layer){

                layer.setStyle(configs.styles.SpatialReferenceStyle)

                layer.on('mouseover', function(){
                    layer.setStyle(configs.styles.SpatialReferencHovereStyle)
                });
                
                layer.on('mouseout', function(){
                    layer.setStyle(configs.styles.SpatialReferenceStyle)
                });
                    
                layer.on('click',  function (){
                    let modal = new ModalUer(feature.properties, 'Departamento',{
                        "Departamento": feature.properties.nombre_dpto
                    }, sist, objFetch)

                    sidebar.setContent(modal.content)
                    modal._disableNavs(sist)
                    sidebar.show()
                })
            }}).addTo(map);

            map.fitBounds(eventosDepartamento.getBounds())
            layerControl.addOverlay({
                active:true,
                name: "Departamentos",
                icon: '<i class="fas fa-square txt-fao opacity-fao"></i>',
                layer: eventosDepartamento            
            })

            evalDataResponse('success','Datos añadidos correctamente', '#004884');
        }
        else {
            evalDataResponse('error','No hay datos para los filtros seleccionados', 'red');
        }

    }).catch((err) => {evalDataResponse('error',err, 'red');})
}

const returnPuntos = (sist, event, inif, finalf) =>{

    let objFetch = {
        "obj": {
            "prodSis": sist,
            "tipoEvento": event,
            "fechaInicial": inif,
            "fechaFinal": finalf
        }
    };
    
    informationEndPoint('filter', objFetch).then((data) => {
        
        let response = (data.message)

        if(response.eventos.length>0){
            let puntos = [];    
            response.eventos.forEach((evento) => {
                let obj = {
                    "type": "Feature",
                    "properties": evento,
                    "geometry": {
                        "type": "Point",
                        "coordinates": [evento.coord_y, evento.coord_x]
                    }
                }
                puntos.push(obj)
            })

            sidebarDefaultInformation();
            clearMap();
            
            document.getElementById("mymap").classList.toggle('active');
	        document.getElementById("right_sidebar").classList.toggle('active');
            if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)){
                ''
            }else{
                sidebar.show()
            }   

            let legendNames = []
        
            eventosPuntuales = L.geoJSON(puntos, {

                pointToLayer: function (feature, latlng) {
                    return L.marker(latlng, {icon: iconType(feature)})
                }, 
                
                onEachFeature: function (feature, layer) {

                    legendNames.push(feature.properties.tipo_evento);

                    layer.on('click',  function (){

                        if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)){
                            ''
                          }else{
                            layer.bounce(2)
                          }

                        let modal = new ModalUer(feature.properties, 'Evento',{
                            "Tipo de evento": feature.properties.tipo_evento,
                            "Fecha de reporte": feature.properties.fecha_registro_evento,
                            "Municipio": feature.properties.nom_municipio,
                            "Departamento": feature.properties.nombre_dpto,
                            "Coordenada X": feature.properties.coord_x,
                            "Coordenada Y": feature.properties.coord_y,
                        }, sist)

                        sidebar.setContent(modal.content)
                        modal._disableNavs(sist)
                        sidebar.show()
                        
                        if(feature.properties.ruta){
                            
                            informationEndPoint('routes', {"id_evento": feature.properties.cod_evento}).then((data) => {
                                
                                let response = (data.message)
                                
                                if (response.length > 0) {
                     
                                    response.forEach( (route, i) => {
                                            
                                        if(route.ruta.split(".")[2]==="jpg" || route.ruta.split(".")[2]==="png" || route.ruta.split(".")[2]==="jpeg"){
                                    
                                            let ruta = `${jwt_decode(urlEndPoint).url}/visor/files?ruta=${route.ruta}`

                                            if (i === 0) {
                                                $('#galeria').append(
                                                    `<a class="venobox" data-gall="myGallery" href="${ruta}"><button class="btn bg-dark-fao mb-4">Ver imagenes</button></a>`
                                                )
                                            }
                                            else {
                                                $('#galeria').append(
                                                    `<a class="venobox" data-gall="myGallery" href="${ruta}"></a>`
                                                )
                                            }

                                            $(".venobox").venobox({
                                                framewidth : 'auto',                         
                                                frameheight: screen.height*0.6
                                            });  
                                        } 
                                    })                     
                                } 
                            }).catch((error) => {console.log(error)})
                        }
                    })
                    featureSubGroupAssignment(feature,layer)
                }
            });

            legendNames = (_.keys(_.countBy(legendNames, function(names) { return names})));
            
            legendNames.forEach((name) => {
                layerControl.addOverlay({
                    active:true,
                    name: `Eventos de tipo ${name}`,
                    icon: `<img src="${configs.images[name]}" width="18px"/>`,
                    layer: eventTypeSubGroup[name]            
                })
            })

            clusterGroupManager('add')
            map.fitBounds(eventosPuntuales.getBounds())
            evalDataResponse('success','Datos añadidos correctamente', '#004884');

        }
        else {
            evalDataResponse('error','No hay datos para los filtros seleccionados', 'red');
        }
        
    }).catch((err) => {evalDataResponse('error',err, 'red');})    
}

export {
    returnPuntos,
    returnMunicipios,
    returnDepartamentos
}
