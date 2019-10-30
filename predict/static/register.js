function arePassAndConfirmIdentical(confirm_ele) {
   
    password_ele = document.getElementById('password')
    if ((confirm_ele.value !== document.getElementById('password').value)) {
        confirm_ele.setCustomValidity('The password and confirm password inputs must be matching!');
    } else {  
        confirm_ele.setCustomValidity('');
    }
}

function clearPass(){
    document.getElementById("password").value = ""
    document.getElementById("confirm_password").value = ""
}