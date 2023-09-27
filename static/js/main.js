var IceContDate=document.getElementsByClassName('IceContDate')
var IceOpt =document.getElementById('IceOpt')
var FechasIce = document.getElementsByClassName('FechasIce')
IceOpt.addEventListener('change',()=>{
    let selected = IceOpt.value;
    for (let i = 0; i < IceContDate.length; i++) {
        if (selected === 'ice') {
            IceContDate[i].style.display = 'table-row'; // or 'table-row', 'block', etc., based on your HTML structure
            FechasIce[i].setAttribute('required','')
        } else {
            IceContDate[i].style.display = 'none';
            FechasIce[i].removeAttribute('required')
        }
    }
})  
