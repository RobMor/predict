function missing_commit_info_page(cve) {
    return function () {
        repo = $("#missing-repo").val()
        commit = $("#missing-commit").val()

        document.getElementById("missing-button").innerHTML = "<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span>"

        window.location.pathname = rootUrl + "cve/" + cve + "/info/" + repo + "/" + commit

        // Return false to avoid the real form submission
        return false
    }
}

function openLabels() {
    $("#labels").addClass("active")
    $("#label-tab").addClass("active")

    $("#cve-info").removeClass("active")
    $("#cve-tab").removeClass("active")

    // Make sure all label textboxes are properly sized when we switch tabs
    $(".hidden-input").each(function() { resizeToContents(this) })
}

function openCVE() {
    $("#cve-info").addClass("active")
    $("#cve-tab").addClass("active")

    $("#labels").removeClass("active")
    $("#label-tab").removeClass("active")
}

document.addEventListener("DOMContentLoaded", (event) => {
    $("hidden-input").on("input", resize)

    $("#label-tab").on("click", openLabels)
    $("#cve-tab").on("click", openCVE)
})

function resize(event) {
    resizeToContents(event.target)
}

function resizeToContents(element) {
    text = $(element).val()
    if (text.length === 0)
        text = element.placeholder

    $("#hidden-text").text(text)
    $(element).width($("#hidden-text").width() + 4)
}

function addLabel(button) {
    group = button.closest(".user-label-group")

    addLabelToGroup(group, null, null, null, null)

    labelsChanged()
}

function addLabelToGroup(group, fixFile, fixHash, introFile, introHash) {
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

function removeLabel(button) {
    label = button.closest(".user-label")
    label.remove()

    labelsChanged()
}

function addGroupWithLabel() {
    group = addGroup(null, null)
    addLabelToGroup(group, null, null, null, null)
}

function addGroup(repoUser, repoName) {
    newGroup = $(labelGroupElement).clone()

    $(newGroup).find(".repo-user").val(repoUser)
    $(newGroup).find(".repo-name").val(repoName)

    $("#user-labels").append(newGroup)

    labelsChanged()

    return newGroup
}

function removeGroup(button) {
    group = button.closest(".user-label-group")
    group.remove()

    labelsChanged()
}
