function checkPassAndConfirm() {
    password = document.getElementById("password")
    confirm = document.getElementById("confirm")
    if (password.value !== confirm.value) {
        confirm.setCustomValidity("Your passwords do not match!");
    } else {  
        confirm.setCustomValidity("");
    }
}
