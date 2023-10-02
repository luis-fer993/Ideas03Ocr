var advancedContDate=document.getElementsByClassName('advancedContDate')
var advancedOpt =document.getElementById('advanced')
var required = document.getElementsByClassName('required')
var Estudio = document.getElementById('Estudio')
advancedOpt.addEventListener('change',()=>{
    let selected = advancedOpt.value;
    for (let i = 0; i < advancedContDate.length; i++) {
        if (selected === '1') {
            advancedContDate[i].style.display = 'table-row'; // or 'table-row', 'block', etc., based on your HTML structure
            required[i].setAttribute('required','')
            while (Estudio.options.length > 0) {
                Estudio.remove(0);
            }
        } else {
            advancedContDate[i].style.display = 'none';
            required[i].removeAttribute('required')
            Estudio.setAttribute('required','')
            Estudio.addEventListener('click',()=>{
                window.location.href=`/test`
            })
        }
    }
})  

var AmbienteEstudios= document.getElementById('AmbienteEstudios')
//how to select the option by value content 
AmbienteEstudios.addEventListener('change',()=>{
    if (AmbienteEstudios.value=='Ambos'){
        Swal.fire('Atencion',
        'Escoger los dos ambientes puede generar un mayor tiempo de carga.',
        'info')
    }
})
