function goto_cve(textbox_id, button_id) {
    return function () {
        cve = document.getElementById(textbox_id).value
        
        // If the user actually gave us a CVE
        if (cve) {
            // Change the button to a loading icon!
            document.getElementById(button_id).innerHTML = "<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span>"
            
            setSidebarOpenOnPageLoad()
            
            // Navigate to the CVE's page
            window.location.pathname = "cve/" + cve
        }
        // Return false to avoid the real form submission
        return false
    }
}
