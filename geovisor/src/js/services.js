import jwt_decode from 'jwt-decode'

const spin = document.querySelector('#spin')
const optionCreator = (list, text, value, type = null, optionContainer = null) => {
    let opt = document.createElement("option")
    opt.text = text
    opt.value = value

    if(!list){
        (optionContainer[type]).push(opt)    
    }
    else {
        list.append(opt)
    }
    
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

const informationEndPoint = async (url, body, jseable = true) => {
    spin.classList.remove('hidden')
    return await fetch(
        `${jwt_decode(urlEndPoint).url}visor/${url}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        }
    ).then((data) => {
        spin.classList.add('hidden')
        if(data.ok && data.status===200){
            return (jseable) ? data.json() : data
        }
        else {
            throw data.statusText
        }           
    }).catch((err) => {throw err});
}

const defaultSidebarInformation =  async (sisProductivo, tipoEvento, fechaMinima, optionContainer) => {
    await fetch(
        `${jwt_decode(urlEndPoint).url}visor/`
    ).then((data)=>{
        if(data.ok && data.status===200){
            (data.json()).then((datos)=>{
                let response = (datos.message)
                response.sistemasProductivos.forEach((sistema)=>{
                    optionCreator(sisProductivo,sistema.sistema_productivo_afectado, sistema.cod_sis_prod_afec)
                })
                $('#sistema_productivo').selectpicker();

                response.tiposEventos.forEach((evento)=>{
                    optionCreator(tipoEvento,evento.tipo_evento, evento.cod_tip_evento)
                })
                $('#tipo_evento').selectpicker();

                response.municipiosEvento.forEach((municipio)=>{
                    optionCreator(null,municipio.nom_municipio, municipio.cod_municipios, 'Municipio',optionContainer)
                })

                response.departamentosEvento.forEach((departamento)=>{
                    optionCreator(null,departamento.nombre_dpto, departamento.cod_dpto, 'Departamento', optionContainer)
                })

                fechaMinima.setAttribute("value",response.primerFecha)
                fechaMinima.setAttribute("min",response.primerFecha)
            })
        }
    }).catch((err) => {evalDataResponse('error',err, 'red')});
}

export {
    defaultSidebarInformation,
    informationEndPoint
}