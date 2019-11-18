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

function getGroup(repoUser, repoName) {
    groups = document.querySelectorAll(".user-label-group")

    for (i = 0; i < groups.length; i++) {
        existingUser = groups[i].querySelector(".repo-user").value
        existingName = groups[i].querySelector(".repo-name").value

        if (repoUser === existingUser && repoName === existingName) {
            return groups[i]
        }
    }
    
    return addGroup(repoUser, repoName)
}

function introducesVulnerability(repoUser, repoName, introFile, introHash) {
    group = getGroup(repoUser, repoName)
    addLabelToGroup(group, null, null, introFile, introHash)
    toggleSidebar()
    openLabels()
}

function fixesVulnerability(repoUser, repoName, fixFile, fixHash) {
    group = getGroup(repoUser, repoName)
    addLabelToGroup(group, fixFile, fixHash, null, null)
    toggleSidebar()
    openLabels()
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
        url: label_url, 
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
