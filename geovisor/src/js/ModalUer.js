import {informationEndPoint} from './services'
import {configs} from '../config/config'
const Rainbow = require('rainbowvis.js');
const spin = document.querySelector('#spin')

class ModalUer{

    content;
    navsIdentifiers = {
        "1": "sp_agricola",
        "2": "sp_pecuario",
        "3": "sp_forestal",
        "4": "sp_pesquero",
        "5": "sp_apicola"
    }

    constructor(feature, uer, tableProperties, sist, objFetch){

        let generalTable = this._TableBuilder(tableProperties)

        if(uer === "Evento"){
            this.content = this._ModalPointContent(feature, uer, generalTable)
        } 
        else {
            this.content = this._ModalPolygonContent(feature, uer, generalTable);

            (uer === "Municipio") ? objFetch.obj.cod_mun = feature.cod_municipios.toString() : objFetch.obj.cod_dpto = feature.cod_dpto.toString();

            (()=>{

                spin.classList.remove('hidden')
                informationEndPoint('graphs',objFetch).then((data) => {

                    spin.classList.add('hidden')
                    
                    if(data){

                        let info = data.message;
                        this._ChartBuilder('event_type_'+feature.cod_dane, 'basicProcess', 'doughnut', info.general, 'tipo_evento', 'cantidad_eventos','Número de eventos por tipo')
                        this._ChartBuilder('forestal_leftchart_'+feature.cod_dane, 'basicProcess', 'doughnut', info.forestal.esp_afectadas_tipo, 'especie_forestal_afectada', 'num_especie', 'Tipo de especies afectadas')
                        this._ChartBuilder('forestal_rightchart_'+feature.cod_dane, 'mediumProcess', 'doughnut', info.forestal.infra_valor, 'tipo_infraestructura',['valor_semilla','valor_fert','valor_pla','valor_maq'],'Valor por tipo de infraestructura afectada','','(COP)')
                        this._ChartBuilder('agricola_leftchart_'+feature.cod_dane,'tableProcess', '', info.agro.inf_plaguicida, ['Tipo de plagicida', 'Presentación', 'Kg', 'Litros', 'Valor (COP)'], ['tipo_plaguicida', 'presentacion','kg','litros','valor'],'')
                        this._ChartBuilder('agricola_rightchart_'+feature.cod_dane, 'basicProcess', 'bar', info.agro.semillas_por_cultivo,'tipo_cultivo','cantidad','Número de semillas por tipo de cultivo', 'Semillas','unidades')
                        this._ChartBuilder('pecuario_leftchart_'+feature.cod_dane,'tableProcess','',info.peq.animales_muertos_por_raza,['Nombre raza','Machos muertos', 'Hembras muertas'],['nombre_raza','machos_muertos','hembras_muertas'])
                        this._ChartBuilder('pecuario_rightchart_'+feature.cod_dane, 'concatProcess', 'line',info.peq.animales_muertos_por_fecha,['mes','anio'],'animales_muertos','Número de animales muertos por mes', 'Animales muertos')
                        this._ChartBuilder('pesquero_'+feature.cod_dane, 'basicProcess', 'doughnut', info.pesq.precio_por_tipo_act, 'tipo_activo','precio_pagado', 'Precio pagado por tipo de activo','','(COP)')
                    }
                }).catch((error) => {console.log(error)});
            })()
        }
    }

    _disableNavs(sist){
        sist.forEach((id)=>{           
            let nav = document.getElementById(this.navsIdentifiers[id])
            nav.classList.remove('disabled')
        })
    }
    _TableBuilder(tableProperties){
        let table = Object.entries(tableProperties)
        let vdm = document.createElement("tbody")

        table.forEach((vector)=> {
            let tr = document.createElement("tr")

            let th = document.createElement("th")
            th.scope = "row"
            th.innerText = vector[0]

            let td = document.createElement("td")
            td.innerText = vector[1]

            tr.appendChild(th)
            tr.appendChild(td)
            
            vdm.appendChild(tr)
        })
        
        return vdm
    }

    PropertyValidator(property){

        if(property){
            return `
            <h4 class="font-weight-bold">${(parseInt(property)).toLocaleString('es-CO')}</h4>
            `
        }
        else {
            return `
            <h4 class="font-weight-bold">0</h4>
            `
        }
    }
    
