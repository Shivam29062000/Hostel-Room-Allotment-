document.addEventListener('DOMContentLoaded',()=>{
    let msg = document.getElementById('student_message');
    msg.addEventListener('keyup', event =>{
        event.preventDefault();
        if(event.keyCode===13){
            document.getElementById('send_message').click();
        }
    })
})