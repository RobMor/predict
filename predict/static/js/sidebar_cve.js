/* --- Sidebar Functionality --- */

document.addEventListener("DOMContentLoaded", (event) => {
    $(".hidden-input").each(function () {
        this.addEventListener("input", resize)
    })

    $("#label-tab").on("click", openLabelTab)
    $("#cve-tab").on("click", openCVETab)
})

function openLabelTab() {
    $("#labels").addClass("active")
    $("#label-tab").addClass("active")

    $("#cve-info").removeClass("active")
    $("#cve-tab").removeClass("active")

    // Make sure all label textboxes are properly sized when we switch tabs
    $(".hidden-input").each(function() { resizeToContents(this) })
}

function openCVETab() {
    $("#cve-info").addClass("active")
    $("#cve-tab").addClass("active")

    $("#labels").removeClass("active")
    $("#label-tab").removeClass("active")
}

function missingCommitLink() {
    repo = $("#missing-repo").val()
    commit = $("#missing-commit").val()

    // Set the button to a spinner
    document.getElementById("missing-button").innerHTML = "<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span>"

    window.location.pathname = rootUrl + "cve/" + currentCVE + "/info/" + repo + "/" + commit

    // Return false to avoid the real form submission
    return false
}

/* --- Label UI functionality --- */

function addGroup(repoUser=null, repoName=null) {
    newGroup = $(labelGroupElement).clone()

    $(newGroup).find(".repo-user").val(repoUser)
    $(newGroup).find(".repo-name").val(repoName)

    $(newGroup).find(".hidden-input").each(function () {
        this.addEventListener("input", resize)
        resizeToContents(this)
    })

    $(newGroup).find(".repo-input").each(function () {
        this.addEventListener("input", labelsChanged)
    })

    $("#user-labels").append(newGroup)

    labelsChanged()

    return newGroup
}

function addGroupWithLabel() {
    group = addGroup()
    addLabelToGroup(group)
}

function addLabelToGroup(group, fixFile=null, fixHash=null, introFile=null, introHash=null) {
    newLabelItem = document.createElement("li")
    newLabelItem.className = "list-group-item user-label"

    newLabel = $(labelElement).clone()

    $(newLabel).find(".fix-file").val(fixFile)
    $(newLabel).find(".fix-hash").val(fixHash)
    $(newLabel).find(".intro-file").val(introFile)
    $(newLabel).find(".intro-hash").val(introHash)

    $(newLabelItem).append(newLabel)

    $(group).find(".user-label-group-list").append(newLabelItem)

    $(newLabel).find(".hidden-input").each(function () {
        this.addEventListener("input", resize)
        resizeToContents(this)
    })

    $(newLabel).find(".label-input").each(function () {
        this.addEventListener("input", labelsChanged)
    })

    labelsChanged()

    return newLabel
}

function addLabel(button) {
    group = button.closest(".user-label-group")

    addLabelToGroup(group)

    labelsChanged()
}

function removeGroup(button) {
    group = button.closest(".user-label-group")
    group.remove()

    labelsChanged()
}

function removeLabel(button) {
    label = button.closest(".user-label")
    label.remove()

    labelsChanged()
}

/* --- Hidden Input Functionality --- */

function resize(event) {
    resizeToContents(event.target)
}

function resizeToContents(element) {
    text = $(element).val()
    if (text.length === 0)
        text = element.placeholder

    $("#hidden-text").text(text)
    $(element).width($("#hidden-text").width()+1)
}

/* --- Collapsing Additional Data Functionality --- */

function showAdditionalDataInputs(button) {
    button.onclick = function() { hideAdditionalDataInputs(this) }

    label = button.closest(".user-label")
    additionalData = label.querySelector(".additional-data-inputs")
    
    $(additionalData).collapse("show")

    icon = button.querySelector(".icon")
    $(icon).replaceWith($(triangleUpSVG).clone()[0])
}

function hideAdditionalDataInputs(button) {
    button.onclick = function() { showAdditionalDataInputs(this) }

    label = button.closest(".user-label")
    additionalData = label.querySelector(".additional-data-inputs")
    
    $(additionalData).collapse("hide")

    icon = button.querySelector(".icon")
    $(icon).replaceWith($(triangleDownSVG).clone()[0])
}

/* --- Labeling Functionality --- */

document.addEventListener("DOMContentLoaded", (event) => {
    labelInputs = document.querySelectorAll(".label-input")
    
    labelInputs.forEach((element) => {
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

var timer;

function labelsChanged() {
    // Update labels after .5 seconds of no edits
    clearTimeout(timer)

    timer = setTimeout(function () {
        labels = getLabels()

        updateLabels(currentCVE, labels, labelUpdateSucceeded, labelUpdateFailed)
    }, 500)
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
                comment: element.querySelector(".comments").value,
            })
        })

        group_num++
    })

    return labels
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
}