    _ModalPointContent(feature, uer, generalTable){
        return `
        
        <nav class="navbar navbar-dark bg-dark-fao">
            <button class="navbar-toggler txt-clarity-fao position-absolute float-left" type="button" data-toggle="collapse" data-target="#collapsibleNavbar" aria-controls="navbarToggleExternalContent" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
        </nav>

        <div class="collapse" id="collapsibleNavbar">
        <ul class="nav nav-tabs nav-fill" id="myTab" role="tablist">
        <li class="nav-item">
            <a class="nav-link active txt-fao" id="sp_general" data-toggle="tab" href="#general" role="tab" aria-controls="general" aria-selected="true"><i class="fas fa-info"></i> Información general</a>
        </li>
        <li class="nav-item">
            <a class="nav-link txt-fao disabled" id="sp_forestal" data-toggle="tab" href="#forestal" role="tab" aria-controls="sp_forestal" aria-selected="false"><i class="fas fa-tree"></i> Forestal</a>
        </li>
        <li class="nav-item">
            <a class="nav-link txt-fao disabled" id="sp_agricola" data-toggle="tab" href="#agricola" role="tab" aria-controls="sp_agricola" aria-selected="false"><i class="fas fa-seedling"></i> Agrícola</a>
        </li>
        <li class="nav-item">
            <a class="nav-link txt-fao disabled" id="sp_pecuario" data-toggle="tab" href="#pecuario" role="tab" aria-controls="sp_pecuario" aria-selected="false"><i class="fas fa-kiwi-bird"></i> Pecuario</a>
        </li>
        <li class="nav-item">
            <a class="nav-link txt-fao disabled" id="sp_apicola" data-toggle="tab" href="#apicola" role="tab" aria-controls="sp_apicola" aria-selected="false"><i class="fab fa-forumbee"></i> Apícola</a>
        </li>
        <li class="nav-item">
            <a class="nav-link txt-fao disabled" id="sp_pesquero" data-toggle="tab" href="#pesquero" role="tab" aria-controls="sp_pesquero" aria-selected="false"><i class="fas fa-fish"></i> Pesquero</a>
        </li>
        </ul>
        </div>
        

        <div class="tab-content" id="myTabContent">                                                                        
        <div class="tab-pane fade show active" id="general" role="tabpanel" aria-labelledby="home-tab">
            
                <div class="row mt-1">
                    <div class="col-sm-12 mt-1">
                                <div class="card text-center">
                                    <div class="card-header bg-fao txt-fao">
                                    <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Datos del ${uer}</div>
                                    </div>
                                    <div class="card-body">
                                        <div class="table-responsive">
                                            <table class="table table-striped table-bordered">
                                                ${generalTable.innerHTML}
                                            </table>
                                        </div>
                                    </div>
                                    <div id="galeria"></div>
                                </div>
    
                    </div>
                </div>

                <div class="row mt-1">
                    <div class="col-sm-12 mt-1">
                
                        <div class="card text-center">

                            <div class="card-header bg-fao txt-fao">
                                <div class="float-left font-weight-bold">Información consolidada de sistemas productivos</div>
                            </div>

                            <div class="card-body">
                                <div class="row">
                                    <div class="col-sm-4">
                                        <div class="">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Forestal
                                            </div>
                                            <div class="card-body">
                                                ${this.PropertyValidator(feature.forestal_ha_afectada)}
                                                <div class="txt-light-fao">Hectáreas afectadas</div>
                                            </div>
                                        </div>   
                                        </div>
                                    </div>

                                    <div class="col-sm-4">
                                        <div class="">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Agrícola
                                            </div>
                                            <div class="card-body">
                                                ${this.PropertyValidator(feature.agricola_cantidad_semilla_siembra)}
                                                <div class="txt-light-fao">Cantidad de semillas</div>
                                            </div>
                                        </div>   
                                        </div>
                                    </div>

                                    <div class="col-sm-4">
                                        <div class="">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Pecuario
                                            </div>
                                            <div class="card-body">
                                                ${this.PropertyValidator(feature.pecuario_animales_muertos)}
                                                <div class="txt-light-fao">Animales muertos</div>
                                            </div>
                                        </div>   
                                        </div>
                                    </div>
                                    
                                </div>
                                <div class="row">
                                    <div class="col-sm-4">
                                        <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Apícola
                                            </div>
                                            <div class="card-body">
                                                ${this.PropertyValidator(feature.colmenas_afectadas)}                                      
                                                <div class="txt-light-fao">Colmenas afectadas</div>
                                            </div>
                                        </div>   
                                        </div>
                                    </div>

                                    <div class="col-sm-8">
                                        <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Pesquero
                                            </div>
                                            <div class="card-body">
                                                ${this.PropertyValidator(feature.redes_afectadas)}
                                                <div class="txt-light-fao">Número de redes afectadas</div>
                                            </div>
                                        </div>   
                                        </div>
                                    </div>
                                    
                                </div>
                            </div>
        
                        </div>
                    </div>  
                
            </div>
        </div>
        

        <div class="tab-pane fade" id="forestal" role="tabpanel" aria-labelledby="home-tab">
                    <div class="card text-center">
                        <div class="card-header bg-fao txt-fao">
                            <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Indicadores del sistema productivo forestal</div>
                            <a class="float-right font-weight-bold" href="${configs.reportsUrl.forestal}" target="_blank"> <i class="fas fa-external-link-alt"></i></i></a>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Costos totales directos
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ctdmf)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Costos totales indirectos
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ctimf)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Costos de producción
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_cpmf)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Valor económico de daños
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_vedmf)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>   
                            </div>

                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Costo de producción afectado
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_cpamf)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Valor pérdida económica plantación
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_vpepmf)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Porcentaje de pérdida estimada
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_pprmf)}</h4>
                                                <div class="txt-light-fao">Porcentaje (%)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Porcentaje de pérdida
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_pemf)}</h4>
                                                <div class="txt-light-fao">Porcentaje (%)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>         
                            </div>
                        </div>
                    </div>   
        </div>

        <div class="tab-pane fade" id="agricola" role="tabpanel" aria-labelledby="profile-tab">
            <div class="card text-center">
            <div class="card-header bg-fao txt-fao">
                <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Indicadores del sistema productivo agrícola</div>
                <a class="float-right font-weight-bold" href="${configs.reportsUrl.agricola}" target="_blank"> <i class="fas fa-external-link-alt"></i></i></a>
            </div>
            <div class="card-body">

                <div class="row">
                    <div class="col-sm-6">
                        <div class="">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Costos totales directos
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ctdma)}</h4>
                                    <div class="txt-light-fao">Pesos (COP)</div>
                                </div>
                            </div>   
                        </div>
                    </div>

                    <div class="col-sm-6">
                        <div class="">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Costos totales indirectos
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ctima)}</h4>
                                    <div class="txt-light-fao">Pesos (COP)</div>
                                </div>
                            </div>   
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-sm-6">
                        <div class="mt-4">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Costos totales
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ctma)}</h4>
                                    <div class="txt-light-fao">Pesos (COP)</div>
                                </div>
                            </div>   
                        </div>
                    </div>

                    <div class="col-sm-6">
                        <div class="mt-4">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Valor de la pérdida económica
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_vpecma)}</h4>
                                    <div class="txt-light-fao">Pesos (COP)</div>
                                </div>
                            </div>   
                        </div>
                    </div>   
                </div>

                <div class="row">
                    <div class="col-sm-6">
                        <div class="mt-4">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Porcentaje de pérdida económica en los cultivos
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_pema)}</h4>
                                    <div class="txt-light-fao">Porcentaje (%)</div>
                                </div>
                            </div>   
                        </div>
                    </div>

                    <div class="col-sm-6">
                        <div class="mt-4">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Valor económico de daños en los cultivos
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_vedma)}</h4>
                                    <div class="txt-light-fao">Pesos (COP)</div>
                                </div>
                            </div>   
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-sm-12">
                        <div class="mt-4">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                    Porcentaje de pérdida en el rendimiento de los cultivos
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_pprdcma)}</h4>
                                    <div class="txt-light-fao">Porcentaje (%)</div>
                                </div>
                            </div>   
                        </div>
                    </div>
                </div>
            </div>
        </div>
        </div>

        <div class="tab-pane fade" id="pecuario" role="tabpanel" aria-labelledby="contact-tab">
            <div class="card text-center">
            <div class="card-header bg-fao txt-fao">
                <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Indicadores del sistema productivo pecuario</div>
                <a class="float-right font-weight-bold" href="${configs.reportsUrl.pecuario}" target="_blank"> <i class="fas fa-external-link-alt"></i></i></a>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-sm-6">
                        <div class="">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Costos fijos pecuarios
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_cfpmpeq)}</h4>
                                    <div class="txt-light-fao">Pesos (COP)</div>
                                </div>
                            </div>   
                        </div>
                    </div>

                    <div class="col-sm-6">
                        <div class="">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Costos variables pecuarios
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_cvpmpeq)}</h4>
                                    <div class="txt-light-fao">Pesos (COP)</div>
                                </div>
                            </div>   
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-sm-6">
                        <div class="mt-4">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Costos totales pecucarios
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ctmpeq)}</h4>
                                    <div class="txt-light-fao">Pesos (COP)</div>
                                </div>
                            </div>   
                        </div>
                    </div>

                    <div class="col-sm-6">
                        <div class="mt-4">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Animales muertos del modulo
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ammpeq)}</h4>
                                    <div class="txt-light-fao">Unidad(es)</div>
                                </div>
                            </div>   
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-sm-6">
                        <div class="mt-4">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Valor de animales muertos
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_vammpeq)}</h4>
                                    <div class="txt-light-fao">Pesos (COP)</div>
                                </div>
                            </div>   
                        </div>
                    </div>

                    <div class="col-sm-6">
                        <div class="mt-4">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Peso de animales muertos
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_pekgammpeq)}</h4>
                                    <div class="txt-light-fao">Kilogramos (Kg)</div>
                                </div>
                            </div>   
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-sm-6">
                        <div class="mt-4">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Pérdida del modulo
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ppmpeq)}</h4>
                                    <div class="txt-light-fao">Porcentaje (%)</div>
                                </div>
                            </div>   
                        </div>
                    </div>

                    <div class="col-sm-6">
                        <div class="mt-4">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Pérdida de la inversión
                                </div>
                                <div class="card-body">
                                    <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ppimpeq)}</h4>
                                    <div class="txt-light-fao">Porcentaje (%)</div>
                                </div>
                            </div>   
                        </div>
                    </div>   
                </div>
            </div>
        </div>
        </div>


        <div class="tab-pane fade" id="apicola" role="tabpanel" aria-labelledby="profile-tab">
            <div class="card text-center">
            <div class="card-header bg-fao txt-fao">
                <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Indicadores del sistema productivo apícola</div>
                <a class="float-right font-weight-bold" href="${configs.reportsUrl.apicola}" target="_blank"> <i class="fas fa-external-link-alt"></i></i></a>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-sm-12">
                        <div class="">
                        <div class="card text-center">
                            <div class="card-header bg-fao txt-fao">
                            Colmenas afectadas
                            </div>
                            <div class="card-body">
                                ${this.PropertyValidator(feature.colmenas_afectadas)}                                      
                                <div class="txt-light-fao">Unidad(es)</div>
                            </div>
                        </div>   
                        </div>
                    </div>
                </div>
            </div>
            </div>
        </div>

        <div class="tab-pane fade" id="pesquero" role="tabpanel" aria-labelledby="contact-tab">
        <div class="card text-center">
        <div class="card-header bg-fao txt-fao">
            <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Indicadores del sistema productivo pesquero</div>
            <a class="float-right font-weight-bold" href="${configs.reportsUrl.pesquero}" target="_blank"> <i class="fas fa-external-link-alt"></i></i></a>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-sm-12">
                    <div class="">
                        <div class="card text-center">
                            <div class="card-header bg-fao txt-fao">
                            Ingresos por faena
                            </div>
                            <div class="card-body">
                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ipfmpesq)}</h4>
                                <div class="txt-light-fao">Pesos (COP)</div>
                            </div>
                        </div>   
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-sm-12">
                    <div class="mt-4">
                        <div class="card text-center">
                            <div class="card-header bg-fao txt-fao">
                            Ingreso actual de pesca
                            </div>
                            <div class="card-body">
                                ${this.PropertyValidator(feature.ind_iapmpesq)}
                                <div class="txt-light-fao">Pesos (COP)</div>
                            </div>
                        </div>   
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-sm-12">
                    <div class="mt-4">
                        <div class="card text-center">
                            <div class="card-header bg-fao txt-fao">
                            Disminución de ingreso
                            </div>
                            <div class="card-body">
                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_dimpesq)}</h4>
                                <div class="txt-light-fao">Porcentaje (%)</div>
                            </div>
                        </div>   
                    </div>
                </div> 
            </div>
        </div>
        </div>
        </div>
        </div>`
    }


