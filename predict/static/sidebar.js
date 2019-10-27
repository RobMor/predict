function toggleSidebar() {
    active = document.getElementById("sidebar").classList.toggle("active");
    document.getElementById("overlay").classList.toggle("active", active);
    if (typeof (Storage) !== "undefined") {
        localStorage.setItem("sidebar_status", active ? "open" : "closed")
    }
}


window.onload = function () {
    // Sidebar functionality
    sidebar = document.getElementById("sidebar");
    overlay = document.getElementById("overlay");
    
    sidebar.classList.add("notransition")

    if (typeof (Storage) !== "undefined") {
        // If the sidebar was open before, open it again...
        if (localStorage.getItem("sidebar_status") === "open") {
            sidebar.classList.toggle("active", true);
            overlay.classList.toggle("active", true);
        }
    }

    sidebar.offsetHeight; // Trigger a "reflow"
    sidebar.classList.remove("notransition")

    // Check for the enter key being pressed in the sidebar input field
    document.getElementById("cve-input").addEventListener("keydown", function (e) {
        if (e.keyCode === 13) {  // Checks whether the pressed key is "Enter"
            goto_cve(e); /* In cve_query.js */
        }
    });
}
