function goto_cve(textbox_id) {
    return function () {
        if (typeof (Storage) !== "undefined") {
            localStorage.setItem("sidebar", "open")
        }

        window.location.pathname = "cve/" + document.getElementById(textbox_id).value
        // Return false to avoid the real form submission
        return false
    }
}
