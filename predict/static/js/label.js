var timer;

document.addEventListener("DOMContentLoaded", (event) => {
    labelInputs = document.querySelectorAll(".label-input")

    labelInputs.forEach((element) => {
        element.addEventListener("input", labelsChanged)
    })

    repoInputs = document.querySelectorAll(".repo-input")

    repoInputs.forEach((element) => {
        element.addEventListener("input", labelsChanged)
    })
})

function introducesVulnerability(cve_id, repo_name, repo_user, intro_file, intro_hash) {
    // TODO need to prompt user for fix file and fix hash here...
    // createLabel(cve_id, repo_name, repo_user, null, null, intro_file, intro_hash, null)
}

function fixesVulnerability(cve_id, repo_name, repo_user, fix_file, fix_hash) {
    // createLabel(cve_id, repo_name, repo_user, fix_file, fix_hash, null, null, null)
}

function labelsChanged() {
    // Update values after .5 seconds of no edits
    clearTimeout(timer)
    timer = setTimeout(updateLabels, 500)
}

function getLabels() {
    labelGroups = document.querySelectorAll(".user-label-group")

    labels = []

    group_num = 0

    groups = labelGroups.forEach((element) => {
        repoUser = element.querySelector(".repo-user").value,
        repoName = element.querySelector(".repo-name").value,
        labelInputs = element.querySelectorAll(".user-label")

        label_num = 0

        labelInputs.forEach((element) => {
            labels.push({
                group_num: group_num,
                label_num: label_num++,
                repo_user: repoUser,
                repo_name: repoName,
                fix_file: element.querySelector(".fix-file").value,
                fix_hash: element.querySelector(".fix-hash").value,
                intro_file: element.querySelector(".intro-file").value,
                intro_hash: element.querySelector(".intro-hash").value,
                comment: "comments not supported yet TODO",
            })
        })
        group_num++
    })

    return labels
}

function updateLabels() {
    data = {
        cve_id: document.getElementById("user-labels").dataset.cve,
        labels: getLabels()
    }

    $.ajax({
        type: "PUT",
        url: "/label", 
        data: JSON.stringify(data),
        contentType: "application/json",
        success: labelUpdateSucceeded,
        error: labelUpdateFailed
    })
}

function labelUpdateSucceeded(data) {
    span = document.getElementById("update-status")
    span.textContent = "Saved!"
    span.className = "text-success"

    $(span).fadeIn(100).fadeOut(200)
}

function labelUpdateFailed(data) {
    span = document.getElementById("update-status")
    span.textContent = "Failed to Save"
    span.className = "text-danger"

    $(span).fadeIn(100).fadeOut(200)

    console.log(data)
}