    _ModalPolygonContent(feature, uer, generalTable){
    
        let content =  `
        <nav class="navbar navbar-dark bg-dark-fao">
            <button class="navbar-toggler txt-clarity-fao position-absolute float-left" type="button" data-toggle="collapse" data-target="#collapsibleNavbar" aria-controls="navbarToggleExternalContent" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
        </nav>

        <div class="collapse" id="collapsibleNavbar">
        <ul class="nav nav-tabs nav-fill" id="myTab" role="tablist">
        <li class="nav-item">
            <a class="nav-link active txt-fao" id="sp_general" data-toggle="tab" href="#general" role="tab" aria-controls="general" aria-selected="true"><i class="fas fa-info"></i> Información general</a>
        </li>
        <li class="nav-item">
            <a class="nav-link txt-fao disabled" id="sp_forestal" data-toggle="tab" href="#forestal" role="tab" aria-controls="sp_forestal" aria-selected="false"><i class="fas fa-tree"></i> Forestal</a>
        </li>
        <li class="nav-item">
            <a class="nav-link txt-fao disabled" id="sp_agricola" data-toggle="tab" href="#agricola" role="tab" aria-controls="sp_agricola" aria-selected="false"><i class="fas fa-seedling"></i> Agrícola</a>
        </li>
        <li class="nav-item">
            <a class="nav-link txt-fao disabled" id="sp_pecuario" data-toggle="tab" href="#pecuario" role="tab" aria-controls="sp_pecuario" aria-selected="false"><i class="fas fa-kiwi-bird"></i> Pecuario</a>
        </li>
        <li class="nav-item">
            <a class="nav-link txt-fao disabled" id="sp_apicola" data-toggle="tab" href="#apicola" role="tab" aria-controls="sp_apicola" aria-selected="false"><i class="fab fa-forumbee"></i> Apícola</a>
        </li>
        <li class="nav-item">
            <a class="nav-link txt-fao disabled" id="sp_pesquero" data-toggle="tab" href="#pesquero" role="tab" aria-controls="sp_pesquero" aria-selected="false"><i class="fas fa-fish"></i> Pesquero</a>
        </li>
        </ul>
        </div>

        <div class="tab-content" id="myTabContent">                                                                        
        <div class="tab-pane fade show active" id="general" role="tabpanel" aria-labelledby="home-tab">
            
                <div class="row mt-1">
                    <div class="col-sm-12 mt-1">
                        <div class="card text-center">
                            <div class="card-header bg-fao txt-fao">
                                <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Datos del ${uer}</div>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-striped table-bordered">
                                        ${generalTable.innerHTML}
                                    </table>
                                </div>
                                <canvas id="event_type_${feature.cod_dane}"></canvas>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-sm-12 mt-1">
                
                        <div class="card text-center">

                            <div class="card-header bg-fao txt-fao">
                                <div class="float-left font-weight-bold">Información consolidada de sistemas productivos</div>
                            </div>

                            <div class="card-body">

                                <div class="row">
                                    <div class="col-sm-6">
                                        <div class="">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Forestal
                                            </div>
                                            <div class="card-body">
                                                ${this.PropertyValidator(feature.forestal_ha_afectada)}
                                                <div class="txt-light-fao">Hectáreas afectadas</div>
                                            </div>
                                        </div>   
                                        </div>
                                    </div>

                                    <div class="col-sm-6">
                                        <div class="">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Agrícola
                                            </div>
                                            <div class="card-body">
                                                ${this.PropertyValidator(feature.agricola_cantidad_semilla_siembra)}
                                                <div class="txt-light-fao">Cantidad de semillas</div>
                                            </div>
                                        </div>   
                                        </div>
                                    </div>
                                </div>

                                <div class="row">
                                    <div class="col-sm-6">
                                        <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Pecuario
                                            </div>
                                            <div class="card-body">
                                                ${this.PropertyValidator(feature.pecuario_animales_muertos)}
                                                <div class="txt-light-fao">Animales muertos</div>
                                            </div>
                                        </div>   
                                        </div>
                                    </div>
                        
                                    <div class="col-sm-6">
                                        <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Apícola
                                            </div>
                                            <div class="card-body">
                                                ${this.PropertyValidator(feature.colmenas_afectadas)}                                      
                                                <div class="txt-light-fao">Colmenas afectadas</div>
                                            </div>
                                        </div>   
                                        </div>
                                    </div>
                                </div>

                                <div class="row">
                                    <div class="col-sm-12">
                                        <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Pesquero
                                            </div>
                                            <div class="card-body">
                                                ${this.PropertyValidator(feature.redes_afectadas)}
                                                <div class="txt-light-fao">Número de redes afectadas</div>
                                            </div>
                                        </div>   
                                        </div>
                                    </div>
                                    
                                </div>
                            </div>
        
                        </div>
                    </div>  
            </div>
        </div>
        

        <div class="tab-pane fade" id="forestal" role="tabpanel" aria-labelledby="home-tab">
            <div class="tab-content" id="myTabContent">
                <div class="tab-pane fade show active" id="forestal_pageone" role="tabpanel" aria-labelledby="home-tab">
                    <div class="card text-center">
                        <div class="card-header bg-fao txt-fao">
                            <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Indicadores del sistema productivo forestal</div>
                            <a class="float-right font-weight-bold" href="${configs.reportsUrl.forestal}" target="_blank"> <i class="fas fa-external-link-alt"></i></i></a>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Costos totales directos
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ctdmf)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Costos totales indirectos
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ctimf)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Costos de producción
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_cpmf)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Valor económico de daños
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_vedmf)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                                
                            </div>

                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Costo de producción afectado
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_cpamf)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Valor pérdida económica plantación
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_vpepmf)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Porcentaje de pérdida estimada
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_pprmf)}</h4>
                                                <div class="txt-light-fao">Porcentaje (%)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Porcentaje de pérdida
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_pemf)}</h4>
                                                <div class="txt-light-fao">Porcentaje (%)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>         
                            </div>
                        </div>
                    </div>
                </div>
            
                <div class="tab-pane fade" id="forestal_pagetwo" role="tabpanel" aria-labelledby="profile-tab">
                    <div class="card text-center">
                        <div class="card-header bg-fao txt-fao">
                            <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Detalle de la novedad</div>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-sm-12">
                                    <canvas id="forestal_leftchart_${feature.cod_dane}"></canvas>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-sm-12">
                                    <canvas id="forestal_rightchart_${feature.cod_dane}"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <ul class="nav nav-tabs justify-content-center border-0 mt-1 pagination-sm" id="myTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <a class="nav-link active" id="home-tab" data-toggle="tab" href="#forestal_pageone" role="tab" aria-controls="home" aria-selected="true">1</a>
                </li>
                <li class="nav-item" role="presentation">
                    <a class="nav-link" id="profile-tab" data-toggle="tab" href="#forestal_pagetwo" role="tab" aria-controls="profile" aria-selected="false">2</a>
                </li>
            </ul>
           
            
        </div>

        <div class="tab-pane fade" id="agricola" role="tabpanel" aria-labelledby="profile-tab">
            <div class="tab-content" id="myTabContent">
                <div class="tab-pane fade show active" id="agricola_pageone" role="tabpanel" aria-labelledby="home-tab">
                    <div class="card text-center">
                        <div class="card-header bg-fao txt-fao">
                            <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Indicadores del sistema productivo agrícola</div>
                            <a class="float-right font-weight-bold" href="${configs.reportsUrl.agricola}" target="_blank"> <i class="fas fa-external-link-alt"></i></i></a>
                        </div>
                        <div class="card-body">

                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Costos totales directos
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ctdma)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Costos totales indirectos
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ctima)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Costos totales
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ctma)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Valor de la pérdida económica
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_vpecma)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>   
                            </div>

                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Porcentaje de pérdida económica en los cultivos
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_pema)}</h4>
                                                <div class="txt-light-fao">Porcentaje (%)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Porcentaje de pérdida en el rendimiento de los cultivos
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_pprdcma)}</h4>
                                                <div class="txt-light-fao">Porcentaje (%)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-sm-12">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Valor económico de daños en los cultivos
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_vedma)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="tab-pane fade" id="agricola_pagetwo" role="tabpanel" aria-labelledby="profile-tab">
                    <div class="card text-center">
                        <div class="card-header bg-fao txt-fao">
                            <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Detalle de la novedad</div>
                        </div>
                
                        <div class="card-body">
                            <div class="row justify-content-md-center">
                                <div class="col-sm-12" style="max-height:400px; overflow-y: scroll;">
                                    <div id="agricola_leftchart_${feature.cod_dane}"></div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-12">
                                    <canvas id="agricola_rightchart_${feature.cod_dane}" style="height:320px"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div> 
            </div>

            <ul class="nav nav-tabs justify-content-center border-0 mt-1 pagination-sm" id="myTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <a class="nav-link active" id="home-tab" data-toggle="tab" href="#agricola_pageone" role="tab" aria-controls="home" aria-selected="true">1</a>
                </li>
                <li class="nav-item" role="presentation">
                    <a class="nav-link" id="profile-tab" data-toggle="tab" href="#agricola_pagetwo" role="tab" aria-controls="profile" aria-selected="false">2</a>
                </li>
            </ul>
        </div>



        <div class="tab-pane fade" id="pecuario" role="tabpanel" aria-labelledby="contact-tab">
            <div class="tab-content" id="myTabContent">
                <div class="tab-pane fade show active" id="pecuario_pageone" role="tabpanel" aria-labelledby="home-tab">
                    <div class="card text-center">
                        <div class="card-header bg-fao txt-fao">
                            <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Indicadores del sistema productivo pecuario</div>
                            <a class="float-right font-weight-bold" href="${configs.reportsUrl.pecuario}" target="_blank"> <i class="fas fa-external-link-alt"></i></i></a>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Costos fijos pecuarios
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_cfpmpeq)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Costos variables pecuarios
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_cvpmpeq)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Costos totales pecucarios
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ctmpeq)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Animales muertos del modulo
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ammpeq)}</h4>
                                                <div class="txt-light-fao">Unidad(es)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                                
                            </div>

                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Valor de animales muertos
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_vammpeq)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Peso de animales muertos
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_pekgammpeq)}</h4>
                                                <div class="txt-light-fao">Kilogramos (Kg)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Pérdida del modulo
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ppmpeq)}</h4>
                                                <div class="txt-light-fao">Porcentaje (%)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>

                                <div class="col-sm-6">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Pérdida de la inversión
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ppimpeq)}</h4>
                                                <div class="txt-light-fao">Porcentaje (%)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                            </div>
                        </div>  
                    </div>
                </div>

                <div class="tab-pane fade" id="pecuario_pagetwo" role="tabpanel" aria-labelledby="profile-tab">
                    <div class="card text-center">
                        <div class="card-header bg-fao txt-fao">
                            <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Detalle de la novedad</div>
                        </div>
                
                        <div class="card-body">
                            <div class="row">
                                <div class="col-sm-12" style="height:250px; overflow-y: scroll;">
                                    <div id="pecuario_leftchart_${feature.cod_dane}"></div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-12 mt-4">
                                    <canvas id="pecuario_rightchart_${feature.cod_dane}" style="height:300px;"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div> 
            </div>

            <ul class="nav nav-tabs justify-content-center border-0 mt-1 pagination-sm" id="myTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <a class="nav-link active" id="home-tab" data-toggle="tab" href="#pecuario_pageone" role="tab" aria-controls="home" aria-selected="true">1</a>
                </li>
                <li class="nav-item" role="presentation">
                    <a class="nav-link" id="profile-tab" data-toggle="tab" href="#pecuario_pagetwo" role="tab" aria-controls="profile" aria-selected="false">2</a>
                </li>
            </ul>
        </div>


        <div class="tab-pane fade" id="apicola" role="tabpanel" aria-labelledby="profile-tab">
            <div class="card text-center">
                <div class="card-header bg-fao txt-fao">
                    <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Indicadores del sistema productivo apícola</div>
                    <a class="float-right font-weight-bold" href="${configs.reportsUrl.apicola}" target="_blank"> <i class="fas fa-external-link-alt"></i></i></a>
                </div>
                
                <div class="card-body">
                    <div class="row">
                        <div class="col-sm-12">
                            <div class="mt-4">
                            <div class="card text-center">
                                <div class="card-header bg-fao txt-fao">
                                Colmenas afectadas
                                </div>
                                <div class="card-body">
                                    ${this.PropertyValidator(feature.colmenas_afectadas)}                                      
                                    <div class="txt-light-fao">Unidad(es)</div>
                                </div>
                            </div>   
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="tab-pane fade" id="pesquero" role="tabpanel" aria-labelledby="contact-tab">
            <div class="tab-content" id="myTabContent">
                <div class="tab-pane fade show active" id="pesquero_pageone" role="tabpanel" aria-labelledby="home-tab">
                    <div class="card text-center">
                        <div class="card-header bg-fao txt-fao">
                            <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Indicadores del sistema productivo pesquero</div>
                            <a class="float-right font-weight-bold" href="${configs.reportsUrl.pesquero}" target="_blank"> <i class="fas fa-external-link-alt"></i></i></a>
                        </div>
                        
                        <div class="card-body">
                            <div class="row">
                                <div class="col-sm-12">
                                    <div class="">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                                Ingresos por faena
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_ipfmpesq)}</h4>
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-sm-12">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Ingreso actual de pesca
                                            </div>
                                            <div class="card-body">
                                                ${this.PropertyValidator(feature.ind_iapmpesq)}
                                                <div class="txt-light-fao">Pesos (COP)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-sm-12">
                                    <div class="mt-4">
                                        <div class="card text-center">
                                            <div class="card-header bg-fao txt-fao">
                                            Disminución de ingreso
                                            </div>
                                            <div class="card-body">
                                                <h4 class="font-weight-bold">${this.PropertyValidator(feature.ind_dimpesq)}</h4>
                                                <div class="txt-light-fao">Porcentaje (%)</div>
                                            </div>
                                        </div>   
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="tab-pane fade" id="pesquero_pagetwo" role="tabpanel" aria-labelledby="profile-tab">
                    <div class="card text-center">
                        <div class="card-header bg-fao txt-fao">
                            <div class="float-left font-weight-bold"><i class="fas fa-map-marker-alt"></i> Detalle de la novedad</div>
                        </div>
                
                        <div class="card-body">
                            <div class="row">
                                <div class="col-sm-12">
                                    <canvas id="pesquero_${feature.cod_dane}"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <ul class="nav nav-tabs justify-content-center border-0 mt-1 pagination-sm" id="myTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <a class="nav-link active" id="home-tab" data-toggle="tab" href="#pesquero_pageone" role="tab" aria-controls="home" aria-selected="true">1</a>
                </li>
                <li class="nav-item" role="presentation">
                    <a class="nav-link" id="profile-tab" data-toggle="tab" href="#pesquero_pagetwo" role="tab" aria-controls="profile" aria-selected="false">2</a>
                </li>
            </ul>
        </div>
        </div>`

        return content
    }

