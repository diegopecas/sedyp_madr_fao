export class TermsAndConditions{
    constructor(data){
        return Swal.fire({
            html: data,
            showCloseButton: false,
            showCancelButton: false,
            focusConfirm: false,
            confirmButtonText: 'Aceptar y continuar',
            width: 1000,
            backdrop: true,
            allowOutsideClick: false,
            confirmButtonColor:'#004884',
        })
    }
}
