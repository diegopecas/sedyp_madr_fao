class IntroWalkThrough{

    constructor() {
     this._walkthrough()
    }
  
    _walkthrough() {
        introJs().setOptions({
            showProgress:true,
            exitOnOverlayClick:false,
            doneLabel:'Cerrar',
            skipLabel:'Saltar',
            nextLabel:'Siguiente',
            prevLabel:'Anterior',
            hidePrev:true,
            exitOnEsc:false,
            showButtons:true,
            showBullets: true,
            steps: [
                {   
                    intro: 'Bienvenido al visor geográfico para la consulta de daños y perdidas del sector agropecuario &#128075; &#128075;. Hagamos un tour de la aplicación para explorar su contenido.'
                },
                {
                    element: document.querySelector('.leaflet-control-zoom'),
                    intro: 'Aquí podrás controlar el zoom del mapa. Tambien puedes hacerlo con la rueda del mouse si te encuentras en un dispositivo de escritorio &#128269;&#128269;',
                    position: 'right'
                },
                {
                    element: document.querySelector('.fa-home'),
                    intro: 'Aquí podrás resturar el zoom del visor geográfico a la vista inicial &#127757;&#127757;',
                    position: 'right'
                },
                {
                    element: document.querySelector('.fa-bars'),
                    intro: 'Aquí podrás desplegar u ocultar el menú de filtros &#128195;&#128195;',
                    position: 'right'
                },
                {
                    element: document.querySelector('.fa-info'),
                    intro: 'Aquí podrás consultar nuevamente los Términos y Condiciones de la aplicación &#128195;&#128195;',
                    position: 'right'
                },
                {
                    element: document.querySelector('.leaflet-panel-layers'),
                    intro: 'Este es el control de capas geográficas donde se irán incorporando las entidades a medida que se visualicen en el mapa &#128064;&#128064;',
                    position: 'left'
                },
                { 
                    element: document.querySelector('.needs-validation'),
                    intro: 'Este es el menú de filtros, podrás seleccionar entre las diferentes opciones para consultar información espacial y alfanumerica &#127759;&#128200;',
                    position: 'left'
                },
                {
                    element: document.querySelector('#col-smlapseZero'),
                    intro: 'Aquí eliges el tipo de visualización',
                    position: 'left'
                },
                {
                    element: document.querySelector('#col-smlapseOne'),
                    intro: 'Aquí eliges uno o varios sistemas productivos',
                    position: 'left'
                },
                {
                    element: document.querySelector('#col-smlapseTwo'),
                    intro: 'Aquí eliges el tipo de evento',
                    position: 'left'
                },
                {
                    element: document.querySelector('#col-smlapseFour'),
                    intro: 'Aquí eliges el rango de fechas en el que se desea consultar la información',
                    position: 'left'
                },
                {   
                    intro: 'El tour ha finalizado, bienvenido a la aplicación'
                }
            ]
        }).start().oncomplete(function() {
            localStorage.setItem('walkthrough', 'true')
        });
  }
}

export {IntroWalkThrough}