    _ProcessData(id, process, arr, label, data) {

        let labels = []
        let datas = []

        if(process === "tableProcess"){

            let head = document.createElement("thead")
            let tr = document.createElement("tr")
            head.appendChild(tr)

            label.forEach((col)=>{
                let th = document.createElement("th")
                th.scope = "row"
                th.innerText = col
                tr.appendChild(th)       
            })

            let col = document.getElementById(id)
            let body = document.createElement("tbody")

            arr.forEach((vector)=> {

                let tr = document.createElement("tr")
                let th = document.createElement("th")
                th.scope = "row"
                th.innerText = vector[data[0]]
                tr.appendChild(th)

                data.forEach((element, i)=>{
                    if(i!==0){
                        let td = document.createElement("td")
                        td.innerText = vector[element]
                        tr.appendChild(td)
                    }
                })
        
                body.appendChild(tr)
            })
            
            let vdm2 = `
            <div class="table-responsive-lg">
                <table class="table table-striped table-bordered">
                    ${head.innerHTML}
                    ${body.innerHTML}
                </table>
            </div>
            `
            col.innerHTML = (vdm2)
        }

        if(process === "mediumProcess"){
            arr.forEach((elem,i)=>{
                labels.push(elem[label])
                datas.push(elem[data[i]])
            })
        }

        if(process === "concatProcess"){
            arr.forEach((elem)=>{
                labels.push(elem[label[0]]+'-'+elem[label[1]])
                datas.push(elem[data])
            })
        }

        if(process === "basicProcess"){
            arr.forEach((elem)=>{
                labels.push(elem[label])
                datas.push(elem[data])
            })
        }

        return {labels, datas}
    }

