function goto_commit(cve) {
    return function () {
        repo = document.getElementById("repo").value
        commit = document.getElementById("commit").value

        document.getElementById("missing-button").innerHTML = "<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span>"

        window.location.pathname = "cve/" + cve + "/info/" + repo + "/" + commit

        // Return false to avoid the real form submission
        return false
    }
}