    _VisualizationBuilder(id, type, processedData, title, label, unit){

        let delayed;
        let ctx = document.getElementById(id)
        let colors;

        if((processedData.datas).length > 1){
            let myRainbow = new Rainbow();
            myRainbow.setSpectrum('#3366cc', '#e6effd');
            myRainbow.setNumberRange(1, (processedData.datas).length);

            colors = (processedData.datas).map((el, i)=> {
                return `#${myRainbow.colourAt(i+1)}`
            })
        }
        if((processedData.datas).length === 1){
            colors = ['#3366cc']
        }

        if (type === "doughnut"){
            new Chart(ctx, {
                type: type,
                data: {
                    labels: processedData.labels,
                    datasets: [{
                        data: processedData.datas,
                        backgroundColor: colors
                    }]
                },
                options: {
                    animation: {
                        onComplete: () => {
                            delayed = true;
                        },
                        delay: (context) => {
                            let delay = 0;
                            if (context.type === 'data' && context.mode === 'default' && !delayed) {
                                delay = context.dataIndex * 300 + context.datasetIndex * 100;
                            }
                            return delay;
                        },
                    },
                    plugins: {
                        scales:{
                            x:{
                                tickWidth:100
                            } 
                        },
                        title: {
                            display: true,
                            text: title
                         },
                         legend: {
                             display: true,
                             position: 'bottom',
                             align:'left',
                             maxWidth: 1,
                             fullSize:false,
                             labels:{
                                 padding: 1,
                                 font: {
                                    size: 9
                                }
                             }
                        },
                        tooltip: {
                            callbacks:{
                                label:function(tooltipItems, data) {
                                    return `${tooltipItems.label}: ${tooltipItems.formattedValue} ${(unit)?unit:''}`
                                }
                            }
                        }
                    }
                }
            })
        }

        if (type === "line"){
            new Chart(ctx, {
                type: type,
                data: {
                    labels: processedData.labels,
                    datasets: [{
                        label: label,
                        data: processedData.datas,
                        borderColor:'#3366cc',
                        backgroundColor: [
                            '#e6effd',
                        ]
                    }]
                },
                options: {
                    pointBackgroundColor: '#004884',
                    elements:{
                        line:{
                            backgroundColor:'white',
                            fill:true
                        },
                    },
                    responsive: true,
                    plugins: {
                      legend: {
                        position: 'bottom',
                      },
                      title: {
                        display: true,
                        text: title
                      }
                    }
                  }
            });
        }

        if (type === "bar"){
            new Chart(ctx, {
                type: type,
                data: {
                    labels: processedData.labels,
                    datasets: [{
                        label: label,
                        data: processedData.datas,
                        backgroundColor: colors
                    }]
                },
                options: {
                    scales:{
                        y: {
                            ticks: {
                                stepSize: 10
                            }
                        }
                    },
                    animation: {
                        onComplete: () => {
                            delayed = true;
                        },
                        delay: (context) => {
                            let delay = 0;
                            if (context.type === 'data' && context.mode === 'default' && !delayed) {
                                delay = context.dataIndex * 300 + context.datasetIndex * 100;
                            }
                            return delay;
                        },
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: title
                        },
                        legend: {
                            display: false,
                            position: 'bottom',
                            align:'left',
                            maxWidth: 10,
                            labels:{
                                boxWidth:20,
                                padding:5,
                                textAlign:'left'
                            }
                        },
                        tooltip: {
                            callbacks:{
                                label:function(tooltipItems, data) {
                                    return `${tooltipItems.label}: ${tooltipItems.formattedValue} ${(unit)?unit:''}`
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    _ChartBuilder(id, process, type, arr, label, data, title, tooltip=null, unit=null){
        
        let processedData = this._ProcessData(id, process, arr, label, data)
        this._VisualizationBuilder(id, type, processedData, title, tooltip, unit)
    }
}

export {ModalUer}
